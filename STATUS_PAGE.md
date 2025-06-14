# Status Page with System Status and Screenshot Functionality

## Overview

The Pileup Buster API includes a `/status` endpoint that generates a static HTML page displaying:
- Current system status (ACTIVE/INACTIVE) with clear visual indicators
- Optional screenshot of the frontend application 
- Clickable link back to the frontend with status indication
- Timestamp information

## Usage

Access the status page at: `http://your-api-server/status`

## Configuration

Configure the frontend URL using the environment variable:

```bash
FRONTEND_URL=http://localhost:3000
```

Add this to your `.env` file or export it in your environment.

## Screenshot Implementation

The status page attempts to capture screenshots using these approaches:

1. **Playwright** (preferred) - Headless browser automation
2. **Selenium** (fallback) - WebDriver-based screenshots

If neither screenshot library is available, the status page will display without a screenshot but still show the system status information.

### Installing Screenshot Dependencies

#### Option 1: Playwright (Recommended)
```bash
pip install playwright
playwright install chromium
```

#### Option 2: Selenium
```bash
pip install selenium
# Also requires Chrome/Chromium and chromedriver
```

### Production Deployment

For production environments, ensure one of the screenshot libraries is installed and properly configured:

```dockerfile
# Example Dockerfile snippet
RUN pip install playwright
RUN playwright install chromium
```

## API Endpoints

### `/status` (HTML Response)
- **Method**: GET
- **Response**: HTML page with screenshot and frontend link
- **Features**:
  - Responsive design
  - Screenshot of frontend
  - Clickable link to frontend URL
  - Error handling for screenshot failures
  - No authentication required

### `/api/public/status` (JSON Response)
- **Method**: GET  
- **Response**: JSON with system status
- **Example**: `{"active": true}`

## Testing

Run the test suite:

```bash
cd backend
python -m pytest tests/test_status_page.py -v
```

## Error Handling

The status page includes robust error handling:

- Screenshot capture failures display status page without image
- Network timeouts are handled gracefully
- Invalid URLs return error page with details
- Service unavailability shows appropriate messages

## HTML Features

The generated status page includes:

- Clean, responsive design
- System status indicator (ACTIVE/INACTIVE) with color coding
- Optional frontend screenshot display when available
- Timestamp of page generation
- Prominent link back to frontend showing current system status
- Instructions for enabling screenshots when not available
- Professional styling with hover effects