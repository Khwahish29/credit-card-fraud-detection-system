#!/bin/bash

# Production Deployment Script for Credit Card Fraud Detection System

set -e  # Exit on error

echo "=========================================="
echo "Credit Card Fraud Detection - Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: docker-compose is not installed${NC}"
    exit 1
fi

# Check if model files exist
if [ ! -f "models/fraud_detection_model.pkl" ] || [ ! -f "models/preprocessor.pkl" ]; then
    echo -e "${YELLOW}Warning: Model files not found${NC}"
    echo "Please train the model first:"
    echo "  python -m src.models.train"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Load environment variables
if [ -f .env ]; then
    echo -e "${GREEN}Loading environment variables from .env${NC}"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}Warning: .env file not found. Using defaults.${NC}"
fi

# Build Docker images
echo -e "${GREEN}Building Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build

# Stop existing containers
echo -e "${GREEN}Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down

# Start services
echo -e "${GREEN}Starting services...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo -e "${GREEN}Waiting for services to be healthy...${NC}"
sleep 10

# Check service status
echo -e "${GREEN}Checking service status...${NC}"
docker-compose -f docker-compose.prod.yml ps

# Test API health
echo -e "${GREEN}Testing API health...${NC}"
sleep 5
if curl -f http://localhost:${API_PORT:-8000}/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API is healthy${NC}"
else
    echo -e "${YELLOW}⚠ API health check failed (may need more time to start)${NC}"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Deployment Complete!"
echo "==========================================${NC}"
echo ""
echo "Services:"
echo "  - API: http://localhost:${API_PORT:-8000}"
echo "  - API Docs: http://localhost:${API_PORT:-8000}/docs"
echo "  - Kafka: localhost:${KAFKA_PORT:-9092}"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  - Stop services: docker-compose -f docker-compose.prod.yml down"
echo "  - Restart: docker-compose -f docker-compose.prod.yml restart"
echo ""

