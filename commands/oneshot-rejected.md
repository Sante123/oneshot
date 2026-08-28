---
description: Diagnose an App Store or Play rejection and produce the fix plus the reply
argument-hint: "<guideline number or the rejection message>"
---

## Locate the CLI

Use the first of these that exists; `${CLAUDE_PLUGIN_ROOT}` is only set under a plugin
install.

```
${CLAUDE_PLUGIN_ROOT}/skills/store-compliance/scripts/oneshot.py
~/.claude/skills/store-compliance/scripts/oneshot.py
./.claude/skills/store-compliance/scripts/oneshot.py
./skills/store-compliance/scripts/oneshot.py
```

Below, `<CLI>` means the path you resolved.

---

The user was rejected. Details: `$ARGUMENTS`

### 1. Get the exact guideline number

Extract it from the pasted message, or ask. Also ask for any screenshots or video the
reviewer attached in Resolution Center — reviewers usually attach evidence, and it is the
fastest route to the cause.

### 2. Explain the rule

```bash
python3 <CLI> explain --guideline <number>
```

### 3. Reproduce in the exact configuration named

Device model, OS version, network, region, account. Most 2.1 rejections reproduce only in
the reviewer's specific setup — an IPv6-only network, a denied permission, a cold install.

### 4. Decide: fix, or clarification

- **Fix** → change the code or metadata, upload a new build, reply describing exactly what
  changed and where to see it.
- **Misunderstanding** → reply in Resolution Center **without a new build**, with a
  step-by-step walkthrough and a screen recording. Uploading a build resets the queue and
  loses the reviewer's context.

### 5. Draft the reply

Use the template in `references/submission-playbook.md` §6. Name exact navigation paths.
Re-verify the demo account and state the time you verified it.

### 6. Then audit everything

A rejection under one guideline usually means the submission was never audited under any of
them — expect more waiting behind it.

```
/oneshot-audit
```

Do not argue with the reviewer, do not resubmit unchanged, and do not contact reviewers
outside the official channels (Apple 5.6 Developer Code of Conduct).
