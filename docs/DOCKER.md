# Docker Setup Guide

This guide explains how to run the Pileup Buster application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (included with Docker Desktop)

## Quick Start

### Option 1: Production Build

Run the full application stack with production-optimized containers:

```bash
docker-compose up -d
```

This will start:
- MongoDB database on port 27017
- Backend API on port 5000
- Frontend on port 3000

### Option 2: Development Mode

For development with hot-reload and debugging:

```bash
docker-compose -f docker-compose.dev.yml up
```

This starts the same services but with:
- Source code mounted for live reloading
- Development configurations
- Verbose logging

## Services

| Service  | Port | Description |
|----------|------|-------------|
| Frontend | 3000 | React application served by nginx |
| Backend  | 5000 | FastAPI application |
| MongoDB  | 27017 | Database |

## Environment Variables

The backend supports these environment variables:

- `MONGO_URI`: MongoDB connection string (default: `mongodb://mongodb:27017/pileup_buster`)
- `SECRET_KEY`: Secret key for API security
- `MAX_QUEUE_SIZE`: Maximum number of callsigns allowed in queue (default: `4`)
- `FLASK_ENV`: Environment mode (development/production)
- `FLASK_DEBUG`: Enable debug mode (true/false)

## Development Workflow

### Building Images

Build backend:
```bash
docker build -t pileup-buster-backend ./backend
```

Build frontend:
```bash
docker build -t pileup-buster-frontend ./frontend
```

### Individual Services

Run only the database:
```bash
docker run -d --name pileup-mongo -p 27017:27017 mongo:7
```

Run only the backend (requires database):
```bash
docker run -d --name pileup-backend \
  -p 5000:5000 \
  -e MONGO_URI=mongodb://host.docker.internal:27017/pileup_buster \
  pileup-buster-backend
```

### Logs and Debugging

View logs from all services:
```bash
docker-compose logs -f
```

View logs from a specific service:
```bash
docker-compose logs -f backend
```

Enter a running container:
```bash
docker-compose exec backend bash
```

## GitHub Codespaces

This repository includes dev container configurations for GitHub Codespaces:

1. **Docker Compose Setup** (`.devcontainer/devcontainer.json`): 
   - Uses the development docker-compose file
   - Pre-configured with VS Code extensions
   - Automatic port forwarding

2. **Simple Setup** (`.devcontainer/devcontainer.simple.json`):
   - Uses a universal dev container image
   - Installs dependencies during container creation
   - Lighter weight option

To use:
1. Open the repository in GitHub Codespaces
2. The dev container will automatically set up the environment
3. Run `docker-compose -f docker-compose.dev.yml up` to start services

## Stopping Services

Stop all services:
```bash
docker-compose down
```

Stop and remove volumes (database data):
```bash
docker-compose down -v
```

## Troubleshooting

### Port Conflicts
If ports are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "3001:80"  # Changed from 3000:80
```

### Database Connection Issues
Ensure MongoDB is accessible. Check logs:
```bash
docker-compose logs mongodb
```

### Frontend Build Issues
For development, use the dev compose file which runs the frontend in development mode:
```bash
docker-compose -f docker-compose.dev.yml up frontend-dev
```