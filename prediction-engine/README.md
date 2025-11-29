# Prediction Engine

Machine learning prediction service for dementia episode risk assessment.

## Features

- Rule-based risk assessment (MVP)
- Support for Random Forest and LightGBM models
- Risk classification (Normal, Mild, Elevated)
- Model training scripts

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Training a Model

```bash
cd training
python train_model.py
```

This will:
1. Generate synthetic training data (replace with real data)
2. Train a Random Forest classifier
3. Evaluate performance
4. Save model to `models/` directory

## Using the Predictor

```python
from predictor import DementiaPredictor

predictor = DementiaPredictor()

features = {
    'alpha_power': 0.12,
    'beta_power': 0.08,
    'theta_power': 0.15,
    'delta_power': 0.10,
    'entropy': 1.43,
    'mobility': 0.91,
    'complexity': 1.2,
    'variance': 45.3
}

result = predictor.predict(features)
print(result)  # {'risk': 0.35, 'state': 'mild', 'model_version': '0.1'}
```

## Model Performance

Current rule-based model is a placeholder. Train with real labeled EEG data for production use.
