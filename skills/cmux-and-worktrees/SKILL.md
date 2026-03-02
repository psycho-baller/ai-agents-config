---
name: cmux-and-worktrees
description: Manage parallel development with cmux-style git worktrees in one repository. Use this skill whenever the user asks to run multiple agents in parallel, create or resume isolated worktrees, list/switch/merge/remove worktrees, set up `.cmux/setup`, or recover from worktree conflicts. In this environment, always use the `cmux` alias in commands.
---

# cmux and Worktrees

Run concurrent coding sessions safely by isolating each task in a git worktree.

## Non-Negotiable Command Rule

- Use `cmux` for every command in this skill.
- Do not substitute `cmux` in normal operation.
- If `cmux` fails, check alias availability with `type cmux` before taking any fallback action.

## Preflight

1. Verify current directory is inside a git repo:

```bash
git rev-parse --is-inside-work-tree
```

2. Verify `cmux` is available:

```bash
type cmux
```

3. Ensure worktrees are ignored in git:

```bash
rg -n '^\.worktrees/$' .gitignore || echo '.worktrees/' >> .gitignore
```

4. Inspect active worktrees:

```bash
cmux ls
```

## Core Commands

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

## Standard Workflow

1. Start feature work:

```bash
cmux new feature-auth
```

2. Start urgent fix in parallel:

```bash
cmux new fix-payments
```

3. Merge and clean up bugfix:

```bash
cmux merge fix-payments --squash
git commit -m "fix(payments): resolve checkout bug"
cmux rm fix-payments
```

4. Resume feature:

```bash
cmux start feature-auth
```

## Setup Hook Workflow

1. Generate a project-specific setup hook:

```bash
cmux init
```

2. If needed, regenerate:

```bash
cmux init --replace
```

3. Commit `.cmux/setup` so future worktrees inherit setup automatically.

## Branch and Path Behavior

- Treat `new` as "new branch + new worktree".
- Treat `start` as "reuse existing worktree/session".
- Expect worktree paths under `.worktrees/<branch>/` in nested layout.
- Expect branch sanitization (e.g., `feature/foo` becomes `feature-foo` path name).

## Safety Rules

- Ask for confirmation before `cmux rm --all`.
- Ask for confirmation before `cmux rm --force`.
- Prefer `cmux merge <branch> --squash` for compact history unless user requests full merge commits.
- Ensure worktree changes are committed before merging.
- Remove finished worktrees after successful merge to reduce branch/worktree drift.

## Troubleshooting

- `Not in a git repo`: move to repo root, then rerun.
- `Worktree not found`: run `cmux ls`, then choose correct branch or create with `cmux new <branch>`.
- Merge blocked by uncommitted changes: commit or stash inside the worktree, then retry.
- Remove blocked by dirty tree: clean state first, or use `cmux rm --force` only with explicit confirmation.
