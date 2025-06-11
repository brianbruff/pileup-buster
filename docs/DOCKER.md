# Docker Setup Guide

This guide covers running Pileup Buster with Docker for both development and production deployment.

## Quick Start

### Production Deployment (Single Container)

For production deployment (including GCP Cloud Run), use the main Dockerfile:

```bash
# Build the container
docker build -t pileup-buster .

# Run with environment variables
docker run -p 8080:8080 \
  -e MONGO_URI="your-mongodb-connection-string" \
  -e SECRET_KEY="your-secret-key" \
  -e ADMIN_USERNAME="admin" \
  -e ADMIN_PASSWORD="your-admin-password" \
  pileup-buster
```

### Local Development with Docker Compose

For local development with hot-reload:

```bash
# Development mode (separate containers)
docker compose -f docker-compose.dev.yml up

# Production mode (single container + MongoDB)
docker compose up
```

## Environment Variables

The application requires these environment variables:

### Required Variables

- `MONGO_URI`: MongoDB connection string
- `SECRET_KEY`: Secret key for sessions
- `ADMIN_USERNAME`: Admin username for protected routes
- `ADMIN_PASSWORD`: Admin password for protected routes

### Optional Variables

- `QRZ_USERNAME`: QRZ.com username for callsign lookups
- `QRZ_PASSWORD`: QRZ.com password for callsign lookups
- `PORT`: Port number (automatically set by Cloud Run)

### Example .env file

```bash
# Copy backend/.env.example to backend/.env and update values
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pileup_buster
SECRET_KEY=your-very-secure-secret-key-here
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password
QRZ_USERNAME=your-qrz-username
QRZ_PASSWORD=your-qrz-password
```

## Development Workflow

### Development Mode

Use `docker-compose.dev.yml` for development with hot-reload:

```bash
# Start development environment
docker compose -f docker-compose.dev.yml up

# Rebuild after dependency changes
docker compose -f docker-compose.dev.yml build

# View logs
docker compose -f docker-compose.dev.yml logs -f
```

Services available at:
- Frontend: http://localhost:3000 (React dev server)
- Backend: http://localhost:8000 (FastAPI with auto-reload)
- MongoDB: localhost:27017

### Production Testing

Test the production build locally:

```bash
# Build and run production container
docker compose up --build

# Access the application
open http://localhost:8080
```

## GCP Cloud Run Deployment

### Prerequisites

1. Google Cloud SDK installed and configured
2. Docker installed locally
3. Project with Cloud Run API enabled

### Deployment Steps

1. **Build and push to Google Container Registry:**

```bash
# Set your project ID
export PROJECT_ID=your-gcp-project-id

# Build and tag the image
docker build -t gcr.io/$PROJECT_ID/pileup-buster .

# Push to GCR
docker push gcr.io/$PROJECT_ID/pileup-buster
```

2. **Deploy to Cloud Run:**

```bash
# Deploy with gcloud CLI
gcloud run deploy pileup-buster \
  --image gcr.io/$PROJECT_ID/pileup-buster \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars "MONGO_URI=your-mongodb-connection-string" \
  --set-env-vars "SECRET_KEY=your-secret-key" \
  --set-env-vars "ADMIN_USERNAME=admin" \
  --set-env-vars "ADMIN_PASSWORD=your-admin-password"
```

3. **Alternative: Using Cloud Console**

- Go to Cloud Run in Google Cloud Console
- Click "Create Service"
- Select the container image from GCR
- Configure environment variables in the "Variables" section
- Deploy

### Cloud Run Configuration

- **Memory**: 512Mi (minimum recommended)
- **CPU**: 1 vCPU
- **Concurrency**: 100 (default)
- **Port**: 8080 (automatically configured)
- **Authentication**: Allow unauthenticated traffic

## Database Setup

### MongoDB Atlas (Recommended for Production)

1. Create a MongoDB Atlas account
2. Create a new cluster
3. Create a database user
4. Whitelist Cloud Run IP ranges (or use 0.0.0.0/0 for simplicity)
5. Get the connection string
6. Use the connection string as `MONGO_URI`

### Local MongoDB (Development)

For local development, MongoDB is included in the docker-compose setup.

## Security Considerations

### Environment Variables

- Never commit sensitive environment variables to source control
- Use Google Secret Manager for production secrets
- Rotate passwords regularly

### Network Security

- Configure MongoDB to accept connections only from your Cloud Run service
- Use strong passwords for admin authentication
- Consider using VPC connector for private database connections

## Troubleshooting

### Build Issues

```bash
# Clean Docker cache
docker system prune -f

# Rebuild without cache
docker build --no-cache -t pileup-buster .
```

### Container Issues

```bash
# Check container logs
docker logs <container-id>

# Run container interactively
docker run -it pileup-buster /bin/bash
```

### Cloud Run Issues

```bash
# View Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision" --limit 100

# Check service status
gcloud run services describe pileup-buster --region=us-central1
```

## Performance Optimization

### Docker Image Size

The production Dockerfile uses multi-stage builds to minimize image size:
- Frontend built in Node.js container, then copied to Python container
- Only production dependencies included
- Alpine Linux base where possible

### Cloud Run Optimization

- Container starts quickly due to minimal image size
- Static files served efficiently from FastAPI
- Database connections are reused across requests

## Monitoring

### Health Checks

The application includes basic health monitoring:
- API endpoints are automatically documented at `/docs`
- Database connectivity is validated on startup

### Logging

- Application logs are automatically collected by Cloud Run
- Use Google Cloud Logging for centralized log management
- Consider adding structured logging for better debugging

## Cost Optimization

### Cloud Run

- Pay per request model
- Automatic scaling to zero when not in use
- Consider setting maximum instances to control costs

### MongoDB Atlas

- Use shared clusters for development
- Monitor data usage and optimize queries
- Set up billing alerts