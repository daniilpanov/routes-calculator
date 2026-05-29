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

## Known Gaps
- **No automated tests** — Python and both frontends lack test coverage
- **Backend docs** (`docs/backend/`) are empty
