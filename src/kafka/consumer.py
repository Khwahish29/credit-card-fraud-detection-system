"""Kafka consumer for processing transactions and publishing scored results."""

import json
import signal
import sys
from typing import Dict, Any, Optional, Callable

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from src.config import KafkaConfig
from src.models.loader import load_model
from src.data.preprocessor import FraudPreprocessor
from src.utils import setup_logger

logger = setup_logger(__name__)


class TransactionConsumer:
    """
    Kafka consumer that scores transactions and publishes results.
    
    Consumes from transactions_raw topic and publishes to transactions_scored topic.
    """
    
    def __init__(
        self,
        bootstrap_servers: Optional[str] = None,
        input_topic: Optional[str] = None,
        output_topic: Optional[str] = None,
        group_id: Optional[str] = None,
        model_path: Optional[str] = None,
        preprocessor_path: Optional[str] = None,
    ):
        """
        Initialize the Kafka consumer.
        
        Args:
            bootstrap_servers: Kafka broker address. If None, uses config default.
            input_topic: Input topic name (transactions_raw). If None, uses config.
            output_topic: Output topic name (transactions_scored). If None, uses config.
            group_id: Consumer group ID. If None, uses config default.
            model_path: Path to the saved model. If None, uses config default.
            preprocessor_path: Path to the saved preprocessor. If None, uses config.
        """
        config = KafkaConfig()
        
        self.bootstrap_servers = (
            bootstrap_servers or config.KAFKA_BOOTSTRAP_SERVERS
        )
        self.input_topic = input_topic or config.TOPIC_RAW
        self.output_topic = output_topic or config.TOPIC_SCORED
        self.group_id = group_id or config.CONSUMER_GROUP_ID
        
        # Load model and preprocessor
        logger.info("Loading model and preprocessor for scoring...")
        try:
            from src.models.loader import load_model as load_model_func
            self.model, self.preprocessor = load_model_func(
                model_path=model_path,
                preprocessor_path=preprocessor_path,
            )
            logger.info("Model and preprocessor loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model/preprocessor: {str(e)}")
            raise
        
        # Initialize producer for output topic
        from src.kafka.producer import TransactionProducer
        self.output_producer = TransactionProducer(
            bootstrap_servers=self.bootstrap_servers,
            topic=self.output_topic,
        )
        
        # Consumer configuration
        consumer_config = {
            "bootstrap_servers": self.bootstrap_servers,
            "group_id": self.group_id,
            "auto_offset_reset": config.CONSUMER_AUTO_OFFSET_RESET,
            "enable_auto_commit": config.CONSUMER_ENABLE_AUTO_COMMIT,
            "value_deserializer": lambda m: json.loads(m.decode("utf-8")),
            "key_deserializer": lambda k: k.decode("utf-8") if k else None,
        }
        
        try:
            self.consumer = KafkaConsumer(
                self.input_topic,
                **consumer_config,
            )
            logger.info(
                f"Kafka consumer initialized for topic: {self.input_topic}, "
                f"broker: {self.bootstrap_servers}, group: {self.group_id}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {str(e)}")
            raise
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def score_transaction(
        self,
        transaction_id: str,
        features: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Score a transaction using the loaded model.
        
        Args:
            transaction_id: Unique transaction identifier.
            features: Dictionary of transaction features.
        
        Returns:
            Dictionary containing transaction_id, fraud_probability, and is_fraud.
        """
        import pandas as pd
        
        try:
            # Convert features to DataFrame
            features_df = pd.DataFrame([features])
            
            # Transform features
            features_transformed = self.preprocessor.transform(features_df)
            
            # Predict
            fraud_probability = float(
                self.model.predict_proba(features_transformed)[0, 1]
            )
            threshold = 0.5
            is_fraud = fraud_probability >= threshold
            
            result = {
                "transaction_id": transaction_id,
                "fraud_probability": fraud_probability,
                "is_fraud": is_fraud,
                "threshold": threshold,
            }
            
            logger.debug(
                f"Scored transaction {transaction_id}: "
                f"probability={fraud_probability:.4f}, is_fraud={is_fraud}"
            )
            
            return result
        
        except Exception as e:
            logger.error(
                f"Error scoring transaction {transaction_id}: {str(e)}"
            )
            raise
    
    def process_message(self, message: Any) -> None:
        """
        Process a single Kafka message.
        
        Args:
            message: Kafka message object.
        """
        try:
            # Parse message
            message_value = message.value
            transaction_id = message_value.get("transaction_id")
            features = message_value.get("features", {})
            
            if not transaction_id:
                logger.warning("Received message without transaction_id, skipping")
                return
            
            # Score transaction
            result = self.score_transaction(transaction_id, features)
            
            # Publish to output topic
            # Send scored result (using send_transaction but with scored data as features)
            scored_message = {
                "fraud_probability": result["fraud_probability"],
                "is_fraud": result["is_fraud"],
                "threshold": result["threshold"],
                "original_features": features,  # Include original features for reference
            }
            self.output_producer.send_transaction(
                transaction_id=result["transaction_id"],
                features=scored_message,
            )
            
            logger.info(
                f"Processed transaction {transaction_id}, "
                f"fraud_probability={result['fraud_probability']:.4f}"
            )
        
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            # Continue processing other messages
    
    def consume(self) -> None:
        """
        Start consuming messages from Kafka.
        
        Runs until interrupted by signal or error.
        """
        logger.info(f"Starting to consume from topic: {self.input_topic}")
        
        try:
            while self.running:
                # Poll for messages (with timeout)
                message_pack = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_pack.items():
                    for message in messages:
                        self.process_message(message)
        
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Error during consumption: {str(e)}")
            raise
        finally:
            self.close()
    
    def close(self) -> None:
        """Close consumer and producer connections."""
        logger.info("Closing Kafka consumer and producer")
        
        if hasattr(self, "consumer"):
            self.consumer.close()
        
        if hasattr(self, "output_producer"):
            self.output_producer.close()

