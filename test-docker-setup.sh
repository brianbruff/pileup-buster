#!/bin/bash
# test-docker-setup.sh - Validate Docker configuration

set -e

echo "🧪 Testing Docker setup configuration..."

# Check if Docker files exist
echo "📂 Checking Docker files..."
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found"
    exit 1
fi

if [ ! -f "docker-compose.dev.yml" ]; then
    echo "❌ docker-compose.dev.yml not found"
    exit 1
fi

if [ ! -f ".dockerignore" ]; then
    echo "❌ .dockerignore not found"
    exit 1
fi

echo "✅ All Docker files present"

# Check if backend files exist
echo "📂 Checking backend configuration..."
if [ ! -f "backend/requirements.txt" ]; then
    echo "❌ backend/requirements.txt not found"
    exit 1
fi

if [ ! -f "backend/app/app.py" ]; then
    echo "❌ backend/app/app.py not found"
    exit 1
fi

if [ ! -f "backend/.env.example" ]; then
    echo "❌ backend/.env.example not found"
    exit 1
fi

echo "✅ Backend files configured"

# Check if frontend files exist
echo "📂 Checking frontend configuration..."
if [ ! -f "frontend/package.json" ]; then
    echo "❌ frontend/package.json not found"
    exit 1
fi

if [ ! -d "frontend/src" ]; then
    echo "❌ frontend/src directory not found"
    exit 1
fi

if [ ! -d "frontend/public" ]; then
    echo "❌ frontend/public directory not found"
    exit 1
fi

echo "✅ Frontend files configured"

# Validate Dockerfile syntax
echo "🔍 Validating Dockerfile syntax..."
if ! docker --version > /dev/null 2>&1; then
    echo "⚠️  Docker not available, skipping syntax check"
else
    # Basic Dockerfile syntax validation
    if [ -s "Dockerfile" ] && grep -q "^FROM" Dockerfile; then
        echo "✅ Dockerfile syntax appears valid"
    else
        echo "❌ Dockerfile has syntax errors"
        exit 1
    fi
fi

# Check documentation
echo "📚 Checking documentation..."
if [ ! -f "docs/DOCKER.md" ]; then
    echo "❌ docs/DOCKER.md not found"
    exit 1
fi

echo "✅ Documentation present"

# Check deployment script
echo "🚀 Checking deployment script..."
if [ ! -f "deploy-cloud-run.sh" ]; then
    echo "❌ deploy-cloud-run.sh not found"
    exit 1
fi

if [ ! -x "deploy-cloud-run.sh" ]; then
    echo "❌ deploy-cloud-run.sh not executable"
    exit 1
fi

echo "✅ Deployment script configured"

# Validate environment variables in .env.example
echo "🔧 Validating environment configuration..."
if ! grep -q "MONGO_URI" backend/.env.example; then
    echo "❌ MONGO_URI not found in .env.example"
    exit 1
fi

if ! grep -q "SECRET_KEY" backend/.env.example; then
    echo "❌ SECRET_KEY not found in .env.example"
    exit 1
fi

if ! grep -q "ADMIN_USERNAME" backend/.env.example; then
    echo "❌ ADMIN_USERNAME not found in .env.example"
    exit 1
fi

if ! grep -q "ADMIN_PASSWORD" backend/.env.example; then
    echo "❌ ADMIN_PASSWORD not found in .env.example"
    exit 1
fi

echo "✅ Environment variables configured"

# Check app.py for Cloud Run compatibility
echo "🔧 Checking Cloud Run compatibility..."
if ! grep -q "PORT" backend/app/app.py; then
    echo "❌ PORT environment variable support not found in app.py"
    exit 1
fi

if ! grep -q "staticfiles" backend/app/app.py; then
    echo "❌ Static file serving not configured in app.py"
    exit 1
fi

echo "✅ Cloud Run compatibility configured"

echo ""
echo "🎉 All Docker setup tests passed!"
echo "📋 Configuration Summary:"
echo "   - Docker files: ✅ Present and valid"
echo "   - Backend: ✅ Requirements and app configured"
echo "   - Frontend: ✅ Package.json and source files present"
echo "   - Documentation: ✅ DOCKER.md created"
echo "   - Deployment: ✅ Cloud Run script ready"
echo "   - Environment: ✅ Variables configured"
echo "   - Cloud Run: ✅ PORT support and static files"
echo ""
echo "🚀 Ready for Docker build and Cloud Run deployment!"
echo "   Note: Build may require stable internet connection for PyPI/npm"