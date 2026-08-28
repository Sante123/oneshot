# Publishing this repository

The one rule: **`.claude-plugin/` must be at the repository root.** Everything else here
follows from that.

---

## Pre-push checklist

```bash
python3 tests/validate_structure.py   # installability — must pass
python3 tests/run_tests.py            # scanner behavior — must pass
git status --short                    # nothing unexpected staged
git ls-files .claude-plugin/          # must list plugin.json AND marketplace.json
git ls-tree --name-only HEAD          # must show .claude-plugin, skills, agents, commands
```

If `git ls-tree --name-only HEAD` shows a single `oneshot/` directory instead, the commit
is nested and no installer will accept it. See [Recovering a nested repo](#recovering-a-nested-repository).

---

## First publish

```bash
git init
git add -A
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOU/oneshot.git
git push -u origin main
```

Then confirm on GitHub that the file list at the top of the repo page shows
`.claude-plugin`, `agents`, `commands`, `skills` — **not** a single folder.

> GitHub hides dotfiles from nothing, but some file browsers do. If you can't see
> `.claude-plugin`, check it directly: `https://github.com/YOU/oneshot/tree/main/.claude-plugin`

Install it:

```
/plugin marketplace add YOU/oneshot
/plugin install oneshot@oneshot
```

---

## Recovering a nested repository

The symptom is an installer saying **"not a marketplace — no `marketplace.json`"**, and a
clone that rolls back after validation. The cause is a commit whose root looks like:

```
README.md
oneshot/          <- everything is in here
```

instead of:

```
.claude-plugin/
agents/
commands/
skills/
...
```

### Fix it locally, then publish

```bash
cd /path/to/repo

# 1. Move everything up one level, preserving history.
git mv oneshot/* .
git mv oneshot/.claude-plugin oneshot/.github oneshot/.gitignore oneshot/.oneshot .
rmdir oneshot

# 2. Prove it worked.
python3 tests/validate_structure.py
git ls-tree --name-only HEAD   # after committing

# 3. Commit.
git add -A
git commit -m "Move plugin contents to the repository root"
```

### Publishing over a diverged remote

If the remote has picked up commits of its own — web-UI edits, partial fixes — your local
history and the remote will have diverged. Two options:

**A. Replace the remote history** (right when the remote commits are only churn on the
broken layout):

```bash
git push --force-with-lease origin main
```

`--force-with-lease` refuses to overwrite if someone else pushed since your last fetch, so
it is the safe form of `--force`. Never use plain `--force` on a shared branch.

**B. Merge, keeping both histories** (right when the remote has changes worth keeping):

```bash
git fetch origin
git merge origin/main --allow-unrelated-histories
# resolve conflicts, keeping the ROOT-LEVEL versions of every file
python3 tests/validate_structure.py
git push origin main
```

After either, re-add the marketplace so the cached manifest refreshes:

```
/plugin marketplace remove oneshot
/plugin marketplace add YOU/oneshot
/plugin install oneshot@oneshot
```

---

## Do not commit

`.gitignore` covers these, but they have a habit of sneaking in via `git add -f` or a
GitHub web upload:

| Don't commit | Why |
|---|---|
| `*.zip` release archives | Bloats the clone; builds belong in Releases |
| `tests/fixtures/*/android/.gradle/` | Machine-specific build state, changes on every run |
| `__pycache__/`, `*.pyc` | Regenerated on import |
| `oneshot-report.*`, `review-notes.md` | Generated output |
| `.oneshot/waivers.yaml` | Project-local; `waivers.example.yaml` is the tracked one |

If something is already tracked and shouldn't be:

```bash
git rm -r --cached path/to/thing
git commit -m "Stop tracking generated files"
```

---

## Cutting a release

```bash
# 1. Bump the version in BOTH manifests and install.py
#    .claude-plugin/plugin.json       -> "version"
#    .claude-plugin/marketplace.json  -> metadata.version AND plugins[0].version
#    install.py                       -> the "version" written to the install manifest

# 2. Re-verify the rule catalog before shipping compliance advice
python3 skills/store-compliance/scripts/oneshot.py verify-deadlines

# 3. Update CHANGELOG.md

# 4. Validate and test
python3 tests/validate_structure.py
python3 tests/run_tests.py

# 5. Tag
git tag -a v1.0.0 -m "v1.0.0"
git push origin main --tags
```

Attach a build archive to the GitHub Release rather than committing one. Build it flat —
**contents at the archive root, no wrapping directory** — so extracting it can't recreate
the nesting problem:

```bash
cd /path/to/oneshot
zip -r ../oneshot-v1.0.0.zip . \
  -x '*__pycache__*' '*.git/*' '*.zip' '*/.gradle/*'
unzip -l ../oneshot-v1.0.0.zip | head -5   # first entries must NOT start with "oneshot/"
```

---

## Making the repo usable by others

Worth doing once, in the GitHub UI:

- **Description**: "Get your iOS and Android app approved on the first App Store / Play submission."
- **Topics**: `app-store`, `google-play`, `app-review`, `ios`, `android`, `compliance`, `claude-code`, `claude-plugin`
- **Enable Issues** — the project depends on people reporting stale rules
- **Branch protection on `main`** requiring the CI check, so a nested or broken layout can
  never be merged again

The CI workflow in `.github/workflows/ci.yml` runs `validate_structure.py`,
`run_tests.py`, and an end-to-end installer test on Python 3.9, 3.11, and 3.13.
