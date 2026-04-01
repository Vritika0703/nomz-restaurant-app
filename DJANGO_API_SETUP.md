# Django Backend API Setup Guide

## Overview

The React frontend requires specific API endpoints from Django. This guide documents what needs to be implemented or configured in the Django backend.

## Phase 1: Authentication Endpoints

### Required Endpoints

#### 1. **POST /api/auth/login/**
Request:
```json
{
  "username": "string",
  "password": "string"
}
```

Response (if 2FA enabled):
```json
{
  "session_token": "string",
  "requires_2fa": true
}
```

Response (if 2FA disabled or not required):
```json
{
  "access": "jwt_token",
  "refresh": "refresh_token",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "role": "diner|restaurant|admin"
  }
}
```

#### 2. **POST /api/auth/verify-2fa/**
Request:
```json
{
  "token": "session_token",
  "code": "six_digit_code"
}
```

Response:
```json
{
  "access": "jwt_token",
  "refresh": "refresh_token",
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "role": "diner|restaurant|admin"
  }
}
```

#### 3. **POST /api/auth/register/**
Request:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password_confirm": "string",
  "role": "diner|restaurant"
}
```

Response: Same as login success response

#### 4. **POST /api/auth/token/refresh/**
Request:
```json
{
  "refresh": "refresh_token"
}
```

Response:
```json
{
  "access": "new_jwt_token",
  "refresh": "new_refresh_token"
}
```

#### 5. **GET /api/auth/user/**
Response:
```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "role": "diner|restaurant|admin",
  "profile": {
    "is_approved": true,
    "is_rejected": false,
    "is_flagged": false
  }
}
```

#### 6. **POST /api/auth/logout/**
Response:
```json
{
  "detail": "Successfully logged out"
}
```

## Phase 2: Restaurant Endpoints

### GET /api/restaurants/
Query Parameters:
- `limit` (default: 20)
- `offset` (default: 0)
- `search` (optional)
- `cuisine` (optional, comma-separated)
- `price_range` (optional: 1-4)
- `sort_by` (optional: rating, name, review_count, distance)

### GET /api/restaurants/{id}/
Response: Full restaurant details + photos

### GET /api/restaurants/search/
Query Parameters: Same as list

### GET /api/restaurants/map-data/
**Already exists** - Verify returns MapData format:
```json
[
  {
    "id": 1,
    "name": "string",
    "latitude": 40.123,
    "longitude": -74.123,
    "rating": 4.5,
    "cuisine": ["Italian", "Pizza"],
    "price_range": 2
  }
]
```

### POST /api/restaurants/
**Create restaurant** (owner only)

### PUT /api/restaurants/{id}/
**Update restaurant** (owner/admin only)

### DELETE /api/restaurants/{id}/
**Delete restaurant** (admin only)

### GET /api/restaurants/{id}/photos/
Returns list of RestaurantPhoto objects

### POST /api/restaurants/{id}/photos/
**Upload photo** - multipart/form-data with `image` field

### PATCH /api/restaurants/{id}/photos/{photo_id}/set-primary/
Set as primary restaurant photo

### DELETE /api/restaurants/{id}/photos/{photo_id}/
Delete photo

## Phase 3: Review Endpoints

### GET /api/restaurants/{id}/reviews/
Query: `limit`, `offset`

### POST /api/restaurants/{restaurant_id}/reviews/
Create review with 8-point rating system:
```json
{
  "food_rating": 5,
  "service_rating": 4,
  "ambience_rating": 4,
  "location_rating": 3,
  "value_rating": 5,
  "dietary_rating": 4,
  "cleanliness_rating": 5,
  "overall_rating": 4,
  "comment": "string"
}
```

### GET /api/reviews/{id}/
Get single review

### PATCH /api/reviews/{id}/
Update review (owner only)

### DELETE /api/reviews/{id}/
Delete review (owner/admin only)

### GET /api/reviews/my-reviews/
Get current user's reviews (authenticated)

### POST /api/reviews/report/
Report review for moderation:
```json
{
  "review_id": 1,
  "reason": "string",
  "details": "string"
}
```

## Phase 4: Messaging Endpoints

### GET /api/messages/conversations/
Query: `limit`, `offset`

### POST /api/messages/conversations/
Start conversation:
```json
{
  "restaurant_id": 1,
  "initial_message": "optional message"
}
```

### GET /api/messages/conversations/{id}/
Get single conversation

### GET /api/messages/conversations/{id}/messages/
Query: `limit`, `offset`

### POST /api/messages/conversations/{id}/send/
Send message:
```json
{
  "content": "string"
}
```

### PATCH /api/messages/conversations/{id}/mark-read/
Mark conversation as read

### GET /api/messages/unread-count/
Get count of unread messages

## Phase 5: User Endpoints

### GET /api/users/profile/
Get current user profile (authenticated)

### PUT /api/users/profile/
Update user profile

### GET /api/users/preferences/
Get user preferences

### PUT /api/users/preferences/
Update preferences:
```json
{
  "cuisines": ["Italian", "Pizza"],
  "dietary_restrictions": ["vegetarian"],
  "price_range": 2,
  "neighborhoods": ["Manhattan", "Brooklyn"]
}
```

### POST /api/restaurants/claims/
Claim restaurant:
```json
{
  "restaurant_id": 1
}
```

## Phase 6: Admin Endpoints

### GET /api/admin/users/
Query: `limit`, `offset`, `status` (pending, approved, rejected)

### PUT /api/admin/users/{id}/approve/
Approve user account

### PUT /api/admin/users/{id}/reject/
Reject user account

### GET /api/admin/reports/
Moderation reports queue

### PUT /api/admin/reports/{id}/resolve/
Resolve moderation report:
```json
{
  "action": "approve|reject",
  "notes": "optional"
}
```

### GET /api/admin/claims/
Restaurant ownership claims queue

### PUT /api/admin/claims/{id}/approve/
Approve restaurant claim

### PUT /api/admin/claims/{id}/reject/
Reject restaurant claim

## Django Configuration Needed

### 1. Install Django REST Framework
```bash
pip install djangorestframework
pip install django-cors-headers
pip install djangorestframework-simplejwt
```

### 2. Update settings.py

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'corsheaders',
]

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # React dev
    "http://localhost:3000",  # Alternative
    "https://yourdomain.com",  # Production
]

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'ALGORITHM': 'HS256',
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}
```

### 3. Create API Serializers
Create `nomz/serializers.py` with DRF serializers for:
- UserSerializer
- RestaurantSerializer
- ReviewSerializer
- ConversationSerializer
- MessageSerializer

### 4. Create API Views
Create `nomz/api/views.py` with ViewSets for:
- AuthViewSet (login, register, verify_2fa, logout)
- RestaurantViewSet
- ReviewViewSet
- ConversationViewSet
- MessageViewSet
- AdminViewSet

### 5. Update URLs
Create `nomz/api/urls.py` with proper routing

## Testing Checklist

- [ ] Login endpoint returns session_token + requires_2fa
- [ ] 2FA verification endpoint accepts token + code
- [ ] JWT token is returned after successful auth
- [ ] Token refresh endpoint works
- [ ] CORS headers present in responses
- [ ] API returns 401 for missing/invalid tokens
- [ ] All restaurant endpoints return proper data
- [ ] Review endpoints support 8-point rating system
- [ ] Messaging endpoints work bidirectionally
- [ ] Admin endpoints restricted to admin role
- [ ] Pagination works on list endpoints

## Migration Path

1. **Week 1**: Set up DRF + JWT, implement auth endpoints
2. **Week 2**: Implement restaurant, review, and user endpoints
3. **Week 3**: Implement messaging and admin endpoints
4. **Week 4**: Testing, documentation, optimization

## References

- [Django REST Framework](https://www.django-rest-framework.org/)
- [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Django CORS Headers](https://github.com/adamchainz/django-cors-headers)
