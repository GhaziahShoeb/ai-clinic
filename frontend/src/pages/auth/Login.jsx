import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../utils/api'
import { saveAuth } from '../../utils/auth'

function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const navigate = useNavigate()

  const fillCredentials = (demoEmail, demoPassword) => {
    setEmail(demoEmail)
    setPassword(demoPassword)
    setError('')
  }

  const handleLogin = async () => {
    setLoading(true)
    setError('')

    try {
      const trimmedEmail = email.trim()
      const formData = new FormData()
      formData.append('username', trimmedEmail)
      formData.append('password', password)

      const response = await api.post('/auth/login', formData)
      const token = response.data.access_token

      // Store fresh token immediately
      localStorage.setItem('token', token)

      const userResponse = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
      const user = userResponse.data

      saveAuth(token, user)

      if (user.role === 'admin') navigate('/admin')
      else if (user.role === 'doctor') navigate('/doctor')
      else navigate('/patient')

    } catch (err) {
      console.log(err)
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Invalid email or password')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center text-blue-600 mb-6">AI Clinic</h1>
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Login</h2>

        {error && (
          <div className="bg-red-100 text-red-600 p-3 rounded mb-4 text-sm">
            {error}
          </div>
        )}

        <div className="mb-3">
          <input
            type="email"
            placeholder="Email"
            value={email}
            autoComplete="off"
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border border-gray-300 rounded p-3 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="relative mb-4">
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Password"
            value={password}
            autoComplete="new-password"
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-gray-300 rounded p-3 pr-16 focus:outline-none focus:border-blue-500"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-3.5 text-xs font-medium text-gray-500 hover:text-gray-700"
          >
            {showPassword ? 'Hide' : 'Show'}
          </button>
        </div>

        <button
          onClick={handleLogin}
          disabled={loading}
          className="w-full bg-blue-600 text-white p-3 rounded font-semibold hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>

        {/* Quick Demo Credentials */}
        <div className="mt-6 pt-5 border-t border-gray-200">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500 mb-3 text-center">
            Quick Fill Demo Accounts (Password: 123456)
          </p>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => fillCredentials('doctor@clinic.com', '123456')}
              className="py-1.5 px-2 text-xs font-medium text-blue-700 bg-blue-50 hover:bg-blue-100 rounded border border-blue-200 transition text-center"
            >
              Doctor
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('admin2@clinic.com', '123456')}
              className="py-1.5 px-2 text-xs font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 rounded border border-purple-200 transition text-center"
            >
              Admin
            </button>
            <button
              type="button"
              onClick={() => fillCredentials('patient@clinic.com', '123456')}
              className="py-1.5 px-2 text-xs font-medium text-green-700 bg-green-50 hover:bg-green-100 rounded border border-green-200 transition text-center"
            >
              Patient
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Login