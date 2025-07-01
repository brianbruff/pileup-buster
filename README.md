# Pileup Buster

A web application for ham radio operators to register their callsign on a callback queue.

## 🚀 Live Application

**Try it now:** [https://pileupbuster.com](https://pileupbuster.com)

![Pileup Buster Screenshot](docs/images/app-screenshot.png)

**System Status:** [https://api.pileupbuster.com/status](https://api.pileupbuster.com/status)

## Acknowledgments

This idea is not unique - we first noticed it being used by the Australian DX helper website developed by Greg and Grant. Kudos to them for the innovative approach! Check out their excellent work in the amateur radio community.

## Project Goals

### Core Objectives
- **Interactive Experience**: Real-time updates without manual page refreshing
- **100% AI-Driven Development**: All design elements (sketches, logos, website, features, issue design, and implementation) powered by AI
- **Single-User Focus**: Designed as a personal tool rather than multi-tenant platform (while multi-tenancy could be easily implemented, maintaining a platform for third parties is not the current goal)

### Technical Goals
- **Universal Deployment**: Support deployment on cloud platforms, any server, or local environments
- **Containerization**: Full Docker support for easy deployment and development
- **Modern Frontend**: Single-page React application hosted on GitHub Pages
- **Embedded Integration**: Backend status page designed for iframe integration (e.g., QRZ.com profiles - see https://www.qrz.com/db/EI6LF)
- **Scalable Architecture**: Clean separation between frontend and backend services
- **Developer Experience**: Streamlined development workflow with hot-reload and modern tooling

### Software Quality Goals
- **Comprehensive Testing**: Unit, integration, and end-to-end test coverage
- **Documentation**: Clear setup guides, API documentation, and contributor guidelines
- **Code Quality**: Consistent coding standards and automated linting
- **Security**: Secure authentication and data protection
- **Performance**: Optimized for fast load times and responsive user experience
- **Maintainability**: Clean, modular code architecture for long-term sustainability

## Project Structure

```
pileup-buster/
├── frontend/          # React frontend application
├── backend/           # Python FastAPI server
├── docs/             # Documentation
└── README.md         # This file
```

## Features

- **User Interface**: React-based frontend for callsign registration
- **Admin Panel**: Secured admin interface for queue management
- **API Backend**: Python FastAPI REST API
- **Database**: MongoDB Atlas for data persistence
- **Queue Management**: FIFO queue system for callsign callbacks
- **QRZ.com Integration**: Automatic lookup of amateur radio callsign information

## Quick Start

### 🐳 Docker (Recommended)

Run the complete application with Docker:

```bash
# Clone the repository
git clone https://github.com/brianbruff/pileup-buster.git
cd pileup-buster

# Start all services
docker compose up -d
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- MongoDB: localhost:27017

For development with hot-reload:
```bash
docker compose -f docker-compose.dev.yml up
```

See [Docker Setup Guide](docs/DOCKER.md) for detailed instructions.

### Manual Setup

### Frontend Development

```bash
cd frontend
npm install
npm start
```

The frontend will be available at http://localhost:3000

### Backend Development

```bash
cd backend

# Install Poetry if not already installed
pip install poetry

# Install dependencies
poetry install

# Run backend server
poetry run uvicorn app.app:app --reload
```

The API will be available at http://localhost:5000

### Environment Setup

1. Copy `backend/.env.example` to `backend/.env`
2. Configure the environment variables as described below

#### Environment Variables

| Variable         | Purpose                              | Required | Example                            |
|------------------|--------------------------------------|----------|------------------------------------|
| MONGO_URI        | MongoDB connection string            | Yes      | mongodb+srv://user:pass@cluster... |
| SECRET_KEY       | Secret key for the API               | Yes      | supersecretkey                     |
| ADMIN_USERNAME   | Admin interface login username       | Yes      | admin                              |
| ADMIN_PASSWORD   | Admin interface login password       | Yes      | password123                        |
| QRZ_USERNAME     | QRZ.com integration username         | No       | myqrzlogin                         |
| QRZ_PASSWORD     | QRZ.com integration password         | No       | myqrzpassword                      |
| MAX_QUEUE_SIZE   | Maximum number of entries in queue  | No       | 4                                  |

**Required Variables:**
- `MONGO_URI`: MongoDB Atlas connection string or local MongoDB URI
- `SECRET_KEY`: Used for API authentication and security
- `ADMIN_USERNAME` & `ADMIN_PASSWORD`: Credentials for accessing the admin interface

**Optional Variables:**
- `QRZ_USERNAME` & `QRZ_PASSWORD`: If not configured, QRZ.com lookups will return "not configured" message
- `MAX_QUEUE_SIZE`: Defaults to a reasonable limit if not specified

3. Ensure MongoDB Atlas cluster is accessible or set up local MongoDB

## API Endpoints

### Queue Management
- `POST /api/queue/register` - Register a callsign
- `GET /api/queue/status/<callsign>` - Get callsign position with QRZ.com profile data
- `GET /api/queue/list` - List current queue

### Public Endpoints (No Authentication Required)
- `GET /api/public/status` - Get system active status (public)

### Admin Functions (Protected with HTTP Basic Auth)
- `GET /api/admin/queue` - Admin view of queue
- `DELETE /api/admin/queue/<callsign>` - Remove callsign
- `POST /api/admin/queue/clear` - Clear entire queue
- `POST /api/admin/queue/next` - Process next callsign
- `GET /api/admin/status` - Get system status (admin)
- `POST /api/admin/status` - Set system status (admin)

## Technology Stack

- **Frontend**: React 18, CSS3, HTML5
- **Backend**: Python 3, FastAPI, uvicorn
- **Database**: MongoDB (MongoDB Atlas or local)
- **Containerization**: Docker, Docker Compose
- **Development**: Node.js, npm, Poetry (Python dependency management)

## GitHub Codespaces

This repository includes dev container configurations for GitHub Codespaces. Simply open the repository in Codespaces and the development environment will be automatically configured.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. This means you are free to use, modify, and distribute this code without restrictions.
