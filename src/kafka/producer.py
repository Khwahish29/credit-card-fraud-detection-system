"""Kafka producer for publishing raw transactions."""

import json
from typing import Dict, Any, Optional

from kafka import KafkaProducer
from kafka.errors import KafkaError

from src.config import KafkaConfig
from src.utils import setup_logger

logger = setup_logger(__name__)


class TransactionProducer:
    """
    Kafka producer for publishing raw transactions to the transactions_raw topic.
    """
    
    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        topic: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the Kafka producer.
        
        Args:
            bootstrap_servers: Kafka broker address. If None, uses config default.
            topic: Topic name. If None, uses config default.
            **kwargs: Additional arguments passed to KafkaProducer.
        """
        config = KafkaConfig()
        
        self.bootstrap_servers = (
            bootstrap_servers or config.KAFKA_BOOTSTRAP_SERVERS
        )
        self.topic = topic or config.TOPIC_RAW
        
        # Producer configuration
        producer_config = {
            "bootstrap_servers": self.bootstrap_servers,
            "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
            "key_serializer": lambda k: k.encode("utf-8") if k else None,
            "acks": config.PRODUCER_ACKS,
            "retries": config.PRODUCER_RETRIES,
            **kwargs,
        }
        
        try:
            self.producer = KafkaProducer(**producer_config)
            logger.info(
                f"Kafka producer initialized for topic: {self.topic}, "
                f"broker: {self.bootstrap_servers}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            raise
    
    def send_transaction(
        self,
        transaction_id: str,
        features: Dict[str, Any],
        key: Optional[str] = None,
    ) -> None:
        """
        Send a transaction to the Kafka topic.
        
        Args:
            transaction_id: Unique transaction identifier.
            features: Dictionary of transaction features.
            key: Optional message key. If None, uses transaction_id.
        
        Raises:
            KafkaError: If sending fails.
        """
        message_key = key or transaction_id
        
        message = {
            "transaction_id": transaction_id,
            "features": features,
        }
        
        try:
            future = self.producer.send(
                self.topic,
                key=message_key,
                value=message,
            )
            
            # Wait for the send to complete (synchronous)
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Transaction {transaction_id} sent to topic "
                f"{record_metadata.topic} partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
        
        except KafkaError as e:
            logger.error(f"Failed to send transaction {transaction_id}: {str(e)}")
            raise
    
    def send_batch(
        self,
        transactions: list[Dict[str, Any]],
    ) -> None:
        """
        Send multiple transactions in batch.
        
        Args:
            transactions: List of transaction dictionaries, each containing
                'transaction_id' and 'features'.
        
        Raises:
            KafkaError: If sending fails.
        """
        logger.info(f"Sending batch of {len(transactions)} transactions")
        
        for transaction in transactions:
            transaction_id = transaction.get("transaction_id")
            features = transaction.get("features", {})
            
            if not transaction_id:
                logger.warning("Skipping transaction without transaction_id")
                continue
            
            self.send_transaction(transaction_id, features)
        
        # Flush to ensure all messages are sent
        self.producer.flush()
        logger.info("Batch send completed")
    
    def close(self) -> None:
        """Close the producer connection."""
        logger.info("Closing Kafka producer")
        self.producer.close()

