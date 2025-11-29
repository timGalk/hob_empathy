import React, { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

function EEGChart({ patientId }) {
  const [data, setData] = useState([])

  useEffect(() => {
    // Simulate real-time EEG data for demo
    const interval = setInterval(() => {
      const timestamp = new Date().toLocaleTimeString()
      const newPoint = {
        time: timestamp,
        ch1: Math.random() * 100 - 50,
        ch2: Math.random() * 100 - 50,
        ch3: Math.random() * 100 - 50,
        ch4: Math.random() * 100 - 50
      }

      setData(prev => [...prev.slice(-50), newPoint])
    }, 500)

    return () => clearInterval(interval)
  }, [patientId])

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="time" />
        <YAxis domain={[-100, 100]} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="ch1" stroke="#8884d8" dot={false} strokeWidth={1} />
        <Line type="monotone" dataKey="ch2" stroke="#82ca9d" dot={false} strokeWidth={1} />
        <Line type="monotone" dataKey="ch3" stroke="#ffc658" dot={false} strokeWidth={1} />
        <Line type="monotone" dataKey="ch4" stroke="#ff7c7c" dot={false} strokeWidth={1} />
      </LineChart>
    </ResponsiveContainer>
  )
}

export default EEGChart
