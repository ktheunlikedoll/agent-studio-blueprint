#!/usr/bin/env python3
"""GitHub issue/PR engagement helper for the studio.

Reads the stored GitHub credential from ~/.git-credentials (never prints it)
and wraps the GitHub REST API for the three things the studio needs:
identity check, duplicate search, comment posting, issue creation.

Usage:
  github-comment.py whoami
  github-comment.py dups     --repo OWNER/REPO --terms "term one,term two" [--limit 10]
  github-comment.py comment  --repo OWNER/REPO --issue N --body-file FILE
  github-comment.py issue    --repo OWNER/REPO --title "T" --body-file FILE [--labels a,b]

`comment` and `issue` accept --body directly instead of --body-file for short bodies.
Output is one line: the resulting URL, or "ERROR: ..." on failure.
"""
import argparse, json, os, re, sys, urllib.request

CRED_FILE = os.path.expanduser("~/.git-credentials")
API = "https://api.github.com"


def token():
    try:
        line = open(CRED_FILE).read().strip()
    except OSError:
        sys.exit("ERROR: cannot read credential file")
    m = re.match(r"https://[^:@/]+:([^@]+)@(?:www\.)?github\.com/?", line)
    if not m:
        sys.exit("ERROR: no github.com credential found in " + CRED_FILE)
    return m.group(1)


def api(method, path, payload=None, tok=None):
    req = urllib.request.Request(
        API + path, method=method,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": "token " + tok,
                 "Content-Type": "application/json",
                 "User-Agent": "studio-engagement-helper"})
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode()).get("message", "")
        except Exception:
            msg = str(e)
        sys.exit(f"ERROR: HTTP {e.code}: {msg}")


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("whoami")

    d = sub.add_parser("dups")
    d.add_argument("--repo", required=True)
    d.add_argument("--terms", required=True, help="comma-separated search terms")
    d.add_argument("--limit", type=int, default=10)

    c = sub.add_parser("comment")
    c.add_argument("--repo", required=True)
    c.add_argument("--issue", type=int, required=True)
    c.add_argument("--body-file")
    c.add_argument("--body")

    i = sub.add_parser("issue")
    i.add_argument("--repo", required=True)
    i.add_argument("--title", required=True)
    i.add_argument("--body-file")
    i.add_argument("--body")
    i.add_argument("--labels", default="")

    a = p.parse_args()
    tok = token()

    if a.cmd == "whoami":
        me = api("GET", "/user", tok=tok)
        print(f"login={me['login']} name={me.get('name','')}")
        return

    if a.cmd == "dups":
        hits = []
        for term in [t.strip() for t in a.terms.split(",") if t.strip()]:
            q = urllib.parse.quote(f"repo:{a.repo} {term}")
            res = api("GET", f"/search/issues?q={q}&per_page={a.limit}&sort=updated", tok=tok)
            for it in res.get("items", []):
                kind = "PR" if "pull_request" in it else "ISSUE"
                hits.append((it["number"], kind, it["state"], it["title"], it["html_url"]))
        seen = set()
        for n, kind, state, title, url in hits:
            if n in seen:
                continue
            seen.add(n)
            print(f"#{n} [{kind}|{state}] {title}\n    {url}")
        if not seen:
            print("NO_MATCHES")
        return

    body = (open(a.body_file).read() if getattr(a, "body_file", None) else a.body)
    if not body:
        sys.exit("ERROR: empty body")

    if a.cmd == "comment":
        r = api("POST", f"/repos/{a.repo}/issues/{a.issue}/comments",
                {"body": body}, tok=tok)
        print(r["html_url"])
    else:
        payload = {"title": a.title, "body": body}
        if a.labels:
            payload["labels"] = [l.strip() for l in a.labels.split(",")]
        r = api("POST", f"/repos/{a.repo}/issues", payload, tok=tok)
        print(r["html_url"])


if __name__ == "__main__":
    main()
