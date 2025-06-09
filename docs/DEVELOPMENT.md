# Development Setup Guide

## Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- MongoDB Atlas account (or local MongoDB)

## Initial Setup

### Option 1: Docker Setup (Recommended)

The easiest way to get started with development:

```bash
# Clone and start the development environment
git clone https://github.com/brianbruff/pileup-buster.git
cd pileup-buster

# Start development with live reload
docker compose -f docker-compose.dev.yml up -d

# View logs
docker compose -f docker-compose.dev.yml logs -f
```

This automatically sets up:
- ✅ MongoDB database
- ✅ Backend FastAPI server with live reload
- ✅ Frontend React development server
- ✅ All dependencies installed

**Access:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000  
- API Documentation: http://localhost:5000/docs

See the [Docker Deployment Guide](DOCKER.md) for more details.

### Option 2: Manual Setup

If you prefer to run services manually:

### 1. Clone Repository
```bash
git clone https://github.com/brianbruff/pileup-buster.git
cd pileup-buster
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB Atlas connection string
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### MongoDB Atlas Setup

1. Create a MongoDB Atlas account
2. Create a new cluster
3. Create a database user
4. Get connection string
5. Update `MONGO_URI` in `backend/.env`

## Project Architecture

- **Frontend**: Single-page React application
- **Backend**: RESTful API using Flask
- **Database**: MongoDB for queue persistence
- **Communication**: HTTP/JSON between frontend and backend