# React UI migration — implementation roadmap (updated)

## Executive summary

Nomz uses a **React SPA** with **Django session authentication** and **JSON endpoints** under `/api/…` (`nomz/spa_api.py`, `nomz/api_views.py`). This document replaces older text that assumed **JWT**, **token refresh**, and a large **DRF** surface area.

**Principle:** Django owns data and rules; the SPA is the primary interactive UI where the project serves the built frontend.

**Authoritative API list:** [DJANGO_API_SETUP.md](./DJANGO_API_SETUP.md)

---

## What exists today (high level)

### Frontend (`frontend/`)

- React 18, TypeScript, Vite
- **React Router** (`react-router` v7) — URL-based navigation (e.g. `/map/`, `/signin/`, `/nomz-admin/…`)
- **`apiFetch`** with **`credentials: "include"`** — session cookies, not `Authorization: Bearer`
- Auth user summary via **`GET /api/auth/session/`** and context (`AppContext`)

### Backend

- **Session auth JSON:** register, login, admin-login, logout, 2FA verify, password reset — `spa_api.py`
- **Map, messaging, claims:** `api_views.py`
- **Restaurant, diner, admin, photos, search, recommendations, reports:** `spa_api.py`
- **SPA shell:** `nomz/spa_shell_views.py` + `nomz/urls.py` (HTML for browser routes; `/api/` unchanged)

---

## Roadmap phases (maintenance & polish)

### Phase 1 — Keep auth docs and env correct

- [x] Document session auth (this file + `DJANGO_API_SETUP.md`)
- [x] CORS / `CSRF_TRUSTED_ORIGINS` for dev origins
- [ ] Optional: short “troubleshooting” runbook for cookie issues (SameSite, HTTPS, proxy)

### Phase 2 — API parity & cleanup

- [ ] Prefer a single table of endpoints in `DJANGO_API_SETUP.md` when adding routes
- [ ] Optional REST shapes (JWT, generic CRUD) only if product requires them

### Phase 3 — Frontend quality

- [ ] Component tests / Playwright for critical flows (login, map, messages)
- [ ] Performance (bundle split, lazy routes) as needed

### Phase 4 — Operations

- [ ] Production: same-origin SPA + API or documented cross-origin cookie setup
- [ ] CI: `npm run build` + Django tests

---

## Development setup

### Terminal 1 — Django

```bash
cd /path/to/team3-mon-spring26
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Terminal 2 — Vite (optional for HMR)

```bash
cd frontend
npm install
npm run dev
```

- **Frontend:** http://localhost:5173 (proxies `/api` to Django in `vite.config.ts`)
- **Backend:** http://localhost:8000
- **Django admin:** http://localhost:8000/admin/

### Production-style (single origin)

```bash
cd frontend && npm run build
# Serve Django with static SPA per project conventions (see deployment docs)
```

---

## API checklist — **implemented** (session + `spa_api` / `api_views`)

Use **[DJANGO_API_SETUP.md](./DJANGO_API_SETUP.md)** for methods and bodies. Summary:

**Auth:** `session`, `register`, `login`, `admin-login`, `logout`, `2fa/verify`, `password-reset`, `password-reset/confirm`

**Core:** `restaurants/map-data`, `restaurants/<id>/`, `restaurants/<id>/review/`, `search`, `recommendations`, `report`, `restaurant-claim`

**Owner:** `restaurant/profile`, `availability`, `communication`, `activation`, `photos/*`

**Diner:** `diner/preferences`, `diner/account`

**Messages:** `messages/conversations/*` (list, start, detail, send)

**Admin:** `admin/dashboard-summary`, `pending-approvals`, `approved-restaurants`, `rejected-restaurants`, `approve/<id>`, `reject/<id>`, `moderation`, `moderation/reports/<id>/resolve/`, `users`, `users/<id>/toggle-active/`, `login-logs`

---

## API checklist — **not** in current `urls.py` (legacy planning only)

Do not treat these as blockers for the SPA unless you add them:

- `POST /api/auth/token/refresh/`, JWT pair on login
- `GET /api/auth/user/` (use `/api/auth/session/`)
- Full DRF resource tree for restaurants/reviews/users as in early JWT specs
- `PATCH .../mark-read/` for conversations
- Standalone `GET /api/reviews/my-reviews/`, etc.

---

## Key considerations (corrected)

### CORS

Needed when the SPA origin ≠ API origin (typical local Vite + Django). See `CORS_ALLOWED_ORIGINS` in `restaurants/settings.py`.

### Authentication

- **Sessions:** Django session cookie after login / 2FA verify.
- **Not** “stateless JWT in `localStorage`” for the current app.

### 2FA

- Login may return `{ "requires_2fa": true }`; the SPA collects the TOTP code and calls **`POST /api/auth/2fa/verify/`** with `{ "token": "<code>" }`.
- Pending state is server-side (`_2fa_user_id` in session), not a client-side JWT “session token”.

### Roles

- **Diner / restaurant / admin** — enforced in views; SPA uses `/api/auth/session/` for `role` / `is_staff`.

---

## Troubleshooting

### CORS / credentialed requests

- Ensure the browser origin is in `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` when using cross-origin dev.

### 401 / redirect to sign-in

- Session missing or expired — user logs in again via `/signin/`.
- Not “clear JWT from localStorage” (unless you add JWT later).

### 404 on `/api/...`

- Confirm route exists in `nomz/urls.py` and that you are not assuming old JWT-only paths.

---

## Success criteria (living)

- [x] SPA auth via session + documented endpoints
- [x] Core diner / owner / admin flows behind `/api/`
- [ ] Expanded automated UI tests (optional)
- [ ] Production deployment checklist satisfied for your host

---

## References

- [DJANGO_API_SETUP.md](./DJANGO_API_SETUP.md) — **API truth**
- [REACT_MIGRATION_PLAN.md](./REACT_MIGRATION_PLAN.md) — architecture
- Code: `nomz/spa_api.py`, `nomz/api_views.py`, `nomz/urls.py`, `frontend/src/app/api.ts`, `frontend/src/app/App.tsx`

---

**Status:** Documentation aligned with session-based SPA  
**Last updated:** April 2026
