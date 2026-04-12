# Nomz Django Project - Comprehensive Codebase Analysis

**Project**: Restaurant Discovery & Review Platform for NYC
**Type**: Django Full-Stack Web Application
**Date Analyzed**: April 1, 2026

---

## 1. Main Views/Pages (Views & URLs)

### Core Public Pages

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `landing_page()` | `/` | GET | No | Splash screen entry point |
| `home()` | `/home/` | GET | No (redirects if authenticated) | Homepage with conditional routing |
| `health_check()` | `/health/` | GET | No | Lightweight ELB/EB health check endpoint |
| `map_view()` | `/map/` | GET | No | Interactive NYC restaurant map with filters |
| `restaurant_search()` | `/search/` | GET | No | Restaurant search & discovery page |

### Authentication & User Management

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `register()` | `/register/` | GET, POST | No | User registration (diner or restaurant owner) |
| `user_logout()` | `/logout/` | POST | Yes | Logout user |
| `admin_login()` | `/admin-login/` | GET, POST | No | Admin-only login with security code |
| `admin_login_logs()` | `/nomz-admin/logs/` | GET | Staff only | View login audit logs |

### User Dashboard & Profile

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `dashboard()` | `/dashboard/` or `/profile/` | GET | Yes | Main user dashboard (routes by role: admin, diner, restaurant) |
| `restaurant_profile()` | `/restaurant-profile/` | GET | Yes (restaurant) | View restaurant owner's profile |

### User Preferences & Recommendations

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `manage_preferences()` | `/preferences/` | GET, POST | Yes | Save dining preferences (cuisines, price, dietary) |
| `recommendations()` | `/recommendations/` | GET | Yes | Get personalized restaurant recommendations |

### Restaurant Management (RestaurantOwner Only)

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `claim_restaurant()` | `/restaurant/claim/` | GET, POST | Yes (restaurant) | Claim ownership of existing restaurant |
| `create_restaurant_profile()` | `/restaurant/create/` | GET, POST | Yes (restaurant) | Create new restaurant profile |
| `edit_restaurant_profile()` | `/restaurant/edit/` | GET, POST | Yes (restaurant) | Edit restaurant details, hours, cuisine, price |
| `manage_availability()` | `/restaurant/availability/` | GET, POST | Yes (restaurant) | Toggle restaurant open/closed status |
| `manage_activation()` | `/restaurant/activate/` | GET, POST | Yes (restaurant) | Manage restaurant visibility |
| `manage_communication_settings()` | `/restaurant/communication/` | GET, POST | Yes (restaurant) | Configure messaging & response hours |

### Restaurant Photo Management

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `restaurant_photos()` | `/restaurant/photos/` | GET | Yes (restaurant) | List restaurant photos |
| `upload_photo()` | `/restaurant/photos/upload/` | POST | Yes (restaurant) | Upload new restaurant photo |
| `delete_photo()` | `/restaurant/photos/<id>/delete/` | POST | Yes (restaurant) | Delete photo |
| `set_primary_photo()` | `/restaurant/photos/<id>/set-primary/` | POST | Yes (restaurant) | Mark photo as primary |

### Restaurant Detail & Reviews

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `restaurant_detail()` | `/restaurant/<id>/` | GET | No | View restaurant profile with inspections & reviews |
| `add_review()` | `/restaurant/<id>/review/` | GET, POST | Yes | Submit review with multi-factor ratings |

### Messaging & Conversations

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `message_inbox()` | `/messages/` | GET | Yes | List all conversations for user |
| `message_restaurant()` | `/messages/restaurant/<id>/` | GET, POST | Yes (diner) | Start/view conversation with restaurant |
| `conversation_detail()` | `/messages/conversations/<id>/` | GET | Yes | View conversation thread details |

### Admin Management

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `admin_manage_users()` | `/nomz-admin/users/` | GET | Staff only | View and manage all users |
| `toggle_user_status()` | `/nomz-admin/users/<id>/toggle/` | POST | Staff only | Activate/deactivate user account |
| `admin_toggle_user_status()` | `/dashboard-action/users/<id>/toggle/` | POST | Staff only | Alternative toggle endpoint |
| `admin_pending_approvals()` | `/nomz-admin/pending-approvals/` | GET | Staff only | View restaurants pending approval |
| `admin_approve_restaurant()` | `/nomz-admin/approve/<id>/` | POST | Staff only | Approve restaurant ownership claim |
| `admin_reject_restaurant()` | `/nomz-admin/reject/<id>/` | POST | Staff only | Reject restaurant ownership claim |
| `admin_approved_accounts()` | `/nomz-admin/approved-accounts/` | GET | Staff only | List approved restaurant accounts |
| `admin_rejected_accounts()` | `/nomz-admin/rejected-accounts/` | GET | Staff only | List rejected restaurant accounts |

### Content Moderation

| View Function | Route | HTTP Method | Auth Required | Purpose |
|---|---|---|---|---|
| `report_content()` | `/report/<type>/<id>/` | GET, POST | Yes | Report review or user for moderation |
| `admin_moderation_dashboard()` | `/nomz-admin/moderation/` | GET | Staff only | View pending moderation reports |
| `admin_resolve_report()` | `/nomz-admin/moderation/resolve/<id>/` | POST | Staff only | Resolve moderation report |

### Password Reset (Django Built-in)

| View | Route | Purpose |
|---|---|---|
| `PasswordResetView` | `/password-reset/` | Request password reset |
| `PasswordResetDoneView` | `/password-reset/done/` | Confirmation page |
| `PasswordResetConfirmView` | `/reset/<uidb64>/<token>/` | Reset form |
| `PasswordResetCompleteView` | `/reset/done/` | Completion page |

---

## 2. Key Models & Relationships

### Core User Models

```
User (Django Built-in)
  ↓ OneToOne
UserProfile
  - role: diner | restaurant
  - is_approved: Boolean (auto_approved for diners, requires review for restaurants)
  - is_rejected: Boolean
  - is_flagged: Boolean (fraud detection)
```

### Restaurant Models

```
Restaurant
  ├─ owner: OneToOne(User) [nullable]
  ├─ photos: ForeignKey(RestaurantPhoto) [reverse]
  ├─ conversations: ForeignKey(Conversation) [reverse]
  ├─ reviews: ForeignKey(Review) [reverse]
  ├─ inspections: ForeignKey(InspectionRecord) [reverse]
  ├─ sources: ForeignKey(RestaurantSourceRecord) [reverse]
  ├─ ownership_claims: ForeignKey(RestaurantOwnershipClaim) [reverse]
  └─ dining_out_profile: OneToOne(DiningOutLocation)

RestaurantOwnershipClaim
  ├─ claimant: ForeignKey(User)
  ├─ restaurant: ForeignKey(Restaurant)
  ├─ status: pending | approved | rejected
  └─ reviewed_by: ForeignKey(User, nullable)

RestaurantPhoto
  ├─ restaurant: ForeignKey(Restaurant)
  ├─ photo: ImageField
  ├─ is_primary: Boolean
  └─ caption: CharField
```

### Inspection & Scoring Models

```
InspectionRecord
  ├─ restaurant: ForeignKey(Restaurant)
  ├─ inspection_date: DateField
  ├─ grade: CharField (A, B, C)
  ├─ score: IntegerField
  ├─ critical_violations: IntegerField
  ├─ noncritical_violations: IntegerField
  └─ violations: JSONField

RestaurantSourceRecord
  ├─ restaurant: ForeignKey(Restaurant)
  ├─ source: CharField (EATERIES | DINING_OUT | DOHMH)
  ├─ external_id: CharField
  ├─ confidence: DecimalField
  └─ raw_payload: JSONField

DiningOutLocation
  ├─ restaurant: OneToOne(Restaurant)
  ├─ license_type, license_status
  ├─ location_type: indoor | outdoor | sidewalk | mixed
  └─ capacity_estimate: IntegerField
```

### User Review & Rating Models

```
Review
  ├─ restaurant: ForeignKey(Restaurant)
  ├─ user: ForeignKey(User)
  ├─ rating: SmallInt (1-5) [overall]
  ├─ food_quality_rating: SmallInt (1-5)
  ├─ service_quality_rating: SmallInt (1-5)
  ├─ ambience_rating: SmallInt (1-5)
  ├─ location_rating: SmallInt (1-5)
  ├─ value_rating: SmallInt (1-5)
  ├─ dietary_accommodation_rating: SmallInt (1-5)
  ├─ cleanliness_rating: SmallInt (1-5)
  ├─ comment: TextField
  ├─ is_flagged: Boolean
  ├─ is_deleted: Boolean (soft delete)
  └─ created_at, updated_at: DateTimeField

UserPreference
  ├─ user: OneToOne(User)
  ├─ favorite_cuisines: JSONField (list)
  ├─ dietary_restrictions: JSONField (list)
  ├─ price_preference: CharField
  └─ neighborhood_preference: CharField
```

### Messaging Models

```
Conversation
  ├─ restaurant: ForeignKey(Restaurant)
  ├─ diner: ForeignKey(User)
  ├─ messages: ForeignKey(Message) [reverse]
  ├─ created_at, updated_at
  └─ unique_together: [restaurant, diner]

Message
  ├─ conversation: ForeignKey(Conversation)
  ├─ sender: ForeignKey(User)
  ├─ body: TextField
  ├─ is_read: Boolean
  └─ created_at: DateTimeField
```

### Moderation Models

```
ModerationReport
  ├─ reporter: ForeignKey(User)
  ├─ review: ForeignKey(Review, nullable)
  ├─ reported_user: ForeignKey(User, nullable)
  ├─ reason: SPAM | FRAUD | HARASSMENT | INAPPROPRIATE | OTHER
  ├─ details: TextField
  ├─ status: PENDING | RESOLVED | DISMISSED
  ├─ action_taken: CharField
  ├─ moderator_note: TextField
  └─ created_at, resolved_at
```

### System Audit & Monitoring Models

```
LoginLog
  ├─ username: CharField
  ├─ user: ForeignKey(User, nullable)
  ├─ ip_address: GenericIPAddressField
  ├─ status: Success | Failure
  ├─ is_suspicious: Boolean (IP or admin path flag)
  ├─ is_user_suspicious: Boolean (>2 failures in 15 min)
  └─ timestamp: DateTimeField

SystemAuditLog
  ├─ actor_user: ForeignKey(User, nullable)
  ├─ actor_username: CharField
  ├─ level: INFO | WARNING | ERROR | CRITICAL
  ├─ action: CharField
  ├─ ip_address: GenericIPAddressField
  ├─ request_path, http_method
  ├─ metadata: JSONField
  └─ created_at: DateTimeField

SystemPerformanceMetric
  ├─ method: CharField (GET, POST, etc.)
  ├─ path: CharField
  ├─ duration_ms: PositiveIntegerField
  ├─ status_code: PositiveIntegerField
  ├─ is_error: Boolean
  ├─ exception_class, exception_message
  └─ created_at: DateTimeField

SystemPerformanceSnapshot
  ├─ interval_start, interval_end: DateTimeField
  ├─ total_requests, error_requests
  ├─ error_rate: DecimalField
  ├─ avg_latency_ms, max_latency_ms
  └─ unique_together: [interval_start, interval_end]

SystemAlert
  ├─ alert_type: HEALTH_CHECK_FAILURE | HIGH_ERROR_RATE | HIGH_LATENCY
  ├─ severity: LOW | MEDIUM | HIGH | CRITICAL
  ├─ message, details: JSONField
  ├─ is_active: Boolean
  ├─ created_at, resolved_at
  └─ db_index: [alert_type, severity]
```

### Data Ingestion Models

```
DataIngestionRun
  ├─ dataset: CharField (dataset name)
  ├─ status: running | success | failed
  ├─ started_at, finished_at
  ├─ records_fetched, records_processed, records_created
  ├─ records_updated, records_matched, records_skipped
  ├─ error_count
  └─ error_log: JSONField

RestaurantSearch
  ├─ name, neighborhood, cuisine
  └─ description
```

### Model Relationships Summary

```
User (Django)
  ├─ restaurant_profile → Restaurant (OneToOne)
  ├─ preferences → UserPreference (OneToOne)
  ├─ diner_conversations → Conversation (reverse)
  ├─ sent_messages → Message (reverse)
  ├─ reviews → Review (reverse)
  ├─ reports_made → ModerationReport (reverse)
  ├─ reports_received → ModerationReport (reverse)
  └─ system_audit_logs → SystemAuditLog (reverse)

Restaurant
  ├─ owner → User (OneToOne)
  ├─ photos, conversations, reviews, inspections, sources
  └─ dining_out_profile → DiningOutLocation (OneToOne)
```

---

## 3. API Endpoints (from api_views.py & urls.py)

### JSON REST Endpoints

| Endpoint | Method | Auth | Purpose | Returns |
|---|---|---|---|---|
| `GET /api/restaurants/map-data/` | GET | No | Fetch map markers with advanced filters | JSON array of restaurants |
| `GET /api/messages/conversations/` | GET | Yes | List all conversations for user | JSON array of conversations |
| `POST /api/messages/conversations/start/` | POST | Yes (diner) | Start new conversation | JSON with conversation_id |
| `GET /api/messages/conversations/<id>/` | GET | Yes | Get all messages in conversation | JSON conversation details |
| `POST /api/messages/conversations/<id>/send/` | POST | Yes | Send message in conversation | JSON with message_id |

### Map Data API Features

The map API (`/api/restaurants/map-data/`) supports:
- **Search**: `?search=query` - filter by name, street, zip, borough, cuisine
- **Location Filters**: 
  - `?borough=Manhattan`
  - `?cuisine=Italian`
  - `?sw_lat, ne_lat, sw_lng, ne_lng` - bounding box
- **Score Filters**: `?min_score=70&max_score=95`
- **Sorting**: `?sort_by=composite_desc|composite_asc|name_asc|name_desc|grade_desc|grade_asc`
- **Pagination**: `?limit=1000` (default, max 4000)
- **Response**: Returns count + array of restaurant points (id, name, address, coordinates, scores, grade)

### Conversation API Features

- **List**: Returns conversations with last message preview
- **Start**: Requires `restaurant_id` and initial `message`
- **Fetch Messages**: Get all messages in chronological order
- **Send Message**: Post `body` to start/continue conversation
- **Access Control**: User must be conversation participant (diner or restaurant owner)

### Response Handling

- All endpoints return JSON with status codes
- Errors return `{"error": "message"}` with appropriate HTTP status
- Authentication failures return 401/redirect to landing
- Permission denied: 403 Forbidden

---

## 4. Forms & Their Purposes

Located in [nomz/forms.py](nomz/forms.py):

### Authentication Forms

| Form | Purpose | Fields |
|---|---|---|
| `UserRegisterForm` | User registration (diner or restaurant owner) | username, email, password1, password2, role |
| `UserLoginForm` | Standard login | username, password (Bootstrap styled) |
| `AdminLoginForm` | Admin-only login with security code | username, password, security_code |

### User Preference Forms

| Form | Purpose | Fields |
|---|---|---|
| `UserPreferenceForm` | Save dining preferences | favorite_cuisines, dietary_restrictions, price_preference, neighborhood_preference |

### Restaurant Profile Forms

| Form | Purpose | Fields |
|---|---|---|
| `RestaurantProfileForm` | Create/edit restaurant profile | name, description, address, phone, website, email, cuisine_type, price_range, hours_open, hours_close |
| `RestaurantOwnershipClaimForm` | Claim existing restaurant | restaurant (search dropdown), business_email, contact_phone, proof_details |
| `RestaurantAvailabilityForm` | Temporarily close restaurant | is_temporarily_unavailable, unavailable_reason, unavailable_until |
| `RestaurantActivationForm` | Toggle profile visibility | is_active |
| `RestaurantCommunicationSettingsForm` | Configure messaging | messaging_enabled, response_hours_start, response_hours_end |

### Media Management Forms

| Form | Purpose | Fields |
|---|---|---|
| `RestaurantPhotoForm` | Upload restaurant photo | photo (file), caption, is_primary |

### Review & Moderation Forms

| Form | Purpose | Fields |
|---|---|---|
| `ReviewForm` | Submit restaurant review | rating, food_quality_rating, service_quality_rating, ambience_rating, location_rating, value_rating, dietary_accommodation_rating, cleanliness_rating, comment |
| `ModerationReportForm` | Report review/user for moderation | reason (dropdown), details (text) |

### Key Form Features

- Bootstrap CSS styling applied consistently
- Custom validation for unique emails, existing restaurants
- Restaurant search with dropdown for ownership claims
- Review form uses 1-5 scale for 8 different rating dimensions
- Moderation reasons: SPAM, FRAUD, HARASSMENT, INAPPROPRIATE, OTHER
- Restaurant hours handled as TimeField pairs

---

## 5. Authentication & Authorization

### Authentication System

**Two-Factor Authentication (2FA)**
- Integrated via `django-two-factor-auth` package
- All non-admin logins go through `/signin/` → redirects to `two_factor:login`
- Template extends `two_factor/_base.html`
- Admin login supports separate security code (hardcoded credentials with bcrypt hash)

**Login Flow**
1. User submits credentials → `UserLoginForm` or `AdminLoginForm`
2. Signals capture login attempts (`user_logged_in`, `user_login_failed`)
3. `LoginLog` records created with:
   - IP address, username, status (Success/Failure)
   - User agent for device fingerprinting
   - Suspicious flags if: >2 failures in 15min (by IP or user), admin path attempt
4. 2FA prompt if first-time auth successful
5. Redirect by role

### Authorization System

**Role-Based Access Control (RBAC)**

```
User Roles:
  ├─ diner (default)
  │   ├─ View restaurant listings, map, reviews
  │   ├─ Search & filter restaurants
  │   ├─ Save preferences & get recommendations
  │   ├─ Message restaurants
  │   ├─ Write reviews
  │   └─ Report content for moderation
  │
  ├─ restaurant (requires admin approval)
  │   ├─ All diner permissions
  │   ├─ Claim restaurant listing
  │   ├─ Create/edit restaurant profile
  │   ├─ Upload photos (set primary)
  │   ├─ Configure messaging & response hours
  │   ├─ View own reviews & messages
  │   ├─ Toggle availability/activation
  │   └─ View restaurant dashboard with metrics
  │
  └─ admin/staff (is_superuser or is_staff)
      ├─ All user permissions
      ├─ View all login logs
      ├─ Manage user accounts (activate/deactivate)
      ├─ Approve/reject restaurant ownership claims
      ├─ Manage approved/rejected/pending accounts
      ├─ View moderation reports
      ├─ Resolve moderation reports
      └─ View system audit logs, alerts, performance metrics
```

### Decorators & Guards

| Decorator | Purpose |
|---|---|
| `@login_required(login_url="landing")` | Restrict to authenticated users, redirect to landing |
| `@staff_member_required` | Restrict to admin/staff only |
| `@require_POST` | Only allow POST requests |
| `@require_GET` | Only allow GET requests |
| `@csrf_exempt` | Disable CSRF for specific endpoints (e.g., JSON endpoints) |

### Helper Functions

```python
_is_restaurant_owner(user) → bool
_is_diner(user) → bool
is_restaurant_owner(user) → bool
```

Check UserProfile role:
- `user.userprofile.role == "restaurant"` → restaurant owner
- `user.userprofile.role == "diner"` → regular diner
- `user.is_staff or user.is_superuser` → admin

### Permission Model

**Restaurant Ownership Claim Workflow**:
```
1. Restaurant owner (role=restaurant) submits claim
   ↓
2. Claim created as PENDING with verification details
   ↓
3. Admin reviews claim (RestaurantOwnershipClaim.approve/reject)
   ↓
4. On approval:
   - Restaurant.owner = claimant
   - UserProfile.is_approved = True (enables full access)
   - Claim.status = APPROVED
   ↓
5. On rejection:
   - UserProfile.is_rejected = True
   - Claim.status = REJECTED
```

**Restaurant Visibility**:
- Only displayed if: `owner.userprofile.is_approved == True` OR `owner == None` (ingested)
- Can be toggled: `is_active`, `is_temporarily_unavailable`
- Flagged accounts show `is_flagged = True` (fraud detection)

**Message Permissions**:
- Diner can message restaurant only if: `restaurant.messaging_enabled == True`
- Message responders must be in response_hours_start to response_hours_end
- Access control via `Conversation.can_access(user)` - checks if user is diner or restaurant owner

**Review Moderation**:
- Reports tracked in `ModerationReport` with status workflow
- Admin can soft-delete reviews: `Review.is_deleted = True`
- Reviews can be flagged: `Review.is_flagged = True`
- Users can be flagged: `UserProfile.is_flagged = True`

---

## 6. Special Features

### A. Two-Factor Authentication (2FA)
- **Package**: `django-two-factor-auth[phonenumbers]==1.17.0`
- **Coverage**: All user logins (not admin)
- **Templates**: `/templates/two_factor/core/`
- **Admin Login**: Uses separate security code (environment variable)

### B. Personalized Recommendations
- **Engine**: `recommend_restaurants_for_user(user, limit=N)` in [restaurant_sorting.py](nomz/restaurant_sorting.py)
- **Factors**:
  - User's saved preferences (cuisines, price, neighborhood)
  - Restaurant's composite score (normalized 0-100)
  - Cuisine match
  - Location proximity
  - Dietary accommodation ratings
- **Trigger**: Dashboard displays recommendations when preferences saved
- **Fallback**: Message if no matches found

### C. Restaurant Scoring & Analytics

**Composite Score Calculation**:
- **Components**:
  1. Health inspection grade (latest) with score weighting
  2. User reviews (8 rating dimensions weighted):
     - Overall (25%)
     - Food Quality (20%)
     - Service Quality (15%)
     - Cleanliness (10%)
     - Location (10%)
     - Value (10%)
     - Ambience (5%)
     - Dietary Accommodation (5%)
  3. Violation counts from inspections
  4. Review confidence (based on review count)
- **Range**: 0-100 decimal scale
- **Auto-Refresh**: Recalculated on review/inspection save/delete via signals
- **Trend Analysis**: Shows historical scores with direction (up/down/flat)

**Restaurant Dashboard Insights**:
- Score summary with grade and confidence
- Review factor breakdown (8 dimensions with averages)
- Trend points (last 8 inspections)
- Neighborhood comparison:
  - Ranking vs. peers in same neighborhood/borough
  - Percentile ranking
  - Average score delta

### D. Messaging System
- **Architecture**: One-to-one persistent conversations
- **Participants**: Restaurant owner ↔ Diner
- **Features**:
  - Lazy message loading
  - Read/unread tracking
  - Response hour restrictions
  - Toggleable via `messaging_enabled`
  - Last message preview in conversation list
- **API**: RESTful JSON endpoints with full access control

### E. Content Moderation
- **Types**:
  1. Review reports (spam, fraud, harassment, inappropriate)
  2. User account reports (suspicious activity)
- **Workflow**:
  - User submits ModerationReport with reason + details
  - Admin views pending reports in dashboard
  - Admin can dismiss or resolve with action taken
  - Soft delete reviews: set `is_deleted = True`
  - Flag accounts: set `is_flagged = True`
- **Metrics**: Admin dashboard shows pending report count

### F. Login Security & Audit Trail

**Suspicious Activity Detection**:
- Tracks >2 failed login attempts per IP/user in 15 minutes
- Marks admin paths (`/admin/`, `/dashboard/`, `/admin-login/`) as suspicious
- `LoginLog` records:
  - Username (guest or authenticated)
  - IP address + user agent
  - Success/Failure status
  - Suspicious flags
  - Timestamp

**Admin Monitoring**:
- View all login logs at `/nomz-admin/logs/`
- Identify users with suspicious activity
- Badge indicating suspicious login attempts

### G. System Monitoring & Alerts

**Real-time Metrics Collection**:
- `SystemPerformanceMetric`: Per-request tracking
  - Method, path, duration_ms, status_code, error status
  - Exception tracking (class, message)
- `SystemPerformanceSnapshot`: Time-bucketed aggregates
  - Interval-based (default 300s)
  - Total requests, error rate, latency stats
  - unique_together: [interval_start, interval_end]

**Alert Generation**:
- `SystemAlert` triggers on:
  1. Health check failures
  2. High error rate (threshold configurable)
  3. High latency (threshold configurable)
- Alert fields: type, severity (LOW/MEDIUM/HIGH/CRITICAL), message, metadata
- Active/resolved tracking with resolved_at timestamp

**Audit Logging**:
- `SystemAuditLog`: All admin changes + system exceptions
- Fields: actor, action, level (INFO/WARNING/ERROR/CRITICAL), metadata
- Used for compliance & incident investigation

**Settings** (in [restaurants/settings.py](restaurants/settings.py)):
```python
SYSTEM_METRICS_SNAPSHOT_INTERVAL_SECONDS = 300  # 5 min buckets
SYSTEM_ALERT_ERROR_RATE_THRESHOLD = 0.2  # 20% error rate
SYSTEM_ALERT_AVG_LATENCY_MS_THRESHOLD = 1000  # 1 second
```

### H. Restaurant Data Ingestion

**Data Sources**:
1. **EATERIES**: Directory of Eateries dataset
2. **DINING_OUT**: Dining Out NYC Locations
3. **DOHMH**: Restaurant Inspection Results

**Models**:
- `RestaurantSourceRecord`: Tracks external IDs, names, confidence, raw payloads
- `DiningOutLocation`: License type/status, location type, capacity estimates
- `InspectionRecord`: Health dept inspection grades, violations, scores
- Relationships: Multiple sources per restaurant (many-to-one)

**Ingestion Process**:
- `DataIngestionRun` tracks each import job
- Records fetched → processed → matched → created/updated
- Error logging for failed records
- Status: running, success, failed

### I. Restaurant Ownership & Verification

**Claim Workflow**:
1. Restaurant-role user claims existing restaurant
2. Submits: business email, contact phone, proof details (links/docs)
3. Admin reviews in pending approvals dashboard
4. Approve: Owner assigned, is_approved=True
5. Reject: is_rejected=True, user blocked

**Constraints**:
- Only one pending claim per user
- Restaurant can only have one approved owner
- Cannot claim if already owns another restaurant
- Claimant proof validated by admin

### J. Restaurant Filtering & Sorting

**Filter Types** (from [filtering.py](nomz/filtering.py)):
- Search: name, description, address, cuisine, borough
- Neighborhood/borough exact match
- Cuisine tags multi-filter
- Price range ($ to $$$$)
- Composite score range (min/max)
- Grade score range
- Dietary restrictions (vegan, vegetarian, gluten-free, etc.)
- Open now: Checks `is_active`, not unavailable, within hours_open/close

**Sort Options**:
- `composite_desc` (default): By score descending
- `composite_asc`: By score ascending
- `name_asc/desc`: Alphabetical
- `grade_desc/asc`: By health grade
- `score_desc`: By health inspection score

### K. User Preferences & Dietary Restrictions

**Preference Model**:
```
UserPreference (OneToOne with User)
  ├─ favorite_cuisines: JSONField (list of cuisine strings)
  ├─ dietary_restrictions: JSONField (list: vegan, vegetarian, gluten-free, halal, kosher)
  ├─ price_preference: CharField ($ to $$$$)
  └─ neighborhood_preference: CharField
```

**Dietary Options**: vegan, vegetarian, non-vegetarian, gluten-free, halal, kosher

**Usage**:
- Filters restaurant queries in recommendations
- Personalizes dashboard suggestions
- Used for scoring restaurant match

### L. Restaurant Profile Customization

**Owner-Editable Fields**:
- Name, description, address, phone, website, email
- Cuisine type, price range
- Operating hours (hours_open, hours_close)
- Messaging settings (enabled, response hours)
- Availability (is_active, temporarily_unavailable, unavailable_reason, unavailable_until)
- Communication preferences

**Photos**:
- Multiple photos per restaurant
- One primary photo (enforced in save())
- Upload with caption
- Delete & reorder

---

## Summary Tables

### Technology Stack

| Layer | Technology |
|---|---|
| Framework | Django 4.x |
| Authentication | django-two-factor-auth, Django auth |
| Database | SQLite (development), PostgreSQL (production via AWS) |
| API | Django REST (JSON endpoints) |
| Forms | Django forms with Bootstrap styling |
| Monitoring | Custom middleware (SystemPerformanceMetric, SystemAuditLog) |
| Tasks | Django signals (auto-refresh scores) |
| Auth Provider | Built-in + 2FA |

### Permission Matrix

| Action | Diner | Restaurant | Admin | Notes |
|---|---|---|---|---|
| View restaurants | ✓ | ✓ | ✓ | |
| Write review | ✓ | ✓ | ✗ | |
| Message restaurant | ✓ | ✗ | ✗ | Requires messaging_enabled |
| Edit profile | ✓ | ✓ (own) | ✓ | |
| Upload photo | ✗ | ✓ (own) | ✗ | |
| Claim restaurant | ✗ | ✓ | ✗ | Pending admin approval |
| Approve claims | ✗ | ✗ | ✓ | |
| Manage users | ✗ | ✗ | ✓ | Activate/deactivate |
| View audit logs | ✗ | ✗ | ✓ | |
| Moderate content | ✗ | ✗ | ✓ | Resolve reports |

### Key File Structure

```
nomz/
├─ models.py              # 19 models
├─ views.py               # Main user-facing views
├─ api_views.py           # RESTful JSON endpoints
├─ forms.py               # 12+ form classes
├─ urls.py                # 60+ URL patterns
├─ filtering.py           # Restaurant filtering & sorting
├─ scoring.py             # Composite score calculation
├─ restaurant_sorting.py  # Recommendation engine
├─ middleware.py          # System monitoring middleware
├─ signals.py             # Auto-refresh signals
├─ ingestion/             # Data import pipeline
│   ├─ runner.py
│   ├─ persistence.py
│   ├─ utils/
│   │   ├─ score.py       # Score computation logic
│   │   └─ source_matcher.py
│   └─ sources/           # Data source adapters
└─ management/commands/   # Django management commands
```

---

## Deployment Notes

- **Health Check**: `/health/` endpoint for ELB/EB
- **Static Files**: `/static/` served separately
- **Media Files**: `/media/restaurant_photos/` for uploads
- **Procfile**: AWS Elastic Beanstalk deployment
- **Travis CI**: Configured for continuous deployment with Coveralls
- **Database Migrations**: 16+ migration files tracking schema evolution

---

**Analysis Complete**: This comprehensive codebase implements a production-ready restaurant discovery platform with multi-user roles, health scoring, user-generated reviews, moderation, messaging, and full system monitoring.
