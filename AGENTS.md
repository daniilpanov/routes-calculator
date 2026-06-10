# AGENTS.md — Project Cache for AI Agents

This file serves as a persistent cache for AI agents working on this project.
Read this first to understand conventions, structure, and constraints.

---

## Project Overview

**Transfer Enigma** — Routes calculator for rail and sea container shipping.
- Calculates shipping routes, prices, and service costs
- Supports internal database + external FESCO API as data sources
- Demo guest links for partner access: blur company names, apply profit overrides
- Demo users authenticate via `X-Demo-User-UID` header (no JWT)

---

## Project Structure

### Python Backend (`Python/`)

Three FastAPI microservices + shared libraries:

```
Python/apps/
├── backend_auth/         # Port 8081 — Auth & demo guest login
│   ├── main.py           # FastAPI app: /login, /token/refresh, /logout, /me
├── backend_user/         # Port 8080 — Route calculator (user-facing API)
│   ├── main.py
│   ├── autodiscover.py   # Auto-discovers routers from api/ subpackages
│   ├── config.py
│   ├── api/v1/, api/v2/  # Versioned API endpoints (routes, points, rates)
│   │   └── v2/demo/      # Demo endpoints (validate, feature_flags)
│   ├── dependencies/     # FastAPI dependencies (auth, auth_context)
│   └── services/         # Business logic (route_calculation, profit, get_rates)
├── backend_admin/        # Port 8082 — Admin data management
│   ├── main.py
│   ├── autodiscover.py
│   ├── api/              # Auto-discovered routers (routes_loading, data_manager, demo_guests)
│   └── service/          # Business logic (routes_loading/, db_management/)
├── module_shared/        # Shared infrastructure (config, database, responses, jwt_handler,
│                         #   feature_flags, repositories/demo_guest, schemas/demo_guest)
├── module_data_internal/ # ORM models + internal data aggregators
│   └── schemas/          # CompanyModel, ContainerModel, PointModel, RouteModel, etc.
└── module_data_fesco_api_adapter/  # External FESCO API client
```

### Node Frontends (`Node/apps/`)

```
Node/apps/
├── user-frontend/        # Vue 3 + Vite — Main user calculator UI
│   └── src/
│       ├── pages/        # CalculatorPage, LoginPage, Error404Page
│       ├── components/   # Reusable Vue components
│       ├── composables/  # Vue composables (useBlurredFields, etc.)
│       ├── stores/       # Pinia stores (user, router, lang, points, rates, routes)
│       ├── services/     # Business logic (auth, calculator, rates, points, etc.)
│       ├── api_helpers/  # API fetch wrappers (user, routes, points, rates)
│       ├── helpers/      # requests.ts (fetchAsJSON wrapper with demo headers)
│       ├── interfaces/   # TypeScript interfaces
│       └── providers/    # Auth provider
├── admin-frontend/       # React 19 + Vite — Admin dashboard
│   └── src/
│       ├── pages/        # Login, Dashboard, DataImport, DemoGuests
│       ├── api/          # Axios API clients (Auth, Data, DemoGuests)
│       ├── services/     # Auth service
│       ├── widgets/      # Sidebar, LoginForm
│       ├── layouts/      # MainLayout, EmptyLayout
│       └── interfaces/   # TypeScript interfaces
└── old-user-frontend/    # Legacy vanilla JS frontend (reference only)
```

### Config & Infrastructure

```
config/
├── nginx/conf/           # Nginx templates (production + dev)
├── database/             # SQL dumps, dev DB init, backup volumes
└── ...

scripts/                  # Dev workflow scripts (run, stop, rebuild, migrate)
```

### Build

**Package Manager:** Poetry (`pyproject.toml` at project root). Always use `poetry add` CLI, don't edit `pyproject.toml` manually.

**Dependency groups:**
| Group | File | Contents |
|-------|------|----------|
| `[tool.poetry.dependencies]` | `Python/requirements.txt` | Runtime deps |
| `[tool.poetry.group.dev.dependencies]` | `Python/requirements-dev.txt` | Linting/pre-commit tools (black, pre-commit, ipython) |
| `[tool.poetry.group.tests.dependencies]` | `Python/requirements-tests.txt` | Test frameworks (pytest, pytest-asyncio, httpx, aiosqlite) |

**Export commands** (run after every `poetry add` / `poetry remove`):
```bash
poetry export -f requirements.txt --output Python/requirements.txt --without-hashes
poetry export -f requirements.txt --output Python/requirements-dev.txt --without-hashes --with dev
poetry export -f requirements.txt --output Python/requirements-tests.txt --without-hashes --with tests
```

The `.txt` files are what the Docker build uses, so they must stay in sync with `poetry.lock`.

**Dockerfile stages** (`Python/Dockerfile`):
| Stage | Base | Purpose |
|-------|------|---------|
| `python-apps` | `python:3.12-slim` | Runs FastAPI microservices via uvicorn |
| `db-migration` | `python:3.12-slim` | Runs Alembic database migrations |
| `test-runner` | `python:3.12-slim` | Runs pytest (install from `requirements-tests.txt`) |

The `test-runner` stage copies `apps/` to `/app/apps/`, `tests/` to `/app/tests/`, and overrides rootdir via `--override-ini` flags (no pyproject.toml in build context). At runtime, the hot-dev compose mounts `pyproject.toml` for config.

### Nginx Routing

| Location | Proxy Target | Purpose |
|----------|-------------|---------|
| `/api/user/` | `auth:8081` | Auth endpoints (login, refresh, me) |
| `/api/` | `calculator:8080` | User API (routes, points, rates, demo) |
| `/admin/api/` | `backadmin:8082` | Admin API (data import, demo guests) |
| `/admin` | Admin frontend static | Admin UI |
| `/` | User frontend | Main calculator UI |

---

## Commit Rules

### Structure
1. **One commit = one micro-feature.** Never mix unrelated features in one commit.
2. **Each commit must produce working code.** All imports must resolve, all called functions must exist. If a commit would be too large, split into smaller commits by module — but each intermediate commit must be functional.
3. **Keep history linear — no fix commits on top.** If the current branch contains a commit with a bug or lint issue, amend that commit via rebase rather than creating a separate fix commit. This keeps history clean and avoids fixup noise.

### Commit Message Format
```
<Module>: <Description in English>
```
Examples:
- `Auth Backend: Add demo guest login by UID`
- `User Frontend: Add blurred company display for demo guests`
- `Python: Add feature flags module`
- `Database: Add demo_guests table`
- `Nginx: Add SSL support`

Module prefixes:
- `Auth Backend:` — `backend_auth` only
- `User Backend:` — `backend_user` only
- `Admin Backend:` — `backend_admin` only
- `Python:` — crosses multiple Python modules (e.g., adding shared code)
- `User Frontend:` — Vue app only
- `Admin Frontend:` — React app only
- `Database:` — Alembic migrations, SQL scripts
- `Nginx:` — Nginx config changes
- `Docs:` — Documentation only
- `CI:` — CI/CD workflow changes

### Pre-Commit Checks
- Before each Python commit: `pre-commit run --all-files` — this catches lint/type errors early, avoiding fix commits on top
- Before each Node commit: run the project's lint script (if available)
- Fix any lint/type errors before committing

### CI Workflows
- `project-lint.yml` — pre-commit + ESLint, runs on every PR
- `project-tests.yml` — pytest (SQLite in-memory), runs on PR, push to main/master, and manual
- `project-build.yml` — Docker Bake build + optional deploy, manual trigger only
- `project-deploy.yml` — SSH deploy, reusable sub-workflow

---

## Code Style & Conventions

### General
- **All code comments must be in English.**
- **All commit messages must be in English.**
- **Maximize code reuse.** Before writing new code, check if existing utilities/modules can be extended. Duplication should be justified.
- Follow existing patterns in the codebase. Don't introduce new libraries or patterns unless necessary.

### Python
- Uses `async`/`await` throughout (FastAPI + SQLAlchemy async)
- Type annotations required (`flake8` + `mypy` enforce this)
- Imports sorted with `isort`
- Max line length: 120 chars
- Max McCabe complexity: 10
- Existing flake8 plugins: `flake8-builtins`, `flake8-comprehensions`, `flake8-eradicate`, `flake8-expression-complexity`, `flake8-simplify`, `flake8-bugbear`, `flake8-pie`, `flake8-print`, `flake8-noqa`, `flake8-broken-line`
- Router auto-discovery pattern: place `router = APIRouter(...)` in any module under `api/` — it gets discovered automatically
- DB sessions: use `async with db.session_context() as session` — auto-commits on exit, auto-rollbacks on exception
- Alembic migrations: placed in `Python/alembic/versions/`, excluded from pre-commit (`exclude: 'Python/alembic/.*'`)

### Python Tests
- Tests live in `Python/tests/`, run with `pytest`
- **70 tests** across 7 files:
  - `test_route_calculation.py` (21) — route calculation (internal, FESCO, mixed, demo/profit, empty IDs, container fail, edge cases)
  - `test_internal_aggregators.py` (17) — containers, paths (rail/sea/COC/SOC/expired/services/drop/dropp_off/no_data/process_results)
  - `test_profit.py` (17) — currency conversion, profit application, segment type filtering, mixed segments, currency conversion in profit
  - `test_auth_utils.py` (8) — `_strip_demo_fields`, `get_auth_context` with/without/invalid demo header, empty routes
  - `test_get_points.py` (4) — `get_departure_points`, `get_destination_points`, no routes, multiple companies
  - `test_demo_guest_repo.py` (5) — `get_demo_guest_by_uid` found/not found/profit overrides, `list_demo_guests` empty/multiple
  - `test_get_rates.py` (3) — `get_rates` returns dict, caching, with datetime
- **Test DB**: SQLite in-memory (`sqlite+aiosqlite`). Tables created via `Base.metadata.create_all()`, **not** via Alembic migrations (migrations have MySQL-specific code).
- **Auth mocks**: patch `get_demo_guest_by_uid`, `get_database`, and `request_auth` directly
- **FESCO API mocks**: use `unittest.mock.patch` on `module_data_fesco_api_adapter.api_client` directly
- **Test data**: factory functions in `Python/tests/data/__init__.py` build ORM objects with sensible defaults
- **Currency rates**: tests use RUB-relative rates `{"USD": 90.0, "RUB": 1.0}`; `_convert_currency` formula is `amount * rates[from] / rates[to]`
- Run locally: `PYTHONPATH=Python/apps python -m pytest Python/tests/ -v`
- Run in Docker (profile `test`, won't start with `docker compose up`):
  `./scripts/run-test.sh`

### Python Module Dependencies Graph
```
module_shared ───┬── backend_auth
                 ├── backend_user ───┬── module_data_internal
                 │                   └── module_data_fesco_api_adapter
                 └── backend_admin ─── module_data_internal
```

### TypeScript / Frontends
- **User Frontend**: Vue 3 Composition API (`<script setup lang="ts">`), Pinia stores, Vue Router
- **Admin Frontend**: React 19 functional components, React Router, Axios for API
- Both use TypeScript, Bootstrap 5

---

## Workflow Rules

### No Direct Merge
- **All merges must go through Pull Requests.** No `git merge` on main/protected branches.
- Rebasing is preferred for feature branches (clean history).

### Branching
- Feature branches: `feature/<short-description>`
- Bugfix branches: `fix/<short-description>`
- Keep branches up to date with the target branch via rebase, not merge.

### Always run linting before committing
- Python: `pre-commit run --all-files`
- Frontends: check `package.json` for lint scripts

---

## Architecture & Design Decisions

### API Versioning
- User API uses URL versioning: `/v1/`, `/v2/`
- Auth and Admin APIs are not versioned

### Auth Flow
1. Login sets JWT access + refresh cookies (httpOnly)
2. Frontend refreshes token on interval via `POST /token/refresh`
3. Demo users authenticate via `X-Demo-User-UID` header (no JWT, no backend_auth)

### Demo Guest Feature
- Admin creates demo guests with UID + profit overrides (stored in `demo_guests` table)
- Demo link format: `/demo/<UID>`
- All demo auth is in `backend_user` — `backend_auth` is NOT involved
- Backend: `get_auth_context` dependency checks `X-Demo-User-UID` header → looks up `demo_guests` table → returns `AuthContext` (is_demo, profit overrides). If no header, falls through to JWT via `request_auth`.
- V2 endpoints use `Depends(get_auth_context)` (supports both JWT and header auth)
- V1 endpoints use `Depends(request_auth)` (JWT only)
- Demo endpoints: `POST /api/v2/demo/validate` (validates UID), `GET /api/v2/demo/feature-flags` (returns blurred_fields list)
- Frontend: `helpers/requests.ts` → `demoHeaders()` reads `useDemoAuth()` Pinia store → injects `X-Demo-User-UID` into every `fetchAsJSON()` call
- Demo users see blurred company names via CSS class (driven by `useBlurredFields` composable ← `featureFlags` store)
- Profits (`sea_profit`, `rail_profit`) are added to route prices for demo users only (in profit service)
- `Error404Page.vue` shown for invalid UIDs or unmatched routes

### Pinia Timing Constraints (Critical!)
- `useStore()` (Pinia) calls `inject(piniaSymbol)` → requires `getCurrentInstance()` (Vue component context)
- **CANNOT use Pinia in route `beforeEnter` guards** — no component context (`getCurrentInstance()` is null). Use plain `fetch()` + try/catch.
- **CAN use Pinia in `<script setup>` top level** — `currentInstance` is set during setup
- **`onMounted` fires children-first in Vue 3** — parent's `onMounted` fires AFTER children's. If demoUid must be set before child API calls, set it at `<script setup>` level.
- `fetchAsJSON()` reads `useDemoAuth()` synchronously before `await`. Works if called from component context (setup, lifecycle, event handler).

### Feature Flags Flow
- `/demo/feature-flags` is fetched **independently of route** — driven by `demoUid` state
- `providers/auth.ts` watches `useDemoAuth().demoUid` → fetches with/without `X-Demo-User-UID` header → sets `useFeatureFlags().blurredFields`
- `immediate: true` ensures correct state on initial load
- Feature flags are **not cleared explicitly** — the watcher auto-updates when `demoUid` changes (clearing demoUid → fetch without header → empty blurred_fields)

### Database
- MariaDB, accessed via SQLAlchemy async + `aiomysql`
- Migrations via Alembic
- Models defined in `module_data_internal/schemas/` and `module_shared/schemas/`
- Both use the same `Base` class from `module_shared.database`

---

## Makefile (`Makefile`)

| Target | Description |
|--------|-------------|
| `make build` | Docker buildx bake (all targets) |
| `make prod` | `docker compose up` — Ctrl+C runs `down` |
| `make dev` | `./scripts/run-dev.sh` — Ctrl+C runs `./scripts/stop-dev.sh` |
| `make update [args]` | `./scripts/prod-update.sh` — pass args directly |
| `make export-deps` | `./scripts/export-python-dependencies.sh` |
| `make alembic [args]` | `./scripts/alembic-proxy.sh` — pass alembic subcommand via args |
| `make migrate [args]` | `./scripts/prod-db-migrate.sh` — pass alembic subcommand via args |

## Known Gaps
- **Backend docs** (`docs/backend/`) are empty

---

## ✅ Critical Rule

**After EVERY completed step** (every commit, every config change, every dependency update, every new file) — **STOP and update this AGENTS.md file** with any relevant new conventions, decisions, or structural changes. This file is the persistent memory for all future sessions. If it's not in AGENTS.md, it doesn't exist.
