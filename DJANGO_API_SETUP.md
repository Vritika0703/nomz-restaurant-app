# Django API setup (SPA) — current implementation

## Overview

The React app talks to Django over **JSON endpoints** under `/api/…`. Authentication is **Django session cookies** (same-origin `fetch` with `credentials: "include"`), implemented in `nomz/spa_api.py` and consumed by `frontend/src/app/api.ts` (`apiFetch`).

There is **no JWT** in the live stack: no `access` / `refresh` tokens, no `POST /api/auth/token/refresh/`, and no `GET /api/auth/user/` alias—the session shape is returned by **`GET /api/auth/session/`**.

Mutating auth and many write endpoints use **`@csrf_exempt`** on the server (see `spa_api.py`); the browser still sends cookies for authentication.

---

## Authentication (`nomz/spa_api.py`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/auth/session/` | Current user: `authenticated`, `username`, `role`, `is_staff`, `userprofile`, etc. |
| POST | `/api/auth/register/` | Register + log in (session established). |
| POST | `/api/auth/login/` | Password login. If 2FA device exists: `{ "requires_2fa": true }` (pending server session key `_2fa_user_id`). |
| POST | `/api/auth/admin-login/` | Staff admin login + security code (parity with Django admin login form). |
| POST | `/api/auth/2fa/verify/` | Body: `{ "token": "<TOTP code>" }` — completes login and sets session. |
| POST | `/api/auth/logout/` | Clears session. |
| POST | `/api/auth/password-reset/` | Triggers email (SPA template). |
| POST | `/api/auth/password-reset/confirm/` | Body: `uid`, `token`, `new_password1`, `new_password2`. |

**2FA:** No separate “session_token” in JSON—the server keeps pending 2FA state in the **Django session** until `POST /api/auth/2fa/verify/`.

**CORS:** `django-cors-headers` is configured for dev origins (e.g. Vite on 5173). Production same-origin (Django serving the built SPA) does not need CORS for the HTML app.

---

## Map & messaging (`nomz/api_views.py`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/restaurants/map-data/` | Map markers / filters. |
| GET | `/api/messages/conversations/` | List conversations. |
| POST | `/api/messages/conversations/start/` | Start thread (diner). |
| GET | `/api/messages/conversations/<id>/` | Messages in thread. |
| POST | `/api/messages/conversations/<id>/send/` | Send message. |
| GET/POST | `/api/restaurant-claim/` | Claim flow (JSON). |

---

## Restaurant, diner, reviews, search (`nomz/spa_api.py`)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/restaurants/<id>/` | Detail + embedded reviews. |
| POST | `/api/restaurants/<id>/review/` | Submit review (JSON body; `ReviewForm` fields). |
| POST | `/api/report/` | Report review or user (`content_type`, `content_id`, …). |
| GET | `/api/search/` | Authenticated restaurant search (parity with legacy search). |
| GET | `/api/recommendations/` | Diner recommendations. |
| GET/POST | `/api/restaurant/profile/` | Owner create/update profile. |
| GET/POST | `/api/restaurant/availability/` | Owner availability. |
| GET/POST | `/api/restaurant/communication/` | Owner messaging settings. |
| GET/POST | `/api/restaurant/activation/` | Owner activation toggle. |
| GET | `/api/restaurant/photos/data/` | List photos. |
| POST | `/api/restaurant/photos/upload/` | Multipart upload. |
| POST | `/api/restaurant/photos/<id>/delete/` | Delete photo. |
| POST | `/api/restaurant/photos/<id>/set-primary/` | Set primary. |
| GET/POST | `/api/diner/preferences/` | Diner preferences. |
| GET/POST | `/api/diner/account/` | Diner account fields. |

---

## Admin JSON (`nomz/spa_api.py`, staff)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/admin/dashboard-summary/` | Dashboard metrics. |
| GET | `/api/admin/pending-approvals/` | Pending restaurant accounts / claims. |
| GET | `/api/admin/approved-restaurants/` | Approved accounts list. |
| GET | `/api/admin/rejected-restaurants/` | Rejected accounts list. |
| POST | `/api/admin/approve/<user_id>/` | Approve user / claim. |
| POST | `/api/admin/reject/<user_id>/` | Reject. |
| GET | `/api/admin/moderation/` | Moderation queue payload. |
| POST | `/api/admin/moderation/reports/<id>/resolve/` | Resolve report (JSON `action`, …). |
| GET | `/api/admin/users/` | User list. |
| POST | `/api/admin/users/<id>/toggle-active/` | Toggle active. |
| GET | `/api/admin/login-logs/` | Login logs. |

---

## Not implemented (older planning docs only)

These were listed in early JWT/DRF checklists and are **not** part of the current `nomz/urls.py` contract:

- `POST /api/auth/token/refresh/`, JWT access/refresh responses on login
- `GET /api/auth/user/` (use `/api/auth/session/` instead)
- Generic `GET/POST /api/restaurants/` CRUD resource
- Standalone `GET /api/restaurants/<id>/reviews/` (reviews are on detail JSON)
- `PATCH/DELETE /api/reviews/<id>/`, `GET /api/reviews/my-reviews/`
- `PATCH .../mark-read/` for conversations
- DRF ViewSets + `djangorestframework-simplejwt` as the primary auth mechanism

If you add mobile or third-party clients later, you can introduce JWT **in addition to** or **instead of** sessions; the SPA would need a new client module—today it only assumes cookies.

---

## Settings relevant to the SPA

- `CORS_ALLOWED_ORIGINS` — dev cross-origin (e.g. `http://127.0.0.1:5173`).
- `CSRF_TRUSTED_ORIGINS` — must include the origin that performs credentialed requests.
- `LOGIN_URL` — browser challenges redirect to `/signin/` (React shell), not the django-two-factor HTML login.
- `FRONTEND_DIST_DIR` / SPA shell — see `nomz/spa_shell_views.py` and `nomz/urls.py`.

---

## References in code

- URL wiring: `nomz/urls.py`
- Session auth JSON: `nomz/spa_api.py` (`session_payload`, `auth_*`)
- Map/messages/claim API: `nomz/api_views.py`
- Frontend HTTP helper: `frontend/src/app/api.ts` (`apiFetch`, `credentials: "include"`)

**Document version:** 2.0 (session-auth, aligned with repo)  
**Last updated:** April 2026
