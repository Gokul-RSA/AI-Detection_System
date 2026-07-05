import os
import sys
import subprocess
import joblib
import pandas as pd
import numpy as np
import time
import random
import threading
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="SentinelNet AI API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Define custom function required for joblib deserialization ---
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

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENTINEL_SRC = os.path.join(BASE_DIR, 'backend')
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
LOG_FILE = os.path.join(BASE_DIR, 'alerts.log')

# Global state for simulation
class SimulationState:
    running = False
    thread = None
    recent_logs = []
    status = "Idle"
    stats = {
        "packets_processed": 0,
        "intrusions_detected": 0,
        "last_confidence": 0.0,
        "status": "Idle"
    }

sim_state = SimulationState()

def run_script(script_name):
    script_path = os.path.join(SENTINEL_SRC, script_name)
    try:
        subprocess.run([sys.executable, script_path], check=True)
        return True
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False

def simulation_worker():
    global sim_state
    sim_state.running = True
    sim_state.status = "Monitoring..."
    
    try:
        # Load the model
        model_path = os.path.join(MODEL_DIR, 'rf_model.pkl')
        if not os.path.exists(model_path):
            sim_state.status = "Failed: Model not trained"
            sim_state.running = False
            return
            
        model = joblib.load(model_path)
        
        # Load seed data
        test_path = os.path.join(DATA_DIR, 'test_selected.csv')
        if not os.path.exists(test_path):
            sim_state.status = "Failed: Test data not found"
            sim_state.running = False
            return
            
        seed_data = pd.read_csv(test_path, nrows=100)
        feature_cols = [c for c in seed_data.columns if c != 'label']
        normal_seeds = seed_data[seed_data['label'] == 0].drop('label', axis=1)
        attack_seeds = seed_data[seed_data['label'] == 1].drop('label', axis=1)

        while sim_state.running:
            # Generate a "live" packet
            is_attack = random.random() < 0.20
            if is_attack and not attack_seeds.empty:
                base_packet = attack_seeds.sample(1).iloc[0].copy()
                packet_type = "Suspicious Packet"
            elif not normal_seeds.empty:
                base_packet = normal_seeds.sample(1).iloc[0].copy()
                packet_type = "User Activity"
            else:
                time.sleep(1)
                continue

            # Add some noise
            for col in feature_cols:
                if isinstance(base_packet[col], (int, float, np.integer, np.floating)) and base_packet[col] > 1:
                    base_packet[col] *= random.uniform(0.9, 1.1)

            live_packet_df = pd.DataFrame([base_packet], columns=feature_cols)
            prediction = int(model.predict(live_packet_df)[0])
            confidence = float(model.predict_proba(live_packet_df)[0].max())
            
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = {
                "timestamp": timestamp,
                "packet_type": packet_type,
                "prediction": "Intrusion" if prediction == 1 else "Normal",
                "confidence": round(confidence, 2),
                "is_alert": prediction == 1
            }
            
            # Update stats
            sim_state.stats["packets_processed"] += 1
            if prediction == 1:
                sim_state.stats["intrusions_detected"] += 1
            sim_state.stats["last_confidence"] = log_entry["confidence"]
            
            # Keep last 50 logs
            sim_state.recent_logs.insert(0, log_entry)
            sim_state.recent_logs = sim_state.recent_logs[:50]
            
            # Write to disk log if it's an intrusion
            if prediction == 1:
                with open(LOG_FILE, 'a') as f:
                    f.write(f"[{timestamp}] ALERT: {packet_type} detected with {confidence:.2f} confidence.\n")

            time.sleep(random.uniform(0.5, 2.0))
            
    except Exception as e:
        print(f"Simulation Error: {e}")
        sim_state.status = f"Error: {str(e)}"
    finally:
        sim_state.running = False

@app.get("/")
def read_root():
    return {"status": "SentinelNet AI API is live"}

@app.get("/stats")
def get_stats():
    # Try to load evaluation stats if they exist
    eval_stats = {}
    # (In a real app, I'd read the output of 06_model_evaluation.py)
    # For now, return the live stats
    return {
        "live": sim_state.stats,
        "is_running": sim_state.running,
        "system_status": sim_state.status
    }

@app.get("/logs")
def get_logs():
    return sim_state.recent_logs

@app.post("/simulation/start")
def start_simulation(background_tasks: BackgroundTasks):
    if not sim_state.running:
        sim_state.thread = threading.Thread(target=simulation_worker)
        sim_state.thread.daemon = True
        sim_state.thread.start()
        return {"message": "Simulation started"}
    return {"message": "Simulation already running"}

@app.post("/simulation/stop")
def stop_simulation():
    sim_state.running = False
    sim_state.status = "Stopped"
    return {"message": "Simulation stopping..."}

@app.post("/train")
def run_training(background_tasks: BackgroundTasks):
    # This runs the full pipeline
    def train_task():
        sim_state.status = "Training in progress..."
        scripts = [
            "02_data_preprocessing.py",
            "03_feature_engineering.py",
            "04_model_training_supervised.py",
            "05_anomaly_detection_unsupervised.py",
            "06_model_evaluation.py"
        ]
        for script in scripts:
            if not run_script(script):
                sim_state.status = f"Training failed at {script}"
                return
        sim_state.status = "Training complete"
        
    background_tasks.add_task(train_task)
    return {"message": "Training pipeline started in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
