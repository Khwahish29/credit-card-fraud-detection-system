# Quick Start - Production Deployment

## Prerequisites

- Docker and docker-compose installed
- Model files trained and saved in `models/` directory
- At least 4GB RAM available
- Ports 8000, 9092, 2181 available

## Quick Deployment (3 Steps)

### Step 1: Prepare Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your production values (optional)
# nano .env
```

### Step 2: Deploy

```bash
# Make deployment script executable (if not already)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### Step 3: Verify

```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Test API
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

## What Gets Deployed

- **Zookeeper**: Kafka coordination service
- **Kafka**: Message broker for transaction processing
- **API Service**: FastAPI application (4 workers)
- **Kafka Consumer**: Processes transactions and scores them

## Access Points

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Kafka**: localhost:9092

## Common Commands

```bash
# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down

# Restart services
docker-compose -f docker-compose.prod.yml restart

# View resource usage
docker stats

# Scale API (edit docker-compose.prod.yml first)
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

## Troubleshooting

**Services won't start:**
```bash
docker-compose -f docker-compose.prod.yml logs
```

**API not responding:**
```bash
curl http://localhost:8000/health
docker-compose -f docker-compose.prod.yml restart api
```

**Out of memory:**
- Reduce workers in Dockerfile.prod
- Increase Docker memory limit
- Check: `docker stats`

## Next Steps

1. Set up reverse proxy (nginx/traefik) with SSL
2. Configure monitoring (Prometheus/Grafana)
3. Set up centralized logging
4. Implement API authentication
5. Configure backup strategy

See `PRODUCTION_DEPLOYMENT.md` for detailed information.

