---
name: studio-github-comment
description: Codified process for posting comments or issues to upstream open-source GitHub repos (e.g. the ArtCraft suite under the storytold org) as the studio's GitHub identity. Use when the user asks to "post an issue", "file a bug", "comment on the PR", "report upstream", or engage any external GitHub repo. Covers credential use, repo resolution, duplicate/PR checking, the comment-vs-issue decision, and the draft format.
---

# Studio GitHub engagement (issues & PR comments)

The studio posts to **external open-source repos as `ktheunlikedoll`** using the
stored credential in `~/.git-credentials` — via the helper
`~/.pi/agent/bin/github-comment.py` (wraps the GitHub REST API; the token is
never echoed). No `gh` CLI is required.

## The process (always in this order)

### 1. Resolve the repo
- RPM-installed apps: `rpm -qi <pkg> | grep URL` → the GitHub repo.
- Suite context: the ArtCraft apps are one repo per app — `storytold/vectorcraft`,
  `storytold/photocraft`, `storytold/designcraft`, `storytold/pdfcraft`,
  `storytold/cadcraft` (+ `storytold/craft-launcher` for the launcher itself).
  **Ask the user which app** if the ask names the suite, not the app.
- Otherwise search the web for `<project> github repository` and confirm from
  the repo homepage/metadata.

### 2. Verify identity before anything
```
python3 ~/.pi/agent/bin/github-comment.py whoami
```
If it errors, stop and tell the user — do not improvise alternate credentials.

### 3. Duplicate & in-flight check (never skip)
```
python3 ~/.pi/agent/bin/github-comment.py dups --repo OWNER/REPO --terms "term,another term"
```
Run 2–3 varied term sets (the bug's behavior words, e.g. "single instance",
"file handoff", "new instance"). For each hit, note **kind**:
- `[PR|open]` — someone is already *implementing* the fix → a new issue is a duplicate.
- `[ISSUE|open]` — already tracked → comment/reference, don't re-file.
- `[...|closed]` — feature may already exist (e.g. opt-in setting); verify the
  user's version before filing.

### 4. Decision matrix
| Finding | Action |
|---|---|
| Open PR implementing the fix | **Recommend commenting on the PR** (real-user confirmation + environment). File a standalone issue only if the user wants tracking independent of the PR's fate. |
| Open issue, no PR | Comment confirming/adding the user's environment, or new cross-reference issue if the user wants it tracked separately. |
| Only closed issues | Check whether the shipped version has the fix/setting; then new issue or nothing. |
| No matches | Draft a new issue. |

The user picks; never post without the user's go on the drafted text.

### 5. Draft format (OS bug reports)
- **Title:** `[<OS>] <concise behavior>` — e.g. `[Linux] Opening an associated file from the file manager launches a new instance instead of reusing the running window`.
- **Body:** what the user does → **Expected** → **Actual**; then an
  **environment block**: distro + desktop (`/etc/os-release`, `uname -r`),
  package + version (`rpm -qi`), app version/date.
- Cross-reference related issues/PRs by number.
- Close with a test offer when plausible ("happy to test on <distro> when a
  build is available") — maintainers weigh this.
- Calibrated honesty: report what was actually observed, not inferred.

### 6. Post, verify, clean up
Write the body to a temp file (JSON-escaping handled by the helper), post, and
confirm the returned URL:
```
python3 ~/.pi/agent/bin/github-comment.py comment --repo OWNER/REPO --issue N --body-file /tmp/body.md
python3 ~/.pi/agent/bin/github-comment.py issue --repo OWNER/REPO --title "..." --body-file /tmp/body.md
```
Report the URL to the user; delete the temp file.

## Pitfalls encoded from the first run (2026-10-30, VectorCraft #3423)
- **Check PRs, not just issues** — search results surface PRs; a PR body reading
  "this PR implements…" means the fix is in flight. Filing a duplicate issue
  there is noise.
- `gh` CLI is absent; the API helper is the path. Fine-grained tokens still
  work for public-repo issue/comment writes.
- PR `mergeable: false` ≠ rejected — just pending conflicts; the comment is
  still useful.
- Search API needs multiple term angles; one query misses.
