# Financial Fraud Detection with Real-Time Monitoring

This project builds a **fraud detection system** for financial transactions using both **supervised** and **unsupervised** machine learning techniques, and extends it to **real-time fraud detection** using **Apache Kafka + Zookeeper**.  
A Streamlit dashboard is also provided for monitoring.

---

### DEMO
[Realtime Monitoring](https://drive.google.com/file/d/13tpnIn1iwtckN-lxdDku1Ge4zECQVCW8/view?usp=drive_link)
[Streamlit Demo](https://drive.google.com/file/d/1pc4rPFCGF2dMdvQxr7Vjzw77KmpzQ7wt/view?usp=drive_link)

## Features
- **Supervised Models** (trained + evaluated):
  - Logistic Regression
  - Random Forest
  - XGBoost (saved as `fraud_detection_model.pkl`)
- **Unsupervised Models**:
  - Isolation Forest
  - One-Class SVM
- **Evaluation Metrics**:
  - ROC-AUC, PR-AUC, Log Loss, Precision, Recall, F1
  - Confusion matrices, classification reports
  - CSV exports for supervised & unsupervised reports
- **Real-Time Streaming**:
  - Kafka Producer sends transactions (`test_frauds2.csv`)
  - Kafka Consumer consumes, predicts fraud, logs results (`latest_transactions.csv`)
- **Visualization**:
  - ROC & PR curves for supervised and unsupervised models
  - Streamlit dashboard for real-time monitoring

---

## Project Structure
Fraud-Detection-Model/
│
├── AquisitionPreProcessing/ # Data cleaning & feature engineering
├── Supervisedmodels/ # Logistic Regression, Random Forest, XGBoost
├── Unsupervisedmodels/ # Isolation Forest, One-Class SVM
├── Kafkaimplementationdocker/ # Kafka producer & consumer scripts
├── Streamlitdeployment/ # Streamlit app for dashboard
├── final_preprocessed_creditcard.csv
├── test_frauds2.csv # Test dataset for Kafka producer
├── fraud_detection_model.pkl # Best saved model (XGBoost)
└── README.md


## ⚙️ Setup & Installation

### 1. Clone Repository
bash
```git clone https://github.com/<your-username>/Fraud-Detection-Model.git```
```cd Fraud-Detection-Model```

### 2. Download Prerequisites
pandas
numpy
scikit-learn
xgboost
matplotlib
seaborn
joblib
streamlit
kafka-python

### 3. Start Zookeeper & Kafka
#### Start Zookeeper
```bin/zookeeper-server-start.sh config/zookeeper.properties```

#### Start Kafka broker
```bin/kafka-server-start.sh config/server.properties```

#### 4. Streamlit deployment
```streamlit run Streamlitdeployment/app.py```
