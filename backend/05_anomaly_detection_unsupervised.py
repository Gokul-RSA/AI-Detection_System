import os
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

# Define Column Names for NSL-KDD
COL_NAMES = ["duration","protocol_type","service","flag","src_bytes",
    "dst_bytes","land","wrong_fragment","urgent","hot","num_failed_logins",
    "logged_in","num_compromised","root_shell","su_attempted","num_root",
    "num_file_creations","num_shells","num_access_files","num_outbound_cmds",
    "is_host_login","is_guest_login","count","srv_count","serror_rate",
    "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate",
    "diff_srv_rate","srv_diff_host_rate","dst_host_count","dst_host_srv_count",
    "dst_host_same_srv_rate","dst_host_diff_srv_rate","dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate","dst_host_serror_rate","dst_host_srv_serror_rate",
    "dst_host_rerror_rate","dst_host_srv_rerror_rate","label", "difficulty_level"]

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
train_path = os.path.join(DATA_DIR, 'KDDTrain+.txt')
prep_engine_path = os.path.join(MODEL_DIR, 'preprocessing_engine.joblib')
anomaly_model_save_path = os.path.join(MODEL_DIR, 'anomaly_detector.pkl')

# Define custom function (required for joblib deserialization)
def sentinel_engineer_features(X):
    """Calculates domain-specific network features."""
    X_out = X.copy()
    # Packet Rate (Avoid div by zero)
    X_out['packet_rate'] = X_out['count'] / (X_out['duration'] + 1e-5)
    # Byte Ratio
    total_bytes = X_out['src_bytes'] + X_out['dst_bytes']
    X_out['src_bytes_ratio'] = X_out['src_bytes'] / (total_bytes + 1e-5)
    # Service Interaction
    X_out['srv_interaction'] = X_out['same_srv_rate'] * X_out['dst_host_same_srv_rate']
    return X_out

def main():
    print("--- Starting Unsupervised Anomaly Detection Training ---")
    
    # 1. Load preprocessor
    if not os.path.exists(prep_engine_path):
        print(f"Error: Preprocessing engine not found at {prep_engine_path}")
        exit(1)
        
    print("Loading preprocessing pipeline...")
    prep_engine = joblib.load(prep_engine_path)
    
    # 2. Load training data
    print("Loading raw training data...")
    df_train = pd.read_csv(train_path, header=None, names=COL_NAMES)
    
    raw_categorical = ['protocol_type', 'service', 'flag']
    raw_binary = ['land', 'logged_in', 'is_host_login', 'is_guest_login']
    metadata_cols = ['label', 'difficulty_level']
    raw_features_cols = [col for col in df_train.columns if col not in metadata_cols]
    
    X_train_raw = df_train[raw_features_cols]
    
    # Preprocess
    print("Preprocessing training features...")
    X_signal = prep_engine.transform(X_train_raw)
    
    # 3. Train Isolation Forest
    print("Training Isolation Forest Anomaly Detector...")
    iso_forest = IsolationForest(contamination=0.1, random_state=42, n_jobs=-1)
    iso_forest.fit(X_signal)
    
    # Save model
    joblib.dump(iso_forest, anomaly_model_save_path)
    print(f"DONE: Unsupervised anomaly detector saved to: {anomaly_model_save_path}")
    
    # Predict anomalies
    predictions = iso_forest.predict(X_signal)
    # Isolation forest outputs 1 for inliers, -1 for outliers
    outliers_count = (predictions == -1).sum()
    inliers_count = (predictions == 1).sum()
    print(f"   Inliers detected: {inliers_count}")
    print(f"   Outliers (Anomalies) detected: {outliers_count}")

if __name__ == "__main__":
    main()
