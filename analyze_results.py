"""Analyze and summarize scored transaction results."""

import json
from collections import defaultdict
from kafka import KafkaConsumer
from src.config import KafkaConfig
from src.utils import setup_logger

logger = setup_logger(__name__)


def analyze_scored_results(num_messages: int = 50):
    """Analyze scored transactions and provide summary statistics."""
    config = KafkaConfig()
    
    consumer = KafkaConsumer(
        config.TOPIC_SCORED,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000,
    )
    
    transactions = []
    message_count = 0
    
    for message in consumer:
        message_count += 1
        data = message.value
        transaction_id = data.get("transaction_id", "unknown")
        features = data.get("features", {})
        
        fraud_prob = features.get("fraud_probability", 0.0)
        is_fraud = features.get("is_fraud", False)
        
        transactions.append({
            "transaction_id": transaction_id,
            "fraud_probability": fraud_prob,
            "is_fraud": is_fraud,
        })
        
        if message_count >= num_messages:
            break
    
    consumer.close()
    
    if not transactions:
        print("No transactions found to analyze.")
        return
    
    # Calculate statistics
    fraud_probs = [t["fraud_probability"] for t in transactions]
    avg_prob = sum(fraud_probs) / len(fraud_probs)
    max_prob = max(fraud_probs)
    min_prob = min(fraud_probs)
    
    # Categorize by probability ranges
    low_risk = [t for t in transactions if t["fraud_probability"] < 0.01]  # < 1%
    medium_risk = [t for t in transactions if 0.01 <= t["fraud_probability"] < 0.10]  # 1-10%
    high_risk = [t for t in transactions if 0.10 <= t["fraud_probability"] < 0.50]  # 10-50%
    very_high_risk = [t for t in transactions if t["fraud_probability"] >= 0.50]  # >= 50%
    
    # Group by transaction type prefix
    type_groups = defaultdict(list)
    for t in transactions:
        tx_id = t["transaction_id"]
        if "_" in tx_id:
            tx_type = tx_id.split("_")[0]
            type_groups[tx_type].append(t)
    
    # Print analysis
    print("\n" + "="*80)
    print("TRANSACTION FRAUD DETECTION ANALYSIS")
    print("="*80)
    print(f"\nTotal Transactions Analyzed: {len(transactions)}")
    print(f"\nFraud Probability Statistics:")
    print(f"  Average: {avg_prob:.4f} ({avg_prob*100:.2f}%)")
    print(f"  Minimum: {min_prob:.4f} ({min_prob*100:.2f}%)")
    print(f"  Maximum: {max_prob:.4f} ({max_prob*100:.2f}%)")
    
    print(f"\nRisk Distribution:")
    print(f"  Low Risk (< 1%):        {len(low_risk):3d} transactions ({len(low_risk)/len(transactions)*100:.1f}%)")
    print(f"  Medium Risk (1-10%):    {len(medium_risk):3d} transactions ({len(medium_risk)/len(transactions)*100:.1f}%)")
    print(f"  High Risk (10-50%):     {len(high_risk):3d} transactions ({len(high_risk)/len(transactions)*100:.1f}%)")
    print(f"  Very High Risk (≥50%):  {len(very_high_risk):3d} transactions ({len(very_high_risk)/len(transactions)*100:.1f}%)")
    
    print(f"\nTransactions Classified as Fraud (≥50% threshold): {len(very_high_risk)}")
    
    # Show top risk transactions
    sorted_txns = sorted(transactions, key=lambda x: x["fraud_probability"], reverse=True)
    print(f"\nTop 10 Highest Risk Transactions:")
    print("-" * 80)
    for i, txn in enumerate(sorted_txns[:10], 1):
        print(f"{i:2d}. {txn['transaction_id']:25s} - {txn['fraud_probability']*100:6.2f}% "
              f"{'(FRAUD)' if txn['is_fraud'] else ''}")
    
    # Show breakdown by transaction type
    if type_groups:
        print(f"\nBreakdown by Transaction Type:")
        print("-" * 80)
        for tx_type, txns in sorted(type_groups.items()):
            avg_type_prob = sum(t["fraud_probability"] for t in txns) / len(txns)
            max_type_prob = max(t["fraud_probability"] for t in txns)
            print(f"  {tx_type:15s}: {len(txns):2d} transactions - "
                  f"Avg: {avg_type_prob*100:5.2f}%, Max: {max_type_prob*100:5.2f}%")
    
    print("\n" + "="*80)
    print("Analysis Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze scored transaction results"
    )
    parser.add_argument(
        "--num",
        type=int,
        default=50,
        help="Number of messages to analyze (default: 50)",
    )
    
    args = parser.parse_args()
    analyze_scored_results(args.num)

