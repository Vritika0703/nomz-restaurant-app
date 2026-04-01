import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { loginStart, loginRequires2FA, loginSuccess, loginFailure, selectAuth } from '@store/slices/auth'
import { authApi } from '@api/auth'

export default function Login() {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { requires2FA, sessionToken, isLoading, error } = useSelector(selectAuth)

  const [formData, setFormData] = useState({
    username: '',
    password: '',
  })
  const [twoFACode, setTwoFACode] = useState('')

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    dispatch(loginStart())

    try {
      const response = await authApi.login(formData)
      if (response.requires_2fa) {
        dispatch(loginRequires2FA(response.session_token))
      } else {
        // Login without 2FA (shouldn't happen if 2FA is enabled)
        const user = await authApi.getCurrentUser()
        dispatch(loginSuccess(user))
        navigate('/dashboard')
      }
    } catch (err: any) {
      dispatch(loginFailure(err.message || 'Login failed'))
    }
  }

  const handleVerify2FA = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!sessionToken) return

    dispatch(loginStart())
    try {
      const response = await authApi.verify2FA({
        token: sessionToken,
        code: twoFACode,
      })
      dispatch(loginSuccess(response.user))
      navigate('/dashboard')
    } catch (err: any) {
      dispatch(loginFailure(err.message || '2FA verification failed'))
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow-md">
        <h1 className="mb-6 text-center text-2xl font-bold text-gray-900">Nomz Login</h1>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

        {!requires2FA ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                required
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
                disabled={isLoading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2"
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerify2FA} className="space-y-4">
            <p className="text-sm text-gray-600">
              Enter the 6-digit code from your authenticator app:
            </p>
            <input
              type="text"
              value={twoFACode}
              onChange={(e) => setTwoFACode(e.target.value)}
              placeholder="000000"
              maxLength={6}
              required
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-center text-2xl tracking-widest"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || twoFACode.length !== 6}
              className="w-full rounded-md bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Verifying...' : 'Verify'}
            </button>
          </form>
        )}

        <div className="mt-6 text-center text-sm">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="font-medium text-blue-600 hover:text-blue-700">
              Register here
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
