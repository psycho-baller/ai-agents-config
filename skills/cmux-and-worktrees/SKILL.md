---
name: cmux-and-worktrees
description: Manage parallel development with cmux-style git worktrees in one repository. Use this skill whenever the user asks to run multiple agents in parallel, create or resume isolated worktrees, list/switch/merge/remove worktrees, set up `.cmux/setup`, or recover from worktree conflicts. Use `cmux` commands in this environment.
---

# cmux and Worktrees

Run concurrent coding sessions safely by isolating each task in a git worktree.

## Non-Negotiable Command Rule

- Use `cmux` for every command in this skill.
- Do not substitute with `git worktree` in normal operation.
- If `cmux` fails, check availability first with `type cmux`.

## Preflight

1. Verify current directory is inside a git repo:

```bash
git rev-parse --is-inside-work-tree
```

1. Verify `cmux` availability:

```bash
type cmux
```

1. Ensure worktrees are ignored in git:

```bash
rg -n '^\.worktrees/$' .gitignore || echo '.worktrees/' >> .gitignore
```

1. Inspect active worktrees:

```bash
cmux ls
```

## Core Commands (cmux)

- Create new isolated task: `cmux new <branch>`
- Resume existing task: `cmux start <branch>`
- Jump to worktree: `cmux cd [branch]`
- List worktrees: `cmux ls`
- Merge into primary checkout: `cmux merge [branch] [--squash]`
- Remove worktree + branch: `cmux rm [branch | --all] [--force]`
- Generate setup hook: `cmux init [--replace]`
- Show/set layout config: `cmux config`, `cmux config set layout <nested|outer-nested|sibling> [--global]`
- Update tool: `cmux update`
- Show version: `cmux version`

## Standard Workflow (cmux)

1. Start feature work:

```bash
cmux new feature-auth
```

1. Start urgent fix in parallel:

```bash
cmux new fix-payments
```

1. Merge and clean up bugfix:

```bash
cmux merge fix-payments --squash
git commit -m "fix(payments): resolve checkout bug"
cmux rm fix-payments
```

1. Resume feature:

```bash
cmux start feature-auth
```

## Setup Hook Workflow

1. Generate a project-specific setup hook (if needed):

```bash
cmux init
```

1. If needed, regenerate:

```bash
cmux init --replace
```

1. Run setup inside each worktree immediately after creation/resume:

```bash
bash "$(git rev-parse --show-toplevel)/.cmux/setup"
```

1. Setup expectations:

- Reuses root dependencies (shared `node_modules`) instead of reinstalling per worktree.
- Links env files into the worktree.
- Prepares mobile workspace shims needed for Metro resolution.

## Branch and Path Behavior

- Treat `new` as "new branch + new worktree".
- Treat `start` as "reuse existing worktree/session".
- Expect worktree paths under `.worktrees/<branch>/` in nested layout.
- Expect branch sanitization (e.g., `feature/foo` becomes `feature-foo` path name).
- One branch can only be checked out in one worktree at a time.

## Safety Rules

- Ask for confirmation before `cmux rm --all`.
- Ask for confirmation before `cmux rm --force`.
- Prefer `cmux merge <branch> --squash` for compact history unless user requests full merge commits.
- Ensure worktree changes are committed before merging.
- Remove finished worktrees after successful merge to reduce branch/worktree drift.

## Troubleshooting

- `Not in a git repo`: move to repo root, then rerun.
- `Worktree not found`: run `cmux ls`, then create/resume the correct one.
- `Branch is already checked out`: run `cmux ls` and reuse the existing worktree path.
- Merge blocked by uncommitted changes: commit or stash inside the worktree, then retry.
- Remove blocked by dirty tree: clean state first, or use `cmux rm --force` only with explicit confirmation.
- Mobile dev server from worktree:
  `cd apps/mobile && npm run dev -- --clear --host lan`
- Expo Router shows "Welcome to Expo" unexpectedly:
  kill stale `expo/metro` processes, restart from the target worktree with `--clear`, and reopen dev client.
