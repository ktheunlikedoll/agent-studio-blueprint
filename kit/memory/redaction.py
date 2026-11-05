#!/usr/bin/env python3
"""Fail-closed admission filter for structured memory observations.

Raw transcript text is never accepted here. Callers provide one structured
observation at a time; this module either returns a bounded, sanitised excerpt
or rejects it completely. It deliberately errs on exclusion.
"""
from __future__ import annotations
import hashlib
import re
from dataclasses import dataclass

MAX_TEXT = 240

# Finance is a separate system. Reject observations containing finance signals,
# even when they appear alongside otherwise useful studio context.
_FINANCE = re.compile(r"\b(?:finance|invoice|invoic(?:e|ing|ed)|payment|paid|bank(?:ing)?|ledger|vat|sars|tax|quote|quotation|credit[- ]?note|accounts? receivable|client billing|bookkeep)\b", re.I)
# High-confidence credential patterns. Any hit rejects the entire observation.
_SECRET = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{12,}\b"),
    re.compile(r"\b(?:xox[baprs]-)[A-Za-z0-9-]{10,}\b", re.I),
    re.compile(r"\b(?:ghp|github_pat|glpat)-[A-Za-z0-9_-]{12,}\b", re.I),
    re.compile(r"\b(?:api[_ -]?key|access[_ -]?token|secret|password|passwd|pwd|mcp[_ -]?key)\s*[:=]\s*[^\s,;]{4,}", re.I),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
]
_EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
_PHONE = re.compile(r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)")
_ADDRESS = re.compile(r"\b(?:street|st\.?|road|rd\.?|avenue|ave\.?|address|postal code|postcode|residential)\b[^\n]{0,120}", re.I)
_PAYMENT = re.compile(r"\b(?:card|cvv|iban|account number|routing number|payment reference|bank reference)\b[^\n]{0,100}", re.I)
_CLIENT_LABEL = re.compile(r"\bclient(?:\s+name)?\s*[:=-]\s*([A-Z][A-Za-z'’-]*(?:\s+[A-Z][A-Za-z'’-]*){0,4})", re.I)
_CLIENT_NAME = re.compile(r"\b(?:client|customer|contact)\s+(?:is\s+)?([A-Z][A-Za-z'’-]*(?:\s+[A-Z][A-Za-z'’-]*){0,4})\b")
_PROJECT = re.compile(r"\b(?:project|job|brief|site)\s*[:=-]\s*([A-Za-z0-9][A-Za-z0-9 _-]{1,40})", re.I)

@dataclass
class RedactionResult:
    accepted: bool
    text: str = ""
    reason: str = ""


def _project_token(text: str) -> str:
    m = _PROJECT.search(text)
    basis = (m.group(1).strip() if m else "unknown-project").lower()
    # Stable, non-reversible project reference. Four digits satisfy the public
    # token shape without retaining a client identifier.
    num = int(hashlib.sha256(basis.encode()).hexdigest()[:8], 16) % 10000
    return f"client-ref:PRJ-{num:04d}"


def redact_observation(text: str) -> RedactionResult:
    """Sanitise an approved structured observation or fail closed."""
    if not isinstance(text, str) or not text.strip():
        return RedactionResult(False, reason="empty")
    if len(text) > MAX_TEXT * 3:
        return RedactionResult(False, reason="oversize")
    if _FINANCE.search(text):
        return RedactionResult(False, reason="finance-excluded")
    for pattern in _SECRET:
        if pattern.search(text):
            return RedactionResult(False, reason="secret-or-credential")
    # Ambiguous high-risk personal data rejects rather than trying to mask it.
    if _ADDRESS.search(text) or _PAYMENT.search(text):
        return RedactionResult(False, reason="personal-sensitive")

    out = text
    out = _EMAIL.sub(_project_token(text), out)
    out = _PHONE.sub(_project_token(text), out)
    # Client-labelled names are replaced, never retained. Restrict this to
    # explicit client/customer labels to avoid destroying ordinary prose.
    token = _project_token(text)
    out = _CLIENT_LABEL.sub(token, out)
    out = _CLIENT_NAME.sub(lambda m: token, out)
    # Email/client substitutions can cascade through the client-name matcher;
    # collapse only immediately repeated references, preserving all other text.
    out = re.sub(r'\b(client-ref:PRJ-(\d{4}))(?::PRJ-\2)+\b', r'\1', out)
    # Any residual email-like or credential-looking fragment is a fail-closed
    # signal after transformations.
    if _EMAIL.search(out) or any(p.search(out) for p in _SECRET):
        return RedactionResult(False, reason="residual-sensitive")
    out = re.sub(r"\s+", " ", out).strip()
    if len(out) > MAX_TEXT:
        out = out[:MAX_TEXT].rsplit(" ", 1)[0] + "…"
    if not out:
        return RedactionResult(False, reason="empty-after-redaction")
    return RedactionResult(True, text=out)
