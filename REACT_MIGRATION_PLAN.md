# React Migration Plan - Architectural Cleanliness Blueprint

**Goal**: Full feature parity with Django backend via React frontend. Zero feature loss.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend (SPA)                    │
│  (TypeScript, React 18+, Vite, Redux/Context, TailwindCSS)  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│            Django Backend (Unchanged)                        │
│  - Authentication (2FA, JWT/Sessions)                       │
│  - Business Logic (Scoring, Recommendations)                │
│  - Database & Models                                        │
│  - Data Ingestion                                           │
│  - Admin Workflows                                          │
└─────────────────────────────────────────────────────────────┘
```

## Phase 1: Foundation Setup

### Step 1A: Django Backend Preparation
- [x] Identify API endpoints needed (30+ endpoints required)
- [ ] Extend Django REST Framework for missing endpoints
- [ ] Configure JWT authentication
- [ ] Set up CORS permissions
- [ ] Add API documentation (Django REST Swagger)

### Step 1B: React Project Scaffold
- [ ] Create React app with Vite (faster than CRA)
- [ ] Set up TypeScript for type safety
- [ ] Configure build/dev environment
- [ ] Set up state management (Redux or Context API)
- [ ] Configure Tailwind CSS for styling

## Phase 2: Core Infrastructure (Week 1)

### 2.1 API Layer
```
frontend/src/api/
├── client.ts           # Axios instance with interceptors
├── auth.ts             # Login, 2FA, token refresh
├── restaurants.ts      # Search, filter, map data
├── reviews.ts          # Create, read reviews
├── messages.ts         # Conversations, messaging
├── preferences.ts      # User preferences
├── admin.ts            # Moderation, user management
└── ...
```

**Key**: Set up JWT token management with automatic refresh.

### 2.2 State Management
```
frontend/src/store/
├── slices/
│   ├── auth.ts         # User, tokens, 2FA state
│   ├── restaurants.ts  # Search results, filters
│   ├── reviews.ts      # Reviews data
│   ├── messages.ts     # Conversations
│   └── admin.ts        # Admin features
```

### 2.3 Authentication Flow
1. User login → Django `/api/auth/login/` returns tokens
2. Store JWT in Redux + localStorage
3. Auto-refresh token before expiry
4. 2FA: Store temporary session, validate OTP at `/api/auth/verify-2fa/`
5. Auto-logout on token expiry

## Phase 3: Feature Migration (Week 2-4)

### Pages to Build (Priority Order)

**A. Public Pages (No Auth Required)**
1. Landing page
2. Map view with restaurant markers
3. Restaurant search & filter
4. Individual restaurant profile

**B. Authentication Pages**
5. Login (with 2FA)
6. Register
7. Password reset

**C. Diner Features**
8. Dashboard
9. Add reviews
10. Message restaurants
11. Conversation view
12. Settings & preferences
13. Recommendations
14. User profile

**D. Restaurant Owner Features**
15. Owner dashboard
16. Restaurant profile edit
17. Photo management
18. Availability settings
19. Claim restaurant
20. View messages from diners
21. Communication settings

**E. Admin Features**
22. Admin dashboard
23. User approval/rejection workflow
24. Moderation queue (reviews/users)
25. Resolve reports
26. System alerts & monitoring

## Phase 4: Data & Services

### Services to Recreate
| Service | Purpose | Migration |
|---------|---------|-----------|
| Restaurant Sorting | Score-based ranking | Replicate in React + API |
| Recommendations | ML recommendations | Keep on Django, expose API |
| Login Security | Brute-force detection | Keep on Django |
| Messaging Throttle | Response hour limits | Keep on Django |
| Moderation | Content reports | Expose admin API |
| System Monitoring | Performance metrics | Dashboard for admins |

### Database: No Changes
- Django handles ALL database operations
- React only reads/writes via API
- Migrations managed by Django

## Phase 5: Testing & QA

- [ ] API contract testing (Swagger validation)
- [ ] Component unit tests (Jest + React Testing Library)
- [ ] Integration tests (full user flows)
- [ ] E2E tests (Cypress or Playwright)
- [ ] Performance testing (Lighthouse)
- [ ] 2FA flow testing
- [ ] Role-based access testing (diner/owner/admin)

## Implementation Checklist

### Backend API Layer (Django)
- [ ] **Auth Endpoints**: `POST /api/auth/login/`, `POST /api/auth/verify-2fa/`, `POST /api/auth/refresh-token/`, `POST /api/auth/logout/`, `POST /api/auth/register/`
- [ ] **Restaurant Endpoints**: `GET /api/restaurants/`, `GET /api/restaurants/<id>/`, `PUT /api/restaurants/<id>/`, `POST /api/restaurants/` (create), `GET /api/restaurants/search/`
- [ ] **Review Endpoints**: `GET /api/restaurants/<id>/reviews/`, `POST /api/restaurants/<id>/reviews/` (create), `PUT /api/reviews/<id>/`, `DELETE /api/reviews/<id>/`
- [ ] **Message Endpoints**: Already exist - verify JWT support
- [ ] **User Endpoints**: `GET /api/users/profile/`, `PUT /api/users/profile/`, `GET /api/users/<id>/`
- [ ] **Photo Endpoints**: `GET /api/restaurants/<id>/photos/`, `POST /api/restaurants/photos/` (upload), `DELETE /api/photos/<id>/`
- [ ] **Preferences Endpoints**: `GET /api/users/preferences/`, `PUT /api/users/preferences/`
- [ ] **Admin Endpoints**: `GET /api/admin/users/`, `PUT /api/admin/users/<id>/approve/`, `PUT /api/admin/users/<id>/reject/`, `GET /api/admin/reports/`, `PUT /api/admin/reports/<id>/resolve/`
- [ ] **Claim Endpoints**: `POST /api/restaurants/claims/`, `GET /api/admin/claims/`, `PUT /api/admin/claims/<id>/approve/`
- [ ] **Recommendations Endpoint**: `GET /api/recommendations/`
- [ ] **Map Data Endpoint**: Already exists - `GET /api/restaurants/map-data/`

### Frontend Structure (React)
- [ ] Project scaffold with Vite + TypeScript
- [ ] API client with JWT interceptors
- [ ] State management setup
- [ ] Routing (React Router v6)
- [ ] Auth context/middleware
- [ ] Reusable components library
- [ ] Tailwind CSS configuration

### Feature Implementation
- [ ] Landing page
- [ ] Auth pages (login with 2FA, register, password reset)
- [ ] Map view
- [ ] Restaurant search & filtering
- [ ] Restaurant profile (public view)
- [ ] Diner dashboard
- [ ] Review creation & management
- [ ] Messaging interface
- [ ] User preferences
- [ ] Owner dashboard
- [ ] Restaurant management (edit, photos, availability)
- [ ] Admin panel
- [ ] Moderation tools
- [ ] Recommendations engine UI

## Deployment Strategy

### Development
```bash
# Terminal 1: Django backend
cd /path/to/project
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Terminal 2: React frontend
cd frontend
npm run dev  # Runs on http://localhost:5173
```

### Production
1. **Backend**: Deploy Django normally (AWS Elastic Beanstalk per your guide)
2. **Frontend Options**:
   - **Option A (Recommended)**: Serve React build from Django static files
     - Run `npm run build` in frontend/
     - Django serves `frontend/dist/` as static files
     - Single deployment
   - **Option B**: Separate deployments
     - React on Vercel/Netlify
     - Django on AWS EB
     - Configure CORS + API base URL per environment

## Django Configuration Changes Needed

### `settings.py` additions:
```python
# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # React dev
    "http://localhost:3000",  # Alternative dev
    "https://yourdomain.com",
]

# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# CORS headers middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]
```

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| 2FA migration | Login issues | Test 2FA flow extensively before cutover |
| API incompleteness | Missing features | Build API endpoints before React components |
| State management complexity | Sync issues | Use Redux for predictable state |
| Performance degradation | UX issues | Profile React build, optimize API queries |
| CORS misconfiguration | Blocked requests | Test CORS headers thoroughly |

## Timeline Estimate

- **Foundation**: 2-3 days (API prep, React scaffold)
- **Core infrastructure**: 3-4 days (Auth, API client, state management)
- **Feature implementation**: 2-3 weeks (depends on team size)
- **Testing & QA**: 1 week
- **Deployment & migration**: 2-3 days

**Total: ~1 month with 2-3 person team**

## Next Steps

1. **Immediate**: Set up Django REST Framework API layer
2. **Week 1**: Create React project + authentication flow
3. **Week 2-3**: Implement core features
4. **Week 4**: Testing, bug fixes, optimization
5. **Week 5**: Deployment & cutover

---

**Document Version**: 1.0  
**Last Updated**: April 1, 2026  
**Status**: Ready for implementation
