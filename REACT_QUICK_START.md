# React Migration - Quick Start Guide

## What's Been Done

✅ **React Frontend Scaffold Created**
- Full TypeScript + Vite + Redux + Tailwind setup
- API client with JWT auth and auto-refresh
- Authentication pages (Login, Register) with 2FA support
- 8 page stubs for main features
- State management configured
- Navigation and routing ready

✅ **Documentation Created**
- `REACT_MIGRATION_PLAN.md` - Full architecture strategy
- `DJANGO_API_SETUP.md` - Backend API requirements (43 endpoints)
- `IMPLEMENTATION_ROADMAP.md` - Week-by-week implementation plan
- `frontend/README.md` - Frontend development guide

---

## How to Get Started

### Step 1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

**Time**: ~2 minutes

### Step 2: Set Up Environment

```bash
cat > frontend/.env << 'EOF'
VITE_API_URL=http://localhost:8000
EOF
```

### Step 3: Start Both Servers

**Terminal 1 - Django Backend**:
```bash
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**Terminal 2 - React Frontend**:
```bash
cd frontend
npm run dev
```

**Access**: http://localhost:5173

### Step 4: Test Login Flow

1. Open http://localhost:5173
2. Click "Login"
3. Try logging in (will fail until Django API is set up)

---

## Next Priority Tasks

### Phase 1A: Django API Setup (Start Here!) ⚡

**Why**: Frontend can't work without backend endpoints

### 1. Install Required Packages
```bash
pip install djangorestframework djangorestframework-simplejwt django-cors-headers
```

### 2. Add to Django INSTALLED_APPS
In `restaurants/settings.py`:
```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
]
```

### 3. Add CORS Middleware
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this first
    'django.middleware.common.CommonMiddleware',
    ...
]
```

### 4. Configure JWT & CORS
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
```

### 5. Create API Endpoints
Create `nomz/api/` directory with serializers and views for:
- Authentication (most important first!)
- Restaurants
- Reviews
- Messaging
- Users

**See** `DJANGO_API_SETUP.md` for exact endpoint specifications.

---

##Key Files Created

```
frontend/
├── package.json                # Dependencies
├── vite.config.ts             # Build config
├── tsconfig.json              # TypeScript config
├── tailwind.config.js         # Tailwind CSS
├── index.html                 # HTML template
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Main app with routing
│   ├── index.css             # Global styles
│   ├── api/                  # API clients
│   │   ├── client.ts         # Axios + JWT
│   │   ├── auth.ts           # Auth endpoints
│   │   ├── restaurants.ts    # Restaurant endpoints
│   │   ├── reviews.ts        # Review endpoints
│   │   └── messages.ts       # Messaging endpoints
│   ├── store/                # Redux state
│   │   ├── index.ts          # Store config
│   │   └── slices/
│   │       └── auth.ts       # Auth state
│   ├── components/           # React components
│   │   ├── Layout.tsx
│   │   ├── ProtectedRoute.tsx
│   │   └── Navbar.tsx
│   ├── pages/                # Page components
│   │   ├── Landing.tsx ✅
│   │   ├── Login.tsx ✅
│   │   ├── Register.tsx ✅
│   │   ├── Dashboard.tsx (stub)
│   │   ├── RestaurantSearch.tsx (stub)
│   │   ├── RestaurantProfile.tsx (stub)
│   │   ├── MapView.tsx (stub)
│   │   ├── AddReview.tsx (stub)
│   │   ├── Messaging.tsx (stub)
│   │   ├── UserPreferences.tsx (stub)
│   │   └── Recommendations.tsx (stub)
│   ├── hooks/                # Custom hooks (empty)
│   ├── utils/                # Utilities (empty)
│   └── types/                # TypeScript types (empty)
├── .gitignore
└── README.md

Root Level Documentation:
├── REACT_MIGRATION_PLAN.md        # Architecture & strategy
├── DJANGO_API_SETUP.md            # Backend requirements
└── IMPLEMENTATION_ROADMAP.md      # Week-by-week plan
```

---

## Development Checklist

### Week 1: Foundation
- [ ] Django packages installed
- [ ] API app created (`nomz/api/`)
- [ ] Auth endpoints implemented (login, 2FA, register, token refresh, get user)
- [ ] CORS configured
- [ ] JWT configured
- [ ] React frontend starts without errors
- [ ] Login page connects to backend
- [ ] 2FA flow tested end-to-end

### Week 2: Core Features
- [ ] Restaurant endpoints working
- [ ] Restaurant search page rendering
- [ ] Restaurant profile page working
- [ ] Map view integrated
- [ ] Review endpoints working

### Week 3: User Features
- [ ] Messaging endpoints working
- [ ] Messaging UI complete
- [ ] User preferences working
- [ ] Recommendations endpoint working

### Week 4: Owner/Admin
- [ ] Owner dashboard pages
- [ ] Admin moderation pages
- [ ] All endpoints implemented

### Week 5: Testing & Polish
- [ ] Unit tests passing
- [ ] E2E tests passing
- [ ] Performance optimized
- [ ] Accessibility checked

### Week 6: Deployment
- [ ] Built production bundle
- [ ] Deployed to staging
- [ ] User acceptance testing
- [ ] Deployed to production

---

## Common Commands

### Frontend
```bash
cd frontend

# Development
npm run dev              # Start dev server (http://localhost:5173)
npm run build           # Build for production
npm run preview        # Preview production build
npm run type-check     # Check TypeScript
npm run lint           # Run linter
npm run test           # Run tests
```

### Backend
```bash
# Django
python manage.py runserver              # Start dev server
python manage.py makemigrations         # Create migrations
python manage.py migrate                # Apply migrations
python manage.py shell                  # Interactive shell
python manage.py test                   # Run tests
python manage.py collectstatic          # Collect static files
```

---

## Troubleshooting

### npm install fails
```bash
# Clear cache and try again
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Port 5173 already in use
```bash
# Use different port
npm run dev -- --port 3000
```

### CORS errors when testing
```bash
# Verify Django has CORS middleware first in MIDDLEWARE list
# Check CORS_ALLOWED_ORIGINS includes http://localhost:5173
```

### JWT token not being sent
```bash
# In browser DevTools → Storage → Local Storage
# You should see 'auth_token' and 'refresh_token' keys after login
```

---

## Architecture at a Glance

```
React Frontend (SPA)
├── Pages (components)
├── API Clients (axios)
├── Redux Store (auth state)
└── Tailwind Styling

↓ (HTTP REST API)

Django Backend
├── User Authentication (JWT + 2FA)
├── Business Logic (scoring, recommendations)
├── Database (PostgreSQL)
└── Admin Interface
```

---

## Important Notes

1. **Django Backend is Unchanged**: All existing features (data ingestion, recommendations, scoring, etc.) remain in Django. React is just the UI.

2. **Zero Feature Loss**: Every current Django template page has a React equivalent planned.

3. **Gradual Migration**: Can migrate features incrementally (one page at a time).

4. **Separate Deployments Option**: React can be deployed to Vercel/Netlify while Django stays on AWS EB, or both on AWS together.

5. **No Database Changes**: Django manages all database operations. React is read-only for most operations.

---

## Resources

- **Frontend Setup**: [frontend/README.md](frontend/README.md)
- **Migration Plan**: [REACT_MIGRATION_PLAN.md](REACT_MIGRATION_PLAN.md)
- **Backend Requirements**: [DJANGO_API_SETUP.md](DJANGO_API_SETUP.md)
- **Implementation Roadmap**: [IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)
- **React Docs**: https://react.dev
- **Redux Toolkit**: https://redux-toolkit.js.org
- **DRF**: https://www.django-rest-framework.org

---

## Next Steps

1. **Read** [DJANGO_API_SETUP.md](DJANGO_API_SETUP.md) - Understand backend requirements
2. **Start** Phase 1: Implement Django API endpoints
3. **Test** auth flow with React frontend
4. **Implement** other pages incrementally
5. **Deploy** gradually as features are complete

**Good luck! 🚀**
