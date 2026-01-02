"""Comprehensive test script to send various types of transactions to Kafka."""

import time
import random
from src.kafka.producer import TransactionProducer
from src.utils import setup_logger

logger = setup_logger(__name__)


def generate_normal_transaction(transaction_id: str) -> dict:
    """Generate a normal transaction with typical feature values."""
    return {
        "transaction_id": transaction_id,
        "features": {
            "Time": random.uniform(0, 172792),
            "V1": random.uniform(-3, 3),
            "V2": random.uniform(-3, 3),
            "V3": random.uniform(-3, 3),
            "V4": random.uniform(-3, 3),
            "V5": random.uniform(-3, 3),
            "V6": random.uniform(-3, 3),
            "V7": random.uniform(-3, 3),
            "V8": random.uniform(-3, 3),
            "V9": random.uniform(-3, 3),
            "V10": random.uniform(-3, 3),
            "V11": random.uniform(-3, 3),
            "V12": random.uniform(-3, 3),
            "V13": random.uniform(-3, 3),
            "V14": random.uniform(-3, 3),
            "V15": random.uniform(-3, 3),
            "V16": random.uniform(-3, 3),
            "V17": random.uniform(-3, 3),
            "V18": random.uniform(-3, 3),
            "V19": random.uniform(-3, 3),
            "V20": random.uniform(-3, 3),
            "V21": random.uniform(-3, 3),
            "V22": random.uniform(-3, 3),
            "V23": random.uniform(-3, 3),
            "V24": random.uniform(-3, 3),
            "V25": random.uniform(-3, 3),
            "V26": random.uniform(-3, 3),
            "V27": random.uniform(-3, 3),
            "V28": random.uniform(-3, 3),
            "Amount": random.uniform(1, 1000),
        }
    }


def generate_suspicious_transaction(transaction_id: str) -> dict:
    """Generate a suspicious transaction with unusual feature values (more likely fraud)."""
    # Features with extreme values that might indicate fraud
    return {
        "transaction_id": transaction_id,
        "features": {
            "Time": random.uniform(0, 172792),
            "V1": random.uniform(2, 5),  # Higher positive values
            "V2": random.uniform(-5, -2),  # Lower negative values
            "V3": random.uniform(3, 6),
            "V4": random.uniform(-6, -3),
            "V5": random.uniform(2, 5),
            "V6": random.uniform(-5, -2),
            "V7": random.uniform(2, 5),
            "V8": random.uniform(-5, -2),
            "V9": random.uniform(2, 4),
            "V10": random.uniform(-4, -2),
            "V11": random.uniform(3, 6),
            "V12": random.uniform(-6, -3),
            "V13": random.uniform(-4, -2),
            "V14": random.uniform(-7, -4),  # Very negative (common in fraud)
            "V15": random.uniform(2, 4),
            "V16": random.uniform(-3, -1),
            "V17": random.uniform(-2, 0),
            "V18": random.uniform(0, 2),
            "V19": random.uniform(1, 3),
            "V20": random.uniform(-2, 0),
            "V21": random.uniform(0, 1),
            "V22": random.uniform(0, 2),
            "V23": random.uniform(-2, 0),
            "V24": random.uniform(0, 1),
            "V25": random.uniform(0, 2),
            "V26": random.uniform(-2, 0),
            "V27": random.uniform(0, 2),
            "V28": random.uniform(-1, 0),
            "Amount": random.uniform(1000, 5000),  # Higher amounts
        }
    }


def generate_high_risk_transaction(transaction_id: str) -> dict:
    """Generate a high-risk transaction with very extreme values."""
    # Very extreme feature values (high fraud probability)
    return {
        "transaction_id": transaction_id,
        "features": {
            "Time": random.uniform(0, 172792),
            "V1": random.uniform(4, 7),
            "V2": random.uniform(-7, -4),
            "V3": random.uniform(5, 8),
            "V4": random.uniform(-8, -5),
            "V5": random.uniform(4, 7),
            "V6": random.uniform(-7, -4),
            "V7": random.uniform(4, 7),
            "V8": random.uniform(-7, -4),
            "V9": random.uniform(3, 6),
            "V10": random.uniform(-6, -3),
            "V11": random.uniform(5, 8),
            "V12": random.uniform(-8, -5),
            "V13": random.uniform(-6, -3),
            "V14": random.uniform(-10, -6),  # Very extreme negative
            "V15": random.uniform(4, 7),
            "V16": random.uniform(-5, -2),
            "V17": random.uniform(-3, -1),
            "V18": random.uniform(1, 3),
            "V19": random.uniform(2, 5),
            "V20": random.uniform(-3, -1),
            "V21": random.uniform(0, 2),
            "V22": random.uniform(1, 3),
            "V23": random.uniform(-3, -1),
            "V24": random.uniform(0, 2),
            "V25": random.uniform(1, 3),
            "V26": random.uniform(-3, -1),
            "V27": random.uniform(1, 3),
            "V28": random.uniform(-2, 0),
            "Amount": random.uniform(5000, 10000),  # Very high amount
        }
    }


def main():
    """Main function to send comprehensive test transactions."""
    logger.info("="*80)
    logger.info("Starting Comprehensive Transaction Testing")
    logger.info("="*80)
    
    try:
        producer = TransactionProducer()
        
        # Test 1: Send 5 normal transactions
        logger.info("\n[TEST 1] Sending 5 normal transactions...")
        for i in range(1, 6):
            tx = generate_normal_transaction(f"normal_txn_{i:03d}")
            producer.send_transaction(tx["transaction_id"], tx["features"])
            logger.info(f"  ✓ Sent: {tx['transaction_id']}")
            time.sleep(0.5)
        
        time.sleep(2)  # Wait for processing
        
        # Test 2: Send 3 suspicious transactions
        logger.info("\n[TEST 2] Sending 3 suspicious transactions...")
        for i in range(1, 4):
            tx = generate_suspicious_transaction(f"suspicious_txn_{i:03d}")
            producer.send_transaction(tx["transaction_id"], tx["features"])
            logger.info(f"  ✓ Sent: {tx['transaction_id']}")
            time.sleep(0.5)
        
        time.sleep(2)
        
        # Test 3: Send 2 high-risk transactions
        logger.info("\n[TEST 3] Sending 2 high-risk transactions...")
        for i in range(1, 3):
            tx = generate_high_risk_transaction(f"highrisk_txn_{i:03d}")
            producer.send_transaction(tx["transaction_id"], tx["features"])
            logger.info(f"  ✓ Sent: {tx['transaction_id']}")
            time.sleep(0.5)
        
        time.sleep(2)
        
        # Test 4: Send a mix in rapid succession
        logger.info("\n[TEST 4] Sending mixed transactions in rapid succession...")
        transactions = [
            ("normal_mix_001", generate_normal_transaction),
            ("suspicious_mix_001", generate_suspicious_transaction),
            ("normal_mix_002", generate_normal_transaction),
            ("highrisk_mix_001", generate_high_risk_transaction),
            ("normal_mix_003", generate_normal_transaction),
        ]
        
        for tx_id, generator in transactions:
            tx = generator(tx_id)
            producer.send_transaction(tx["transaction_id"], tx["features"])
            logger.info(f"  ✓ Sent: {tx['transaction_id']}")
            time.sleep(0.3)
        
        producer.close()
        
        logger.info("\n" + "="*80)
        logger.info("All test transactions sent successfully!")
        logger.info("="*80)
        logger.info("\nNext steps:")
        logger.info("1. Check your consumer terminal to see transactions being processed")
        logger.info("2. Run: python view_scored_results.py --num 20")
        logger.info("   to view the scored results")
    
    except Exception as e:
        logger.error(f"Error sending transactions: {str(e)}")
        raise


if __name__ == "__main__":
    main()

