import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../utils/api'
import { getUser, logout } from '../../utils/auth'

function PatientDashboard() {
  const [record, setRecord] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const currentUser = getUser()

  useEffect(() => {
    const fetchRecord = async () => {
      try {
        const response = await api.get('/patients/me')
        setRecord(response.data)
      } catch (err) {
        console.log(err)
      } finally {
        setLoading(false)
      }
    }
    fetchRecord()
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* navbar */}
      <div className="bg-white shadow p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-blue-600">AI Clinic — Patient</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-600">Hi, {currentUser?.name}</span>
          <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            Logout
          </button>
        </div>
      </div>

      <div className="p-8">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">My Health Record</h2>

        {loading ? (
          <p>Loading...</p>
        ) : !record ? (
          <p className="text-gray-500">No health record found.</p>
        ) : (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-700 mb-3">Personal Info</h3>
              <p className="text-gray-600">Age: <span className="font-medium">{record.age}</span></p>
              <p className="text-gray-600">Blood Type: <span className="font-medium">{record.blood_type}</span></p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-700 mb-3">Medical Info</h3>
              <p className="text-gray-600">Allergies: <span className="font-medium">{record.allergies || 'None'}</span></p>
              <p className="text-gray-600">Conditions: <span className="font-medium">{record.conditions || 'None'}</span></p>
              <p className="text-gray-600">Medications: <span className="font-medium">{record.medications || 'None'}</span></p>
            </div>

            <div className="bg-white rounded-lg shadow p-6 col-span-2">
              <h3 className="font-semibold text-gray-700 mb-3">Doctor's Notes</h3>
              <p className="text-gray-600">{record.notes || 'No notes yet'}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default PatientDashboard