# Credit Card Fraud Detection System

An end-to-end machine learning system for detecting credit card fraud using XGBoost, FastAPI, and Kafka.

## Features

- XGBoost model trained on imbalanced credit card fraud dataset
- Class imbalance handling using SMOTE and class weights
- Comprehensive evaluation metrics (Precision, Recall, F1, ROC-AUC, PR-AUC)
- FastAPI microservice with `/predict` endpoint
- Kafka integration for real-time transaction scoring
- Dockerized deployment with docker-compose

## Tech Stack

- Python 3.11
- pandas, scikit-learn, imbalanced-learn, xgboost
- FastAPI, uvicorn
- Kafka (kafka-python)
- Docker, docker-compose

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration module
│   ├── data/              # Data loading utilities
│   ├── models/            # Model training and evaluation
│   ├── api/               # FastAPI application
│   └── kafka/             # Kafka producer and consumer
├── data/
│   ├── raw/               # Raw datasets
│   └── processed/         # Processed datasets
├── models/                # Saved model artifacts
├── logs/                  # Application logs
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Setup

1. Create a virtual environment:
```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place your credit card fraud dataset in `data/raw/`

## Usage

### Training the Model

```bash
python -m src.models.train
```

### Running the API

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Running Kafka Consumer

To process transactions from Kafka and publish scored results:

```bash
python -m src.kafka.consumer_main
```

### Running with Docker Compose

```bash
docker-compose up -d
```

This will start:
- Zookeeper (port 2181)
- Kafka broker (port 9092)
- FastAPI service (port 8000)

To stop all services:
```bash
docker-compose down
```

To run the Kafka consumer separately (outside docker-compose):
```bash
python -m src.kafka.consumer_main
```

## API Endpoints

### POST /predict

Predict fraud probability for a transaction.

**Request Body:**
```json
{
  "transaction_id": "txn_123",
  "features": {
    "feature_1": 0.5,
    "feature_2": -1.2,
    ...
  }
}
```

**Response:**
```json
{
  "transaction_id": "txn_123",
  "fraud_probability": 0.85,
  "is_fraud": true
}
```

## License

MIT

