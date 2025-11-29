# Dashboard

React-based web dashboard for real-time EEG monitoring.

## Features

- Real-time EEG signal visualization
- Risk gauge with color-coded states
- Alert notifications
- Patient information panel
- WebSocket-based live updates
- Responsive design

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

Dashboard available at: http://localhost:3000

## Building for Production

```bash
npm run build
```

## Configuration

Configure backend URL in `vite.config.js` proxy settings or use environment variable:

```bash
VITE_API_URL=http://your-backend-url npm run dev
```

## Components

- `RiskGauge` - Visual risk indicator
- `EEGChart` - Real-time signal visualization
- `AlertsPanel` - Alert notifications
- `PatientInfo` - Patient details

## Technology Stack

- React 18
- Vite
- Recharts (data visualization)
- Axios (HTTP client)
- WebSocket API
