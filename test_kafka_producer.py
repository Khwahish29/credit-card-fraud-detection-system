"""Simple test script to send sample transactions to Kafka."""

import json
import time
from src.kafka.producer import TransactionProducer
from src.utils import setup_logger

logger = setup_logger(__name__)


def create_sample_transaction(transaction_id: str, is_likely_fraud: bool = False) -> dict:
    """
    Create a sample transaction with features.
    
    Args:
        transaction_id: Unique transaction ID.
        is_likely_fraud: If True, creates features more likely to be fraud.
    
    Returns:
        Dictionary with transaction_id and features.
    """
    if is_likely_fraud:
        # Sample features that might indicate fraud (higher absolute values)
        features = {
            "Time": 0.0,
            "V1": 2.0, "V2": -1.5, "V3": 3.0, "V4": -2.0,
            "V5": 1.5, "V6": -2.5, "V7": 2.0, "V8": -1.0,
            "V9": 1.0, "V10": -1.5, "V11": 2.5, "V12": -2.0,
            "V13": -1.0, "V14": -3.0, "V15": 1.5, "V16": -1.0,
            "V17": -0.5, "V18": 0.5, "V19": 1.0, "V20": -0.5,
            "V21": 0.0, "V22": 0.5, "V23": -0.5, "V24": 0.0,
            "V25": 0.5, "V26": -0.5, "V27": 0.5, "V28": -0.1,
            "Amount": 2000.0  # Higher amount
        }
    else:
        # Normal transaction features
        features = {
            "Time": 0.0,
            "V1": -1.359807134, "V2": -0.072781173, "V3": 2.536346738,
            "V4": 1.378155224, "V5": -0.338261777, "V6": 0.462388125,
            "V7": 0.239598554, "V8": 0.098697901, "V9": 0.363787,
            "V10": 0.090794, "V11": -0.551600, "V12": -0.617801,
            "V13": -0.991390, "V14": -0.311169, "V15": 1.468177,
            "V16": -0.470401, "V17": 0.207971, "V18": 0.025791,
            "V19": 0.403993, "V20": 0.251412, "V21": -0.018307,
            "V22": 0.277838, "V23": -0.110474, "V24": 0.066928,
            "V25": 0.128539, "V26": -0.189115, "V27": 0.133558,
            "V28": -0.021053, "Amount": 149.62
        }
    
    return {
        "transaction_id": transaction_id,
        "features": features,
    }


def main():
    """Main function to send test transactions to Kafka."""
    logger.info("Starting Kafka producer test...")
    
    try:
        producer = TransactionProducer()
        
        # Send a few sample transactions
        logger.info("Sending sample transactions to Kafka...")
        
        # Send normal transaction
        normal_tx = create_sample_transaction("test_txn_001", is_likely_fraud=False)
        producer.send_transaction(
            transaction_id=normal_tx["transaction_id"],
            features=normal_tx["features"],
        )
        logger.info(f"Sent transaction: {normal_tx['transaction_id']}")
        
        time.sleep(1)
        
        # Send potentially fraudulent transaction
        fraud_tx = create_sample_transaction("test_txn_002", is_likely_fraud=True)
        producer.send_transaction(
            transaction_id=fraud_tx["transaction_id"],
            features=fraud_tx["features"],
        )
        logger.info(f"Sent transaction: {fraud_tx['transaction_id']}")
        
        time.sleep(1)
        
        # Send another normal transaction
        normal_tx2 = create_sample_transaction("test_txn_003", is_likely_fraud=False)
        producer.send_transaction(
            transaction_id=normal_tx2["transaction_id"],
            features=normal_tx2["features"],
        )
        logger.info(f"Sent transaction: {normal_tx2['transaction_id']}")
        
        producer.close()
        logger.info("Test transactions sent successfully!")
        logger.info("You can now run the consumer to process these transactions.")
    
    except Exception as e:
        logger.error(f"Error sending transactions: {str(e)}")
        logger.error("Make sure Kafka is running (docker-compose up)")
        raise


if __name__ == "__main__":
    main()

