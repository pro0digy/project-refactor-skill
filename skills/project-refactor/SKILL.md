---
name: project-refactor
description: Safely audit, clean up, refactor, and optimize an established software project without changing intended behavior. Use when asked "очисти проект", "проведи рефакторинг", "убери мертвый код", "проект разросся после доработок", "подготовь стабильный релиз", "оптимизируй готовую программу", "code cleanup", "technical debt audit", or "release optimization". Supports Python, JavaScript/TypeScript, SQL/data pipelines, mixed stacks, and projects without Git; modes are quick-cleanup, deep-audit, and release-optimization.
---

# Project Refactor

Reduce accidental complexity while preserving observable behavior, data integrity, integrations, and deployment contracts. Prefer evidence and small reversible changes over a rewrite or a smaller line count.

## Select a mode

| Mode | Trigger | Default authority |
| --- | --- | --- |
| `quick-cleanup` | Recently edited or specifically named code | Focused, behavior-preserving edits after a baseline; no unapproved removal of files or packages |
| `deep-audit` | Entire project, accumulated clutter, unclear architecture | Read-only inventory and prioritized cleanup plan; wait before modifying |
| `release-optimization` | Stable features, pre-release, "final architecture" | Freeze scope, characterize behavior, propose batches, then implement approved batches with full verification |

If the request is ambiguous, choose `deep-audit` for a whole project and `quick-cleanup` for named files. Tell the user the selected mode and scope. Do not interpret a request for advice or diagnosis as authorization to edit files.

## Non-negotiable safeguards

1. Preserve existing user edits. Identify dirty files and overlapping work; never erase or reset them. If Git is absent, do **not** require Git: use an approved, restorable project snapshot outside the working tree. Check size, destination, access, and sensitive content before copying. If no reliable rollback exists, keep work read-only until resolved.
2. Treat source-code searches as clues, not proof of non-use. Check dynamic imports, reflection, dependency injection, plugins, web routes, scheduled jobs, command-line entry points, SQL, configuration, deployment scripts, external consumers, and feature flags.
3. Protect user data, databases, credentials, `.env` files, migration history, deployed assets, API contracts, business rules, licensing notices, and agent/tool configuration. Never delete or archive them merely because they are unreferenced locally. Preserve data directories and external storage by default.
4. Before deleting/moving a file or removing a dependency, list exact candidates, evidence, likely impact, rollback method, and risk. Obtain explicit approval for those exact candidates or an explicitly approved bounded batch. Keep uncertain items.
5. Do not introduce new features, major upgrades, architecture rewrites, or formatting of unrelated files during cleanup. Make each change independently reviewable and reversible.
6. Run tests, builds, benchmarks, or scripts against production systems only when their side effects are understood and permitted. Do not run destructive migrations, live writes, unsolicited installations, or commands that contact external services just to validate a cleanup.
7. Do not claim full behavior equivalence without sufficient tests or controlled before/after evidence. When evidence is insufficient, report this limitation and pause risky changes.

## Procedure

### 1. Discover the actual system

- Read applicable `AGENTS.md`, project instructions, and existing documentation.
- Resolve the exact project root; do not scan unrelated user directories or a broad filesystem root.
- Identify stack, runtimes, package managers, entry points, tests, environment configuration, builds, database/schema dependencies, external integrations, persistent data, deployment scripts, and generated files. Never assume a stack from prior projects.
- Check for Git/version history, changes already in progress, and an existing restorable version. If Git is unavailable, choose safe no-Git comparison and backup procedures.
- For a large tree, optionally run the **read-only** `scripts/project_inventory.py --root <project-path>` to summarize file types, sizes, and byte-identical files. Treat duplicate results as candidates, not deletion permission.

### 2. Establish a baseline

- Record current build/lint/typecheck/test commands and their actual results. Note pre-existing failures explicitly; do not mark them as regressions caused by cleanup.
- Identify critical observable behaviors: user journeys, API schemas, business calculations, data exports, background jobs, scheduled tasks, and external integrations.
- Capture representative known-good inputs/outputs (characterization or golden tests) and runtime measurements where authorized. Normalize non-deterministic timestamps/IDs deliberately and document tolerances.
- If tests do not cover critical behavior, propose targeted characterization tests before major refactoring. Do not assert that an apparently working UI proves the whole system is unchanged.
- Read `references/verification.md` for stack-specific checks and side-effect cautions.

### 3. Inventory the candidates

Classify findings as:

- **Confirmed**: demonstrated unused/duplicated code or unused dependencies after entry-point, config, dynamic-use, and test checks.
- **Possible**: weak static evidence, dynamic dispatch, plugin references, or missing test coverage. Keep pending further investigation.
- **Protected**: data, public contracts, migrations, operational assets, configs, secret material, and user changes. Keep unless separately authorized.

Look for obsolete prototypes, abandoned feature flags, duplicate modules, stale adapters, repeated SQL/data transformations, needless indirection, unused imports/dependencies, contradictory configuration, generated clutter, and overly broad function responsibilities. Distinguish **source cleanup** from **disk cleanup**: caches and generated outputs may be safely reproducible, but do not remove them without confirming their role.

### 4. Show the plan and obtain approval

For `deep-audit`, stop after a prioritized, read-only findings report unless the user has subsequently approved specific changes. For `release-optimization`, show a staged plan and secure approval before the first modification. For `quick-cleanup`, low-risk edits within the named scope may proceed when the user requested implementation and rollback/verification are available, but removals still need the explicit candidate gate.

Use this concise report table:

| Candidate | Evidence | Proposed action | Risk / dependency | Verification | Decision |
| --- | --- | --- | --- | --- | --- |

Prioritize by benefit, confidence, and regression risk; avoid speculative performance gains.

### 5. Implement in small batches

1. Make/verify a recoverable baseline and record the exact intended files.
2. Apply one coherent change (e.g., deduplicate helpers, simplify a function, remove one approved dependency, consolidate one pipeline stage).
3. Run targeted tests and relevant static checks, compare representative outputs, and inspect the changes for accidental side effects.
4. If checks fail, stop and report; revert only changes made in this batch when a safe rollback is available. Never overwrite unrelated edits.
5. Continue to the next approved batch only after verification. Do not silently widen the scope.

Optimize performance only after measuring bottlenecks. Consider repeated queries, N+1 access, redundant transformation passes, excessive I/O, serialization, and memory pressure; preserve numerical precision, row grain, ordering contracts, null semantics, and permissions. Compare before/after with the same inputs and environment.

### 6. Verify the final state

- Re-run baseline tests, build, lint/typecheck, security checks already used by the project, and safe smoke tests of affected user journeys.
- Compare API/data contracts, DB schema/migrations, background jobs, critical calculations, relevant configuration, and operational startup/deployment prerequisites.
- Compare benchmark results only when measurement conditions are comparable. Use "not measured" rather than inventing an improvement.
- Confirm backup/rollback availability and inspect the final change list. Never deploy or alter production as an implied part of a refactor.

## Required handoff

Report: selected mode and scope; baseline and pre-existing failures; candidates classified by confidence; approved changes and exact changed/removed files; tests and output comparisons actually run; before/after size and performance **if measured**; unresolved risks and decisions still needed. If the user asked only for an audit, hand off the plan without edits.

## Examples

- "Use `$project-refactor` in quick-cleanup mode for the Python parser I just changed."
- "Use `$project-refactor` in deep-audit mode for the whole app; only show candidates and risks."
- "Use `$project-refactor` in release-optimization mode, keep the same SQL results and API contracts, and proceed batch by batch."
