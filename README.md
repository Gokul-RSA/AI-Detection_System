# SentinelNet: AI-Powered Network Intrusion Detection System

SentinelNet is a real-time network security monitoring system that leverages Machine Learning (Supervised Random Forest Classifier & Unsupervised Isolation Forest) to analyze network traffic patterns, detect potential network intrusions, and flag anomalies.

---

## 🚀 Features

* **Interactive Threat Dashboard:** Real-time data streams displaying threat confidence scores, recent network incidents, and key security statistics.
* **Supervised Classifier:** Classifies packets as either "Normal" or "Intrusion" using a binary Random Forest model trained on the NSL-KDD dataset.
* **Unsupervised Anomaly Detector:** Utilizes an Isolation Forest model to detect outliers and potential zero-day threats in network flows.
* **Live Flow Simulation:** Multi-threaded simulator that samples from test sets, adds synthetic noise, and streams live network connections to the interface.
* **Asynchronous Re-training:** Full-pipeline execution triggered directly from the web interface to reprocess, re-engineer features, and train the ML models.
* **Disk Logging:** Logs high-priority network threats locally to `alerts.log` for audit trails.

---

## 🛠️ Technology Stack

### Frontend
* **React** (v18.2) & **Vite** (v4.4)
* **Recharts** (v2.7) for real-time threat activity visualization
* **Framer Motion** (v10.15) for smooth UI transitions
* **Lucide React** (v0.26) for vector icons
* **Vanilla CSS** (`index.css`) with utility classes and glassmorphism styling

### Backend
* **FastAPI** (Python Web Framework)
* **Uvicorn** (ASGI Web Server)
* **Pandas** & **NumPy** for data frame manipulation
* **Joblib** for model and scaler persistence

### Machine Learning
* **Scikit-learn** for pipeline generation, scaling, and classification algorithms
* **RobustScaler** & **OneHotEncoder** for numerical and categorical preprocessing
* **SelectFromModel** (Random Forest) for feature selection
* **NSL-KDD Dataset** (benchmark dataset for cyber-security intrusion evaluation)

---

## 📂 Project Structure

```text
├── backend/
│   ├── 02_data_preprocessing.py                 # Loads raw NSL-KDD data
│   ├── 03_feature_engineering.py               # Implements scalers, encoders, and selects features
│   ├── 04_model_training_supervised.py         # Trains Random Forest binary classifier
│   ├── 05_anomaly_detection_unsupervised.py     # Trains Isolation Forest anomaly detector
│   ├── 06_model_evaluation.py                  # Evaluates model performance on the test dataset
│   └── main.py                                 # FastAPI application and live simulation worker
├── frontend/
│   ├── src/
│   │   ├── App.jsx                             # React Dashboard Component
│   │   ├── index.css                           # Core styling rules and layout utilities
│   │   └── main.jsx                            # React bootstrap file
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── KDDTrain+.txt                           # Raw NSL-KDD training file (Excluded from git)
│   ├── KDDTest+.txt                            # Raw NSL-KDD testing file (Excluded from git)
│   └── test_selected.csv                       # Extracted seed packet records for simulation
├── models/
│   ├── preprocessing_engine.joblib             # Saved sklearn preprocessing pipeline
│   ├── rf_model.pkl                            # Saved Random Forest classifier model
│   └── anomaly_detector.pkl                    # Saved Isolation Forest anomaly detector
├── alerts.log                                  # Saved logs for detected intrusions
└── README.md
```

---

## 📥 Installation & Setup

### 1. Pre-requisites
* Python 3.8+
* Node.js v16+
* npm

### 2. Python Backend Setup
Run the following commands in the project root directory:

```powershell
# Install the required Python libraries
pip install fastapi uvicorn pandas numpy scikit-learn joblib

# Run the FastAPI server
python backend/main.py
```
The backend API server will start running on **`http://localhost:8000`**.

### 3. Frontend Setup
Open a separate terminal window, navigate to the `frontend` folder, and execute:

```powershell
# Navigate into the frontend folder
cd frontend

# Install package dependencies
npm install

# Start Vite developer server
npm run dev
```
The dashboard interface will start running on **`http://localhost:5173`**.

---

## 📈 ML Pipeline Execution

If you wish to re-train the models from scratch using the raw NSL-KDD files in `data/`, you can click **"Re-Train AI"** on the dashboard header, or run the scripts sequentially in the backend folder:

```powershell
python backend/02_data_preprocessing.py
python backend/03_feature_engineering.py
python backend/04_model_training_supervised.py
python backend/05_anomaly_detection_unsupervised.py
python backend/06_model_evaluation.py
```
