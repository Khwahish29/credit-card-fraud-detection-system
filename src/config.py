"""Configuration module for the Credit Card Fraud Detection System."""

import os
from pathlib import Path
from typing import Optional

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data paths
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Model artifacts path
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_FILE = MODELS_DIR / "fraud_detection_model.pkl"
PREPROCESSOR_FILE = MODELS_DIR / "preprocessor.pkl"

# Create directories if they don't exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Model training configuration
class ModelConfig:
    """Model training configuration."""
    
    # Random seed for reproducibility
    RANDOM_SEED: int = 42
    
    # Test size for train-test split
    TEST_SIZE: float = 0.2
    
    # Validation size (from training set)
    VAL_SIZE: float = 0.2
    
    # Fraud detection threshold (probability above which transaction is flagged as fraud)
    FRAUD_THRESHOLD: float = float(os.getenv("FRAUD_THRESHOLD", "0.15"))  # 15% default
    
    # XGBoost parameters
    XGB_PARAMS: dict = {
        "objective": "binary:logistic",
        "eval_metric": "aucpr",  # Precision-Recall AUC for imbalanced data
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "n_estimators": 100,
        "random_state": RANDOM_SEED,
        "scale_pos_weight": None,  # Will be calculated based on class distribution
    }
    
    # Early stopping
    EARLY_STOPPING_ROUNDS: int = 10
    
    # SMOTE configuration
    USE_SMOTE: bool = True
    SMOTE_K_NEIGHBORS: int = 5
    SMOTE_RANDOM_STATE: int = RANDOM_SEED


# Kafka configuration
class KafkaConfig:
    """Kafka configuration."""
    
    # Kafka broker
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    # Topics
    TOPIC_RAW: str = "transactions_raw"
    TOPIC_SCORED: str = "transactions_scored"
    
    # Consumer configuration
    CONSUMER_GROUP_ID: str = "fraud_detection_consumer"
    CONSUMER_AUTO_OFFSET_RESET: str = "earliest"
    CONSUMER_ENABLE_AUTO_COMMIT: bool = True
    
    # Producer configuration
    PRODUCER_ACKS: str = "all"
    PRODUCER_RETRIES: int = 3


# FastAPI configuration
class APIConfig:
    """FastAPI application configuration."""
    
    API_TITLE: str = "Credit Card Fraud Detection API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for credit card fraud detection using XGBoost"
    
    # Server configuration
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Model loading
    MODEL_PATH: Optional[Path] = MODEL_FILE
    PREPROCESSOR_PATH: Optional[Path] = PREPROCESSOR_FILE


# Logging configuration
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "fraud_detection.log"

