"""
Screenshot service for capturing frontend screenshots
"""
import os
import base64
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


async def capture_screenshot_with_playwright(url: str) -> Optional[str]:
    """
    Capture screenshot using playwright (if available)
    
    Args:
        url: The URL to capture
        
    Returns:
        Base64 encoded screenshot image, or None if capture fails
    """
    try:
        from playwright.async_api import async_playwright
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            screenshot_bytes = await page.screenshot(type='png', full_page=True)
            await browser.close()
            
            return base64.b64encode(screenshot_bytes).decode('utf-8')
            
    except ImportError:
        logger.warning("Playwright not available, falling back to mock screenshot")
        return None
    except Exception as e:
        logger.error(f"Playwright screenshot failed: {e}")
        return None


def _capture_screenshot_with_selenium_sync(url: str) -> Optional[str]:
    """
    Synchronous selenium screenshot function to be run in thread pool
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        
        # Wait a moment for page to load
        import time
        time.sleep(2)
        
        screenshot_b64 = driver.get_screenshot_as_base64()
        driver.quit()
        
        return screenshot_b64
        
    except ImportError:
        logger.warning("Selenium not available")
        return None
    except Exception as e:
        logger.error(f"Selenium screenshot failed: {e}")
        return None


async def capture_screenshot_with_selenium(url: str) -> Optional[str]:
    """
    Capture screenshot using selenium (if available) - async wrapper
    
    Args:
        url: The URL to capture
        
    Returns:
        Base64 encoded screenshot image, or None if capture fails
    """
    try:
        # Run selenium in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, 
                _capture_screenshot_with_selenium_sync, 
                url
            )
            return result
            
    except Exception as e:
        logger.error(f"Selenium screenshot failed: {e}")
        return None


async def capture_screenshot(url: str) -> Optional[str]:
    """
    Capture a screenshot of the given URL
    
    Args:
        url: The URL to capture
        
    Returns:
        Base64 encoded screenshot image, or None if capture fails
    """
    try:
        logger.info(f"Capturing screenshot of {url}")
        
        # Try playwright first
        screenshot_b64 = await capture_screenshot_with_playwright(url)
        if screenshot_b64:
            logger.info("Screenshot captured with playwright")
            return screenshot_b64
        
        # Try selenium as fallback
        screenshot_b64 = await capture_screenshot_with_selenium(url)
        if screenshot_b64:
            logger.info("Screenshot captured with selenium")
            return screenshot_b64
        
        # No screenshot available
        logger.warning("No screenshot libraries available")
        return None
        
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        return None


def generate_status_html(screenshot_b64: Optional[str], frontend_url: str, timestamp: str, system_status: Dict[str, Any]) -> str:
    """
    Generate HTML status page with optional screenshot and system status
    
    Args:
        screenshot_b64: Base64 encoded screenshot (optional)
        frontend_url: URL to link back to frontend
        timestamp: Timestamp of screenshot
        system_status: System status information from database
        
    Returns:
        HTML content as string
    """
    is_active = system_status.get('active', False)
    status_class = 'active' if is_active else 'inactive'
    status_text = 'ACTIVE' if is_active else 'INACTIVE'
    status_color = '#28a745' if is_active else '#dc3545'
    
    screenshot_section = ""
    if screenshot_b64:
        screenshot_section = f"""
        <div class="screenshot-container">
            <img src="data:image/png;base64,{screenshot_b64}" 
                 alt="Frontend Screenshot" 
                 class="screenshot">
        </div>"""
    else:
        screenshot_section = """
        <div class="no-screenshot">
            <p>Screenshot not available. To enable screenshots, install playwright or selenium:</p>
            <code>pip install playwright && playwright install chromium</code>
        </div>"""

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pileup Buster Status</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
        }}
        .status-banner {{
            background-color: {status_color};
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
            font-size: 18px;
            font-weight: bold;
        }}
        .screenshot-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .screenshot {{
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .no-screenshot {{
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border: 2px dashed #ddd;
            border-radius: 8px;
            color: #666;
        }}
        .no-screenshot code {{
            background-color: #e9ecef;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }}
        .link-container {{
            text-align: center;
            margin-top: 30px;
        }}
        .frontend-link {{
            display: inline-block;
            background-color: {status_color};
            color: white;
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: 500;
            transition: background-color 0.2s;
        }}
        .frontend-link:hover {{
            opacity: 0.8;
        }}
        .note {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid {status_color};
            color: #666;
            font-size: 14px;
        }}
        .status-details {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 6px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Pileup Buster Status</h1>
            <div class="timestamp">Last updated: {timestamp}</div>
        </div>
        
        <div class="status-banner {status_class}">
            System Status: {status_text}
        </div>
        
        {screenshot_section}
        
        <div class="link-container">
            <a href="{frontend_url}" class="frontend-link" target="_blank">
                ← Go to Pileup Buster Frontend ({status_text})
            </a>
        </div>
        
        <div class="note">
            This page shows the current status of the Pileup Buster system. 
            Click the link above to access the live application.
        </div>
        
        <div class="status-details">
            <strong>System Status:</strong> {status_text}<br>
            <strong>Last Status Update:</strong> {system_status.get('last_updated', 'Unknown')}<br>
            <strong>Page Generated:</strong> {timestamp}
        </div>
    </div>
</body>
</html>
"""
    return html_template