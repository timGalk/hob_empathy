import numpy as np
import pandas as pd
import joblib
from scipy.signal import welch
from scipy.stats import entropy
from xgboost import XGBClassifier

# =========================
# CONFIG
# =========================
MODEL_PATH = "absence_detector_model.pkl"
SCALER_PATH = "absence_detector_scaler.pkl"
WINDOW_SIZE = 256  # same as training

EEG_COLS = ["F4","C4","P4","O2","O1","F3","C3","P3"]
ACC_COLS = ["AccZ","AccY","AccX"]

# =========================
# FEATURE FUNCTIONS
# =========================

def bandpower(x, fs=250):
    bands = {
        "delta": (0.5, 4),
        "theta": (4, 8),
        "alpha": (8, 12),
        "beta": (12, 30),
        "gamma": (30, 45),
    }
    freqs, psd = welch(x, fs=fs, nperseg=256)
    return [np.trapz(psd[(freqs>=low) & (freqs<=high)], freqs[(freqs>=low) & (freqs<=high)]) for low, high in bands.values()]

def spectral_entropy(x, fs=250):
    freqs, psd = welch(x, fs=fs, nperseg=256)
    psd_norm = psd / np.sum(psd)
    return entropy(psd_norm)

def hjorth_params(x):
    dx = np.diff(x)
    ddx = np.diff(dx)
    var_x = np.var(x)
    var_dx = np.var(dx)
    var_ddx = np.var(ddx)
    activity = var_x
    mobility = np.sqrt(var_dx / var_x) if var_x > 0 else 0
    complexity = (np.sqrt(var_ddx / var_dx)/mobility) if var_dx >0 and mobility>0 else 0
    return [activity, mobility, complexity]

def extract_features(eeg_win, acc_win):
    feats = []
    for ch in range(eeg_win.shape[1]):
        x = eeg_win[:, ch]
        feats += [x.mean(), x.std(), np.var(x), np.sum(x**2)]
        feats += bandpower(x)
        feats.append(spectral_entropy(x))
        feats += hjorth_params(x)
    for ch in range(acc_win.shape[1]):
        x = acc_win[:, ch]
        feats += [x.mean(), x.std(), np.var(x)]
    return feats

# =========================
# MOTION ARTIFACT REMOVAL
# =========================

def remove_motion_artifacts(X_eeg, X_acc):
    X_eeg_clean = np.zeros_like(X_eeg)
    for ch in range(X_eeg.shape[1]):
        eeg_ch = X_eeg[:, ch].reshape(-1,1)
        beta = np.linalg.lstsq(X_acc, eeg_ch, rcond=None)[0]
        X_eeg_clean[:, ch] = (eeg_ch - X_acc.dot(beta)).ravel()
    return X_eeg_clean

# =========================
# LOAD MODEL & SCALER
# =========================

clf = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# =========================
# MAIN FUNCTION
# =========================

def classify_csv(file_path):
    df = pd.read_csv(file_path, comment="#")

    X_eeg = df[EEG_COLS].values
    X_acc = df[ACC_COLS].values

    X_eeg_clean = remove_motion_artifacts(X_eeg, X_acc)

    feature_list = []
    for start in range(0, len(df) - WINDOW_SIZE, WINDOW_SIZE):
        end = start + WINDOW_SIZE
        eeg_win = X_eeg_clean[start:end]
        acc_win = X_acc[start:end]
        feature_list.append(extract_features(eeg_win, acc_win))

    X_features = np.array(feature_list)
    X_scaled = scaler.transform(X_features)
    y_pred = clf.predict(X_scaled)

    return y_pred  # returns 0/1 for each window

# =========================
# USAGE EXAMPLE
# =========================

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python classify_single_csv.py <csv_file>")
        sys.exit(1)

    csv_file = sys.argv[1]
    predictions = classify_csv(csv_file)
    print("Predictions per window:")
    print(predictions)
