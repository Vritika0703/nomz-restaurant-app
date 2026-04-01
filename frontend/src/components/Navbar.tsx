import { Link, useNavigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { selectUser, selectIsAuthenticated, logout } from '@store/slices/auth'
import { authApi } from '@api/auth'

export default function Navbar() {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const user = useSelector(selectUser)
  const isAuthenticated = useSelector(selectIsAuthenticated)

  const handleLogout = async () => {
    try {
      await authApi.logout()
      dispatch(logout())
      navigate('/')
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto flex items-center justify-between px-4 py-4">
        <Link to="/" className="flex items-center space-x-2">
          <div className="text-2xl font-bold text-blue-600">Nomz</div>
        </Link>

        <div className="flex items-center space-x-6">
          <Link to="/map" className="text-gray-700 hover:text-blue-600">
            Map
          </Link>
          <Link to="/restaurants" className="text-gray-700 hover:text-blue-600">
            Search
          </Link>

          {isAuthenticated && user ? (
            <>
              <Link to="/messages" className="text-gray-700 hover:text-blue-600">
                Messages
              </Link>
              <Link to="/dashboard" className="text-gray-700 hover:text-blue-600">
                Dashboard
              </Link>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">{user.username}</span>
                <button
                  onClick={handleLogout}
                  className="rounded-md bg-red-600 px-4 py-2 text-white hover:bg-red-700"
                >
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="rounded-md border border-blue-600 px-4 py-2 text-blue-600 hover:bg-blue-50"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
