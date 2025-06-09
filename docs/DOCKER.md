# Docker Deployment Guide

This guide explains how to run the Pileup Buster application using Docker and Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (version 20.10 or later)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 2.0 or later)

## Quick Start

### Production Deployment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/brianbruff/pileup-buster.git
   cd pileup-buster
   ```

2. **Start the application:**
   ```bash
   docker compose up -d
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/docs

4. **Stop the application:**
   ```bash
   docker compose down
   ```

### Development with Live Reload

For development with live reload and volume mounting:

1. **Start development environment:**
   ```bash
   docker compose -f docker-compose.dev.yml up -d
   ```

2. **View logs:**
   ```bash
   docker compose -f docker-compose.dev.yml logs -f
   ```

3. **Stop development environment:**
   ```bash
   docker compose -f docker-compose.dev.yml down
   ```

## Services

The application consists of three services:

### 1. MongoDB Database
- **Image**: `mongo:7.0`
- **Port**: 27017
- **Credentials**: 
  - Username: `admin`
  - Password: `password`
  - Database: `pileup_buster`

### 2. Backend API
- **Framework**: FastAPI with uvicorn
- **Port**: 5000
- **Features**:
  - Ham radio callsign queue management
  - RESTful API endpoints
  - Interactive API documentation at `/docs`

### 3. Frontend Web Application
- **Framework**: React 18
- **Port**: 3000
- **Features**:
  - User interface for callsign registration
  - Admin panel for queue management

## Configuration

### Environment Variables

#### Backend
- `MONGO_URI`: MongoDB connection string (default: `mongodb://admin:password@mongodb:27017/pileup_buster?authSource=admin`)
- `SECRET_KEY`: Secret key for session management (default: `dev-docker-secret-key`)

#### Frontend
- `REACT_APP_API_URL`: Backend API URL (default: `http://localhost:5000`)
- `CHOKIDAR_USEPOLLING`: Enable file watching for development (dev only)

### Custom Configuration

To customize configuration, create a `.env` file in the project root:

```env
# Backend Configuration
MONGO_URI=mongodb://admin:custom_password@mongodb:27017/pileup_buster?authSource=admin
SECRET_KEY=your-production-secret-key

# Frontend Configuration
REACT_APP_API_URL=http://localhost:5000
```

## Docker Commands

### Build Images
```bash
# Build all services
docker compose build

# Build specific service
docker compose build backend
docker compose build frontend
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mongodb
```

### Execute Commands in Containers
```bash
# Backend shell
docker compose exec backend bash

# Frontend shell
docker compose exec frontend sh

# MongoDB shell
docker compose exec mongodb mongosh
```

### Database Operations
```bash
# Connect to MongoDB
docker compose exec mongodb mongosh -u admin -p password --authenticationDatabase admin

# Backup database
docker compose exec mongodb mongodump -u admin -p password --authenticationDatabase admin

# View database logs
docker compose logs mongodb
```

## VS Code Dev Containers

This project includes VS Code Dev Containers configuration for a complete development environment.

### Setup

1. **Install VS Code extensions:**
   - [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

2. **Open in Dev Container:**
   - Open the project in VS Code
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
   - Select "Remote-Containers: Reopen in Container"

3. **Features included:**
   - Python development environment with FastAPI
   - Node.js for frontend development
   - MongoDB database
   - Pre-configured extensions for Python, JavaScript, and formatting
   - Port forwarding for all services

## Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Check what's using the port
   lsof -i :3000
   lsof -i :5000
   lsof -i :27017
   
   # Stop existing containers
   docker compose down
   ```

2. **Database connection issues:**
   ```bash
   # Check MongoDB logs
   docker compose logs mongodb
   
   # Restart MongoDB service
   docker compose restart mongodb
   ```

3. **Frontend build issues:**
   ```bash
   # Clear node_modules and rebuild
   docker compose down
   docker compose build --no-cache frontend
   docker compose up -d
   ```

4. **Permission issues (Linux/macOS):**
   ```bash
   # Fix ownership of files created by containers
   sudo chown -R $USER:$USER .
   ```

### Health Checks

Check service health:

```bash
# Backend health check
curl http://localhost:5000/docs

# Frontend health check
curl http://localhost:3000

# MongoDB health check
docker compose exec mongodb mongosh --eval "db.runCommand('ping')"
```

### Cleanup

Remove all containers, networks, and volumes:

```bash
# Remove everything
docker compose down -v

# Remove images as well
docker compose down -v --rmi all

# Remove unused Docker resources
docker system prune -f
```

## Production Considerations

For production deployment, consider these security and performance improvements:

1. **Use environment-specific configurations:**
   - Create separate `docker-compose.prod.yml`
   - Use secrets management for sensitive data
   - Configure proper MongoDB authentication

2. **Security hardening:**
   - Remove development volumes in production
   - Use non-root users in containers
   - Configure proper firewall rules
   - Use HTTPS with SSL certificates

3. **Performance optimization:**
   - Use multi-stage Docker builds
   - Implement health checks
   - Configure resource limits
   - Use production MongoDB replica sets

4. **Monitoring and logging:**
   - Configure centralized logging
   - Set up monitoring and alerting
   - Use Docker health checks
   - Implement backup strategies

## Contributing

When contributing to the Docker configuration:

1. Test changes with both `docker-compose.yml` and `docker-compose.dev.yml`
2. Update this documentation for any configuration changes
3. Ensure Docker images build successfully on different platforms
4. Verify the development container setup works correctly