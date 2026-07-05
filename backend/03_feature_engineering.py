import os
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import RobustScaler, OneHotEncoder, FunctionTransformer
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

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
save_path = os.path.join(MODEL_DIR, 'preprocessing_engine.joblib')

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
    print("--- Starting Feature Engineering Pipeline ---")
    
    # Load training data
    df_train = pd.read_csv(train_path, header=None, names=COL_NAMES)
    
    # Map attack labels to attack classes
    attack_mapping = {
        'normal': 'normal',
        'back': 'DoS', 'land': 'DoS', 'neptune': 'DoS', 'pod': 'DoS', 'smurf': 'DoS', 'teardrop': 'DoS',
        'satan': 'Probe', 'ipsweep': 'Probe', 'nmap': 'Probe', 'portsweep': 'Probe',
        'guess_passwd': 'R2L', 'ftp_write': 'R2L', 'imap': 'R2L', 'warezmaster': 'R2L', 'warezclient': 'R2L',
        'buffer_overflow': 'U2R', 'loadmodule': 'U2R', 'perl': 'U2R', 'rootkit': 'U2R'
    }
    df_train['attack_class'] = df_train['label'].map(lambda x: attack_mapping.get(x, 'other'))
    
    raw_categorical = ['protocol_type', 'service', 'flag']
    raw_binary = ['land', 'logged_in', 'is_host_login', 'is_guest_login']
    metadata_cols = ['label', 'difficulty_level', 'attack_class']
    raw_numerical = [col for col in df_train.columns if col not in raw_categorical + raw_binary + metadata_cols]
    
    # Preprocessor
    num_transformer = Pipeline([
        ('impute', SimpleImputer(strategy='median')),
        ('log',    FunctionTransformer(np.log1p)),
        ('scale',  RobustScaler())
    ])
    
    cat_transformer = Pipeline([
        ('impute', SimpleImputer(strategy='most_frequent')),
        ('ohe',    OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])
    
    preprocessor = ColumnTransformer(transformers=[
        ('num', num_transformer, raw_numerical),
        ('cat', cat_transformer, raw_categorical),
        ('bin', SimpleImputer(strategy='most_frequent'), raw_binary)
    ])
    
    sentinel_prep_engine = Pipeline([
        ('engineering', FunctionTransformer(sentinel_engineer_features)),
        ('preprocessor', preprocessor),
        ('selection',   SelectFromModel(
            RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1),
            threshold='median'))
    ])
    
    X_train_raw = df_train[raw_numerical + raw_categorical + raw_binary]
    le = LabelEncoder()
    y_train_raw = le.fit_transform(df_train['attack_class'])
    
    print("Fitting feature selector and scaler pipeline...")
    sentinel_prep_engine.fit(X_train_raw, y_train_raw)
    
    # Save the pipeline
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(sentinel_prep_engine, save_path)
    print(f"DONE: Preprocessing pipeline fitted and saved successfully to: {save_path}")

if __name__ == "__main__":
    main()
