#!/usr/bin/env python3
"""site-maintenance — deterministic, report-only monitor for registered client sites.

Plan: WORKSHOPS/plans/2026-11-04-site-maintenance-plan.md (CONVERGED, §15 fold).
Stdlib only (Python 3.11+ for tomllib). No model in the check or feed path.
Only the optional digest stage calls a model (tools-off, payload by file).

Subcommands
  weekly                 check -> feeds -> doctor -> notify -> digest (one run record)
  check                  per-site checks for every active site (standalone run)
  feeds [--only X]       security feeds: kev | nvd | hn | hugo (standalone run)
  kev                    daily KEV-only stack-match diff, no model, notify on high
  doctor                 arm-state vs live systemd / crontab state
  digest                 tools-off model summary of the latest run record
  validate               schema-check sites.toml and config.toml
  add PRJ-####           register a site: needs --evidence, baseline check, refuses high faults
  list [--all]           triage: open faults from faults.json
  show FAULT_ID          triage: one fault plus where to look
  suppress FAULT_ID      reason + expiry (<=180 days), still shown in run records
  resolve FAULT_ID       manual resolve with reason

Exit codes: 0 completed (faults may exist) · 1 refused (add/suppress/resolve gate) · 2 inconclusive
(control check failed) · 3 runner error.

Storage: $SITE_MAINT_HOME or ~/.pi/agent/maintenance — sites.toml, config.toml, faults.json,
runs/<id>.json, latest.json (symlink), state/feeds.json, digest-prompt.md. Files 0600.
Redaction rule: secret values are never stored. Findings carry pattern ID, path, line and the
first 12 hex of sha256(matched value) only. Response bodies are never persisted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import html.parser
import ipaddress
import json
import os
import re
import shutil
import socket
import ssl
import subprocess
import sys
import time
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

EXIT_OK, EXIT_REFUSED, EXIT_INCONCLUSIVE, EXIT_ERROR = 0, 1, 2, 3
UA = "Mozilla/5.0 (compatible; site-maintenance/1.0; report-only)"
MAX_PAGE = 2_000_000
MAX_PROBE = 4096
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ATOM_NS = "{http://www.w3.org/2005/Atom}"
BOGUS_PATH = "/maint-probe-404-7f3a9c"
TIMERS = ("site-maintenance.timer", "site-maintenance-kev.timer")

STACK_TAGS = {"wordpress", "php", "apache", "nginx", "hugo", "static"}
# Product-level keywords, matched on whole words. "apache" alone would also catch Apache Struts,
# Tomcat and friends, so apache matches only the httpd product names.
STACK_KEYWORDS = {
    "wordpress": [r"wordpress"], "php": [r"php"],
    "apache": [r"http server", r"http_server", r"httpd", r"apache http"],
    "nginx": [r"nginx"], "hugo": [r"hugo"], "static": [],
}
DRIFT_MODES = {"static-files", "build-output", "manifest", "none"}
SITE_KEYS = {"ref", "domain", "canonical", "repo_path", "site_root", "stack", "profile",
             "expiry", "state", "bootstrap", "evidence"}
PII_KEYS = {"contact", "email", "phone", "address", "name"}
PROFILE_KEYS = {"bogus_404_marker", "sitemap_expected", "drift_mode", "domain_check", "served_files"}
EXPIRY_KEYS = {"domain", "tls"}
REF_RE = re.compile(r"^PRJ-\d{4}$")
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Fixed secret pattern set (Q15 accepted). ID -> regex. Values are never stored.
SECRET_PATTERNS = [
    ("PRIVATE-KEY", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("AWS-ACCESS-KEY", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("STRIPE-LIVE-SECRET", re.compile(r"\bsk_live_[0-9A-Za-z]{16,}\b")),
    ("GOOGLE-API-KEY", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("GITHUB-TOKEN", re.compile(r"\bgh[pousr]_[0-9A-Za-z]{36,}\b")),
    ("SLACK-TOKEN", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,}\b")),
    ("DB-URI-CREDENTIALS", re.compile(r"\b(?:mysql|postgres(?:ql)?|mongodb(?:\+srv)?)://[^\s:/@'\"<>]+:[^\s@'\"<>]{4,}@[^\s'\"<>]+")),
    ("ENV-STYLE-SECRET", re.compile(r"(?i)\b(?:db_pass(?:word)?|secret[_-]?key|api[_-]?secret|client[_-]?secret|auth[_-]?token)\b[\"']?\s*[:=]\s*[\"'][^\"'\s]{8,}[\"']")),
    ("WP-DB-PASSWORD", re.compile(r"define\(\s*['\"]DB_PASSWORD['\"]\s*,\s*['\"][^'\"]+['\"]")),
]


def _has_html(b: bytes) -> bool:
    return b"<html" in b.lower() or b"<!doctype" in b.lower()


# Exposure probes: (check_id, path, signature-name, signature-fn, severity)
EXPOSURE_PROBES = [
    ("GIT-EXPOSED", "/.git/HEAD", "git-head", lambda b: bool(re.match(rb"ref: refs/", b)), "high"),
    ("GIT-EXPOSED", "/.git/config", "git-config", lambda b: b"[core]" in b and not _has_html(b), "high"),
    ("ENV-EXPOSED", "/.env", "env-file", lambda b: bool(re.search(rb"(?m)^[A-Z][A-Z0-9_]{2,}=", b)) and not _has_html(b), "high"),
    ("ENV-EXPOSED", "/wp-config.php.bak", "wp-config", lambda b: (b"DB_PASSWORD" in b or b"DB_NAME" in b) and not _has_html(b), "high"),
    ("SVN-EXPOSED", "/.svn/entries", "svn-entries", lambda b: bool(re.match(rb"^\d{1,2}\s*\n", b)) and not _has_html(b), "high"),
    ("DSSTORE-EXPOSED", "/.DS_Store", "ds-store", lambda b: b[4:8] == b"Bud1", "medium"),
    ("BACKUP-EXPOSED", "/backup.zip", "zip", lambda b: b[:4] == b"PK\x03\x04", "high"),
    ("BACKUP-EXPOSED", "/site.zip", "zip", lambda b: b[:4] == b"PK\x03\x04", "high"),
    ("BACKUP-EXPOSED", "/db.sql", "sql-dump", lambda b: bool(re.search(rb"(?i)CREATE TABLE|INSERT INTO|mysqldump", b)) and not _has_html(b), "high"),
]


class FeedError(Exception):
    pass


# ----------------------------------------------------------------- paths / io

class Paths:
    def __init__(self, home: str | None = None):
        base = home or os.environ.get("SITE_MAINT_HOME") or str(Path.home() / ".pi/agent/maintenance")
        self.home = Path(base)
        self.sites = self.home / "sites.toml"
        self.config = self.home / "config.toml"
        self.faults = self.home / "faults.json"
        self.runs = self.home / "runs"
        self.latest = self.home / "latest.json"
        self.state = self.home / "state"
        self.feeds_state = self.state / "feeds.json"
        self.lock = self.home / ".lock"
        self.digest_prompt = self.home / "digest-prompt.md"

    def ensure(self):
        for d in (self.home, self.runs, self.state):
            d.mkdir(parents=True, exist_ok=True)
            os.chmod(d, 0o700)


def now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def iso(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def atomic_write(path: Path, text: str, mode: int = 0o600):
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(tmp, mode)
    os.replace(tmp, path)


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def toml_val(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "[" + ", ".join(toml_val(x) for x in v) + "]"
    raise TypeError(f"unsupported TOML value {type(v).__name__}")


def dump_sites(sites: list[dict]) -> str:
    out = ["# Site registry. Engine-side, 0600. Written by site-maintenance.py; edit via `maint add` / validate.", ""]
    for s in sites:
        out.append("[[site]]")
        for k in ("ref", "domain", "canonical", "repo_path", "site_root", "stack", "state", "bootstrap", "evidence"):
            if k in s:
                out.append(f"{k} = {toml_val(s[k])}")
        out.append("")
        if s.get("profile"):
            out.append("[site.profile]")
            for k, v in s["profile"].items():
                out.append(f"{k} = {toml_val(v)}")
            out.append("")
        if s.get("expiry"):
            out.append("[site.expiry]")
            for k, v in s["expiry"].items():
                out.append(f"{k} = {toml_val(v)}")
            out.append("")
    return "\n".join(out) + "\n"


DEFAULT_CONFIG = {
    "armed": False,
    "control_hosts": [
        "https://www.cloudflare.com/cdn-cgi/trace",
        "https://www.gstatic.com/generate_204",
    ],
    "request_timeout_s": 15,
    "max_links": 200,
    "max_secret_urls": 50,
    "max_drift_files": 400,
    "max_drift_file_bytes": 5_242_880,
    "notify": True,
    "feeds": {
        "kev_url": "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
        "nvd_url": "https://services.nvd.nist.gov/rest/json/cves/2.0",
        "nvd_sleep_s": 6,
        "hn_url": "https://hn.algolia.com/api/v1/search_by_date",
        "hugo_url": "https://github.com/gohugoio/hugo/releases.atom",
        "window_days": 7,
        "window_cap_days": 30,
    },
    "digest": {"enabled": True, "model": "z-ai/glm-5.3-flash", "timeout_s": 240},
    "suppress": [],
}


def load_config(p: Paths) -> dict:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if p.config.exists():
        raw = tomllib.loads(p.config.read_text(encoding="utf-8"))
        for k, v in raw.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    if not isinstance(cfg["armed"], bool):
        raise ValueError("config.toml: armed must be a boolean")
    return cfg


def dump_config(cfg: dict) -> str:
    out = ["# site-maintenance config. `armed` is flipped only by the orchestrator at arm time (see skill)."]
    for k in ("armed", "control_hosts", "request_timeout_s", "max_links", "max_secret_urls",
              "max_drift_files", "max_drift_file_bytes", "notify"):
        out.append(f"{k} = {toml_val(cfg[k])}")
    for section in ("feeds", "digest"):
        out.append("")
        out.append(f"[{section}]")
        for k, v in cfg[section].items():
            out.append(f"{k} = {toml_val(v)}")
    for s in cfg.get("suppress", []):
        out.append("")
        out.append("[[suppress]]")
        for k in ("fault_id", "reason", "until", "added"):
            out.append(f"{k} = {toml_val(s[k])}")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------- registry / validation

def is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def validate_sites(sites: list) -> list[str]:
    errs: list[str] = []
    seen: set[str] = set()
    for i, s in enumerate(sites):
        tag = f"site[{i}]"
        if not isinstance(s, dict):
            errs.append(f"{tag}: not a table")
            continue
        for k in s:
            if k in PII_KEYS:
                errs.append(f"{tag}: PII-keyed field '{k}' is not permitted")
            elif k not in SITE_KEYS:
                errs.append(f"{tag}: unknown key '{k}'")
        for k in ("ref", "domain", "canonical", "repo_path", "site_root", "stack", "state"):
            if k not in s:
                errs.append(f"{tag}: missing required key '{k}'")
        ref = s.get("ref")
        if isinstance(ref, str):
            tag = f"site[{i}] {ref}"
            if not REF_RE.match(ref):
                errs.append(f"{tag}: ref must match PRJ-####")
            elif ref in seen:
                errs.append(f"{tag}: duplicate ref")
            seen.add(ref)
        domain = s.get("domain")
        if not isinstance(domain, str) or not (DOMAIN_RE.match(domain) or is_ip(domain)):
            errs.append(f"{tag}: domain is not a valid host name")
        canon = s.get("canonical")
        if not isinstance(canon, str):
            errs.append(f"{tag}: canonical must be a URL string")
        else:
            parts = urllib.parse.urlsplit(canon)
            local_test = parts.hostname in ("127.0.0.1", "localhost")
            if parts.scheme != "https" and not (parts.scheme == "http" and local_test):
                errs.append(f"{tag}: canonical must be https://")
            if parts.hostname != domain:
                errs.append(f"{tag}: canonical host must equal domain")
        rp = s.get("repo_path")
        if not isinstance(rp, str) or not os.path.isabs(rp):
            errs.append(f"{tag}: repo_path must be an absolute path")
        sr = s.get("site_root")
        if not isinstance(sr, str) or os.path.isabs(sr) or ".." in Path(sr).parts:
            errs.append(f"{tag}: site_root must be a relative path inside the repo")
        stack = s.get("stack")
        if not isinstance(stack, list) or not stack or any(x not in STACK_TAGS for x in stack):
            errs.append(f"{tag}: stack must be a non-empty list from {sorted(STACK_TAGS)}")
        if s.get("state") not in ("active", "candidate"):
            errs.append(f"{tag}: state must be active|candidate")
        prof = s.get("profile", {})
        if not isinstance(prof, dict):
            errs.append(f"{tag}: profile must be a table")
        else:
            for k in prof:
                if k not in PROFILE_KEYS:
                    errs.append(f"{tag}: unknown profile key '{k}'")
            if "drift_mode" in prof and prof["drift_mode"] not in DRIFT_MODES:
                errs.append(f"{tag}: drift_mode must be one of {sorted(DRIFT_MODES)}")
            if prof.get("drift_mode") == "manifest" and "served_files" not in prof:
                errs.append(f"{tag}: drift_mode manifest requires profile.served_files")
            if "served_files" in prof:
                sf = prof["served_files"]
                if prof.get("drift_mode") != "manifest":
                    errs.append(f"{tag}: profile.served_files is only valid with drift_mode = manifest")
                elif not isinstance(sf, list) or not sf or not all(isinstance(x, str) for x in sf):
                    errs.append(f"{tag}: profile.served_files must be a non-empty list of strings")
                else:
                    for x in sf:
                        if not x or x.startswith("/") or x.endswith("/") or "//" in x or ".." in Path(x).parts:
                            errs.append(f"{tag}: served_files entry {x!r} must be a relative repo path")
                    if len(set(sf)) != len(sf):
                        errs.append(f"{tag}: served_files has duplicate entries")
            for k in ("sitemap_expected", "domain_check"):
                if k in prof and not isinstance(prof[k], bool):
                    errs.append(f"{tag}: profile.{k} must be boolean")
            if "bogus_404_marker" in prof and not isinstance(prof["bogus_404_marker"], str):
                errs.append(f"{tag}: profile.bogus_404_marker must be a string")
        exp = s.get("expiry", {})
        if not isinstance(exp, dict):
            errs.append(f"{tag}: expiry must be a table")
        else:
            for k, v in exp.items():
                if k not in EXPIRY_KEYS:
                    errs.append(f"{tag}: unknown expiry key '{k}'")
                elif not (isinstance(v, str) and DATE_RE.match(v)):
                    errs.append(f"{tag}: expiry.{k} must be YYYY-MM-DD")
        if "evidence" in s and (not isinstance(s["evidence"], str) or not s["evidence"].strip()):
            errs.append(f"{tag}: evidence must be a non-empty string")
    return errs


def load_sites(p: Paths) -> list[dict]:
    if not p.sites.exists():
        raise ValueError(f"registry missing: {p.sites}")
    data = tomllib.loads(p.sites.read_text(encoding="utf-8"))
    unknown = set(data) - {"site"}
    if unknown:
        raise ValueError(f"sites.toml: unknown top-level keys {sorted(unknown)}")
    sites = data.get("site", [])
    errs = validate_sites(sites)
    if errs:
        raise ValueError("registry invalid: " + "; ".join(errs))
    return sites


def origin_of(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    return f"{p.scheme}://{p.netloc}"


def same_origin(url: str, origin: str) -> bool:
    p = urllib.parse.urlsplit(url)
    o = urllib.parse.urlsplit(origin)
    return p.scheme in ("http", "https") and p.netloc.lower() == o.netloc.lower()


def site_profile(site: dict) -> dict:
    prof = {"bogus_404_marker": None, "sitemap_expected": True, "drift_mode": "none", "domain_check": True}
    prof.update(site.get("profile", {}))
    return prof


def deploy_excludes(repo: Path) -> list[str]:
    f = repo / ".studio" / "deploy.json"
    try:
        return [e.strip("/") for e in json.loads(f.read_text(encoding="utf-8")).get("excludes", [])]
    except (OSError, ValueError):
        return []


# --------------------------------------------------------------------- http

class Resp:
    __slots__ = ("status", "headers", "body", "url", "error")

    def __init__(self, status, headers, body, url, error):
        self.status, self.headers, self.body, self.url, self.error = status, headers, body, url, error


_OPENER = urllib.request.build_opener()


def fetch(url: str, method: str = "GET", cap: int = MAX_PAGE, timeout: float = 15) -> Resp:
    """Read-only HTTP. Bodies are capped; callers decide what to keep (nothing is persisted)."""
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
    try:
        with _OPENER.open(req, timeout=timeout) as r:
            body = r.read(cap) if method != "HEAD" else None
            return Resp(r.status, {k.lower(): v for k, v in r.headers.items()}, body, r.geturl(), None)
    except urllib.error.HTTPError as e:
        body = None
        try:
            if method != "HEAD":
                body = e.read(cap)
        except Exception:
            body = None
        finally:
            e.close()
        return Resp(e.code, {k.lower(): v for k, v in (e.headers or {}).items()}, body, url, None)
    except Exception as e:  # network, DNS, TLS, timeout: class name only
        return Resp(None, {}, None, url, type(e).__name__)


# --------------------------------------------------------------- html parse

class PageParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang = None
        self.title = ""
        self._in_title = False
        self.metas: list[dict] = []
        self.links: list[dict] = []
        self.script_srcs: list[str] = []
        self.jsonld: list[str] = []
        self._in_jsonld = False
        self._jbuf: list[str] = []
        self.h1_texts: list[str] = []
        self._in_h1 = False
        self._h1buf: list[str] = []
        self.hrefs: list[str] = []
        self.comments: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            self.metas.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "script":
            if a.get("type", "").lower() == "application/ld+json":
                self._in_jsonld = True
                self._jbuf = []
            if a.get("src"):
                self.script_srcs.append(a["src"])
        elif tag == "h1":
            self._in_h1 = True
            self._h1buf = []
        elif tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._jbuf))
            self._in_jsonld = False
        elif tag == "h1" and self._in_h1:
            self.h1_texts.append("".join(self._h1buf).strip())
            self._in_h1 = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_jsonld:
            self._jbuf.append(data)
        if self._in_h1:
            self._h1buf.append(data)

    def handle_comment(self, data):
        self.comments.append(data)


# ------------------------------------------------------------- site results

class SiteResult:
    def __init__(self, site: dict):
        self.site = site
        self.ref = site["ref"]
        self.findings: list[dict] = []
        self.reasons: dict[str, list[str]] = {}
        self.checks_run: set[str] = set()
        self.extra: dict = {}
        self.cache: dict[str, Resp] = {}

    def run(self, cid):
        self.checks_run.add(cid)

    def fail(self, cid, severity, stable_key, evidence):
        self.checks_run.add(cid)
        fid = fault_id(self.ref, cid, stable_key)
        self.findings.append({"fault_id": fid, "ref": self.ref, "check_id": cid,
                              "severity": severity, "evidence": evidence})

    def inconc(self, cid, reason):
        self.checks_run.add(cid)
        self.reasons.setdefault(cid, []).append(reason)

    def get(self, url, cap=MAX_PAGE, method="GET", timeout=15.0) -> Resp:
        key = f"{method} {url}"
        if key not in self.cache:
            self.cache[key] = fetch(url, method=method, cap=cap, timeout=timeout)
        return self.cache[key]

    def finalize(self):
        seen, uniq = set(), []
        for f in self.findings:
            if f["fault_id"] not in seen:
                seen.add(f["fault_id"])
                uniq.append(f)
        self.findings = uniq
        status, entries = {}, []
        for cid in sorted(self.checks_run):
            fs = [f for f in self.findings if f["check_id"] == cid]
            if fs:
                status[cid] = "fail"
            elif cid in self.reasons:
                status[cid] = "inconclusive"
            else:
                status[cid] = "pass"
        for f in self.findings:
            entries.append({"fault_id": f["fault_id"], "check_id": f["check_id"], "severity": f["severity"],
                            "status": "fail", "evidence": f["evidence"]})
        for cid, rs in sorted(self.reasons.items()):
            entries.append({"fault_id": None, "check_id": cid, "severity": None,
                            "status": "inconclusive", "evidence": "; ".join(rs)})
        for cid in sorted(self.checks_run):
            if status[cid] == "pass":
                entries.append({"fault_id": None, "check_id": cid, "severity": None,
                                "status": "pass", "evidence": ""})
        return status, entries

    def as_record(self) -> dict:
        status, entries = self.finalize()
        rec = {"ref": self.ref, "domain": self.site["domain"], "canonical": self.site["canonical"],
               "check_status": status, "checks": entries}
        rec.update({k: v for k, v in self.extra.items()})
        return rec


def fault_id(ref: str, check_id: str, stable_key: str) -> str:
    k8 = hashlib.sha256(f"{ref}|{check_id}|{stable_key}".encode()).hexdigest()[:8]
    return f"MNT-{ref}-{check_id}-{k8}"


# ------------------------------------------------------------------ checks

def check_uptime(r: SiteResult, canon: str, timeout: float) -> Resp:
    r.run("UPTIME")
    home = r.get(canon, timeout=timeout)
    if home.status is None:
        r.fail("UPTIME", "high", "canonical", f"unreachable: {home.error}")
    elif home.status in (401, 403, 429):
        r.inconc("UPTIME", f"blocked or rate-limited: HTTP {home.status}")
    elif home.status >= 400:
        r.fail("UPTIME", "high", "canonical", f"HTTP {home.status} on canonical")
    return home


def check_tls(r: SiteResult, canon: str, timeout: float):
    if not canon.startswith("https://"):
        return
    p = urllib.parse.urlsplit(canon)
    host, port = p.hostname, p.port or 443
    r.run("TLS-EXPIRY")
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ss:
                cert = ss.getpeercert()
    except ssl.SSLCertVerificationError as e:
        msg = (e.verify_message or "verification failed")
        if "expired" in msg.lower():
            r.fail("TLS-EXPIRY", "high", "expiry", "certificate expired")
        else:
            r.run("TLS-VERIFY")
            r.fail("TLS-VERIFY", "high", "verify", f"certificate verification failed: {msg[:80]}")
        return
    except (OSError, ssl.SSLError) as e:
        r.inconc("TLS-EXPIRY", f"handshake error: {type(e).__name__}")
        return
    days = int((ssl.cert_time_to_seconds(cert["notAfter"]) - time.time()) // 86400)
    if days < 7:
        r.fail("TLS-EXPIRY", "high", "expiry", f"{days} days remaining (high under 7)")
    elif days < 21:
        r.fail("TLS-EXPIRY", "medium", "expiry", f"{days} days remaining (warn under 21)")


def check_domain(r: SiteResult, site: dict, timeout: float):
    prof = site_profile(site)
    domain = site["domain"]
    if not prof["domain_check"] or is_ip(domain):
        return
    cid = "DOMAIN-EXPIRY"
    r.run(cid)
    days, source = None, None
    rd = fetch(f"https://rdap.org/domain/{domain}", cap=512_000, timeout=timeout)
    if rd.status == 200 and rd.body:
        try:
            for ev in json.loads(rd.body).get("events", []):
                if ev.get("eventAction") == "expiration":
                    exp = dt.datetime.fromisoformat(ev["eventDate"].replace("Z", "+00:00"))
                    days = (exp - now_utc()).days
                    source = "rdap"
        except (ValueError, KeyError, TypeError):
            days = None
    manual = site.get("expiry", {}).get("domain")
    if days is None and manual:
        days = (dt.date.fromisoformat(manual) - now_utc().date()).days
        source = "manual"
    if days is None:
        r.inconc(cid, f"no expiry source (RDAP {rd.status or rd.error}; no manual expiry date in registry)")
        return
    if days < 14:
        r.fail(cid, "high", "expiry", f"{days} days to expiry (source {source}; high under 14)")
    elif days < 30:
        r.fail(cid, "medium", "expiry", f"{days} days to expiry (source {source}; warn under 30)")


def check_hygiene(r: SiteResult, site: dict, origin: str, canon: str, home: Resp, timeout: float) -> tuple[PageParser | None, list[str]]:
    """Items 1-7, 9, 10, 11 of site-launch-hygiene (8 is source-level, out of v1 scope)."""
    prof = site_profile(site)
    host = urllib.parse.urlsplit(canon).hostname
    sitemap_locs: list[str] = []

    # item 1: robots.txt with absolute Sitemap line
    cid = "HYGIENE-ROBOTS"
    r.run(cid)
    rob = r.get(origin + "/robots.txt", cap=200_000, timeout=timeout)
    if rob.status is None:
        r.inconc(cid, f"robots fetch error: {rob.error}")
    elif rob.status in (401, 403, 429):
        r.inconc(cid, f"blocked: HTTP {rob.status}")
    elif rob.status != 200:
        r.fail(cid, "medium", "status", f"HTTP {rob.status} for /robots.txt")
    else:
        lines = rob.body.decode("utf-8", "replace").splitlines()
        sm = [ln.split(":", 1)[1].strip() for ln in lines if ln.lower().lstrip().startswith("sitemap:")]
        if origin + "/sitemap.xml" not in sm:
            r.fail(cid, "medium", "sitemap-line", "no absolute Sitemap line for canonical /sitemap.xml")

    # item 2: sitemap.xml, exact sitemaps.org namespace, every <loc> on canonical origin
    if prof["sitemap_expected"]:
        cid = "HYGIENE-SITEMAP"
        r.run(cid)
        sm = r.get(origin + "/sitemap.xml", cap=5_000_000, timeout=timeout)
        if sm.status is None:
            r.inconc(cid, f"sitemap fetch error: {sm.error}")
        elif sm.status in (401, 403, 429):
            r.inconc(cid, f"blocked: HTTP {sm.status}")
        elif sm.status != 200:
            r.fail(cid, "medium", "status", f"HTTP {sm.status} for /sitemap.xml")
        else:
            try:
                root = ET.fromstring(sm.body)
            except ET.ParseError:
                root = None
                r.fail(cid, "medium", "parse", "sitemap.xml does not parse as XML")
            if root is not None:
                if root.tag not in (f"{{{SITEMAP_NS}}}urlset", f"{{{SITEMAP_NS}}}sitemapindex"):
                    r.fail(cid, "medium", "namespace", "root element not in exact sitemaps.org namespace")
                sitemap_locs = [el.text.strip() for el in root.iter() if el.tag.endswith("}loc") and el.text]
                off = [u for u in sitemap_locs if not same_origin(u, origin)]
                if off:
                    r.fail(cid, "medium", "loc-origin", f"{len(off)} <loc> outside canonical origin")

    # item 3: branded 404 for a bogus path
    cid = "HYGIENE-404"
    r.run(cid)
    b404 = r.get(origin + BOGUS_PATH, cap=MAX_PAGE, timeout=timeout)
    if b404.status is None:
        r.inconc(cid, f"probe error: {b404.error}")
    elif b404.status in (401, 403, 429):
        r.inconc(cid, f"blocked: HTTP {b404.status} on bogus path")
    elif b404.status != 404:
        r.fail(cid, "medium", "status", f"bogus path returned HTTP {b404.status}, expected 404")
    else:
        marker = prof.get("bogus_404_marker")
        if marker and marker.encode() not in (b404.body or b""):
            r.fail(cid, "medium", "marker", "branded 404 marker absent from 404 body")

    # homepage-derived items
    homepage_checks = ["HYGIENE-OG", "HYGIENE-TITLE", "HYGIENE-H1", "HYGIENE-JSONLD",
                       "HYGIENE-CACHEBUST", "HYGIENE-HEAD", "HYGIENE-COMMENTS"]
    if home.status != 200 or home.body is None:
        for cid in homepage_checks:
            r.inconc(cid, f"homepage not fetched (status {home.status or home.error})")
        return None, sitemap_locs

    page = PageParser()
    page.feed(home.body.decode("utf-8", "replace"))
    metas = {}
    for m in page.metas:
        k = m.get("property") or m.get("name")
        if k and k not in metas:
            metas[k] = m.get("content", "")

    # item 4: OG + Twitter set
    cid = "HYGIENE-OG"
    r.run(cid)
    for k in ("og:title", "og:description", "og:type", "og:url", "og:image",
              "og:image:width", "og:image:height", "og:image:alt"):
        if not metas.get(k):
            r.fail(cid, "medium", k, f"{k} missing")
    if metas.get("og:image") and not metas["og:image"].startswith("http"):
        r.fail(cid, "medium", "og:image-absolute", "og:image is not an absolute URL")
    if metas.get("og:url") and not metas["og:url"].startswith("http"):
        r.fail(cid, "medium", "og:url-absolute", "og:url is not an absolute URL")
    if metas.get("twitter:card") != "summary_large_image":
        r.fail(cid, "medium", "twitter:card", "twitter:card is not summary_large_image")

    # item 5: title discipline
    cid = "HYGIENE-TITLE"
    r.run(cid)
    t = page.title.strip()
    if not t:
        r.fail(cid, "medium", "empty", "no <title>")
    else:
        if len(t) > 70:
            r.fail(cid, "medium", "length", f"title length {len(t)} exceeds 70")
        if t.lower() in ("home", "untitled", "index"):
            r.fail(cid, "medium", "generic", "generic title")
        if t.lower() == (host or "").lower():
            r.fail(cid, "medium", "raw-domain", "title is the raw domain")

    # item 6: exactly one h1 with real text (logo-as-h1 has no text node)
    cid = "HYGIENE-H1"
    r.run(cid)
    if len(page.h1_texts) != 1:
        r.fail(cid, "medium", "h1-count", f"{len(page.h1_texts)} h1 elements, expected 1")
    elif not page.h1_texts[0]:
        r.fail(cid, "medium", "h1-empty", "h1 has no text")

    # item 7: JSON-LD presence (facts verified manually)
    cid = "HYGIENE-JSONLD"
    r.run(cid)
    parsed_ok = False
    for block in page.jsonld:
        try:
            json.loads(block)
            parsed_ok = True
        except ValueError:
            pass
    if not parsed_ok:
        r.fail(cid, "medium", "jsonld", "no parseable application/ld+json block")

    # item 9: cache-bust presence on same-origin css/js
    cid = "HYGIENE-CACHEBUST"
    r.run(cid)
    refs = [lk.get("href", "") for lk in page.links if "stylesheet" in lk.get("rel", "").lower()]
    refs += page.script_srcs
    for ref in refs:
        absu = urllib.parse.urljoin(canon, ref)
        if not same_origin(absu, origin):
            continue
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(absu).query)
        if "v" not in q:
            path = urllib.parse.urlsplit(absu).path
            r.fail(cid, "medium", f"asset:{path}", f"no ?v= cache-bust on {path}")

    # item 10: lang, viewport, canonical
    cid = "HYGIENE-HEAD"
    r.run(cid)
    if not page.lang:
        r.fail(cid, "medium", "lang", "<html lang> missing")
    if not any(m.get("name", "").lower() == "viewport" for m in page.metas):
        r.fail(cid, "medium", "viewport", "meta viewport missing")
    can = [lk.get("href", "") for lk in page.links if lk.get("rel", "").lower() == "canonical"]
    if not can:
        r.fail(cid, "medium", "canonical-missing", "link rel=canonical missing")
    elif can[0].rstrip("/") != canon.rstrip("/"):
        r.fail(cid, "medium", "canonical-mismatch", "link rel=canonical does not equal canonical URL")

    # item 11: zero process commentary in served HTML (text is never recorded, only a hash)
    cid = "HYGIENE-COMMENTS"
    r.run(cid)
    for c in page.comments:
        k = hashlib.sha256(c.strip().encode("utf-8")).hexdigest()[:12]
        r.fail(cid, "medium", f"comment:{k}", "HTML comment present in served markup (text not recorded)")
    return page, sitemap_locs


def check_exposure(r: SiteResult, origin: str, timeout: float):
    statuses = []
    for cid, path, sig_name, sig, sev in EXPOSURE_PROBES:
        r.run(cid)
        rsp = fetch(origin + path, cap=MAX_PROBE, timeout=timeout)
        statuses.append(rsp.status)
        if rsp.status is None:
            r.inconc(cid, f"probe error on {path}: {rsp.error}")
        elif rsp.status == 200:
            if rsp.body is not None and sig(rsp.body):
                r.fail(cid, sev, path, f"{path} served with {sig_name} content signature")
        elif rsp.status in (401, 403, 429):
            r.inconc(cid, f"probe blocked on {path}: HTTP {rsp.status}")
        elif rsp.status >= 500:
            r.inconc(cid, f"probe {path}: HTTP {rsp.status}")


def manifest_selection(repo: Path, served: list[str], max_bytes: int):
    """Resolve an explicit served_files list (repo-root-relative) against git HEAD.

    Returns (files, absent, counts), or None when git fails. files is [(rel, blob_sha)].
    absent lists registered paths that are not blobs at HEAD; the caller reports them as
    inconclusive, never as drift faults. Skip rules match the static walk: .php and
    dot-paths are never compared, oversized blobs are counted and not fetched.
    """
    out = subprocess_text(["git", "-C", str(repo), "ls-tree", "-z", "-l", "HEAD", "--", *served])
    if out is None:
        return None
    entries: dict[str, tuple[str, str, int]] = {}
    for line in out.split("\0"):
        if not line:
            continue
        meta, path = line.split("\t", 1)
        _mode, typ, sha, size = meta.split()
        entries[path] = (typ, sha, int(size))
    files: list[tuple[str, str]] = []
    absent: list[str] = []
    counts = {"skipped_large": 0, "skipped_php": 0, "skipped_dot": 0}
    for rel in served:
        ent = entries.get(rel)
        if ent is None or ent[0] != "blob":
            absent.append(rel)
            continue
        _typ, sha, size = ent
        if rel.lower().endswith(".php"):
            counts["skipped_php"] += 1
        elif any(p.startswith(".") for p in rel.split("/")):
            counts["skipped_dot"] += 1
        elif size > max_bytes:
            counts["skipped_large"] += 1
        else:
            files.append((rel, sha))
    return files, absent, counts


def check_drift(r: SiteResult, site: dict, origin: str, cfg: dict, timeout: float):
    prof = site_profile(site)
    mode = prof["drift_mode"]
    if mode in ("none", "build-output"):
        r.extra["drift"] = {"mode": mode, "checked": False}
        return
    cid = "DRIFT"
    r.run(cid)
    repo = Path(site["repo_path"])
    max_bytes = cfg["max_drift_file_bytes"]
    if not (repo / ".git").exists():
        r.inconc(cid, "repo not found at registered repo_path")
        return
    absent: list[str] = []
    if mode == "manifest":
        # Explicit list: a registered site may deploy from the repo root, so the
        # live tree is not always a site_root subtree.
        sel = manifest_selection(repo, prof["served_files"], max_bytes)
        if sel is None:
            r.inconc(cid, "git ls-tree failed")
            return
        files, absent, counts = sel
        skipped_large, skipped_php, skipped_dot = counts["skipped_large"], counts["skipped_php"], counts["skipped_dot"]
        excluded = 0
    else:
        root = site["site_root"].strip("/")
        excludes = deploy_excludes(repo)
        out = subprocess_text(["git", "-C", str(repo), "ls-tree", "-r", "-z", "-l", "HEAD", "--", root])
        if out is None:
            r.inconc(cid, "git ls-tree failed")
            return
        files, skipped_large, skipped_php, skipped_dot, excluded = [], 0, 0, 0, 0
        for line in out.split("\0"):
            if not line:
                continue
            meta, path = line.split("\t", 1)
            _mode, typ, sha, size = meta.split()
            if typ != "blob":
                continue
            rel = path[len(root) + 1:]
            parts = rel.split("/")
            if any(p.startswith(".") for p in parts):
                skipped_dot += 1
                continue
            if any(rel == e or rel.startswith(e + "/") for e in excludes):
                excluded += 1
                continue
            if rel.lower().endswith(".php"):
                skipped_php += 1
                continue
            if int(size) > max_bytes:
                skipped_large += 1
                continue
            files.append((rel, sha))
    info = {"mode": mode, "checked": True, "files": len(files), "skipped_large": skipped_large,
            "skipped_php": skipped_php, "skipped_dot": skipped_dot, "excluded": excluded}
    if mode == "manifest":
        info["absent_from_head"] = len(absent)
    r.extra["drift"] = info
    if absent:
        r.inconc(cid, f"{len(absent)} served_files not present as files in git HEAD: {', '.join(absent)}")
    if len(files) > cfg["max_drift_files"]:
        r.inconc(cid, f"{len(files)} files exceed max_drift_files cap; not compared")
        return
    mismatched = missing = blocked = compared = 0

    def _get(item):
        return fetch(origin + "/" + urllib.parse.quote(item[0]), cap=max_bytes + 1, timeout=timeout)

    # bounded concurrency (6) for the GETs only; processing stays sequential so output is deterministic
    with ThreadPoolExecutor(max_workers=6) as pool:
        served_list = list(pool.map(_get, files))
    for (rel, sha), rsp in zip(files, served_list):
        if rsp.status is None or rsp.status in (401, 403, 429) or (rsp.status and rsp.status >= 500):
            blocked += 1
            continue
        if rsp.status == 404:
            missing += 1
            r.fail(cid, "medium", rel, f"{rel} in HEAD but not served (404)")
            continue
        if rsp.status != 200 or rsp.body is None or len(rsp.body) > max_bytes:
            blocked += 1
            continue
        compared += 1
        served = rsp.body
        head = subprocess_bytes(["git", "-C", str(repo), "cat-file", "blob", sha])
        if head is None:
            blocked += 1
            continue
        if hashlib.sha256(served).digest() == hashlib.sha256(head).digest():
            continue
        if rel.lower().endswith((".html", ".htm", ".css", ".js")):
            norm = lambda b: re.sub(rb"\?v=[0-9A-Za-z._-]+", b"", b)
            if hashlib.sha256(norm(served)).digest() == hashlib.sha256(norm(head)).digest():
                continue
        mismatched += 1
        r.fail(cid, "medium", rel, f"{rel}: served bytes differ from git HEAD blob")
    info.update({"compared": compared, "mismatched": mismatched, "missing": missing, "blocked": blocked})
    if blocked:
        r.inconc(cid, f"{blocked} files could not be compared (blocked, errored or oversized after fetch)")


def subprocess_text(args: list[str]) -> str | None:
    try:
        res = subprocess.run(args, capture_output=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return res.stdout.decode("utf-8", "replace") if res.returncode == 0 else None


def subprocess_bytes(args: list[str]) -> bytes | None:
    try:
        res = subprocess.run(args, capture_output=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return res.stdout if res.returncode == 0 else None


def check_links(r: SiteResult, origin: str, canon: str, page: PageParser | None,
                sitemap_locs: list[str], cfg: dict, timeout: float):
    cid = "LINKS"
    r.run(cid)
    targets: dict[str, str] = {}
    if page is not None:
        for href in page.hrefs:
            absu = urllib.parse.urldefrag(urllib.parse.urljoin(canon, href))[0]
            if same_origin(absu, origin):
                targets.setdefault(absu, "home")
    for loc in sitemap_locs:
        if same_origin(loc, origin):
            targets.setdefault(loc, "sitemap")
    items = sorted(targets.items())
    cap = cfg["max_links"]
    if len(items) > cap:
        r.inconc(cid, f"{len(items)} same-origin targets exceed max_links={cap}; first {cap} checked")
        items = items[:cap]
    checked = 0
    for url, src in items:
        rsp = fetch(url, method="HEAD", cap=0, timeout=timeout)
        if rsp.status in (405, 501) or rsp.status is None:
            rsp = fetch(url, method="GET", cap=MAX_PROBE, timeout=timeout)
        checked += 1
        path = urllib.parse.urlsplit(url).path or "/"
        if rsp.status is None:
            r.inconc(cid, f"link probe error ({src}): {rsp.error}")
        elif rsp.status in (401, 403, 429):
            r.inconc(cid, f"link blocked ({src}): HTTP {rsp.status}")
        elif rsp.status >= 400:
            r.fail(cid, "medium", f"{src}|{path}", f"broken internal link ({src}): HTTP {rsp.status} on {path}")
    r.extra["links"] = {"targets": len(items), "checked": checked}


def check_secrets(r: SiteResult, origin: str, canon: str, page: PageParser | None,
                  sitemap_locs: list[str], cfg: dict, timeout: float):
    cid = "SECRET-EXPOSED"
    r.run(cid)
    urls = [canon]
    if page is not None:
        for ref in [lk.get("href", "") for lk in page.links if "stylesheet" in lk.get("rel", "").lower()] + page.script_srcs:
            absu = urllib.parse.urldefrag(urllib.parse.urljoin(canon, ref))[0]
            if same_origin(absu, origin) and absu not in urls:
                urls.append(absu)
    for loc in sitemap_locs:
        if same_origin(loc, origin) and loc not in urls and loc.rstrip("/") != origin:
            if urllib.parse.urlsplit(loc).path.lower().endswith((".xml", ".txt", ".png", ".jpg", ".webp", ".pdf")):
                continue
            urls.append(loc)
    urls = urls[: cfg["max_secret_urls"]]
    scanned = 0
    for u in urls:
        rsp = r.get(u, cap=MAX_PAGE, timeout=timeout)
        if rsp.status != 200 or rsp.body is None:
            continue
        ctype = rsp.headers.get("content-type", "")
        if ctype and not any(t in ctype for t in ("text/", "javascript", "json", "xml")):
            continue
        scanned += 1
        text = rsp.body.decode("utf-8", "replace")
        path = urllib.parse.urlsplit(u).path or "/"
        for pid, rx in SECRET_PATTERNS:
            m = rx.search(text)
            if m:
                line = text.count("\n", 0, m.start()) + 1
                digest12 = hashlib.sha256(m.group(0).encode("utf-8")).hexdigest()[:12]
                r.fail(cid, "high", f"{pid}|{path}",
                       f"pattern={pid} path={path} line={line} value_sha256_12={digest12}")
    r.extra["secrets"] = {"urls_queued": len(urls), "scanned": scanned}
    if scanned == 0:
        r.inconc(cid, "no same-origin text assets fetched; nothing scanned")


def check_site(site: dict, cfg: dict) -> SiteResult:
    r = SiteResult(site)
    canon = site["canonical"]
    origin = origin_of(canon)
    timeout = float(cfg["request_timeout_s"])
    home = check_uptime(r, canon, timeout)
    check_tls(r, canon, timeout)
    check_domain(r, site, timeout)
    page, sitemap_locs = check_hygiene(r, site, origin, canon, home, timeout)
    check_exposure(r, origin, timeout)
    check_drift(r, site, origin, cfg, timeout)
    check_links(r, origin, canon, page, sitemap_locs, cfg, timeout)
    check_secrets(r, origin, canon, page, sitemap_locs, cfg, timeout)
    r.extra["homepage"] = {"status": home.status}
    return r


def control_check(hosts: list[str], timeout: float) -> dict:
    rows = []
    for u in hosts:
        rsp = fetch(u, cap=1024, timeout=timeout)
        ok = rsp.status is not None and rsp.status < 500
        rows.append({"url": u, "ok": ok, "result": rsp.status if rsp.status is not None else rsp.error})
    ok_any = any(x["ok"] for x in rows)
    return {"status": "ok" if ok_any else "failed", "ok": ok_any, "hosts": rows}


# ------------------------------------------------------------------- feeds

HN_TERMS = {"wordpress": ["wordpress"], "php": ["php"], "apache": ["apache"], "nginx": ["nginx"], "hugo": ["hugo"]}


def kw_hits(stack, text: str) -> list[str]:
    t = text.lower().replace("_", " ")
    hits = set()
    for tag in stack:
        for kw in STACK_KEYWORDS.get(tag, []):
            if re.search(r"(?<![a-z0-9])" + re.escape(kw.replace("_", " ")) + r"(?![a-z0-9])", t):
                hits.add(tag)
    return sorted(hits)


def cpe_vendor_product(criteria: str) -> tuple[str, str] | None:
    """(vendor, product) from a CPE 2.3 criteria string (cpe:2.3:part:vendor:product:...), else None."""
    parts = criteria.split(":")
    if len(parts) < 5 or parts[0] != "cpe" or parts[2] not in {"a", "o", "h"}:
        return None
    return parts[3], parts[4]


def nvd_stack_tags(stack, criteria: list[str]) -> list[str]:
    """Strict NVD stack matching against the CPE registry only.

    Only the structured vendor/product fields of cpeMatch criteria are keyword-matched
    against stack tags; the free-text description is never matched. This is what keeps
    WordPress-plugin CVEs (CPE vendor `wordpress`, descriptions commonly mention "PHP")
    from matching php-stack sites: a `wordpress`-vendor CVE is WordPress-ecosystem and
    can only match the `wordpress` tag. Sites without the tag see nothing.
    """
    fields = [f for f in (cpe_vendor_product(c) for c in criteria) if f]
    if not fields:
        return []
    if any(vendor == "wordpress" for vendor, _product in fields):
        return ["wordpress"] if "wordpress" in stack else []
    return kw_hits(stack, " ".join(x for f in fields for x in f))


def get_json(url: str, timeout: float, cap: int = 50_000_000):
    rsp = fetch(url, cap=cap, timeout=timeout)
    if rsp.status != 200 or rsp.body is None:
        raise FeedError(f"HTTP {rsp.status if rsp.status is not None else rsp.error}")
    try:
        return json.loads(rsp.body)
    except ValueError as e:
        raise FeedError("invalid JSON") from e


def feed_cursor_window(state: dict, now: dt.datetime, cfg: dict) -> tuple[dt.datetime, dt.datetime]:
    """Start = earlier of last success and now-7d, never further back than the 30d cap.

    The plan text says max(); that would narrow the window and open a gap after a missed week.
    The stated purpose (no news gap) needs the earlier bound, so that is what is implemented.
    """
    f = cfg["feeds"]
    cap_start = now - dt.timedelta(days=f["window_cap_days"])
    base = now - dt.timedelta(days=f["window_days"])
    last = state.get("last_success")
    start = base
    if last:
        start = min(dt.datetime.fromisoformat(last.replace("Z", "+00:00")), base)
    return max(start, cap_start), now


def feed_kev(ctx: dict) -> tuple[dict, list[dict]]:
    cfg, state, now = ctx["cfg"], ctx["state"], ctx["now"]
    data = ctx["getter"](cfg["feeds"]["kev_url"], cfg["request_timeout_s"])
    vulns = data.get("vulnerabilities") or []
    count = data.get("count")
    if not isinstance(count, int) or count != len(vulns):
        raise FeedError(f"catalog count mismatch (declared {count}, parsed {len(vulns)})")
    ks = state.setdefault("kev", {})
    seen = set(ks.get("seen", []))
    cutoff = (now - dt.timedelta(days=30)).date().isoformat()
    if seen:
        new = [v for v in vulns if v.get("cveID") not in seen]
    else:  # first run: alert only on the last 30 days; older entries become the baseline
        new = [v for v in vulns if v.get("dateAdded", "") >= cutoff]
    matches = []
    for v in new:
        text = f"{v.get('vendorProject', '')} {v.get('product', '')}"
        for ref, stack in ctx["active"]:
            tags = kw_hits(stack, text)
            if tags:
                matches.append({
                    "feed": "kev", "id": v.get("cveID"), "ref": ref, "severity": "high",
                    "check_id": "FEED-KEV",
                    "evidence": (f"KEV {v.get('cveID')}: {v.get('vendorProject', '')} / {v.get('product', '')}; "
                                 f"dateAdded {v.get('dateAdded', '')}; dueDate {v.get('dueDate', '')}; "
                                 f"stack {','.join(tags)}"),
                })
    state["kev"] = {"seen": sorted(v.get("cveID") for v in vulns if v.get("cveID")),
                    "catalogVersion": data.get("catalogVersion"), "last_success": iso(now)}
    rec = {"feed": "kev", "status": "ok", "catalogVersion": data.get("catalogVersion"),
           "catalog_count": count, "new": len(new), "matches": len(matches)}
    return rec, matches


def feed_nvd(ctx: dict) -> tuple[dict, list[dict]]:
    cfg, state, now = ctx["cfg"], ctx["state"], ctx["now"]
    f = cfg["feeds"]
    start, end = feed_cursor_window(state.get("nvd", {}), now, cfg)
    base = {"pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000"), "pubEndDate": end.strftime("%Y-%m-%dT%H:%M:%S.000"),
            "cvssV3Severity": "CRITICAL", "resultsPerPage": 2000}
    vulns, idx, total = [], 0, None
    while True:
        q = dict(base, startIndex=idx)
        url = f["nvd_url"] + "?" + urllib.parse.urlencode(q)
        data = ctx["getter"](url, cfg["request_timeout_s"])
        total = data.get("totalResults", 0)
        page = data.get("vulnerabilities") or []
        vulns += page
        idx += len(page)
        if not page or idx >= total:
            break
        ctx["sleeper"](f["nvd_sleep_s"])
    if total is not None and len(vulns) != total:
        raise FeedError(f"incomplete pagination ({len(vulns)} of {total})")
    matches = []
    for item in vulns:
        c = item.get("cve", {})
        cid = c.get("id", "")
        crits = [m.get("criteria", "") for cfgn in c.get("configurations", [])
                 for n in cfgn.get("nodes", []) for m in n.get("cpeMatch", [])]
        for ref, stack in ctx["active"]:
            tags = nvd_stack_tags(stack, crits)
            if tags:
                matches.append({"feed": "nvd", "id": cid, "ref": ref, "severity": "medium", "check_id": "FEED-NVD",
                                "evidence": f"NVD {cid} CRITICAL; stack {','.join(tags)}"})
    state["nvd"] = {"last_success": iso(end)}
    return {"feed": "nvd", "status": "ok", "window": [iso(start), iso(end)], "critical": len(vulns),
            "matches": len(matches)}, matches


def hn_window(ctx: dict, term: str, start: int, end: int) -> list[dict]:
    url = (ctx["cfg"]["feeds"]["hn_url"] + "?" + urllib.parse.urlencode({
        "query": term, "tags": "story", "hitsPerPage": 1000,
        "numericFilters": f"created_at_i>{start},created_at_i<={end}"}))
    data = ctx["getter"](url, ctx["cfg"]["request_timeout_s"])
    n = int(data.get("nbHits", 0))
    if n >= 1000:  # Algolia caps retrievable hits at 1000: split, never truncate silently
        if end - start < 2:
            raise FeedError("HN window cannot be split below 2s while nbHits >= 1000")
        mid = (start + end) // 2
        return hn_window(ctx, term, start, mid) + hn_window(ctx, term, mid, end)
    return data.get("hits", [])


def feed_hn(ctx: dict) -> tuple[dict, list[dict]]:
    cfg, state, now = ctx["cfg"], ctx["state"], ctx["now"]
    start, end = feed_cursor_window(state.get("hn", {}), now, cfg)
    terms = ["exploit"] + sorted({kw for _ref, stack in ctx["active"] for tag in stack for kw in HN_TERMS.get(tag, [])})
    items, per_term = {}, {}
    for term in dict.fromkeys(terms):
        hits = hn_window(ctx, term, int(start.timestamp()), int(end.timestamp()))
        per_term[term] = len(hits)
        for h in hits:
            items.setdefault(h.get("objectID"), {"title": h.get("title") or "", "points": h.get("points") or 0,
                                                 "created_at": h.get("created_at", ""), "terms": []})["terms"].append(term)
    state["hn"] = {"last_success": iso(end)}
    top = sorted(items.values(), key=lambda x: -(x["points"] or 0))[:10]
    return {"feed": "hn", "status": "ok", "window": [iso(start), iso(end)], "terms": per_term,
            "unique_stories": len(items), "context_top": top}, []  # HN is context only, never a severity source


def feed_hugo(ctx: dict) -> tuple[dict, list[dict]]:
    cfg, state, now = ctx["cfg"], ctx["state"], ctx["now"]
    rsp = fetch(cfg["feeds"]["hugo_url"], cap=2_000_000, timeout=cfg["request_timeout_s"])
    if rsp.status != 200 or rsp.body is None:
        raise FeedError(f"HTTP {rsp.status if rsp.status is not None else rsp.error}")
    try:
        root = ET.fromstring(rsp.body)
    except ET.ParseError as e:
        raise FeedError("atom parse error") from e
    last = state.get("hugo", {}).get("last_success")
    cutoff = dt.datetime.fromisoformat(last.replace("Z", "+00:00")) if last else now - dt.timedelta(days=cfg["feeds"]["window_days"])
    items = []
    for e in root.iter(f"{ATOM_NS}entry"):
        upd = e.findtext(f"{ATOM_NS}updated", "")
        try:
            when = dt.datetime.fromisoformat(upd.replace("Z", "+00:00"))
        except ValueError:
            continue
        if when > cutoff:
            items.append({"title": e.findtext(f"{ATOM_NS}title", ""), "updated": upd})
    state["hugo"] = {"last_success": iso(now)}
    return {"feed": "hugo", "status": "ok", "new_entries": len(items), "context_top": items[:10]}, []


FEEDS = {"kev": feed_kev, "nvd": feed_nvd, "hn": feed_hn, "hugo": feed_hugo}


# ----------------------------------------------------------------- run record

class Run:
    def __init__(self, kind: str, p: Paths):
        self.p = p
        base = now_utc().strftime("%Y-%m-%dT%H%M%SZ")
        rid, n = base, 1
        while (p.runs / f"{rid}.json").exists():
            n += 1
            rid = f"{base}-{n}"
        self.id = rid
        self.rec = {"run_id": rid, "kind": kind, "started": iso(now_utc()), "finished": None,
                    "control": None, "sites": [], "feeds": [], "doctor": None, "drift": [],
                    "notify": None, "digest": None, "errors": [], "exit_code": None}

    def err(self, stage: str, exc: Exception):
        self.rec["errors"].append({"stage": stage, "error": type(exc).__name__, "message": str(exc)[:200]})

    def save(self):
        self.rec["finished"] = iso(now_utc())
        target = self.p.runs / f"{self.id}.json"
        atomic_write(target, json.dumps(self.rec, indent=1, sort_keys=True) + "\n")
        link_tmp = self.p.home / "latest.json.tmp"
        if link_tmp.exists() or link_tmp.is_symlink():
            link_tmp.unlink()
        os.symlink(os.path.join("runs", f"{self.id}.json"), link_tmp)
        os.replace(link_tmp, self.p.latest)


class Lock:
    def __init__(self, p: Paths):
        self.fh = open(p.lock, "a+")
        os.chmod(p.lock, 0o600)

    def __enter__(self):
        fcntl.flock(self.fh.fileno(), fcntl.LOCK_EX)
        return self

    def __exit__(self, *a):
        fcntl.flock(self.fh.fileno(), fcntl.LOCK_UN)
        self.fh.close()


# ------------------------------------------------------------------- faults

def load_faults(p: Paths) -> dict:
    return load_json(p.faults, {"schema": 1, "updated": None, "faults": {}})


def save_faults(p: Paths, data: dict, stamp: str):
    data["updated"] = stamp
    data["faults"] = dict(sorted(data["faults"].items()))
    atomic_write(p.faults, json.dumps(data, indent=1, sort_keys=True) + "\n")


def apply_suppressions(data: dict, cfg: dict, today: dt.date):
    rules = {s["fault_id"]: s for s in cfg.get("suppress", [])}
    for fid, f in data["faults"].items():
        rule = rules.get(fid)
        if rule and dt.date.fromisoformat(rule["until"]) >= today and f["state"] in ("open", "suppressed"):
            f["state"] = "suppressed"
            f["suppress"] = {"reason": rule["reason"], "until": rule["until"]}
        else:
            if f["state"] == "suppressed":
                f["state"] = "open"
            f["suppress"] = None


def apply_findings(data: dict, findings: list[dict], status_by_ref: dict, run_id: str, stamp: str):
    """Upsert findings; resolve faults whose site/check returned `pass` this run. Inconclusive keeps state."""
    seen = set()
    for f in findings:
        fid = f["fault_id"]
        seen.add(fid)
        rec = data["faults"].get(fid)
        if rec is None:
            rec = {"ref": f["ref"], "check_id": f["check_id"], "kind": f.get("kind", "site"),
                   "first_seen": stamp, "state": "open", "suppress": None, "resolved_run": None}
            data["faults"][fid] = rec
        rec.update({"severity": f["severity"], "last_seen": stamp, "last_run": run_id,
                    "evidence": f["evidence"], "domain": f.get("domain")})
        if rec["state"] == "resolved":
            rec["state"] = "open"
            rec["resolved_run"] = None
    for fid, rec in data["faults"].items():
        if fid in seen or rec["state"] not in ("open", "suppressed"):
            continue
        st = status_by_ref.get(rec["ref"], {}).get(rec["check_id"])
        if st == "pass":
            rec["state"] = "resolved"
            rec["resolved_run"] = run_id


def stage_faults(run: Run, findings: list[dict], status_by_ref: dict, cfg: dict):
    stamp = iso(now_utc())
    data = load_faults(run.p)
    apply_findings(data, findings, status_by_ref, run.id, stamp)
    apply_suppressions(data, cfg, now_utc().date())
    save_faults(run.p, data, stamp)
    return data


def site_findings(sites_results: list[dict]) -> tuple[list[dict], dict]:
    findings, status = [], {}
    for s in sites_results:
        status[s["ref"]] = s["check_status"]
        for e in s["checks"]:
            if e["status"] == "fail" and e["fault_id"]:
                findings.append({"fault_id": e["fault_id"], "ref": s["ref"], "check_id": e["check_id"],
                                 "severity": e["severity"], "evidence": e["evidence"], "kind": "site",
                                 "domain": s["domain"]})
    return findings, status


# ------------------------------------------------------------------- stages

def stage_check(run: Run, cfg: dict, sites: list[dict], persist: bool = True) -> int:
    ctl = control_check(cfg["control_hosts"], float(cfg["request_timeout_s"]))
    run.rec["control"] = ctl
    if not ctl["ok"]:
        for s in sites:
            run.rec["sites"].append({"ref": s["ref"], "domain": s["domain"], "canonical": s["canonical"],
                                     "check_status": {}, "checks": [],
                                     "skipped": "control check failed; no site faults recorded"})
        return EXIT_INCONCLUSIVE
    results = []
    for s in sites:
        try:
            results.append(check_site(s, cfg).as_record())
        except Exception as e:  # runner error on one site: that site is inconclusive, not pass
            run.err(f"check:{s['ref']}", e)
            results.append({"ref": s["ref"], "domain": s["domain"], "canonical": s["canonical"],
                            "check_status": {"RUNNER": "inconclusive"},
                            "checks": [{"fault_id": None, "check_id": "RUNNER", "severity": None,
                                        "status": "inconclusive", "evidence": type(e).__name__}]})
    run.rec["sites"].extend(results)
    run.rec["drift"] = [{"ref": s["ref"], **(s.get("drift") or {"checked": False})} for s in results]
    if persist:
        findings, status = site_findings(results)
        stage_faults(run, findings, status, cfg)
    return EXIT_OK


def stage_feeds(run: Run, cfg: dict, sites: list[dict], only: list[str] | None, getter=None, sleeper=None) -> list[dict]:
    p = run.p
    active = [(s["ref"], set(s["stack"])) for s in sites]
    stacks_all = set().union(*[st for _r, st in active]) if active else set()
    state = load_json(p.feeds_state, {})
    names = only or ["kev", "nvd", "hn", "hugo"]
    ctx = {"cfg": cfg, "active": active, "now": now_utc(), "getter": getter or get_json,
           "sleeper": sleeper or time.sleep}
    findings: list[dict] = []
    for name in names:
        if name == "hugo" and "hugo" not in stacks_all:
            continue
        ctx["state"] = state
        try:
            rec, matches = FEEDS[name](ctx)
        except FeedError as e:
            rec, matches = {"feed": name, "status": "unavailable", "reason": str(e),
                            "note": f"feed {name} not checked this run; cursor not advanced"}, []
        except Exception as e:
            rec, matches = {"feed": name, "status": "unavailable", "reason": type(e).__name__,
                            "note": f"feed {name} not checked this run; cursor not advanced"}, []
            run.err(f"feed:{name}", e)
        run.rec["feeds"].append(rec)
        rec["match_list"] = [{"id": m["id"], "ref": m["ref"], "severity": m["severity"], "check_id": m["check_id"]}
                             for m in matches]
        for m in matches:
            findings.append({"fault_id": fault_id(m["ref"], m["check_id"], m["id"]), "ref": m["ref"],
                             "check_id": m["check_id"], "severity": m["severity"], "evidence": m["evidence"],
                             "kind": "feed"})
    save_json_atomic(p.feeds_state, state)
    stage_faults(run, findings, {}, cfg)
    return findings


def save_json_atomic(path: Path, data):
    atomic_write(path, json.dumps(data, indent=1, sort_keys=True) + "\n")


def evaluate_arm(armed: bool, probes: dict[str, dict], cron_hits: list[str]) -> list[str]:
    """Pure function: returns problems. Empty list means armed/disarmed state matches live state."""
    problems = []
    for unit, p in probes.items():
        enabled = p.get("enabled") == "enabled"
        active = p.get("active") == "active"
        nxt = p.get("next", "")
        if armed:
            if not enabled:
                problems.append(f"{unit} not enabled but armed=true")
            if not active:
                problems.append(f"{unit} not active but armed=true")
            if not nxt or nxt == "0":
                problems.append(f"{unit} has no next elapse but armed=true")
        else:
            if enabled:
                problems.append(f"{unit} enabled but armed=false")
            if active:
                problems.append(f"{unit} active but armed=false")
    for line in cron_hits:
        problems.append(f"crontab line invokes site-maintenance: {line[:60]}")
    return problems


def _sh(args: list[str]) -> str:
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def probe_live() -> tuple[dict, list[str]]:
    probes = {}
    for unit in TIMERS:
        sh = _sh
        probes[unit] = {
            "enabled": sh(["systemctl", "--user", "is-enabled", unit]),
            "active": sh(["systemctl", "--user", "is-active", unit]),
            "next": sh(["systemctl", "--user", "show", unit, "-p", "NextElapseUSecRealtime", "--value"]),
        }
    cron = subprocess_text(["crontab", "-l"]) or ""
    hits = [ln for ln in cron.splitlines() if "site-maintenance" in ln and not ln.lstrip().startswith("#")]
    return probes, hits


def stage_doctor(run: Run, cfg: dict, probe=None) -> dict:
    probes, hits = (probe or probe_live)()
    problems = evaluate_arm(cfg["armed"], probes, hits)
    status = "consistent" if not problems else "drift"
    run.rec["doctor"] = {"armed": cfg["armed"], "status": status, "problems": problems, "probes": probes}
    finding = []
    if problems:
        finding.append({"fault_id": fault_id("ENGINE", "DRIFT", "arm-state"), "ref": "ENGINE", "check_id": "DRIFT",
                        "severity": "high", "evidence": "; ".join(problems)[:400], "kind": "engine"})
    stage_faults(run, finding, {"ENGINE": {"DRIFT": "fail" if problems else "pass"}}, cfg)
    return run.rec["doctor"]


def stage_notify(run: Run, cfg: dict, scope: str = "new"):
    """One desktop nudge per run. scope=new: high faults first seen/refreshed this run (daily KEV).
    scope=open: every open high fault (weekly reminder, so a standing exposure is not silent forever)."""
    if not cfg["notify"]:
        run.rec["notify"] = {"status": "disabled"}
        return
    data = load_faults(run.p)
    high = [(fid, f) for fid, f in data["faults"].items()
            if f["severity"] == "high" and f["state"] == "open"
            and (scope == "open" or f.get("last_run") == run.id)]
    if not high:
        run.rec["notify"] = {"status": "not-required", "high_open": 0, "scope": scope}
        return
    feeds = ", ".join(f"{r['feed']} {r['status']}" for r in run.rec["feeds"]) or "not run"
    ids = [fid for fid, _f in high][:5]
    more = f" (+{len(high) - 5} more)" if len(high) > 5 else ""
    summary = f"{len(high)} high open. Feeds: {feeds}. IDs: {', '.join(ids)}{more}. See latest.json."
    env = dict(os.environ)
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{os.getuid()}/bus")
    try:
        res = subprocess.run(["notify-send", "--app-name=site-maintenance", "--urgency=critical",
                              "Site maintenance", summary], capture_output=True, timeout=15, env=env)
        run.rec["notify"] = {"status": "sent" if res.returncode == 0 else "failed", "rc": res.returncode,
                             "high_open": len(high), "scope": scope}
    except (OSError, subprocess.SubprocessError) as e:
        run.rec["notify"] = {"status": "failed", "error": type(e).__name__, "high_open": len(high)}


def build_payload(rec: dict, open_faults: list[dict] | None = None) -> dict:
    """Redacted view: refs, fault IDs, check IDs, severities, counts, public feed items. No evidence strings.
    open_faults: every open/suppressed fault from faults.json (across runs), so faults recorded by an earlier
    run (e.g. a KEV match) are still visible to the digest when this run finds nothing new."""
    sites = []
    for s in rec["sites"]:
        sites.append({"ref": s["ref"], "domain": s["domain"], "check_status": s.get("check_status", {}),
                      "findings": [{"fault_id": e["fault_id"], "check_id": e["check_id"], "severity": e["severity"]}
                                   for e in s.get("checks", []) if e.get("status") == "fail"]})
    feeds = []
    for f in rec["feeds"]:
        feeds.append({"feed": f["feed"], "status": f["status"], "match_list": f.get("match_list", []),
                      "context_titles": [c.get("title", "") for c in f.get("context_top", [])][:10]})
    return {"run_id": rec["run_id"], "control": (rec.get("control") or {}).get("status"),
            "sites": sites, "feeds": feeds, "doctor": (rec.get("doctor") or {}).get("status"),
            "open_faults": open_faults or []}


def stage_digest(run: Run, cfg: dict):
    dcfg = cfg["digest"]
    if not dcfg["enabled"]:
        run.rec["digest"] = {"status": "disabled"}
        return
    p = run.p
    faults = load_faults(p)["faults"]
    open_faults = [{"fault_id": fid, "ref": f["ref"], "check_id": f["check_id"], "severity": f["severity"],
                    "state": f["state"], "first_seen": f["first_seen"][:10]}
                   for fid, f in sorted(faults.items()) if f["state"] in ("open", "suppressed")]
    payload = json.dumps(build_payload(run.rec, open_faults), indent=1, sort_keys=True).encode()
    h = hashlib.sha256(payload).hexdigest()
    prompt = p.digest_prompt.read_text(encoding="utf-8") if p.digest_prompt.exists() else None
    if prompt is None:
        run.rec["digest"] = {"status": "unavailable", "reason": "digest-prompt.md missing"}
        return
    pi = shutil.which("pi") or str(Path.home() / ".pi/agent/bin/pi")
    tmp = p.state / f"digest-{run.id}.json"
    attempts, text, reason = 0, None, None
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "wb") as f:  # payload by FILE: `pi --print` does not accept stdin
            f.write(payload)
        for _ in range(2):  # one retry max
            attempts += 1
            try:
                res = subprocess.run(
                    [pi, "--print", "--no-session", "--no-tools", "--no-extensions",
                     "--model", dcfg["model"], "--system-prompt", prompt,
                     f"@{tmp}", "Write the digest now from the attached JSON."],
                    capture_output=True, text=True, timeout=int(dcfg["timeout_s"]), check=False)
                if res.returncode == 0 and res.stdout.strip():
                    text, reason = res.stdout.strip()[:4000], None
                    break
                reason = f"pi exit {res.returncode}"
            except (OSError, subprocess.SubprocessError) as e:
                reason = type(e).__name__
    finally:
        if tmp.exists():
            tmp.unlink()
    run.rec["digest"] = {"status": "ok" if text else "unavailable", "model": dcfg["model"],
                         "payload_sha256": h, "payload_bytes": len(payload), "attempts": attempts,
                         "reason": None if text else reason, "text": text}


# ----------------------------------------------------------------- commands

def active_sites(p: Paths) -> list[dict]:
    return [s for s in load_sites(p) if s.get("state") == "active"]


def print_summary(rec: dict):
    print(f"run {rec['run_id']} kind={rec['kind']} exit={rec['exit_code']}")
    if rec.get("control"):
        print(f"control: {rec['control']['status']}")
    for s in rec["sites"]:
        counts = {k: sum(1 for v in s.get("check_status", {}).values() if v == k) for k in ("fail", "inconclusive", "pass")}
        print(f"  {s['ref']} {s['domain']}: fail={counts['fail']} inconclusive={counts['inconclusive']} pass={counts['pass']}")
        for e in s.get("checks", []):
            if e["status"] == "fail":
                print(f"    [{e['severity']}] {e['fault_id']} {e['evidence']}")
    for f in rec.get("feeds", []):
        print(f"  feed {f['feed']}: {f['status']}" + (f" ({f.get('reason')})" if f["status"] != "ok" else ""))
    if rec.get("doctor"):
        print(f"  doctor: {rec['doctor']['status']}")
    if rec.get("notify"):
        print(f"  notify: {rec['notify'].get('status')}")
    if rec.get("digest"):
        print(f"  digest: {rec['digest'].get('status')}")
    for e in rec.get("errors", []):
        print(f"  ERROR {e['stage']}: {e['error']}")


def cmd_check(p: Paths, args) -> int:
    cfg = load_config(p)
    if args.control_hosts:
        cfg["control_hosts"] = args.control_hosts.split(",")
    sites = active_sites(p)
    run = Run("check", p)
    rc = EXIT_ERROR
    try:
        rc = stage_check(run, cfg, sites)
    except Exception as e:
        run.err("check", e)
    if run.rec["errors"]:
        rc = EXIT_ERROR
    run.rec["exit_code"] = rc
    run.save()
    print_summary(run.rec)
    return rc


def cmd_feeds(p: Paths, args, notify: bool = False) -> int:
    cfg = load_config(p)
    if args.notify:
        notify = True
    only = [args.only] if getattr(args, "only", None) else None
    sites = active_sites(p)
    run = Run("kev" if only == ["kev"] else "feeds", p)
    try:
        stage_feeds(run, cfg, sites, only)
    except Exception as e:
        run.err("feeds", e)
    if notify:
        try:
            stage_notify(run, cfg)
        except Exception as e:
            run.err("notify", e)
    rc = EXIT_ERROR if run.rec["errors"] else EXIT_OK
    run.rec["exit_code"] = rc
    run.save()
    print_summary(run.rec)
    return rc


def cmd_doctor(p: Paths, args) -> int:
    cfg = load_config(p)
    run = Run("doctor", p)
    rc = EXIT_OK
    try:
        d = stage_doctor(run, cfg)
        rc = EXIT_OK if d["status"] == "consistent" else EXIT_ERROR
    except Exception as e:
        run.err("doctor", e)
        rc = EXIT_ERROR
    run.rec["exit_code"] = rc
    run.save()
    print_summary(run.rec)
    return rc


def cmd_digest(p: Paths, args) -> int:
    cfg = load_config(p)
    if not p.latest.exists():
        print("no run record to digest", file=sys.stderr)
        return EXIT_ERROR
    rec = json.loads(p.latest.resolve().read_text(encoding="utf-8"))
    run = Run("digest", p)
    run.id = rec["run_id"]
    run.rec = rec
    stage_digest(run, cfg)
    run.save()
    print((run.rec["digest"] or {}).get("text") or f"digest unavailable: {run.rec['digest'].get('reason')}")
    return EXIT_OK


def cmd_weekly(p: Paths, args) -> int:
    cfg = load_config(p)
    sites = active_sites(p)
    run = Run("weekly", p)
    rc_check = EXIT_OK
    for stage, fn in [
        ("check", lambda: stage_check(run, cfg, sites)),
        ("feeds", lambda: stage_feeds(run, cfg, sites, None)),
        ("doctor", lambda: stage_doctor(run, cfg)),
        ("notify", lambda: stage_notify(run, cfg, scope="open")),
        ("digest", lambda: stage_digest(run, cfg)),
    ]:
        try:
            out = fn()
            if stage == "check":
                rc_check = out
        except Exception as e:
            run.err(stage, e)
        run.save()  # persist after every stage; a crash leaves a partial but honest record
    rc = EXIT_ERROR if run.rec["errors"] else (EXIT_INCONCLUSIVE if rc_check == EXIT_INCONCLUSIVE else EXIT_OK)
    run.rec["exit_code"] = rc
    run.save()
    print_summary(run.rec)
    return rc


def cmd_validate(p: Paths, args) -> int:
    ok = True
    try:
        load_sites(p)
        print("sites.toml: OK")
    except Exception as e:
        ok = False
        print(f"sites.toml: {e}")
    try:
        load_config(p)
        print("config.toml: OK")
    except Exception as e:
        ok = False
        print(f"config.toml: {e}")
    return EXIT_OK if ok else EXIT_ERROR


def cmd_add(p: Paths, args) -> int:
    if not args.evidence or not args.evidence.strip():
        print("refused: --evidence (two-green hygiene reference) is required", file=sys.stderr)
        return EXIT_REFUSED
    cfg = load_config(p)
    raw = tomllib.loads(p.sites.read_text(encoding="utf-8")) if p.sites.exists() else {}
    sites = raw.get("site", [])
    if any(s.get("ref") == args.ref for s in sites):
        print(f"refused: {args.ref} already registered", file=sys.stderr)
        return EXIT_REFUSED
    site = {"ref": args.ref, "domain": args.domain, "canonical": args.canonical or f"https://{args.domain}/",
            "repo_path": args.repo_path, "site_root": args.site_root,
            "stack": [s.strip() for s in args.stack.split(",") if s.strip()],
            "profile": {"sitemap_expected": not args.no_sitemap, "drift_mode": args.drift_mode,
                        "domain_check": not args.no_domain_check},
            "state": "candidate", "evidence": args.evidence.strip()}
    if args.served_file:
        site["profile"]["served_files"] = list(args.served_file)
    if args.bogus_marker:
        site["profile"]["bogus_404_marker"] = args.bogus_marker
    if args.expiry_domain:
        site["expiry"] = {"domain": args.expiry_domain}
    errs = validate_sites(sites + [site])
    if errs:
        print("refused: " + "; ".join(errs), file=sys.stderr)
        return EXIT_REFUSED
    # baseline check on the candidate before it may become active
    run = Run("add-baseline", p)
    run.rec["sites_pending"] = args.ref
    rc = EXIT_REFUSED
    try:
        rc_ctl = stage_check(run, cfg, [site], persist=False)
        if rc_ctl == EXIT_INCONCLUSIVE:
            rc = EXIT_INCONCLUSIVE
            print("refused: control check failed; baseline inconclusive", file=sys.stderr)
        else:
            highs = [e for s in run.rec["sites"] for e in s.get("checks", [])
                     if e["status"] == "fail" and e["severity"] == "high"]
            if highs:
                print("refused: high-severity faults at baseline: " + ", ".join(e["fault_id"] for e in highs), file=sys.stderr)
                rc = EXIT_REFUSED
            else:
                site["state"] = "active"
                rc = EXIT_OK
    except Exception as e:
        run.err("add-baseline", e)
    run.rec["exit_code"] = rc
    run.save()
    if rc == EXIT_OK:
        atomic_write(p.sites, dump_sites(sites + [site]))
        print(f"added {args.ref} as active (baseline run {run.id})")
    else:
        print(f"{args.ref} not activated; baseline run {run.id} recorded (state would have been candidate)")
    print_summary(run.rec)
    return rc


def cmd_list(p: Paths, args) -> int:
    data = load_faults(p)
    rows = [(fid, f) for fid, f in data["faults"].items() if args.all or f["state"] in ("open", "suppressed")]
    if args.ref:
        rows = [(fid, f) for fid, f in rows if f["ref"] == args.ref]
    rank = {"high": 0, "medium": 1, "low": 2}
    rows.sort(key=lambda x: (rank.get(x[1]["severity"], 9), x[0]))
    for fid, f in rows:
        print(f"{f['severity']:<7} {f['state']:<10} {fid}  first={f['first_seen'][:10]} last={f['last_seen'][:10]}")
    print(f"{len(rows)} fault(s); faults.json updated {data.get('updated')}")
    return EXIT_OK


def cmd_show(p: Paths, args) -> int:
    data = load_faults(p)
    f = data["faults"].get(args.fault_id)
    if f is None:
        print(f"unknown fault id {args.fault_id}", file=sys.stderr)
        return EXIT_REFUSED
    sites = {s["ref"]: s for s in load_sites(p)} if p.sites.exists() else {}
    site = sites.get(f["ref"], {})
    print(json.dumps({"fault_id": args.fault_id, **f}, indent=1, sort_keys=True))
    if site:
        print(f"site {f['ref']}: {site.get('domain')} repo={site.get('repo_path')} site_root={site.get('site_root')}")
    print(f"last run record: {p.latest.resolve().name if p.latest.exists() else 'none'}")
    print("re-check: site-maintenance.py check   (or: site-maintenance.py list --ref " + f["ref"] + ")")
    return EXIT_OK


def cmd_suppress(p: Paths, args) -> int:
    if not args.reason.strip():
        print("refused: reason required", file=sys.stderr)
        return EXIT_REFUSED
    until = dt.date.fromisoformat(args.until)
    today = now_utc().date()
    if until <= today or (until - today).days > 180:
        print("refused: until must be a future date within 180 days", file=sys.stderr)
        return EXIT_REFUSED
    cfg = load_config(p)
    cfg["suppress"] = [s for s in cfg["suppress"] if s["fault_id"] != args.fault_id]
    cfg["suppress"].append({"fault_id": args.fault_id, "reason": args.reason.strip(),
                            "until": until.isoformat(), "added": today.isoformat()})
    atomic_write(p.config, dump_config(cfg))
    stamp = iso(now_utc())
    data = load_faults(p)
    apply_suppressions(data, cfg, today)
    save_faults(p, data, stamp)
    print(f"suppressed {args.fault_id} until {until.isoformat()} (still visible in run records)")
    return EXIT_OK


def cmd_resolve(p: Paths, args) -> int:
    if not args.reason.strip():
        print("refused: reason required", file=sys.stderr)
        return EXIT_REFUSED
    stamp = iso(now_utc())
    data = load_faults(p)
    f = data["faults"].get(args.fault_id)
    if f is None:
        print(f"unknown fault id {args.fault_id}", file=sys.stderr)
        return EXIT_REFUSED
    f["state"] = "resolved"
    f["resolved_run"] = f"manual: {args.reason.strip()[:120]}"
    save_faults(p, data, stamp)
    print(f"resolved {args.fault_id} (manual)")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    os.umask(0o077)
    ap = argparse.ArgumentParser(prog="site-maintenance.py", description=__doc__.split("\n\n")[0])
    ap.add_argument("--home", help="maintenance directory (default $SITE_MAINT_HOME or ~/.pi/agent/maintenance)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--control-hosts", help="comma-separated override (tests / drills)")
    f = sub.add_parser("feeds")
    f.add_argument("--only", choices=["kev", "nvd", "hn", "hugo"])
    f.add_argument("--notify", action="store_true")
    sub.add_parser("kev").set_defaults(only="kev", notify=True)
    sub.add_parser("doctor")
    sub.add_parser("digest")
    sub.add_parser("weekly")
    sub.add_parser("validate")
    a = sub.add_parser("add")
    a.add_argument("ref")
    a.add_argument("--domain", required=True)
    a.add_argument("--canonical")
    a.add_argument("--repo-path", required=True)
    a.add_argument("--site-root", required=True)
    a.add_argument("--stack", required=True, help="comma list from wordpress,php,apache,nginx,hugo,static")
    a.add_argument("--drift-mode", default="static-files", choices=sorted(DRIFT_MODES))
    a.add_argument("--served-file", action="append", default=None,
                   help="repo-root-relative served file; repeat for each (required with --drift-mode manifest)")
    a.add_argument("--bogus-marker")
    a.add_argument("--expiry-domain", help="YYYY-MM-DD manual domain expiry (RDAP fallback)")
    a.add_argument("--no-sitemap", action="store_true")
    a.add_argument("--no-domain-check", action="store_true")
    a.add_argument("--evidence", required=True, help="two-green verification reference (deployed sha + verifier pass)")
    ls = sub.add_parser("list")
    ls.add_argument("--all", action="store_true")
    ls.add_argument("--ref")
    sh = sub.add_parser("show")
    sh.add_argument("fault_id")
    sp = sub.add_parser("suppress")
    sp.add_argument("fault_id")
    sp.add_argument("--reason", required=True)
    sp.add_argument("--until", required=True)
    rs = sub.add_parser("resolve")
    rs.add_argument("fault_id")
    rs.add_argument("--reason", required=True)
    args = ap.parse_args(argv)

    p = Paths(args.home)
    p.ensure()
    handlers = {
        "check": cmd_check, "feeds": cmd_feeds, "kev": lambda p, a: cmd_feeds(p, a, notify=True),
        "doctor": cmd_doctor, "digest": cmd_digest, "weekly": cmd_weekly, "validate": cmd_validate,
        "add": cmd_add, "list": cmd_list, "show": cmd_show, "suppress": cmd_suppress, "resolve": cmd_resolve,
    }
    try:
        if args.cmd in ("check", "feeds", "kev", "doctor", "digest", "weekly", "add"):
            with Lock(p):
                return handlers[args.cmd](p, args)
        return handlers[args.cmd](p, args)
    except (ValueError, OSError, tomllib.TOMLDecodeError) as e:
        print(f"runner error: {type(e).__name__}: {str(e)[:300]}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
