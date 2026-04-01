# React UI Migration - Complete Implementation Guide

## Executive Summary

Your Nomz restaurant discovery platform is being migrated from Django server-side rendering to a modern React SPA (Single Page Application). This document provides the complete implementation roadmap.

**Key Principle**: Zero feature loss. Django handles all backend logic; React replaces only the UI layer.

---

## What's Been Created

### ✅ React Frontend Scaffold
- **Location**: `/frontend/` directory
- **Stack**: React 18 + TypeScript + Vite + Redux Toolkit + Tailwind CSS
- **Project Setup**: Full development environment ready
- **API Client**: Complete with JWT auto-refresh and error handling
- **Pages**: Landing, Login, Register, Dashboard stubs (26+ pages in plan)
- **State Management**: Redux with auth slice
- **Routing**: React Router v6 configured

### ✅ Documentation
- [REACT_MIGRATION_PLAN.md](REACT_MIGRATION_PLAN.md) - High-level strategy
- [DJANGO_API_SETUP.md](DJANGO_API_SETUP.md) - Backend requirements
- [frontend/README.md](frontend/README.md) - Frontend development guide

### ✅ Backend API Layer
- Authentication client with 2FA support
- Restaurant API client
- Review API client
- Messaging API client
- Base axios client with JWT interceptors

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)

#### 1.1 Django Backend API Setup
**Estimated Time**: 3-4 days

**Tasks**:
- [ ] Install DRF + CORS + JWT packages
- [ ] Configure Django settings (CORS, JWT, REST Framework)
- [ ] Create serializers for all models
- [ ] Implement auth endpoints (login, 2FA, register, token refresh)
- [ ] Create API views with ViewSets

**Files to Create**:
- `nomz/api/serializers.py` - All model serializers
- `nomz/api/views.py` - API viewsets
- `nomz/api/urls.py` - API routing
- `nomz/api/permissions.py` - Custom permission classes

**Key Endpoints to Test**:
- POST /api/auth/login/ ✓ 2FA flow
- POST /api/auth/verify-2fa/
- POST /api/auth/register/
- POST /api/auth/token/refresh/
- GET /api/auth/user/

#### 1.2 React Development Environment
**Estimated Time**: 1 day

**Tasks**:
- [ ] `cd frontend && npm install`
- [ ] Configure `.env` file with `VITE_API_URL`
- [ ] Test that `npm run dev` works
- [ ] Verify Tailwind CSS loads
- [ ] Test Redux connection

**Commands**:
```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

#### 1.3 Auth Flow Implementation
**Estimated Time**: 2 days

**Tasks**:
- [ ] Test login form → Django endpoint
- [ ] Implement 2FA form
- [ ] Test token storage + refresh
- [ ] Add logout flow
- [ ] Test ProtectedRoute component
- [ ] Verify auth persists on page reload

**Files to Update**:
- `frontend/src/api/client.ts` - Verify JWT interceptors
- `frontend/src/pages/Login.tsx` - Test with backend
- `frontend/src/store/slices/auth.ts` - Verify Redux actions

---

### Phase 2: Core Restaurant Features (Week 2)

#### 2.1 Restaurant Search & Listing
**Estimated Time**: 3 days

**Tasks**:
- [ ] Create Django endpoint: `GET /api/restaurants/`
- [ ] Add filtering support (cuisine, price, neighborhood)
- [ ] Create React RestaurantSearch page
- [ ] Build RestaurantCard component
- [ ] Implement client-side pagination
- [ ] Add search input + filters UI

**Components**:
- `RestaurantCard.tsx` - Display single restaurant
- `FilterPanel.tsx` - Filter options
- `PaginationControls.tsx` - Page navigation

#### 2.2 Individual Restaurant Profile
**Estimated Time**: 2 days

**Tasks**:
- [ ] Create Django endpoint: `GET /api/restaurants/{id}/`
- [ ] Build RestaurantProfile page
- [ ] Display photos, hours, reviews, ratings
- [ ] Show health inspection grade
- [ ] Add "Contact" or "Review" CTAs

#### 2.3 Map View Integration
**Estimated Time**: 2.5 days

**Tasks**:
- [ ] Choose map library (Google Maps or Leaflet)
- [ ] Create MapView page with markers
- [ ] Verify existing `/api/restaurants/map-data/` endpoint
- [ ] Add filtering on map
- [ ] Mobile responsiveness

**Libraries**: 
- Install Leaflet: `npm install leaflet react-leaflet`

---

### Phase 3: User Features (Week 3)

#### 3.1 Reviews System
**Estimated Time**: 2 days

**Tasks**:
- [ ] Create Django endpoints:
  - `POST /api/reviews/` - Create review
  - `GET /api/restaurants/{id}/reviews/` - List reviews
  - `PATCH /api/reviews/{id}/` - Update review
  - `DELETE /api/reviews/{id}/` - Delete review
- [ ] Build AddReview form with 8-point ratings
- [ ] Add ReviewList component
- [ ] Implement edit/delete for user's own reviews

**8-Point Ratings**:
```
1. Food Quality
2. Service
3. Ambience
4. Location Value
5. Value for Money
6. Dietary Accommodations
7. Cleanliness
8. Overall Rating
```

#### 3.2 Messaging System
**Estimated Time**: 2 days

**Tasks**:
- [ ] Verify Django endpoints work with JWT
- [ ] Create Messaging page with conversation list + chat window
- [ ] Build ConversationList component
- [ ] Build ChatWindow component
- [ ] Implement real-time updates (polling or WebSocket)
- [ ] Add unread count badge

**Components**:
- `ConversationList.tsx`
- `ChatWindow.tsx`
- `MessageBubble.tsx`

#### 3.3 User Dashboard
**Estimated Time**: 2 days

**Tasks**:
- [ ] Create Django endpoint: `GET /api/users/profile/`
- [ ] Build user dashboard with stats
- [ ] Show recent reviews
- [ ] Show message activity
- [ ] Add profile edit form

---

### Phase 4: User Preferences & Recommendations (Week 4)

#### 4.1 User Preferences
**Estimated Time**: 1 day

**Tasks**:
- [ ] Create Django endpoints:
  - `GET /api/users/preferences/`
  - `PUT /api/users/preferences/`
- [ ] Build preference form with:
  - Favorite cuisines (multi-select)
  - Dietary restrictions
  - Price range preference
  - Neighborhood preferences
- [ ] Save to database

#### 4.2 Recommendations Engine
**Estimated Time**: 1.5 days

**Tasks**:
- [ ] Verify Django recommendation logic works
- [ ] Create endpoint: `GET /api/recommendations/`
- [ ] Build Recommendations page
- [ ] Display recommended restaurants
- [ ] Add "why recommended" explanation

---

### Phase 5: Owner & Admin Features (Week 5)

#### 5.1 Restaurant Owner Dashboard
**Estimated Time**: 3 days

**Tasks**:
- [ ] Build OwnerDashboard page with:
  - Restaurant details management
  - Photo uploads
  - Availability/hours editing
  - Message inbox
[ ] Create Django endpoints:
  - `PUT /api/restaurants/{id}/` - Edit restaurant
  - `POST /api/restaurants/{id}/photos/` - Upload photos
  - `DELETE /api/restaurants/{id}/photos/{photo_id}/` - Delete photo
- [ ] Add restaurant claim workflow

#### 5.2 Admin Moderation Panel
**Estimated Time**: 3 days

**Tasks**:
- [ ] Build AdminDashboard page with:
  - User approval/rejection queue
  - Moderation reports (flagged reviews/users)
  - System alerts and metrics
- [ ] Create Django admin endpoints:
  - `GET /api/admin/users/` - Pending approvals
  - `PUT /api/admin/users/{id}/approve/`
  - `PUT /api/admin/users/{id}/reject/`
  - `GET /api/admin/reports/` - Moderation queue
  - `PUT /api/admin/reports/{id}/resolve/`

---

### Phase 6: Testing & Optimization (Week 6)

#### 6.1 Testing
**Estimated Time**: 3 days

**Tasks**:
- [ ] Unit tests for API clients
- [ ] Component tests for key pages
- [ ] Integration tests for auth flow
- [ ] E2E tests (Cypress) for critical user paths
- [ ] 2FA flow testing
- [ ] Role-based access testing (diner/owner/admin)

#### 6.2 Performance & QA
**Estimated Time**: 2 days

**Tasks**:
- [ ] Lighthouse audit
- [ ] API response optimization
- [ ] UI responsiveness testing
- [ ] Browser compatibility
- [ ] Mobile experience
- [ ] Accessibility (a11y) audit

---

## Development Setup

### Terminal 1: Django Backend
```bash
cd /Users/ananyaagarwal/Desktop/github/team3-mon-spring26
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### Terminal 2: React Frontend
```bash
cd /Users/ananyaagarwal/Desktop/github/team3-mon-spring26/frontend
npm run dev
```

**Access**:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

---

## API Endpoint Implementation Checklist

### Authentication (5 endpoints)
- [ ] `POST /api/auth/login/`
- [ ] `POST /api/auth/verify-2fa/`
- [ ] `POST /api/auth/register/`
- [ ] `POST /api/auth/token/refresh/`
- [ ] `GET /api/auth/user/`
- [ ] `POST /api/auth/logout/`

### Restaurants (8 endpoints)
- [ ] `GET /api/restaurants/`
- [ ] `GET /api/restaurants/{id}/`
- [ ] `POST /api/restaurants/`
- [ ] `PUT /api/restaurants/{id}/`
- [ ] `GET /api/restaurants/map-data/` (already exists)
- [ ] `GET /api/restaurants/{id}/photos/`
- [ ] `POST /api/restaurants/{id}/photos/`
- [ ] `DELETE /api/restaurants/{id}/photos/{photo_id}/`

### Reviews (6 endpoints)
- [ ] `GET /api/restaurants/{id}/reviews/`
- [ ] `POST /api/reviews/`
- [ ] `PATCH /api/reviews/{id}/`
- [ ] `DELETE /api/reviews/{id}/`
- [ ] `GET /api/reviews/my-reviews/`
- [ ] `POST /api/reviews/report/`

### Messaging (6 endpoints)
- [ ] `GET /api/messages/conversations/`
- [ ] `POST /api/messages/conversations/`
- [ ] `GET /api/messages/conversations/{id}/`
- [ ] `GET /api/messages/conversations/{id}/messages/`
- [ ] `POST /api/messages/conversations/{id}/send/`
- [ ] `PATCH /api/messages/conversations/{id}/mark-read/`

### Users (4 endpoints)
- [ ] `GET /api/users/profile/`
- [ ] `PUT /api/users/profile/`
- [ ] `GET /api/users/preferences/`
- [ ] `PUT /api/users/preferences/`

### Admin (7 endpoints)
- [ ] `GET /api/admin/users/`
- [ ] `PUT /api/admin/users/{id}/approve/`
- [ ] `PUT /api/admin/users/{id}/reject/`
- [ ] `GET /api/admin/reports/`
- [ ] `PUT /api/admin/reports/{id}/resolve/`
- [ ] `GET /api/admin/claims/`
- [ ] `PUT /api/admin/claims/{id}/approve/`

**Total: 43 endpoints**

---

## Deployment Strategy

### Development
- Django: `localhost:8000`
- React: `localhost:5173`
- CORS enabled for dev

### Production - Option A (Recommended)
```
┌─────────────────────────────────────────┐
│  AWS Elastic Beanstalk (Single Service)  │
│  Django Backend + React Static Files    │
└─────────────────────────────────────────┘
```

**Process**:
1. Build React: `npm run build` → `dist/` folder
2. Copy to Django: `frontend/dist/* → nomz/static/`
3. Deploy Django normally (per AWS_PART3 guide)
4. Django serves React's index.html for all non-API requests

### Production - Option B (Separate)
```
┌──────────────────┐         ┌──────────────────┐
│ Vercel/Netlify   │◄────────│ AWS EB (Django)  │
│   (React)        │  API    │                  │
└──────────────────┘         └──────────────────┘
```

**Process**:
1. Build React: `npm run build`
2. Deploy `dist/` to Vercel/Netlify
3. Update `VITE_API_URL` to production Django URL
4. Deploy Django normally

---

## Key Considerations

### 1. **CORS Configuration**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://yourdomain.com",
]
```

### 2. **JWT Token Handling**
- Frontend stores tokens in `localStorage`
- Auto-refresh happens via interceptor
- Token expires after 15 minutes
- Refresh token lifetime: 7 days

### 3. **2FA Implementation**
- Temporary session token issued on login
- User verifies code with session token
- JWT tokens issued only after successful 2FA
- Existing `django-two-factor-auth` plugin used

### 4. **Role-Based Access**
- **Diner**: Can view restaurants, add reviews, message owners, get recommendations
- **Restaurant**: Can manage own restaurant, view messages, view reviews
- **Admin**: Can approve users, moderate content, view reports

### 5. **State Persistence**
- Redux persists auth state in `localStorage`
- Cookies not used (stateless API design)
- JWT tokens validated server-side

---

## Troubleshooting Guide

### CORS Errors
```
Error: Access to XMLHttpRequest has been blocked by CORS policy
```
**Solution**: 
- Check Django `CORS_ALLOWED_ORIGINS` setting
- Verify React dev server URL matches
- Check response headers in Network tab

### 401 Unauthorized Errors
```
Error: {"detail": "Invalid token"}
```
**Solution**:
- Clear localStorage: `localStorage.clear()`
- Check token expiry
- Verify JWT secret matches
- Try login again

### 404 API Not Found
```
Error: 404 not found on /api/restaurants/
```
**Solution**:
- Verify endpoint exists in Django
- Check URL routing in Django URLs
- Ensure API app is in INSTALLED_APPS
- Run `python manage.py check`

### Blank Page on React
**Solution**:
- Check browser console for errors
- Verify `VITE_API_URL` is correct
- Check that port 5173 is accessible
- Try `npm run build` locally to test build

---

## Git Workflow

### Add Frontend to Git
```bash
cd /Users/ananyaagarwal/Desktop/github/team3-mon-spring26
git add frontend/
git commit -m "feat: add React frontend scaffold with migration setup"
git push
```

### Environment-Specific Config
```bash
# .env (not checked in)
VITE_API_URL=http://localhost:8000

# .env.production (not checked in)
VITE_API_URL=https://api.nomz.com
```

---

## Success Criteria

- [x] React project created and dependencies installed
- [x] API client with JWT auth ready
- [x] Landing page functional
- [x] Login/Register pages ready
- [ ] Django API endpoints implemented
- [ ] Restaurant search functional
- [ ] Reviews system working
- [ ] Messaging functional
- [ ] Recommendations working
- [ ] Admin panel complete
- [ ] All tests passing
- [ ] Performance optimized
- [ ] Deployed to production

---

## Questions & Support

For implementation questions, refer to:
- [REACT_MIGRATION_PLAN.md](REACT_MIGRATION_PLAN.md) - Architecture
- [DJANGO_API_SETUP.md](DJANGO_API_SETUP.md) - Backend requirements
- [frontend/README.md](frontend/README.md) - Development setup
- React docs: https://react.dev
- Redux Toolkit: https://redux-toolkit.js.org
- Django REST Framework: https://www.django-rest-framework.org

---

**Status**: Ready for Phase 1 Implementation  
**Created**: April 1, 2026  
**Total Estimated Timeline**: 6 weeks (with full team)  
**Risk Level**: Low (incremental migration, Django backend unchanged)
