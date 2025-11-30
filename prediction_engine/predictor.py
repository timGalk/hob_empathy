import numpy as np
import pandas as pd
import glob
import os
import joblib
from scipy.signal import welch
from scipy.stats import entropy
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

MODEL_PATH = "absence_detector_model.pkl"
SCALER_PATH = "absence_detector_scaler.pkl"
JSON_MODEL_PATH = "absence_detector_model.json"
all_files = glob.glob("/home/dmin/PycharmProjects/HeroesOfTheBrain/eeg_recordings/*.csv")


"""
===========================
    READ ME 
- в моделе уже есть градиент 
- в модели есть обучение с прошлой лучше версии 
- all_files єто путь ко всем данньім
- csv файл должен иметь колонки 
    F4, C4, P4, O2, O1, F3, C3, P3, AccZ, AccY, AccX, "Obsense"
===========================
"""


def bandpower(x, fs=250):
    bands = {
        "delta": (0.5, 4),
        "theta": (4, 8),
        "alpha": (8, 12),
        "beta": (12, 30),
        "gamma": (30, 45),
    }
    freqs, psd = welch(x, fs=fs, nperseg=256)
    return [np.trapz(psd[(freqs >= low) & (freqs <= high)], freqs[(freqs >= low) & (freqs <= high)])
            for low, high in bands.values()]


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
    complexity = (np.sqrt(var_ddx / var_dx) / mobility) if var_dx > 0 and mobility > 0 else 0
    return [activity, mobility, complexity]


# ===========================
#    FEATURE EXTRACTION
# ===========================

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


# ===========================
#    LOAD ALL DATA FILES
# ===========================

features = []
labels = []

window_size = 256

for file in all_files:
    df = pd.read_csv(file, comment="#")

    eeg_cols = ["F4","C4","P4","O2","O1","F3","C3","P3"]
    acc_cols = ["AccZ","AccY","AccX"]
    target = "Obsense"

    X_eeg = df[eeg_cols].values
    X_acc = df[acc_cols].values
    y = df[target].values

    for start in range(0, len(df) - window_size, window_size):
        end = start + window_size
        features.append(extract_features(X_eeg[start:end], X_acc[start:end]))
        labels.append(int(np.mean(y[start:end]) > 0.5))

X = np.array(features)
y = np.array(labels)

print("Dataset shape:", X.shape)


# ===========================
#    SCALING
# ===========================

if os.path.exists(SCALER_PATH):
    scaler = joblib.load(SCALER_PATH)
    print("Loaded existing scaler.")
else:
    scaler = StandardScaler()
    print("Created new scaler.")

X_scaled = scaler.fit_transform(X)


# ===========================
#    TRAIN / CONTINUE TRAINING
# ===========================

# train/test split for reporting only:
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, shuffle=True
)

# Create model
clf = XGBClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=5,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="logloss",
    scale_pos_weight=(sum(y==0)/sum(y==1))
)

# Load previous weights IF AVAILABLE
if os.path.exists(JSON_MODEL_PATH):
    print("Loading previous model weights...")
    clf.load_model(JSON_MODEL_PATH)
else:
    print("Starting fresh model.")

# Continue training
clf.fit(
    X_train, y_train,
    xgb_model=JSON_MODEL_PATH if os.path.exists(JSON_MODEL_PATH) else None
)

# ===========================
#    EVALUATE
# ===========================

y_pred = clf.predict(X_test)
print("\n=== FINAL REPORT ===")
print(classification_report(y_test, y_pred))


# ===========================
#    SAVE UPDATED MODEL
# ===========================

joblib.dump(clf, MODEL_PATH)
joblib.dump(scaler, SCALER_PATH)
clf.save_model(JSON_MODEL_PATH)

print("\nModel updated and saved:")
print(" - absence_detector_model.pkl")
print(" - absence_detector_model.json")
print(" - absence_detector_scaler.pkl")