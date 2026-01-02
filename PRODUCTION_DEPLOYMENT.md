# Production Deployment Guide

## Pre-Deployment Checklist

### 1. Model Training
- [ ] Train and save the model: `python -m src.models.train`
- [ ] Verify model files exist in `models/` directory:
  - `fraud_detection_model.pkl`
  - `preprocessor.pkl`

### 2. Environment Setup
- [ ] Copy `.env.production` to `.env` and update values
- [ ] Set production environment variables
- [ ] Configure fraud threshold (default: 0.15)
- [ ] Set appropriate log levels

### 3. Security
- [ ] Review and update security settings
- [ ] Set strong API keys/secrets if implementing authentication
- [ ] Configure firewall rules
- [ ] Review Docker security settings

### 4. Infrastructure
- [ ] Ensure Docker and docker-compose are installed
- [ ] Allocate sufficient resources (CPU, memory)
- [ ] Configure persistent storage for Kafka data
- [ ] Set up monitoring and alerting

## Deployment Steps

### Option 1: Using Deployment Script (Recommended)

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Option 2: Manual Deployment

```bash
# 1. Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# 2. Build images
docker-compose -f docker-compose.prod.yml build

# 3. Start services
docker-compose -f docker-compose.prod.yml up -d

# 4. Check status
docker-compose -f docker-compose.prod.yml ps

# 5. View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## Service Configuration

### API Service
- **Port**: Configurable via `API_PORT` (default: 8000)
- **Workers**: 4 workers for production (configured in Dockerfile.prod)
- **Health Check**: `/health` endpoint
- **Documentation**: `/docs` endpoint

### Kafka Configuration
- **Port**: Configurable via `KAFKA_PORT` (default: 9092)
- **Retention**: 7 days (168 hours)
- **Replication**: Configured for single broker (increase for production cluster)

### Consumer Service
- Runs automatically with docker-compose
- Processes transactions from `transactions_raw` topic
- Publishes results to `transactions_scored` topic

## Environment Variables

Key environment variables (set in `.env` file):

```bash
# API
API_PORT=8000
FRAUD_THRESHOLD=0.15
LOG_LEVEL=INFO

# Kafka
KAFKA_PORT=9092
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Zookeeper
ZOOKEEPER_PORT=2181
```

## Monitoring

### Health Checks
```bash
# API health
curl http://localhost:8000/health

# Service status
docker-compose -f docker-compose.prod.yml ps
```

### Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f api
docker-compose -f docker-compose.prod.yml logs -f kafka-consumer
```

### Metrics
- API metrics available at `/docs` endpoint
- Application logs in `logs/` directory
- Docker container metrics: `docker stats`

## Scaling

### Horizontal Scaling (Multiple API Instances)

Update `docker-compose.prod.yml`:

```yaml
api:
  deploy:
    replicas: 3  # Run 3 API instances
```

Use a load balancer (nginx, traefik) in front of the API instances.

### Kafka Consumer Scaling

Run multiple consumer instances:

```yaml
kafka-consumer:
  deploy:
    replicas: 3  # Run 3 consumer instances
```

Kafka will automatically distribute messages across consumers in the same consumer group.

## Backup and Recovery

### Model Files
- Backup `models/` directory regularly
- Store backups in version control or object storage

### Kafka Data
- Kafka data persisted in Docker volume: `kafka-data`
- Backup volume: `docker run --rm -v fraud-detection-kafka-data:/data -v $(pwd):/backup alpine tar czf /backup/kafka-backup.tar.gz /data`

### Recovery
1. Restore model files to `models/` directory
2. Restore Kafka volumes if needed
3. Restart services: `docker-compose -f docker-compose.prod.yml restart`

## Security Best Practices

1. **Use HTTPS**: Set up reverse proxy (nginx/traefik) with SSL certificates
2. **API Authentication**: Implement API key or OAuth2 authentication
3. **Network Security**: Use Docker networks and firewall rules
4. **Secrets Management**: Use Docker secrets or external secret management
5. **Regular Updates**: Keep Docker images and dependencies updated
6. **Read-only Volumes**: Model files mounted as read-only
7. **Non-root User**: Containers run as non-root user

## Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs

# Check resource usage
docker stats

# Restart services
docker-compose -f docker-compose.prod.yml restart
```

### API Not Responding
```bash
# Check API health
curl http://localhost:8000/health

# Check if model files are accessible
docker exec fraud-detection-api ls -la /app/models
```

### Kafka Connection Issues
```bash
# Check Kafka status
docker exec fraud-detection-kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Check topics
docker exec fraud-detection-kafka kafka-topics --list --bootstrap-server localhost:9092
```

## Production Recommendations

1. **Use Kubernetes**: For better orchestration and scaling
2. **Monitoring**: Integrate Prometheus/Grafana for metrics
3. **Logging**: Use centralized logging (ELK stack, Loki)
4. **High Availability**: Run multiple instances of each service
5. **Kafka Cluster**: Use multi-broker Kafka cluster for production
6. **Database**: Consider storing transaction history in a database
7. **Alerting**: Set up alerts for fraud detections and system issues

## Rollback

If deployment fails:

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore previous version
git checkout <previous-commit>
./deploy.sh
```

## Support

For issues or questions:
- Check logs: `docker-compose -f docker-compose.prod.yml logs`
- Review documentation in `README.md` and `TESTING_GUIDE.md`
- Check application logs in `logs/` directory

