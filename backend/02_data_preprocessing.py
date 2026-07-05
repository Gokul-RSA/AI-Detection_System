import os
import pandas as pd

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
train_path = os.path.join(DATA_DIR, 'KDDTrain+.txt')
test_path = os.path.join(DATA_DIR, 'KDDTest+.txt')

def main():
    print("--- Starting Data Preprocessing Validation ---")
    
    if not os.path.exists(train_path):
        print(f"Error: Training file not found at {train_path}")
        exit(1)
        
    if not os.path.exists(test_path):
        print(f"Error: Test file not found at {test_path}")
        exit(1)
        
    print("Loading training data...")
    df_train = pd.read_csv(train_path, header=None, names=COL_NAMES)
    print(f"DONE: Training data loaded successfully: {df_train.shape[0]} connections, {df_train.shape[1]} columns.")
    
    print("Loading test data...")
    df_test = pd.read_csv(test_path, header=None, names=COL_NAMES)
    print(f"DONE: Test data loaded successfully: {df_test.shape[0]} connections, {df_test.shape[1]} columns.")
    
    # Simple check on class balance
    print("\nClass distribution in Training data:")
    print(df_train['label'].value_counts().head())
    
    print("\nData preprocessing check complete.")

if __name__ == "__main__":
    main()
