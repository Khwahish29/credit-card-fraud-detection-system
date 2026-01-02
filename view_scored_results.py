"""Script to view scored transaction results from Kafka."""

import json
from kafka import KafkaConsumer
from src.config import KafkaConfig
from src.utils import setup_logger

logger = setup_logger(__name__)


def view_scored_results(num_messages: int = 10):
    """
    View scored transaction results from the transactions_scored topic.
    
    Args:
        num_messages: Number of messages to retrieve.
    """
    config = KafkaConfig()
    
    logger.info(f"Connecting to Kafka topic: {config.TOPIC_SCORED}")
    
    consumer = KafkaConsumer(
        config.TOPIC_SCORED,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000,  # 5 second timeout
    )
    
    logger.info(f"Retrieving up to {num_messages} scored transactions...")
    print("\n" + "="*80)
    print("SCORED TRANSACTION RESULTS")
    print("="*80 + "\n")
    
    message_count = 0
    for message in consumer:
        message_count += 1
        data = message.value
        
        transaction_id = data.get("transaction_id", "unknown")
        features = data.get("features", {})
        
        fraud_prob = features.get("fraud_probability", 0.0)
        is_fraud = features.get("is_fraud", False)
        threshold = features.get("threshold", 0.5)
        
        print(f"Transaction ID: {transaction_id}")
        print(f"  Fraud Probability: {fraud_prob:.4f} ({fraud_prob*100:.2f}%)")
        print(f"  Is Fraud: {is_fraud}")
        print(f"  Threshold: {threshold}")
        print("-" * 80)
        
        if message_count >= num_messages:
            break
    
    consumer.close()
    
    if message_count == 0:
        print("No scored transactions found in the topic.")
        print("Make sure the consumer has processed some transactions.")
    else:
        print(f"\nRetrieved {message_count} scored transaction(s).")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="View scored transaction results from Kafka"
    )
    parser.add_argument(
        "--num",
        type=int,
        default=10,
        help="Number of messages to retrieve (default: 10)",
    )
    
    args = parser.parse_args()
    view_scored_results(args.num)

