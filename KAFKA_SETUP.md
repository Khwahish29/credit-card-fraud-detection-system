# Kafka Setup Guide

## Option 1: Using Docker (Recommended)

### Install Docker Desktop for Mac

1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Verify installation:
   ```bash
   docker --version
   docker-compose --version
   ```

### Start Kafka Services

Once Docker is installed:

```bash
docker-compose up -d
```

This will start:
- Zookeeper (port 2181)
- Kafka broker (port 9092)
- FastAPI service (port 8000)

### Verify Kafka is Running

```bash
docker-compose ps
```

## Option 2: Local Kafka Installation (Advanced)

If you prefer to install Kafka locally:

1. Download Kafka from: https://kafka.apache.org/downloads
2. Extract and start Zookeeper:
   ```bash
   bin/zookeeper-server-start.sh config/zookeeper.properties
   ```
3. Start Kafka:
   ```bash
   bin/kafka-server-start.sh config/server.properties
   ```

## Testing Kafka Integration

### 1. Start the Consumer (in one terminal)

```bash
source venv/bin/activate
python -m src.kafka.consumer_main
```

### 2. Send Test Transactions (in another terminal)

```bash
source venv/bin/activate
python test_kafka_producer.py
```

### 3. Check Logs

The consumer will process transactions and publish scored results to the `transactions_scored` topic.

## Troubleshooting

- **Connection refused**: Make sure Kafka is running (check with `docker-compose ps`)
- **Topic not found**: Topics are auto-created, but you can manually create them if needed
- **Consumer not receiving messages**: Check that messages are being sent and topics exist

