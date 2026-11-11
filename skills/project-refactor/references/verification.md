# Verification matrix

Read only the rows relevant to the detected stack. Prefer existing project commands; do not install tooling, change lockfiles, or run internet-accessing scripts just to satisfy this matrix.

| Stack | Baseline examples | High-risk hidden use | Behavior parity checks |
| --- | --- | --- | --- |
| Python | Existing `pytest`, `ruff`, `mypy`, import/startup checks; `pip check` where applicable | Entry-point scripts, `importlib`, decorators, plugin registries, Celery/cron, ORM signals, dynamic reflection | Same test fixtures, CLI outputs, exported data, API schemas, background-task registration |
| JS/TS | Existing `npm`/`pnpm`/`yarn`/`bun` scripts for test, lint, typecheck, build | Router conventions, dynamic imports, server actions, build-time plugins, CSS imports, environment-based paths | Same route rendering, API contracts, UI smoke tests, SSR/build outputs |
| SQL / ETL / DWH | Query tests, safe query plans, data reconciliation, schema checks | Stored procedures, views, dashboards, scheduled refreshes, external clients, dynamic SQL, roles/RLS | Same row grain, counts, aggregates, ordering where specified, null semantics, decimals, time zones, lineage |
| CLI / services | Existing service tests, startup in isolated environment, contract tests | CLI flags, environment variables, scheduled jobs, health probes, message consumers | Same exit statuses, config resolution, endpoints, message formats, logging/audit requirements |
| Windows / no Git | Project-local tests and commands; compare approved stable-copy against working tree | Scheduled Tasks, PowerShell/batch launchers, registry/service references, UNC paths | Restore test if practical; compare file manifests, critical inputs/outputs, run from documented paths |

## Coverage and safety

- A function with no static references may still be part of a public API, route, plugin, serialization hook, or script invocation.
- A file can be byte-identical to another yet have a different runtime role; duplicates from the inventory tool are **not** evidence of safe removal.
- Golden tests need a known-good reference and explicit tolerances. Do not casually change SQL aggregations, float/decimal math, timezone conversions, encoding, sorting, or date filters.
- Do not run benchmarks against production databases if they may lock, scan very large tables, write data, invoke side-effecting functions, or affect availability.
- Treat tests with payments, notifications, emails, messaging, file deletion, or live credentials as potentially state-changing. Use mocks/sandbox environments or skip and report.
- In projects without a test suite, create or propose small characterization tests before structural edits. Passing a build alone is not sufficient evidence of functional parity.
- A backup copy must stay outside the project being cleaned, be restorable, and be appropriate for the project size and data classification. Never assume an unsynchronized copy of source includes external databases or uploaded files.

## Reports

Use actual counts and command results. For baseline and final comparison include only available metrics: source file count, total source bytes, confirmed dead files removed, dependency count, test pass/fail counts, latency/memory (if measured), and named unresolved risks. Separate **measured** values from estimates.
