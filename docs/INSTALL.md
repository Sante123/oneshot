# Installing oneshot

There are three ways in. **Route C always works** — if a plugin installer rejects the
repo for any reason, skip straight to it.

| Route | Best for | Needs |
|---|---|---|
| **A — Marketplace** | Claude Code / Cowork users who want `/plugin` management and updates | A published Git repo |
| **B — Local plugin** | Working on a clone, or a private repo | A local checkout |
| **C — Direct install** | Anything else, or when A and B fail | Python 3.8+ |
| **D — Standalone CLI** | CI, or using the scanner without Claude at all | Python 3.9+ |

---

## Before anything: verify the layout

Almost every install failure is the same one — **the repository contents are one
directory level too deep**, so no installer can find `.claude-plugin/`.

```bash
cd /path/to/oneshot
python3 tests/validate_structure.py
```

A healthy checkout prints:

```
Structure is valid: installable as a plugin, as a marketplace, and by install.py.
```

The repository root must **directly** contain:

```
oneshot/                     <- the repo root, and the plugin root
├── .claude-plugin/
│   ├── plugin.json          <- REQUIRED here, at the root
│   └── marketplace.json     <- REQUIRED here, at the root
├── skills/store-compliance/SKILL.md
├── agents/*.md
├── commands/*.md
└── install.py
```

If instead you have `oneshot/oneshot/.claude-plugin/...`, see
[Troubleshooting § Nested repository](#1-not-a-marketplace--no-marketplacejson).

---

## Route A — Install from a marketplace

Once the repo is pushed to GitHub with the layout above:

```
/plugin marketplace add Sante123/oneshot
/plugin install oneshot@oneshot
```

`marketplace add` accepts `owner/repo`, a full Git URL, or a local path. It reads
`.claude-plugin/marketplace.json` **at the repository root** — nowhere else.

Verify:

```
/plugin
```

You should see `oneshot` listed with 1 skill, 8 agents, and 4 commands.

---

## Route B — Install from a local checkout

```
/plugin marketplace add /absolute/path/to/oneshot
/plugin install oneshot@oneshot
```

The same root-level manifest requirement applies. This is the fastest loop while
developing — edit files in the checkout, then `/plugin reload` or restart the session.

---

## Route C — Direct install (always works)

This copies the skill, agents, and commands straight into your Claude directory. No
manifest validation, no marketplace, no network.

### macOS / Linux

```bash
cd /path/to/oneshot
python3 install.py
```

### Windows (PowerShell)

```powershell
cd C:\Users\you\Desktop\oneshot
.\install.ps1
```

If PowerShell blocks the script:

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Or skip the wrapper entirely:

```powershell
python install.py
```

### What it does

```
~/.claude/
├── skills/store-compliance/     <- the whole skill, including scripts/ and references/
├── agents/                      <- 8 *.md files
└── commands/                    <- 4 oneshot-*.md files
```

### Options

```bash
python3 install.py --project     # install into ./.claude (this repo only, not global)
python3 install.py --dest PATH   # install into an explicit .claude directory
python3 install.py --check       # report what is installed; change nothing
python3 install.py --uninstall   # remove exactly what the installer added
python3 install.py --force       # overwrite without warnings
```

The installer records what it wrote to `~/.claude/skills/store-compliance/.oneshot-installed.json`,
so `--uninstall` removes precisely those files and nothing else.

**Restart your Claude session after installing** — skills, agents, and commands are read
at startup.

---

## Route D — Standalone CLI, no Claude

The scanner is a plain Python program with **no third-party dependencies**.

```bash
python3 skills/store-compliance/scripts/oneshot.py audit --path /path/to/your/app
```

Nothing needs to be installed. Copy the `skills/store-compliance/scripts/` directory
anywhere you like — it is self-contained.

---

## Verify the install

```bash
# 1. Is the toolkit where Claude reads it?
python3 install.py --check

# 2. Does the scanner run?
python3 ~/.claude/skills/store-compliance/scripts/oneshot.py verify-deadlines

# 3. Does it produce findings on a known-bad project?
python3 ~/.claude/skills/store-compliance/scripts/oneshot.py \
  audit --path tests/fixtures/bad-app --format text | tail -3
# expect: BLOCKER=22  HIGH=17  MEDIUM=4  LOW=1  INFO=3

# 4. Full self-test (from the repo, not the install location)
python3 tests/run_tests.py
python3 tests/validate_structure.py
```

In Claude, after a restart, `/oneshot-audit` should appear in the command list and
"store-compliance" in the skills list.

---

## Troubleshooting

### 1. "Not a marketplace — no `marketplace.json`"

The installer looked for `.claude-plugin/marketplace.json` **at the repository root** and
didn't find it. Almost always this means the contents are nested one level deep — for
example the repo was created by extracting an archive that had a top-level folder, or by
`git init` in the parent of the project directory.

Check:

```bash
ls .claude-plugin/          # should list marketplace.json and plugin.json
ls oneshot/.claude-plugin/  # if THIS is what exists, you are nested
```

Fix, preserving history:

```bash
cd /path/to/repo
git mv oneshot/* .
git mv oneshot/.claude-plugin oneshot/.github oneshot/.gitignore oneshot/.oneshot .
rmdir oneshot
python3 tests/validate_structure.py
git commit -am "Move plugin contents to the repository root"
git push
```

Then re-run `/plugin marketplace add`. If the marketplace was already added, remove and
re-add it so the cached manifest is refreshed:

```
/plugin marketplace remove oneshot
/plugin marketplace add Sante123/oneshot
```

### 2. "The clone was rolled back after validation failed"

Validation is atomic — a rejected repo leaves nothing behind. Run
`python3 tests/validate_structure.py` in a local clone; it reports the specific problem
and the exact command to fix it. Common causes:

- Contents nested one level deep (see above)
- `plugin.json` listing `skills` / `agents` / `commands` paths that don't resolve
- Malformed JSON in either manifest
- An agent whose frontmatter `name` doesn't match its filename

### 3. "No `.claude-plugin` manifest anywhere"

`.claude-plugin` starts with a dot, so `ls` hides it. Use `ls -a`. On Windows, hidden
items are off by default in Explorer — View ▸ Show ▸ Hidden items.

Also check it wasn't excluded from the commit:

```bash
git check-ignore -v .claude-plugin/marketplace.json   # should print nothing
git ls-files .claude-plugin/                          # should list both manifests
```

If the files exist on disk but aren't tracked, they were never pushed:

```bash
git add -f .claude-plugin/
git commit -m "Add plugin manifests"
git push
```

### 4. Slash commands don't appear after installing

- Restart the Claude session — commands are read at startup.
- Confirm the files landed: `ls ~/.claude/commands/oneshot-*.md`
- Check for a name collision with another plugin's `/oneshot-*` command.
- Run `python3 install.py --check`.

### 5. The skill never triggers on its own

The skill fires on its `description`, not its name. Ask for it explicitly:

> Use the store-compliance skill to audit this app for App Store submission.

Or invoke `/oneshot-audit` directly. If it still doesn't load, confirm
`~/.claude/skills/store-compliance/SKILL.md` exists and its frontmatter `name` is
`store-compliance` (it must match the directory name).

### 6. `python3: command not found` on Windows

Windows usually installs `python`, not `python3`. Use `python install.py`, or the py
launcher: `py -3 install.py`. If neither is found, install Python from
<https://www.python.org/downloads/> and tick **Add python.exe to PATH**.

### 7. The audit is very slow

You are probably scanning across a network mount or a synced folder. Copy the project to
local disk first. On local disk a mid-sized app scans in one to three seconds.

### 8. `PLAY-MANIFEST-UNMERGED` / `PLAY-ARTIFACT-MISSING` / `APPLE-SDK-UNVERIFIED`

These are `INFO` findings, not failures. They mean the scan only saw source, so it could
not verify the merged Android manifest, native library alignment, or the build SDK
version. Build first, then re-audit:

```bash
./gradlew :app:processReleaseManifest
./gradlew bundleRelease
```

---

## Uninstalling

```bash
python3 install.py --uninstall          # Route C
```

```
/plugin uninstall oneshot               # Routes A and B
/plugin marketplace remove oneshot
```

---

## Updating

```bash
cd /path/to/oneshot
git pull
python3 tests/validate_structure.py
python3 tests/run_tests.py
python3 install.py --force              # Route C: re-copy over the old install
```

For Routes A and B, `/plugin update oneshot`.

**After any update, re-check the rule catalog's freshness** — store rules change several
times a year:

```bash
python3 ~/.claude/skills/store-compliance/scripts/oneshot.py verify-deadlines
```

It exits non-zero when the catalog is more than 30 days old.
