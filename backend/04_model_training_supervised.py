import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

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
test_path = os.path.join(DATA_DIR, 'KDDTest+.txt')
prep_engine_path = os.path.join(MODEL_DIR, 'preprocessing_engine.joblib')
model_save_path = os.path.join(MODEL_DIR, 'rf_model.pkl')
test_selected_path = os.path.join(DATA_DIR, 'test_selected.csv')

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
    print("--- Starting Supervised Model Training ---")
    
    # 1. Load the fitted feature selection pipeline
    if not os.path.exists(prep_engine_path):
        print(f"Error: Preprocessing engine not found at {prep_engine_path}")
        print("Please run 03_feature_engineering.py first.")
        exit(1)
        
    print("Loading preprocessing pipeline...")
    prep_engine = joblib.load(prep_engine_path)
    
    # 2. Load training data
    print("Loading raw training data...")
    df_train = pd.read_csv(train_path, header=None, names=COL_NAMES)
    
    # Create binary labels: 0 for normal, 1 for any attack
    y_train = (df_train['label'] != 'normal').astype(int)
    
    # Get raw features (matching what prep_engine was trained on)
    raw_categorical = ['protocol_type', 'service', 'flag']
    raw_binary = ['land', 'logged_in', 'is_host_login', 'is_guest_login']
    metadata_cols = ['label', 'difficulty_level']
    raw_features_cols = [col for col in df_train.columns if col not in metadata_cols]
    
    X_train_raw = df_train[raw_features_cols]
    
    # 3. Create unified pipeline
    print("Training binary Random Forest Classifier...")
    classifier = RandomForestClassifier(
        max_depth=20, 
        min_samples_leaf=2, 
        n_estimators=50, 
        random_state=42, 
        n_jobs=-1, 
        class_weight='balanced'
    )
    
    rf_model = Pipeline([
        ('prep', prep_engine),
        ('classifier', classifier)
    ])
    
    rf_model.fit(X_train_raw, y_train)
    
    # Save unified model
    joblib.dump(rf_model, model_save_path)
    print(f"DONE: Unified model (pipeline + classifier) saved to: {model_save_path}")
    
    # 4. Generate data/test_selected.csv for simulation
    print("Generating simulated test seed data...")
    df_test = pd.read_csv(test_path, header=None, names=COL_NAMES)
    
    # Add target label to test data: 0 for normal, 1 for attack
    df_test['binary_label'] = (df_test['label'] != 'normal').astype(int)
    
    # Separate normal and attack
    df_normal = df_test[df_test['binary_label'] == 0]
    df_attack = df_test[df_test['binary_label'] == 1]
    
    # Sample 50 of each
    normal_sample = df_normal.sample(n=min(50, len(df_normal)), random_state=42)
    attack_sample = df_attack.sample(n=min(50, len(df_attack)), random_state=42)
    
    # Combine and shuffle
    test_seed = pd.concat([normal_sample, attack_sample]).sample(frac=1, random_state=42)
    
    # Keep raw features and the binary label column renamed to "label"
    sim_cols = raw_features_cols + ['binary_label']
    test_seed = test_seed[sim_cols].rename(columns={'binary_label': 'label'})
    
    test_seed.to_csv(test_selected_path, index=False)
    print(f"DONE: Simulation seeds saved to: {test_selected_path}")
    print(f"   ({len(normal_sample)} normal rows, {len(attack_sample)} attack rows)")

if __name__ == "__main__":
    main()
