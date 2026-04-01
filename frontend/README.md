# Nomz Frontend

React-based frontend for the Nomz restaurant discovery platform.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Redux Toolkit** - State management
- **Axios** - HTTP client
- **React Router v6** - Routing
- **Tailwind CSS** - Styling

## Project Structure

```
src/
├── api/              # API client and endpoints
│   ├── client.ts     # Axios instance with JWT handling
│   ├── auth.ts       # Authentication endpoints
│   ├── restaurants.ts # Restaurant endpoints
│   ├── reviews.ts    # Review endpoints
│   └── messages.ts   # Messaging endpoints
├── components/       # Reusable React components
│   ├── ProtectedRoute.tsx
│   ├── Layout.tsx
│   └── Navbar.tsx
├── pages/           # Page components
│   ├── Landing.tsx
│   ├── Login.tsx
│   ├── Register.tsx
│   ├── Dashboard.tsx
│   ├── RestaurantSearch.tsx
│   ├── RestaurantProfile.tsx
│   ├── MapView.tsx
│   ├── AddReview.tsx
│   ├── Messaging.tsx
│   ├── UserPreferences.tsx
│   └── Recommendations.tsx
├── store/           # Redux state management
│   ├── slices/
│   │   └── auth.ts   # Auth state slice
│   └── index.ts      # Store configuration
├── hooks/           # Custom React hooks
├── utils/           # Utility functions
├── types/           # TypeScript type definitions
├── App.tsx          # Main app component
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## Getting Started

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Building

```bash
npm run build
```

Output: `dist/` folder (ready for production deployment)

## Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:8000
```

For production:

```
VITE_API_URL=https://api.nomz.com
```

## Features

### Authentication (Partial)
- ✅ Login with 2FA support
- ✅ Registration
- ✅ JWT token management with auto-refresh
- ⏳ Password reset

### Restaurants (Scaffolded)
- ⏳ Search and filtering
- ⏳ View restaurant profile
- ⏳ Map view
- ⏳ Photos and details

### User Features (Scaffolded)
- ⏳ Add reviews
- ⏳ Messaging system
- ⏳ Recommendations
- ⏳ User preferences
- ⏳ Dashboard

### Admin Features (To be implemented)
- User approval/rejection
- Content moderation
- System monitoring

## API Integration

### Available API Clients

```typescript
import { authApi } from '@api/auth'
import { restaurantApi } from '@api/restaurants'
import { reviewApi } from '@api/reviews'
import { messageApi } from '@api/messages'
```

### Example Usage

```typescript
// Login
const response = await authApi.login({
  username: 'user',
  password: 'pass'
})

// Search restaurants
const restaurants = await restaurantApi.searchRestaurants({
  query: 'pizza',
  cuisine: ['Italian'],
})

// Create review
const review = await reviewApi.createReview({
  restaurant_id: 1,
  food_rating: 5,
  // ... other ratings
  comment: 'Great food!'
})
```

## State Management

Uses Redux Toolkit for predictable state management.

### Auth State

```typescript
{
  user: User | null,
  isAuthenticated: boolean,
  isLoading: boolean,
  error: string | null,
  requires2FA: boolean,
  sessionToken: string | null,
}
```

### Usage

```typescript
import { useDispatch, useSelector } from 'react-redux'
import { selectUser, logout } from '@store/slices/auth'

function MyComponent() {
  const user = useSelector(selectUser)
  const dispatch = useDispatch()
  
  const handleLogout = () => {
    dispatch(logout())
  }
}
```

## Testing

```bash
npm run test
npm run test:ui
```

## Linting

```bash
npm run lint
npm run type-check
```

## Deployment

### Option A: Serve from Django (Recommended for single deployment)

```bash
# 1. Build React
npm run build

# 2. Copy dist/ to Django's static files
cp -r dist/* ../path/to/django/static/

# 3. Configure Django to serve React's index.html for SPA routing
```

### Option B: Deploy separately

```bash
# Deploy to Vercel, Netlify, or any static hosting
npm run build
# Upload dist/ folder
```

## Next Steps

1. Implement restaurant search and filtering
2. Build map integration (Google Maps/Mapbox)
3. Create review form with 8-point rating system
4. Implement messaging UI
5. Build admin dashboard
6. Add E2E tests with Cypress
7. Performance optimization

## Troubleshooting

### CORS Errors

Ensure Django has CORS configured:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://yourdomain.com",
]
```

### JWT Token Issues

Tokens auto-refresh when expired. If issues persist:

1. Clear browser storage: `localStorage.clear()`
2. Check token in Network DevTools
3. Verify `VITE_API_URL` is correct

### Build Errors

```bash
npm run type-check  # Check for TypeScript errors
npm run lint        # Check for linting issues
```

## Contributing

- Follow TypeScript best practices
- Use functional components with hooks
- Keep components small and focused
- Use custom hooks for logic reuse

---

**Backend**: Django at `/Users/ananyaagarwal/Desktop/github/team3-mon-spring26/`  
**Frontend**: React at `/Users/ananyaagarwal/Desktop/github/team3-mon-spring26/frontend/`
