import React, { useState, useEffect } from 'react'
import './App.css'
import RiskGauge from './components/RiskGauge'
import EEGChart from './components/EEGChart'
import AlertsPanel from './components/AlertsPanel'
import PatientInfo from './components/PatientInfo'

function App() {
  const [patientId, setPatientId] = useState('patient_001')
  const [patientState, setPatientState] = useState({
    risk: 0.0,
    state: 'normal',
    timestamp: new Date().toISOString()
  })
  const [alerts, setAlerts] = useState([])
  const [wsConnected, setWsConnected] = useState(false)

  useEffect(() => {
    // Fetch initial patient state
    fetchPatientState()

    // Connect to WebSocket for real-time updates
    const ws = new WebSocket('ws://localhost:8000/api/v1/stream')

    ws.onopen = () => {
      console.log('WebSocket connected')
      setWsConnected(true)
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'prediction') {
        setPatientState(data.prediction)
      } else if (data.type === 'alert') {
        setAlerts(prev => [data.alert, ...prev].slice(0, 10))
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setWsConnected(false)
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setWsConnected(false)
    }

    // Cleanup
    return () => {
      ws.close()
    }
  }, [patientId])

  const fetchPatientState = async () => {
    try {
      const response = await fetch(`/api/v1/patient/${patientId}/state`)
      if (response.ok) {
        const data = await response.json()
        setPatientState(data)
      }
    } catch (error) {
      console.error('Failed to fetch patient state:', error)
    }
  }

  return (
    <div className="App">
      <header className="header">
        <h1>EEG Dementia Monitoring Dashboard</h1>
        <div className="connection-status">
          <span className={wsConnected ? 'status-indicator connected' : 'status-indicator disconnected'}></span>
          {wsConnected ? 'Connected' : 'Disconnected'}
        </div>
      </header>

      <div className="dashboard-grid">
        <div className="panel patient-panel">
          <PatientInfo patientId={patientId} />
        </div>

        <div className="panel risk-panel">
          <h2>Current Risk Level</h2>
          <RiskGauge risk={patientState.risk} state={patientState.state} />
        </div>

        <div className="panel chart-panel">
          <h2>EEG Signal Visualization</h2>
          <EEGChart patientId={patientId} />
        </div>

        <div className="panel alerts-panel">
          <h2>Alerts & Events</h2>
          <AlertsPanel alerts={alerts} />
        </div>
      </div>
    </div>
  )
}

export default App
