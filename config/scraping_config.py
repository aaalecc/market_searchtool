"""
Scraping Configuration for Market Search Tool
Headers, user agents, and settings for both requests and Selenium scrapers.
"""

import random
from typing import Dict, List, Any
import requests

# =============================================================================
# USER AGENTS POOL
# =============================================================================
# Rotate between different browser user agents to avoid detection
USER_AGENTS = [
    # Chrome (Windows)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    
    # Firefox (Windows)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
    
    # Edge (Windows)
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    
    # Chrome (Mac)
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    
    # Safari (Mac)
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
]

# =============================================================================
# REQUEST HEADERS (for requests library)
# =============================================================================
# Base headers that look like a real browser
BASE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

# Additional headers for AJAX requests
AJAX_HEADERS = {
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}

# =============================================================================
# SITE-SPECIFIC HEADERS (for requests library)
# =============================================================================
SITE_HEADERS = {
    'yahoo_auctions': {
        'Referer': 'https://auctions.yahoo.co.jp/',
        'Origin': 'https://auctions.yahoo.co.jp'
    },
    'yahoo_flea_market': {
        'Referer': 'https://paypayfleamarket.yahoo.co.jp/',
        'Origin': 'https://paypayfleamarket.yahoo.co.jp'
    },
    'rakuten': {
        'Referer': 'https://www.rakuten.co.jp/',
        'Origin': 'https://www.rakuten.co.jp'
    },
    'mercari': {
        'Referer': 'https://jp.mercari.com/',
        'Origin': 'https://jp.mercari.com'
    },
    'grailed': {
        'Referer': 'https://www.grailed.com/',
        'Origin': 'https://www.grailed.com'
    },
    'sneaker_dunk': {
        'Referer': 'https://snkrdunk.com/',
        'Origin': 'https://snkrdunk.com'
    }
}

# =============================================================================
# SELENIUM CONFIGURATION
# =============================================================================
# Chrome options for Selenium WebDriver
CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-features=VizDisplayCompositor',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-images',  # Speed up loading
    '--disable-javascript',  # Disable for some sites if possible
    '--user-agent={user_agent}',  # Will be formatted with random user agent
    '--window-size=1920,1080',
    '--lang=ja-JP',  # Japanese locale for Japanese sites
    '--accept-lang=ja-JP,ja,en-US,en',
]

# Chrome options for stealth mode (anti-detection)
STEALTH_CHROME_OPTIONS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-features=VizDisplayCompositor',
    '--disable-extensions',
    '--disable-plugins',
    '--disable-blink-features=AutomationControlled',  # Hide automation
    '--exclude-switches=enable-automation',
    '--use-fake-ui-for-media-stream',
    '--disable-web-security',
    '--allow-running-insecure-content',
    '--window-size=1920,1080',
    '--lang=ja-JP',
    '--accept-lang=ja-JP,ja,en-US,en',
]

# Selenium wait timeouts
SELENIUM_TIMEOUTS = {
    'implicit_wait': 10,  # Seconds to wait for elements
    'page_load_timeout': 30,  # Seconds to wait for page load
    'script_timeout': 30,  # Seconds to wait for scripts
    'element_wait': 15,  # Explicit wait for specific elements
    'retry_wait': 3  # Wait between retries
}

# Common element selectors for Selenium
SELENIUM_SELECTORS = {
    # Common selectors that might be used across sites
    'search_input': ['input[type="search"]', 'input[name="q"]', 'input[placeholder*="search"]'],
    'search_button': ['button[type="submit"]', 'input[type="submit"]', '.search-button'],
    'product_links': ['a[href*="/item/"]', 'a[href*="/product/"]', '.product-link'],
    'price_elements': ['.price', '.cost', '[class*="price"]', '[data-price]'],
    'title_elements': ['.title', '.name', 'h1', 'h2', 'h3', '[class*="title"]'],
    'image_elements': ['img[src*="jpg"]', 'img[src*="jpeg"]', 'img[src*="png"]', 'img[src*="webp"]']
}

# =============================================================================
# REQUEST SESSION CONFIGURATION
# =============================================================================
# Session settings for requests library
SESSION_CONFIG = {
    'max_retries': 3,
    'backoff_factor': 0.3,
    'timeout': (10, 30),  # (connect timeout, read timeout)
    'allow_redirects': True,
    'verify_ssl': True
}

# Connection pool settings
POOL_CONFIG = {
    'pool_connections': 10,
    'pool_maxsize': 20,
    'max_retries': 3
}

# =============================================================================
# PROXY CONFIGURATION (Optional)
# =============================================================================
# Framework for proxy rotation if needed in the future
PROXY_CONFIG = {
    'enabled': False,  # Disabled by default
    'proxies': [],     # List of proxy URLs
    'rotation': True,  # Rotate between proxies
    'timeout': 10      # Proxy timeout
}

# =============================================================================
# RATE LIMITING AND DELAYS
# =============================================================================
# Import from settings.py to avoid duplication
from .settings import REQUEST_DELAYS

# Additional rate limiting for specific scenarios
BURST_PROTECTION = {
    'max_requests_per_minute': 20,
    'max_concurrent_requests': 3,
    'cooldown_after_error': 30,  # Seconds to wait after getting blocked
    'exponential_backoff': True
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_random_user_agent() -> str:
    """Get a random user agent string."""
    return random.choice(USER_AGENTS)

def get_request_headers(site_id: str = None, ajax: bool = False) -> Dict[str, str]:
    """
    Generate request headers for a specific site.
    
    Args:
        site_id: Site identifier (e.g., 'yahoo_auctions')
        ajax: Whether this is an AJAX request
        
    Returns:
        Dictionary of HTTP headers
    """
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    
    # Add AJAX headers if needed
    if ajax:
        headers.update(AJAX_HEADERS)
    
    # Add site-specific headers
    if site_id and site_id in SITE_HEADERS:
        headers.update(SITE_HEADERS[site_id])
    
    return headers

def get_chrome_options(stealth_mode: bool = False, headless: bool = True) -> List[str]:
    """
    Get Chrome options for Selenium WebDriver.
    
    Args:
        stealth_mode: Use anti-detection options
        headless: Run browser in headless mode
        
    Returns:
        List of Chrome options
    """
    options = STEALTH_CHROME_OPTIONS.copy() if stealth_mode else CHROME_OPTIONS.copy()
    
    if headless:
        options.append('--headless=new')  # Use new headless mode
    
    # Format user agent
    user_agent = get_random_user_agent()
    for i, option in enumerate(options):
        if '{user_agent}' in option:
            options[i] = option.format(user_agent=user_agent)
    
    return options

def get_selenium_driver_config(site_id: str = None) -> Dict[str, Any]:
    """
    Get complete Selenium WebDriver configuration for a site.
    
    Args:
        site_id: Site identifier for site-specific config
        
    Returns:
        Dictionary with WebDriver configuration
    """
    # Determine if site needs stealth mode
    stealth_sites = ['mercari', 'grailed', 'sneaker_dunk']
    stealth_mode = site_id in stealth_sites if site_id else False
    
    return {
        'chrome_options': get_chrome_options(stealth_mode=stealth_mode),
        'timeouts': SELENIUM_TIMEOUTS,
        'selectors': SELENIUM_SELECTORS,
        'stealth_mode': stealth_mode
    }

def should_use_selenium(site_id: str) -> bool:
    """
    Determine if a site requires Selenium vs requests.
    
    Args:
        site_id: Site identifier
        
    Returns:
        True if site needs Selenium, False for requests
    """
    selenium_sites = ['mercari', 'grailed', 'sneaker_dunk']
    return site_id in selenium_sites

def get_delay_config(site_id: str) -> Dict[str, float]:
    """
    Get delay configuration for a specific site.
    
    Args:
        site_id: Site identifier
        
    Returns:
        Dictionary with delay settings
    """
    if should_use_selenium(site_id):
        return REQUEST_DELAYS['dynamic_sites']
    else:
        return REQUEST_DELAYS['simple_sites']

# Add to scraping_config.py
COOKIE_CONFIG = {
    'enabled': True,
    'persist_cookies': True,
    'cookie_jar_file': 'data/cookies.txt',
    'max_cookie_age_days': 7
}

# Implementation
session = requests.Session()
session.cookies.update(cookie_jar)  # Maintain session state 