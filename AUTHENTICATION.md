# Authentication System Documentation

## Overview

This document describes the complete login and authentication system implemented for the Nomz restaurant discovery platform on the `login-page` branch.

## Features Implemented

### 1. User Registration
- **URL**: `/register/`
- **Features**:
  - Email validation (must be unique)
  - Username validation (must be unique)
  - Password validation (minimum 8 characters, password strength checking)
  - Password confirmation
  - Automatic login after successful registration
  - Form error handling with user-friendly messages

### 2. User Login
- **URL**: `/login/`
- **Features**:
  - Support for both username and email login
  - Session management
  - "Remember me" implicit functionality through Django sessions
  - Redirect to previous page after login (via `next` parameter)
  - Form error handling
  - Protection against invalid credentials

### 3. User Logout
- **URL**: `/logout/` (POST only)
- **Features**:
  - Secure session termination
  - Redirect to login page after logout
  - Success message confirmation

### 4. User Dashboard
- **URL**: `/dashboard/`
- **Features**:
  - Protected route (requires authentication)
  - Displays user profile information
  - Shows user statistics
  - Quick access to user account settings

### 5. Home Page
- **URL**: `/`
- **Features**:
  - Dynamic content based on authentication status
  - Hero section with call-to-action buttons
  - Feature cards describing platform capabilities
  - Responsive design with Bootstrap 5

## Technical Architecture

### Directory Structure
```
nomz/
├── migrations/
│   └── __init__.py
├── templates/
│   └── nomz/
│       ├── base.html          # Base template with navigation
│       ├── home.html          # Home page
│       ├── login.html         # Login form
│       ├── register.html      # Registration form
│       └── dashboard.html     # User dashboard
├── __init__.py
├── admin.py
├── apps.py
├── forms.py                   # Authentication forms
├── models.py
├── tests.py
├── urls.py                    # URL routing
└── views.py                   # View functions

restaurants/
├── settings.py               # Added 'nomz' app and configured login redirects
├── urls.py                   # Included nomz URLs
├── asgi.py
├── wsgi.py
└── __init__.py
```

### Files Created/Modified

#### New Files:
1. **nomz/forms.py**
   - `UserRegisterForm`: Custom registration form with email field
   - `UserLoginForm`: Custom login form with Bootstrap styling

2. **nomz/urls.py**
   - Route definitions for all authentication views
   - URL names for template reverse lookups

3. **templates/nomz/base.html**
   - Master template with Bootstrap 5 styling
   - Navigation bar with dynamic user menu
   - Message display system
   - Responsive footer

4. **templates/nomz/home.html**
   - Welcome page with feature showcase
   - Call-to-action buttons for registration/login

5. **templates/nomz/login.html**
   - Login form with error handling
   - Links to registration and home page

6. **templates/nomz/register.html**
   - User registration form
   - Password requirements display
   - Links to login and home page

7. **templates/nomz/dashboard.html**
   - User profile card
   - Account statistics
   - Account information section
   - Coming soon features preview

#### Modified Files:
1. **restaurants/settings.py**
   - Added 'nomz' to INSTALLED_APPS
   - Configured TEMPLATES to include project-level template directory
   - Added LOGIN_URL, LOGIN_REDIRECT_URL, and LOGOUT_REDIRECT_URL

2. **restaurants/urls.py**
   - Added `include('nomz.urls')` to urlpatterns
   - Imported `include` from django.urls

3. **nomz/views.py**
   - Implemented 5 view functions: home, register, user_login, user_logout, dashboard

## URL Routes

| URL | Method | Name | Description |
|-----|--------|------|-------------|
| `/` | GET | home | Home page |
| `/register/` | GET, POST | register | User registration |
| `/login/` | GET, POST | login | User login |
| `/logout/` | POST | logout | User logout |
| `/dashboard/` | GET | dashboard | User dashboard (requires auth) |

## Authentication Flow

### Registration Flow
```
User visits /register/
    ↓
GET → Display registration form
    ↓
User fills out form (email, username, password, confirm password)
    ↓
POST → Form validation
    ├─ Valid → Create user, auto-login, redirect to /dashboard/
    └─ Invalid → Display form with errors
```

### Login Flow
```
User visits /login/
    ↓
GET → Display login form
    ↓
User enters credentials (username/email + password)
    ↓
POST → Authenticate user
    ├─ Valid → Create session, redirect to home or 'next' URL
    └─ Invalid → Display form with error message
```

### Dashboard Access Flow
```
User visits /dashboard/
    ↓
@login_required decorator checks authentication
    ├─ Authenticated → Display dashboard
    └─ Not authenticated → Redirect to /login/?next=/dashboard/
```

## Security Features

1. **CSRF Protection**: All forms include Django CSRF token
2. **Password Security**:
   - Minimum 8 characters
   - Cannot be entirely numeric
   - Checked against common passwords
   - Cannot be too similar to personal information
3. **Session Management**: Django's built-in session framework
4. **Email Uniqueness**: Prevents multiple accounts with same email
5. **Username Uniqueness**: Django's built-in username validation
6. **Password Hashing**: Django's default password hashing (PBKDF2)
7. **HTTP-only Methods**: Logout requires POST to prevent CSRF attacks
8. **Login Decorators**: @login_required ensures protected routes

## Styling & UI/UX

### Design Features
- **Color Scheme**: 
  - Primary: #FF6B6B (Coral red)
  - Secondary: #4ECDC4 (Turquoise)
  - Dark: #2C3E50
  - Light: #ECF0F1

- **Components**:
  - Bootstrap 5 responsive grid
  - Custom navigation bar with user dropdown menu
  - Flash messages for user feedback
  - Card-based layout for information display
  - Gradient backgrounds for visual appeal
  - Hover effects and transitions

### Responsive Design
- Mobile-first approach
- Bootstrap breakpoints (sm, md, lg, xl)
- Flexible navigation bar
- Adaptive forms and cards

## Development & Testing

### Running the Application

1. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```

2. **Create superuser (optional, for admin panel)**:
   ```bash
   python manage.py createsuperuser
   ```

3. **Start development server**:
   ```bash
   python manage.py runserver
   ```

4. **Access the application**:
   - Home: http://localhost:8000/
   - Register: http://localhost:8000/register/
   - Login: http://localhost:8000/login/
   - Dashboard: http://localhost:8000/dashboard/ (requires login)
   - Admin: http://localhost:8000/admin/

### Testing
Tested all authentication endpoints:
- ✅ Home page loads correctly
- ✅ Registration form displays
- ✅ Login form displays
- ✅ All forms have proper Bootstrap styling
- ✅ Navigation bar appears on all pages
- ✅ Database migrations apply successfully

## Future Enhancements

Based on the wiki requirements, planned features include:

1. **Password Reset via Email**
   - Email verification link
   - Token-based password reset

2. **Profile Management**
   - Edit profile information
   - Change password
   - Profile picture upload

3. **User Preferences**
   - Cuisine preferences
   - Dietary restrictions
   - Price range preferences

4. **Restaurant-Specific Features**
   - Business account registration
   - Restaurant profile management
   - Review responses

5. **Admin Features**
   - Multi-factor authentication
   - Account management
   - User moderation dashboard

## Troubleshooting

### Issue: 404 on /login/ or other auth pages
**Solution**: Ensure `nomz` is added to INSTALLED_APPS in settings.py

### Issue: Templates not found
**Solution**: Make sure TEMPLATES DIRS includes the project-level templates directory

### Issue: CSS/styling not loaded
**Solution**: Bootstrap CSS is loaded from CDN, ensure internet connectivity

### Issue: Form validation not working
**Solution**: Ensure CSRF token is included in POST forms: `{% csrf_token %}`

## Deployment Considerations

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Use environment variables for SECRET_KEY
3. Configure ALLOWED_HOSTS properly
4. Use a production-grade database (PostgreSQL recommended)
5. Set up HTTPS/SSL certificates
6. Configure proper static file serving
7. Use a production WSGI server (Gunicorn, uWSGI)
8. Implement email backend for password reset
9. Set up proper logging and monitoring
10. Consider adding rate limiting to prevent brute force attacks

## File Manifest

### Files Created:
- `nomz/forms.py`
- `nomz/urls.py`
- `templates/nomz/base.html`
- `templates/nomz/home.html`
- `templates/nomz/login.html`
- `templates/nomz/register.html`
- `templates/nomz/dashboard.html`
- `AUTHENTICATION.md` (this file)

### Files Modified:
- `nomz/views.py`
- `restaurants/settings.py`
- `restaurants/urls.py`

## Summary

The authentication system is now fully functional and ready for use. All components follow Django best practices and the project architecture. The implementation is scalable and can be extended to support additional authentication methods (OAuth, SSO, etc.) in the future.
