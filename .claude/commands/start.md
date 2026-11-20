---
description: Session start routine – bring the local repo up to date and report the project status from git, GitHub and the live site
---

Run the session start routine from CLAUDE.md ("Session start") and report the
result to the maintainer **in German**.

Rules: show `gh` output unfiltered (no `tail`, `head`, `grep`, no hidden
stderr). If a step fails, report the error and continue with the next step.
Do not change anything (no commits, merges, deploys) – this is read-only
except for switching to `main` and pulling.

1. Local repo:
   - `git status --short` – if there are uncommitted changes, stop here and
     ask the maintainer before switching branches.
   - `git switch main && git pull`
2. Read `docs/STATUS.md`.
3. `git log --oneline -15`
4. `gh pr list --state open`
5. `gh issue list --state open`
6. `gh run list --limit 10`
7. Live site:
   - `curl -s {{LIVE_URL}}/version`
   - `git rev-parse origin/main`
   - Compare: is the deployed commit the head of `main`? If not, list the
     commits not yet deployed (`git log --oneline <deployed>..origin/main`)
     and check that CI pushed an image for `origin/main` (step 6).
   - `curl -s -o /dev/null -w "%{http_code}\n" {{LIVE_URL}}/`

Then summarise in German, short:
- what is live (commit, date) and whether it matches `main`,
- open PRs, failed or cancelled CI runs,
- open issues grouped by who has to act,
- anything in `docs/STATUS.md` that contradicts what you found (point it out,
  do not fix it silently),
- a suggestion for what to do next.
