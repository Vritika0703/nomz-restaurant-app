# React migration plan — architecture (current direction)

**Goal:** Feature parity with the Django app via the React SPA; Django remains the source of truth for data and business rules.

## Architecture overview

```
┌─────────────────────────────────────────────────────────────┐
│                 React SPA (Vite + TypeScript)               │
│  React Router, apiFetch(..., credentials: "include")        │
└────────────────────────┬────────────────────────────────────┘
                         │ JSON /api/* + session cookie
┌────────────────────────▼────────────────────────────────────┐
│                     Django                                   │
│  • Session auth: spa_api (login, 2FA verify, register, …)   │
│  • JSON APIs: spa_api + api_views                            │
│  • Optional: django-two-factor (2FA devices; HTML login     │
│    at /account/login/ redirected to /signin/ SPA)           │
│  • Models, scoring, recommendations, moderation, ingestion   │
└─────────────────────────────────────────────────────────────┘
```

**Auth model:** **Session cookies**, not JWT. After successful login or 2FA verification, the browser holds the standard Django session; the SPA calls **`GET /api/auth/session/`** to learn `authenticated`, `username`, `role`, etc.

For endpoint-level detail see **[DJANGO_API_SETUP.md](./DJANGO_API_SETUP.md)**.

---

## Phase 1 — Foundation (status)

### Django

- [x] JSON endpoints for SPA (`nomz/spa_api.py`, `nomz/api_views.py`, `nomz/urls.py`)
- [x] CORS for local dev (`django-cors-headers`)
- [ ] Optional: OpenAPI / Swagger (not required for current SPA)
- [ ] **Not used for SPA auth:** DRF + SimpleJWT as the primary mechanism (docs below are historical alternatives only)

### React

- [x] Vite + TypeScript app under `frontend/`
- [x] Tailwind-related tooling in the template
- [x] Routing: React Router (`react-router` v7)
- [x] Auth state: React context (`AppContext`) + `apiFetch` with cookies
- [ ] Optional: Redux if global complexity grows (not required today)

---

## Phase 2 — API usage (frontend)

The SPA does **not** use a JWT refresh interceptor. Patterns in use:

- **`apiFetch(path, { credentials: "include" })`** — same-origin or CORS with credentials
- **Login:** `POST /api/auth/login/` → optional `POST /api/auth/2fa/verify/`
- **Who am I:** `GET /api/auth/session/`

A split `frontend/src/api/*.ts` module tree (per resource) is optional; calls are currently colocated in components or a single `api.ts` helper.

---

## Phase 3 — Feature migration (screens)

Most flows exist as React routes under `frontend/src/app/App.tsx` with paths aligned to Django’s SPA shell (e.g. `/signin/`, `/map/`, `/messages/`, `/nomz-admin/…`). See that file for the canonical route list.

Legacy Django templates are no longer the primary UI where the SPA is deployed; deep links should hit the same paths the router defines.

---

## Phase 4 — Services

| Concern | Where it lives |
|--------|----------------|
| Sorting / search / recommendations | Django + JSON APIs |
| 2FA devices | `django-two-factor-auth` + SPA verify endpoint |
| Moderation | Admin JSON in `spa_api` |
| Messaging rules | `api_views` + models |

---

## Phase 5 — Testing

- [x] Django tests for APIs and behaviour (`nomz/tests.py`, etc.)
- [ ] Expand React component / E2E tests as needed
- [ ] Lighthouse / a11y on a schedule

---

## Deployment (reminder)

**Dev:** Django `:8000`, Vite `:5173`, proxy `/api` → Django (see `frontend/vite.config.ts`).

**Prod:** Build `frontend/dist`, serve shell + assets from Django (or reverse proxy) so the SPA and API share an origin and cookies work without extra CORS.

---

## Historical note (JWT / DRF)

Early drafts of this file assumed **JWT + DRF ViewSets** and a token refresh flow. The **implemented** app uses **sessions + `spa_api`**. Do not add SimpleJWT to the checklist unless you explicitly change the auth design.

---

**Document version:** 2.0  
**Last updated:** April 2026  
**Status:** Aligned with session-based SPA in repo
