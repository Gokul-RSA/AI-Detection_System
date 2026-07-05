import os
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

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
test_path = os.path.join(DATA_DIR, 'KDDTest+.txt')
model_path = os.path.join(MODEL_DIR, 'rf_model.pkl')

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
    print("--- Starting Supervised Model Evaluation ---")
    
    # 1. Load trained model
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        exit(1)
        
    print("Loading unified Random Forest model...")
    model = joblib.load(model_path)
    
    # 2. Load test data
    print("Loading test dataset...")
    df_test = pd.read_csv(test_path, header=None, names=COL_NAMES)
    
    # Target binary labels
    y_test = (df_test['label'] != 'normal').astype(int)
    
    # Features
    raw_categorical = ['protocol_type', 'service', 'flag']
    raw_binary = ['land', 'logged_in', 'is_host_login', 'is_guest_login']
    metadata_cols = ['label', 'difficulty_level']
    raw_features_cols = [col for col in df_test.columns if col not in metadata_cols]
    
    X_test_raw = df_test[raw_features_cols]
    
    # 3. Evaluate
    print("Running predictions on test set...")
    y_pred = model.predict(X_test_raw)
    
    # Print metrics
    print("\n" + "="*20 + " CLASSIFICATION REPORT " + "="*20)
    print(classification_report(y_test, y_pred, target_names=["Normal (0)", "Intrusion (1)"]))
    
    print("="*20 + " CONFUSION MATRIX " + "="*20)
    print(confusion_matrix(y_test, y_pred))
    print("="*58)
    
    print("\nModel evaluation completed.")

if __name__ == "__main__":
    main()
