import React from 'react'
import './PatientInfo.css'

function PatientInfo({ patientId }) {
  return (
    <div className="patient-info">
      <h3>Patient Information</h3>
      <div className="info-row">
        <span className="info-label">Patient ID:</span>
        <span className="info-value">{patientId}</span>
      </div>
      <div className="info-row">
        <span className="info-label">Name:</span>
        <span className="info-value">Demo Patient</span>
      </div>
      <div className="info-row">
        <span className="info-label">Age:</span>
        <span className="info-value">75</span>
      </div>
      <div className="info-row">
        <span className="info-label">Monitoring:</span>
        <span className="info-value status-active">Active</span>
      </div>
    </div>
  )
}

export default PatientInfo
