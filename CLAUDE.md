# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**connect4** is a Spec Driven Development (SDD) proof-of-concept using [Speckit](https://speckit.io) (v0.6.1) with Claude AI integration. The project demonstrates a workflow where specifications drive implementation through structured planning and task generation.

## Architecture & Workflow

Speckit enforces a linear workflow with built-in git hooks that auto-commit at each stage:

1. **Constitution** - Define project principles (in `.specify/memory/constitution.md`)
2. **Specify** - Write specification; triggers `speckit.git.feature` to create feature branch
3. **Clarify** - Refine specification details
4. **Plan** - Generate implementation plan
5. **Tasks** - Break plan into granular tasks
6. **Implement** - Execute tasks (uses Claude Code skills)
7. **Analyze** - Review implementation against spec
8. **Checklist** - Verify completion criteria
9. **TasksToIssues** - Convert tasks to GitHub issues (optional)

Each stage before/after hooks trigger optional git commits (see `.specify/extensions.yml`).

## Directory Structure

- `.specify/` - Speckit configuration and templates
  - `init-options.json` - Setup metadata (speckit v0.6.1, Claude AI, sequential branch numbering)
  - `extensions.yml` - Git hooks configuration
  - `extensions/git/` - Git command definitions
  - `integrations/claude/` - Claude AI integration scripts
  - `memory/constitution.md` - Project constitution template (fill this in)
  - `templates/` - Markdown templates for specs, plans, tasks, checklists
- `.claude/skills/` - Available Claude Code skills for each workflow stage
- `README.md` - Basic project description
- `LICENSE` - MIT license

## Available Skills

Access via `/speckit-*` (shown in Claude Code UI):
- `/speckit-specify` - Write/edit specification
- `/speckit-clarify` - Refine specification
- `/speckit-plan` - Generate implementation plan
- `/speckit-tasks` - Convert plan to task list
- `/speckit-implement` - Execute implementation
- `/speckit-analyze` - Review against specification
- `/speckit-checklist` - Generate completion checklist
- `/speckit-constitution` - Edit project constitution
- `/speckit-git-*` - Git operations (feature branch, commit, validate, remote)

## Git Workflow

The git extension automates feature branch creation and commits:
- Feature branches follow: `feature/sequential-number-description` (e.g., `feature/001-core-logic`)
- All speckit operations trigger optional auto-commits
- Commits include context from specification/plan/tasks

## Getting Started

1. **Fill in Constitution**: Edit `.specify/memory/constitution.md` with project principles
2. **Start Specification**: Use `/speckit-specify` skill to define requirements
3. **Follow Workflow**: Each skill creates artifacts (spec, plan, tasks) committed to feature branch
4. **Implement**: Use `/speckit-implement` for code changes
5. **Validate**: Use `/speckit-analyze` to verify against spec

## Key Files for Future Context

- `.specify/memory/constitution.md` - Project decision principles (update after ratification)
- `.specify/extensions.yml` - Modify if changing git hook behavior
- `.specify/init-options.json` - Don't edit; records initial setup
- `.claude/skills/` - Reference for what speckit operations are available

## Notes for Claude Code

- This is a meta-repository showing the *process* of specification-driven development, not a traditional codebase
- No build/test/lint commands apply yet (no application code exists)
- When specifications/plans/tasks are added, they'll be versioned in git by auto-commits
- The Constitution file is critical—fill it early to guide all downstream decisions
- Use `/speckit-git-*` for explicit branch/commit control if needed

## Active Technologies
- HTML5, CSS3, JavaScript ES2022+ + None (vanilla); Vitest (unit tests), Playwright (e2e/BDD) (001-connect4-game)
- N/A (in-memory game state only) (001-connect4-game)

## Recent Changes
- 001-connect4-game: Added HTML5, CSS3, JavaScript ES2022+ + None (vanilla); Vitest (unit tests), Playwright (e2e/BDD)
