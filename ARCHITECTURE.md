

# EEG Dementia-Monitoring MVP — System Architecture

## Overview

A lightweight 24-hour hackathon MVP for real-time monitoring of elderly patients with dementia.
The system streams **8-channel EEG at 250 Hz**, performs on-device preprocessing, pushes features to a backend, and runs a basic frustration/dementia-episode prediction model.
A clinician dashboard visualizes alerts and raw signals.

---

## High-Level Architecture

```
EEG Headset (8ch @ 250Hz)
        │
        ▼
Mobile/Edge Collector (Android/iOS or Raspberry Pi)
  - Signal acquisition
  - Filtering (band-pass)
  - Noise reduction (Notch 50/60Hz)
  - Windowing (1–2s)
  - Feature extraction (Bandpower, PSD, Entropy)
        │
        ▼
Backend API (FastAPI / Node / Go)
  - Auth
  - Feature ingest
  - Model inference
  - Alerts generation
        │
        ▼
Prediction Engine (Python)
  - Baseline classifier (Random Forest / LightGBM)
  - Threshold logic for “frustration episode risk”
        │
        ▼
Database (PostgreSQL)
  - Patient profiles
  - EEG feature history
  - Prediction logs
        │
        ▼
Dashboard (React / Next.js)
  - Live signal view
  - Predicted risk states
  - Alert stream
  - Historical charts
```

---

## Components

### 1. **EEG Acquisition Module**

* Hardware: any BLE/WiFi EEG device supporting **8 channels, 250 Hz**
* Data format:

  ```json
  {
    "timestamp": "...",
    "channels": [c1, c2, ..., c8],
    "sampling_rate": 250
  }
  ```

---

### 2. **Edge Preprocessing Layer**

Runs directly on a phone or Raspberry Pi.

**Responsibilities:**

* Band-pass filter (1–40 Hz)
* Notch filter (50 Hz EU / 60 Hz US)
* Normalize signals
* Segment EEG into windows (e.g., 2 s → 500 samples/window)
* Extract lightweight features:

  * Delta/Theta/Alpha/Beta bandpower
  * Spectral entropy
  * Signal variance
  * Hjorth parameters

**Output payload example:**

```json
{
  "patient_id": "123",
  "window_start": "...",
  "features": {
    "alpha_power": 0.12,
    "beta_power": 0.08,
    "entropy": 1.43,
    "mobility": 0.91
  }
}
```

---

### 3. **Backend API**

Framework recommendations: **FastAPI**

Endpoints:

* `POST /ingest` — receive windowed EEG features
* `GET /patient/{id}/state` — latest prediction
* `GET /history` — feature & prediction time-series
* `WS /stream` — real-time event push

---

### 4. **Prediction Engine**

Minimal model due to time constraints.

**Options:**

* Rule-based thresholding
* Random Forest classifier
* LightGBM (fast training, small footprint)

**Input:** feature vector
**Output:**

```json
{
  "risk": 0.74,
  "state": "elevated",
  "model_version": "0.1"
}
```

Risk levels:

* 0.0–0.3 — normal
* 0.3–0.6 — mild agitation
* 0.6–1.0 — high frustration episode risk

---

### 5. **Database Layer**

**PostgreSQL schema:**

```
patients (id, name, age, notes)
features (id, patient_id, ts, feature_json)
predictions (id, patient_id, ts, risk, state)
alerts (id, patient_id, ts, type, message)
```

---

### 6. **Clinician Dashboard**

Tech: **React / Next.js + WebSocket streaming**

**Features:**

* Live EEG feed (downsampled for browser ≈ 50 Hz)
* Risk meter (gauge or color-coded badge)
* Timeline of predictions
* Alerts panel
* Patient switching

---

## Data Flow Summary

1. **EEG device → Edge**
   Raw 8×250 data streamed continuously.

2. **Edge → Backend**
   Cleaned, windowed features pushed every 1–2 seconds.

3. **Backend → Model**
   Model calculates risk score.

4. **Backend → DB**
   Stores features + predictions.

5. **Backend → Dashboard**
   WebSocket pushes live updates.

---

## Non-Functional Requirements

* Latency: <500 ms end-to-end for prediction
* Data loss tolerance: handle intermittent connectivity
* Security: JWT auth, HTTPS
* Scalability: stateless backend, horizontal scaling
* Offline mode: edge device queues windows

---

## Deployment (24h-friendly)

* **Backend**: Docker (FastAPI + LightGBM)
* **DB**: Cloud PostgreSQL / Supabase
* **Dashboard**: Vercel / Netlify
* **Edge App**: Android Kotlin or Python script on Raspberry Pi

---

