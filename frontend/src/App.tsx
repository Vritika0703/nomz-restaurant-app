import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Provider } from 'react-redux'
import store from '@store'
import ProtectedRoute from '@components/ProtectedRoute'
import Layout from '@components/Layout'

// Pages
import Landing from '@pages/Landing'
import Login from '@pages/Login'
import Register from '@pages/Register'
import Dashboard from '@pages/Dashboard'
import RestaurantSearch from '@pages/RestaurantSearch'
import RestaurantProfile from '@pages/RestaurantProfile'
import MapView from '@pages/MapView'
import AddReview from '@pages/AddReview'
import Messaging from '@pages/Messaging'
import UserPreferences from '@pages/UserPreferences'
import Recommendations from '@pages/Recommendations'

function App() {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/map" element={<MapView />} />
          <Route path="/restaurants" element={<RestaurantSearch />} />
          <Route path="/restaurants/:id" element={<RestaurantProfile />} />

          {/* Protected routes */}
          <Route element={<Layout />}>
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/reviews/add"
              element={
                <ProtectedRoute>
                  <AddReview />
                </ProtectedRoute>
              }
            />
            <Route
              path="/messages"
              element={
                <ProtectedRoute>
                  <Messaging />
                </ProtectedRoute>
              }
            />
            <Route
              path="/preferences"
              element={
                <ProtectedRoute>
                  <UserPreferences />
                </ProtectedRoute>
              }
            />
            <Route
              path="/recommendations"
              element={
                <ProtectedRoute>
                  <Recommendations />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </Provider>
  )
}

export default App
