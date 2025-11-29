import React from 'react'
import './RiskGauge.css'

function RiskGauge({ risk, state }) {
  const getRiskColor = () => {
    if (risk < 0.3) return '#4caf50'  // green
    if (risk < 0.6) return '#ff9800'  // orange
    return '#f44336'  // red
  }

  const getStateLabel = () => {
    switch(state) {
      case 'normal': return 'Normal'
      case 'mild': return 'Mild Agitation'
      case 'elevated': return 'Elevated Risk'
      default: return 'Unknown'
    }
  }

  const percentage = Math.round(risk * 100)

  return (
    <div className="risk-gauge">
      <div className="gauge-container">
        <svg viewBox="0 0 200 120" className="gauge-svg">
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#e0e0e0"
            strokeWidth="20"
            strokeLinecap="round"
          />
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke={getRiskColor()}
            strokeWidth="20"
            strokeLinecap="round"
            strokeDasharray={`${risk * 251.2} 251.2`}
          />
        </svg>
        <div className="gauge-value">
          <span className="risk-percentage">{percentage}%</span>
          <span className="risk-state">{getStateLabel()}</span>
        </div>
      </div>
    </div>
  )
}

export default RiskGauge
