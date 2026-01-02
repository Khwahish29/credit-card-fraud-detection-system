"""Main script to run the Kafka consumer."""

import argparse
from pathlib import Path

from src.kafka.consumer import TransactionConsumer
from src.utils import setup_logger

logger = setup_logger(__name__)


def main() -> None:
    """Main function to run the consumer."""
    parser = argparse.ArgumentParser(
        description="Kafka consumer for fraud detection scoring"
    )
    parser.add_argument(
        "--bootstrap-servers",
        type=str,
        default=None,
        help="Kafka bootstrap servers (default: from config)",
    )
    parser.add_argument(
        "--input-topic",
        type=str,
        default=None,
        help="Input topic name (default: from config)",
    )
    parser.add_argument(
        "--output-topic",
        type=str,
        default=None,
        help="Output topic name (default: from config)",
    )
    parser.add_argument(
        "--group-id",
        type=str,
        default=None,
        help="Consumer group ID (default: from config)",
    )
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="Path to model file (default: from config)",
    )
    parser.add_argument(
        "--preprocessor-path",
        type=str,
        default=None,
        help="Path to preprocessor file (default: from config)",
    )
    
    args = parser.parse_args()
    
    # Convert paths to Path objects
    model_path = Path(args.model_path) if args.model_path else None
    preprocessor_path = (
        Path(args.preprocessor_path) if args.preprocessor_path else None
    )
    
    logger.info("Starting Kafka consumer...")
    
    try:
        consumer = TransactionConsumer(
            bootstrap_servers=args.bootstrap_servers,
            input_topic=args.input_topic,
            output_topic=args.output_topic,
            group_id=args.group_id,
            model_path=model_path,
            preprocessor_path=preprocessor_path,
        )
        
        consumer.consume()
    
    except Exception as e:
        logger.error(f"Consumer failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()

