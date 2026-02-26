---
name: cmux-and-worktrees
description: Manage parallel development with cmux-style git worktrees in one repository. Use this skill whenever the user asks to run multiple agents in parallel, create or resume isolated worktrees, list/switch/merge/remove worktrees, set up `.cmux/setup`, or recover from worktree conflicts. In this environment, always use the `cmx` alias in commands.
---

# CMX and Worktrees

Run concurrent coding sessions safely by isolating each task in a git worktree.

## Non-Negotiable Command Rule

- Use `cmx` for every command in this skill.
- Do not substitute `cmux` in normal operation.
- If `cmx` fails, check alias availability with `type cmx` before taking any fallback action.

## Preflight

1. Verify current directory is inside a git repo:
```bash
git rev-parse --is-inside-work-tree
```
2. Verify `cmx` is available:
```bash
type cmx
```
3. Ensure worktrees are ignored in git:
```bash
rg -n '^\.worktrees/$' .gitignore || echo '.worktrees/' >> .gitignore
```
4. Inspect active worktrees:
```bash
cmx ls
```

## Core Commands

- Create new isolated task: `cmx new <branch>`
- Resume existing task: `cmx start <branch>`
- Jump to worktree: `cmx cd [branch]`
- List worktrees: `cmx ls`
- Merge into primary checkout: `cmx merge [branch] [--squash]`
- Remove worktree + branch: `cmx rm [branch | --all] [--force]`
- Generate setup hook: `cmx init [--replace]`
- Show/set layout config: `cmx config`, `cmx config set layout <nested|outer-nested|sibling> [--global]`
- Update tool: `cmx update`
- Show version: `cmx version`

## Standard Workflow

1. Start feature work:
```bash
cmx new feature-auth
```
2. Start urgent fix in parallel:
```bash
cmx new fix-payments
```
3. Merge and clean up bugfix:
```bash
cmx merge fix-payments --squash
git commit -m "fix(payments): resolve checkout bug"
cmx rm fix-payments
```
4. Resume feature:
```bash
cmx start feature-auth
```

## Setup Hook Workflow

1. Generate a project-specific setup hook:
```bash
cmx init
```
2. If needed, regenerate:
```bash
cmx init --replace
```
3. Commit `.cmux/setup` so future worktrees inherit setup automatically.

## Branch and Path Behavior

- Treat `new` as "new branch + new worktree".
- Treat `start` as "reuse existing worktree/session".
- Expect worktree paths under `.worktrees/<branch>/` in nested layout.
- Expect branch sanitization (e.g., `feature/foo` becomes `feature-foo` path name).

## Safety Rules

- Ask for confirmation before `cmx rm --all`.
- Ask for confirmation before `cmx rm --force`.
- Prefer `cmx merge <branch> --squash` for compact history unless user requests full merge commits.
- Ensure worktree changes are committed before merging.
- Remove finished worktrees after successful merge to reduce branch/worktree drift.

## Troubleshooting

- `Not in a git repo`: move to repo root, then rerun.
- `Worktree not found`: run `cmx ls`, then choose correct branch or create with `cmx new <branch>`.
- Merge blocked by uncommitted changes: commit or stash inside the worktree, then retry.
- Remove blocked by dirty tree: clean state first, or use `cmx rm --force` only with explicit confirmation.
