"""Test script using real transaction data from the dataset."""

import time
import pandas as pd
from src.kafka.producer import TransactionProducer
from src.config import RAW_DATA_DIR
from src.utils import setup_logger

logger = setup_logger(__name__)


def load_real_transactions(num_transactions: int = 10, include_fraud: bool = True):
    """
    Load real transactions from the dataset.
    
    Args:
        num_transactions: Number of transactions to load.
        include_fraud: Whether to include fraud transactions.
    
    Returns:
        List of transaction dictionaries.
    """
    from src.data.loader import load_data
    
    logger.info("Loading real transaction data from dataset...")
    df = load_data(file_name="creditcard.csv")
    
    # Filter based on fraud flag
    if include_fraud:
        # Get mix of fraud and non-fraud
        fraud_df = df[df["Class"] == 1].head(num_transactions // 2)
        normal_df = df[df["Class"] == 0].head(num_transactions - len(fraud_df))
        sample_df = pd.concat([fraud_df, normal_df]).sample(frac=1).reset_index(drop=True)
    else:
        sample_df = df[df["Class"] == 0].head(num_transactions)
    
    logger.info(f"Loaded {len(sample_df)} real transactions "
                f"({(sample_df['Class'] == 1).sum()} fraud, "
                f"{(sample_df['Class'] == 0).sum()} normal)")
    
    transactions = []
    feature_columns = [col for col in df.columns if col not in ["Class", "Time"]]
    
    for idx, row in sample_df.iterrows():
        transaction_id = f"real_txn_{idx:06d}_class{int(row['Class'])}"
        
        features = {col: float(row[col]) for col in feature_columns}
        
        transactions.append({
            "transaction_id": transaction_id,
            "features": features,
            "actual_class": int(row["Class"]),
        })
    
    return transactions


def main():
    """Main function to send real transactions to Kafka."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Send real transactions from dataset to Kafka"
    )
    parser.add_argument(
        "--num",
        type=int,
        default=20,
        help="Number of transactions to send (default: 20)",
    )
    parser.add_argument(
        "--no-fraud",
        action="store_true",
        help="Only send normal transactions (no fraud)",
    )
    
    args = parser.parse_args()
    
    logger.info("="*80)
    logger.info("Sending Real Transaction Data to Kafka")
    logger.info("="*80)
    
    try:
        # Load real transactions
        transactions = load_real_transactions(
            num_transactions=args.num,
            include_fraud=not args.no_fraud,
        )
        
        # Send to Kafka
        producer = TransactionProducer()
        
        logger.info(f"\nSending {len(transactions)} real transactions to Kafka...")
        
        fraud_count = 0
        normal_count = 0
        
        for i, txn in enumerate(transactions, 1):
            producer.send_transaction(txn["transaction_id"], txn["features"])
            
            if txn["actual_class"] == 1:
                fraud_count += 1
                logger.info(f"  [{i:3d}] ✓ Sent: {txn['transaction_id']} (ACTUAL FRAUD)")
            else:
                normal_count += 1
                logger.info(f"  [{i:3d}] ✓ Sent: {txn['transaction_id']} (normal)")
            
            if i % 5 == 0:
                time.sleep(0.5)  # Small delay every 5 transactions
        
        producer.close()
        
        logger.info("\n" + "="*80)
        logger.info("Real transactions sent successfully!")
        logger.info(f"  Normal transactions: {normal_count}")
        logger.info(f"  Fraud transactions: {fraud_count}")
        logger.info("="*80)
        logger.info("\nNext steps:")
        logger.info("1. Check your consumer terminal to see transactions being processed")
        logger.info("2. Run: python analyze_results.py --num 50")
        logger.info("   to see how the model performed on real data")
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise


if __name__ == "__main__":
    import time
    main()

