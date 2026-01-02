"""Quick test to verify Kafka connection before running consumer."""

from kafka import KafkaProducer, KafkaConsumer
from src.config import KafkaConfig

config = KafkaConfig()
bootstrap_servers = config.KAFKA_BOOTSTRAP_SERVERS

print(f"Testing connection to Kafka at {bootstrap_servers}...")

try:
    # Test producer
    producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    print("✓ Producer connection successful!")
    producer.close()
    
    # Test consumer (quick check)
    consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers, consumer_timeout_ms=1000)
    print("✓ Consumer connection successful!")
    consumer.close()
    
    print("\nKafka is ready! You can now run the consumer.")
    
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nMake sure Kafka is running:")
    print("  docker-compose up -d")
    print("  docker-compose ps  # Check if kafka and zookeeper are healthy")

