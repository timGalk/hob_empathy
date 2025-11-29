import React from 'react'
import './AlertsPanel.css'

function AlertsPanel({ alerts }) {
  if (alerts.length === 0) {
    return (
      <div className="alerts-empty">
        <p>No alerts at this time</p>
      </div>
    )
  }

  return (
    <div className="alerts-list">
      {alerts.map((alert, index) => (
        <div key={index} className={`alert alert-${alert.severity || 'medium'}`}>
          <div className="alert-header">
            <span className="alert-type">{alert.alert_type || 'Alert'}</span>
            <span className="alert-time">{new Date(alert.timestamp).toLocaleTimeString()}</span>
          </div>
          <div className="alert-message">{alert.message}</div>
        </div>
      ))}
    </div>
  )
}

export default AlertsPanel
