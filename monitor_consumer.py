"""Monitor Kafka consumer in real-time to see transactions being processed."""

import json
import time
from kafka import KafkaConsumer
from src.config import KafkaConfig, ModelConfig
from src.utils import setup_logger

logger = setup_logger(__name__)


def monitor_consumer(num_messages: int = None, duration: int = None):
    """
    Monitor the transactions_scored topic to see real-time processing.
    
    Args:
        num_messages: Number of messages to process before stopping (None = unlimited).
        duration: Duration in seconds to monitor (None = unlimited).
    """
    config = KafkaConfig()
    
    logger.info("="*80)
    logger.info("MONITORING FRAUD DETECTION CONSUMER")
    logger.info("="*80)
    logger.info(f"Fraud Threshold: {ModelConfig.FRAUD_THRESHOLD*100:.1f}%")
    logger.info(f"Monitoring topic: {config.TOPIC_SCORED}")
    logger.info("Press Ctrl+C to stop monitoring\n")
    
    consumer = KafkaConsumer(
        config.TOPIC_SCORED,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',  # Only new messages
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=1000,
    )
    
    start_time = time.time()
    message_count = 0
    fraud_count = 0
    high_risk_count = 0
    
    try:
        while True:
            # Check duration limit
            if duration and (time.time() - start_time) > duration:
                logger.info(f"\nDuration limit ({duration}s) reached. Stopping...")
                break
            
            # Check message limit
            if num_messages and message_count >= num_messages:
                logger.info(f"\nMessage limit ({num_messages}) reached. Stopping...")
                break
            
            # Poll for messages
            message_pack = consumer.poll(timeout_ms=1000)
            
            for topic_partition, messages in message_pack.items():
                for message in messages:
                    message_count += 1
                    data = message.value
                    
                    transaction_id = data.get("transaction_id", "unknown")
                    features = data.get("features", {})
                    fraud_prob = features.get("fraud_probability", 0.0)
                    is_fraud = features.get("is_fraud", False)
                    threshold = features.get("threshold", ModelConfig.FRAUD_THRESHOLD)
                    
                    # Categorize risk
                    if fraud_prob >= 0.50:
                        risk_level = "🔴 VERY HIGH"
                        fraud_count += 1
                    elif fraud_prob >= 0.15:
                        risk_level = "🟠 HIGH"
                        high_risk_count += 1
                    elif fraud_prob >= 0.10:
                        risk_level = "🟡 MEDIUM"
                    elif fraud_prob >= 0.01:
                        risk_level = "🟢 LOW"
                    else:
                        risk_level = "✅ VERY LOW"
                    
                    # Print transaction info
                    status = "🚨 FRAUD" if is_fraud else "✓ Normal"
                    print(f"[{message_count:4d}] {transaction_id:30s} | "
                          f"Prob: {fraud_prob*100:6.2f}% | "
                          f"{risk_level:15s} | {status}")
                    
                    # Highlight fraud detections
                    if is_fraud:
                        print(f"      ⚠️  FRAUD DETECTED! Transaction flagged for review.")
            
            # Small delay to avoid CPU spinning
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        logger.info("\n\nMonitoring stopped by user.")
    
    finally:
        consumer.close()
        
        # Print summary
        print("\n" + "="*80)
        print("MONITORING SUMMARY")
        print("="*80)
        print(f"Total transactions processed: {message_count}")
        print(f"Fraud detections (≥{threshold*100:.0f}%): {fraud_count}")
        print(f"High risk (15-50%): {high_risk_count}")
        print(f"Monitoring duration: {time.time() - start_time:.1f} seconds")
        print("="*80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Monitor fraud detection consumer in real-time"
    )
    parser.add_argument(
        "--num",
        type=int,
        default=None,
        help="Number of messages to process (default: unlimited)",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Duration in seconds to monitor (default: unlimited)",
    )
    
    args = parser.parse_args()
    monitor_consumer(args.num, args.duration)

