import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../utils/api'
import { getUser, logout } from '../../utils/auth'

function DoctorDashboard() {
  const [patients, setPatients] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [asking, setAsking] = useState(false)
  const [summary, setSummary] = useState('')
  const [summarizing, setSummarizing] = useState(false)
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

  const handleSelectPatient = async (patient) => {
    setSelectedPatient(patient)
    setAnswer('')
    setQuestion('')
    // embed patient record when selected
    try {
      await api.post(`/ai/embed/${patient.id}`)
    } catch (err) {
      console.log(err)
    }
  }

  const handleAsk = async () => {
    if (!question.trim()) return
    setAsking(true)
    setAnswer('')
    try {
      const response = await api.post(`/ai/ask/${selectedPatient.id}`, {
        question
      })
      setAnswer(response.data.answer)
    } catch (err) {
      setAnswer('Error getting answer. Please try again.')
    } finally {
      setAsking(false)
    }
  }
  const handleSummary = async () => {
  setSummarizing(true)
  setSummary('')
  try {
    const response = await api.get(`/ai/summary/${selectedPatient.id}`)
    setSummary(response.data.summary)
  } catch (err) {
    setSummary('Error generating summary.')
  } finally {
    setSummarizing(false)
  }
}

  return (
    <div className="min-h-screen bg-gray-100">
      {/* navbar */}
      <div className="bg-white shadow p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold text-blue-600">AI Clinic — Doctor</h1>
        <div className="flex items-center gap-4">
          <span className="text-gray-600">Hi, {currentUser?.name}</span>
          <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            Logout
          </button>
        </div>
      </div>

      <div className="p-8 grid grid-cols-3 gap-6">
        {/* patient list */}
        <div className="col-span-1">
          <h2 className="text-lg font-semibold text-gray-700 mb-4">My Patients</h2>
          {loading ? <p>Loading...</p> : (
            <div className="space-y-2">
              {patients.map(patient => (
                <div
                  key={patient.id}
                  onClick={() => handleSelectPatient(patient)}
                  className={`bg-white rounded-lg shadow p-4 cursor-pointer hover:bg-blue-50 ${
                    selectedPatient?.id === patient.id ? 'border-2 border-blue-500' : ''
                  }`}
                >
                  <p className="font-medium">{patient.name}</p>
                  <p className="text-sm text-gray-500">{patient.conditions || 'No conditions'}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* patient detail + AI Q&A */}
        <div className="col-span-2">
          {!selectedPatient ? (
            <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
              Select a patient to view their record and ask AI questions
            </div>
          ) : (
            <div className="space-y-4">
              {/* patient record */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="font-semibold text-gray-700 mb-3">{selectedPatient.name}'s Record</h3>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <p className="text-gray-600">Age: <span className="font-medium">{selectedPatient.age}</span></p>
                  <p className="text-gray-600">Blood Type: <span className="font-medium">{selectedPatient.blood_type}</span></p>
                  <p className="text-gray-600">Allergies: <span className="font-medium">{selectedPatient.allergies || 'None'}</span></p>
                  <p className="text-gray-600">Conditions: <span className="font-medium">{selectedPatient.conditions || 'None'}</span></p>
                  <p className="text-gray-600">Medications: <span className="font-medium">{selectedPatient.medications || 'None'}</span></p>
                </div>
              </div>

              {/* AI Q&A */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="font-semibold text-gray-700 mb-3">Ask AI about {selectedPatient.name}</h3>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
                    placeholder="e.g. What medications is this patient on?"
                    className="flex-1 border border-gray-300 rounded p-3 focus:outline-none focus:border-blue-500"
                  />
                  <button
                    onClick={handleAsk}
                    disabled={asking}
                    className="bg-blue-600 text-white px-6 py-3 rounded font-semibold hover:bg-blue-700 disabled:opacity-50"
                  >
                    {asking ? 'Asking...' : 'Ask'}
                  </button>
                </div>
                {answer && (
  <div className="mt-4 bg-blue-50 border border-blue-200 rounded p-4">
    <p className="text-sm font-medium text-blue-700 mb-1">AI Answer:</p>
    <p className="text-gray-700">{answer}</p>
  </div>
)}

<button
  onClick={handleSummary}
  disabled={summarizing}
  className="mt-3 w-full bg-green-600 text-white p-3 rounded font-semibold hover:bg-green-700 disabled:opacity-50"
>
  {summarizing ? 'Generating Summary...' : '📋 Generate Patient Summary'}
</button>

{summary && (
  <div className="mt-4 bg-green-50 border border-green-200 rounded p-4">
    <p className="text-sm font-medium text-green-700 mb-1">Patient Summary:</p>
    <p className="text-gray-700 whitespace-pre-line">{summary}</p>
  </div>
)}
                
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DoctorDashboard