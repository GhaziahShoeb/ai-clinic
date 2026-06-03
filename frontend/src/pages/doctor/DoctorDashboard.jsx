import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../utils/api'
import { getUser, logout } from '../../utils/auth'

function DoctorDashboard() {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const currentUser = getUser()

  useEffect(() => {
    const fetchPatients = async () => {
      try {
        const response = await api.get('/doctors/patients')
        setPatients(response.data)
      } catch (err) {
        console.log(err)
      } finally {
        setLoading(false)
      }
    }
    fetchPatients()
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* navbar */}
      <div className="bg-white shadow p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-blue-600">AI Clinic — Doctor</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-600">Hi, Dr. {currentUser?.name}</span>
          <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            Logout
          </button>
        </div>
      </div>

      <div className="p-8">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">My Patients</h2>

        {loading ? (
          <p>Loading...</p>
        ) : patients.length === 0 ? (
          <p className="text-gray-500">No patients found.</p>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-4 text-left text-gray-600">Name</th>
                  <th className="p-4 text-left text-gray-600">Age</th>
                  <th className="p-4 text-left text-gray-600">Blood Type</th>
                  <th className="p-4 text-left text-gray-600">Conditions</th>
                </tr>
              </thead>
              <tbody>
                {patients.map(patient => (
                  <tr key={patient.id} className="border-t hover:bg-gray-50 cursor-pointer">
                    <td className="p-4">{patient.name}</td>
                    <td className="p-4">{patient.age}</td>
                    <td className="p-4">{patient.blood_type}</td>
                    <td className="p-4">{patient.conditions || 'None'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default DoctorDashboard