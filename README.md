# Pileup Buster

A web application for ham radio operators to register their callsign on a callback queue.

## Project Structure

```
pileup-buster/
├── frontend/             # React frontend application
├── backend/              # Python FastAPI server
├── docs/                 # Documentation
├── .devcontainer/        # VS Code dev container configuration
├── docker-compose.yml    # Production Docker configuration
├── docker-compose.dev.yml # Development Docker configuration
└── README.md            # This file
```

## Features

- **User Interface**: React-based frontend for callsign registration
- **Admin Panel**: Secured admin interface for queue management
- **API Backend**: Python Flask REST API
- **Database**: MongoDB Atlas for data persistence
- **Queue Management**: FIFO queue system for callsign callbacks

## Quick Start

### 🐳 Docker (Recommended)

The easiest way to run the entire application:

```bash
# Clone the repository
git clone https://github.com/brianbruff/pileup-buster.git
cd pileup-buster

# Start all services with Docker Compose
docker compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:5000
# API Docs: http://localhost:5000/docs
```

For development with live reload:
```bash
docker compose -f docker-compose.dev.yml up -d
```

📚 See [Docker Deployment Guide](docs/DOCKER.md) for detailed instructions.

### Manual Development Setup

#### Frontend Development

```bash
cd frontend
npm install
npm start
```

The frontend will be available at http://localhost:3000

#### Backend Development

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The API will be available at http://localhost:5000

#### Environment Setup

1. Copy `backend/.env.example` to `backend/.env`
2. Update MongoDB connection string and secret key
3. Ensure MongoDB Atlas cluster is accessible

📚 See [Development Guide](docs/DEVELOPMENT.md) for detailed setup instructions.

## API Endpoints

### Queue Management
- `POST /api/queue/register` - Register a callsign
- `GET /api/queue/status/<callsign>` - Get callsign position
- `GET /api/queue/list` - List current queue

### Admin Functions
- `GET /api/admin/queue` - Admin view of queue
- `DELETE /api/admin/queue/<callsign>` - Remove callsign
- `POST /api/admin/queue/clear` - Clear entire queue
- `POST /api/admin/queue/next` - Process next callsign

## Technology Stack

- **Frontend**: React 18, CSS3, HTML5
- **Backend**: Python 3, FastAPI, uvicorn
- **Database**: MongoDB
- **Deployment**: Docker, Docker Compose
- **Development**: Node.js, npm, pip, VS Code Dev Containers
