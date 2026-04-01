import { Link } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { selectIsAuthenticated } from '@store/slices/auth'

export default function Landing() {
  const isAuthenticated = useSelector(selectIsAuthenticated)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800">
      <nav className="bg-white bg-opacity-10 backdrop-blur-md">
        <div className="container mx-auto flex items-center justify-between px-4 py-4">
          <div className="text-3xl font-bold text-white">Nomz</div>
          <div className="space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="text-white hover:text-blue-100">
                  Dashboard
                </Link>
                <Link to="/map" className="text-white hover:text-blue-100">
                  Map
                </Link>
              </>
            ) : (
              <>
                <Link to="/login" className="text-white hover:text-blue-100">
                  Login
                </Link>
                <Link to="/register" className="text-white hover:text-blue-100">
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4">
        <div className="flex flex-col items-center justify-center py-20 text-center">
          <h1 className="mb-6 text-5xl font-bold text-white">Welcome to Nomz</h1>
          <p className="mb-12 text-xl text-blue-100">
            Discover and review NYC's best restaurants
          </p>

          <div className="space-y-4 sm:space-x-4 sm:space-y-0">
            <Link
              to="/restaurants"
              className="inline-block rounded-lg bg-white px-8 py-3 font-semibold text-blue-600 hover:bg-blue-50"
            >
              Search Restaurants
            </Link>
            <Link
              to="/map"
              className="inline-block rounded-lg border-2 border-white px-8 py-3 font-semibold text-white hover:bg-white hover:bg-opacity-10"
            >
              View Map
            </Link>
          </div>

          {!isAuthenticated && (
            <div className="mt-12">
              <p className="mb-6 text-blue-100">Ready to get started?</p>
              <Link
                to="/register"
                className="inline-block rounded-lg bg-yellow-400 px-8 py-3 font-semibold text-gray-900 hover:bg-yellow-300"
              >
                Create Account
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
