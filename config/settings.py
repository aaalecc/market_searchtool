"""
Market Search Tool - Application Settings
Default configuration values for all app components.
"""

import os
from pathlib import Path

# =============================================================================
# APPLICATION INFO
# =============================================================================
APP_NAME = "Market Search Tool"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Market Search Team"

# =============================================================================
# PATHS AND DIRECTORIES
# =============================================================================
# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = PROJECT_ROOT / "cache"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, CACHE_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Database
DATABASE_PATH = DATA_DIR / "market_search.db"

# =============================================================================
# MARKETPLACE SITES CONFIGURATION
# =============================================================================
# Sites that use requests + BeautifulSoup (faster)
SIMPLE_SITES = {
    'yahoo_auctions': {
        'name': 'Yahoo Auctions',
        'enabled': True,
        'base_url': 'https://auctions.yahoo.co.jp',
        'search_url': 'https://auctions.yahoo.co.jp/search/search',
        'priority': 1  # 1 = highest priority
    },
    'yahoo_flea_market': {
        'name': 'Yahoo Flea Market',
        'enabled': True,
        'base_url': 'https://paypayfleamarket.yahoo.co.jp',
        'search_url': 'https://paypayfleamarket.yahoo.co.jp/search',
        'priority': 2
    },
    'yahoo_shopping': {
        'name': 'Yahoo Shopping',
        'enabled': True,
        'base_url': 'https://shopping.yahoo.co.jp',
        'search_url': 'https://shopping.yahoo.co.jp/search',
        'priority': 3
    },
    'rakuten': {
        'name': 'Rakuten',
        'enabled': True,
        'base_url': 'https://search.rakuten.co.jp',
        'search_url': 'https://search.rakuten.co.jp/search/mall',
        'priority': 4
    }
}

# Sites that need Selenium (slower but handle JS/anti-bot)
DYNAMIC_SITES = {
    'mercari': {
        'name': 'Mercari',
        'enabled': True,
        'base_url': 'https://jp.mercari.com',
        'search_url': 'https://jp.mercari.com/search',
        'priority': 5
    },
    'grailed': {
        'name': 'Grailed',
        'enabled': False,  # International site, disabled by default
        'base_url': 'https://www.grailed.com',
        'search_url': 'https://www.grailed.com/shop',
        'priority': 6
    },
    'sneaker_dunk': {
        'name': 'SneakerDunk',
        'enabled': False,  # Specialized site, disabled by default
        'base_url': 'https://snkrdunk.com',
        'search_url': 'https://snkrdunk.com/search',
        'priority': 7
    }
}

# Combined sites configuration
ALL_SITES = {**SIMPLE_SITES, **DYNAMIC_SITES}

# Default enabled sites (only Japanese mainstream sites)
DEFAULT_ENABLED_SITES = ['yahoo_auctions', 'yahoo_flea_market', 'yahoo_shopping', 'rakuten', 'mercari']

# =============================================================================
# SEARCH CONFIGURATION
# =============================================================================
# Default search parameters
DEFAULT_SEARCH_PARAMS = {
    'max_results_per_site': 50,
    'max_pages_per_site': 5,
    'timeout_seconds': 30,
    'sort_by': 'price_low_to_high',  # price_low_to_high, price_high_to_low, newest, relevance
    'include_sold_items': False,
    'min_price': 0,
    'max_price': 1000000,  # 1 million yen
    'currency': 'JPY'
}

# Default price range (user can input custom values)
DEFAULT_PRICE_RANGE = {
    'min': 0,
    'max': 1000000,  # 1 million yen
    'currency': 'JPY'
}

# =============================================================================
# SCRAPING CONFIGURATION
# =============================================================================
# Request delays to avoid being blocked (seconds)
REQUEST_DELAYS = {
    'simple_sites': {
        'min_delay': 1.0,
        'max_delay': 3.0,
        'between_pages': 2.0
    },
    'dynamic_sites': {
        'min_delay': 2.0,
        'max_delay': 5.0,
        'between_pages': 3.0,
        'page_load_timeout': 10.0
    }
}

# Maximum concurrent scrapers
MAX_CONCURRENT_SCRAPERS = 3

# Retry configuration
RETRY_CONFIG = {
    'max_retries': 3,
    'retry_delay': 5.0,
    'backoff_multiplier': 2.0
}

# Cache settings
CACHE_CONFIG = {
    'enabled': True,
    'search_results_ttl': 300,  # 5 minutes
    'images_ttl': 3600,  # 1 hour
    'max_cache_size_mb': 100
}

# =============================================================================
# GUI CONFIGURATION
# =============================================================================
# Window settings
WINDOW_CONFIG = {
    'title': APP_NAME,
    'width': 1200,
    'height': 800,
    'min_width': 800,
    'min_height': 600,
    'resizable': True,
    'theme': 'dark'  # 'dark', 'light', 'system'
}

# Tab configuration
TAB_CONFIG = {
    'default_tab': 'search',  # 'search', 'feed', 'favorites'
    'tab_names': ['Search', 'Feed', 'Favorites']
}

# Results display
RESULTS_DISPLAY = {
    'results_per_page': 20,
    'grid_columns': 4,
    'show_thumbnails': True,
    'thumbnail_size': (150, 150),
    'auto_refresh_interval': 300  # 5 minutes
}

# =============================================================================
# FEED AND MONITORING CONFIGURATION
# =============================================================================
# Feed update settings
FEED_CONFIG = {
    'update_interval_minutes': 15,
    'max_feed_items': 200,
    'keep_items_days': 7,
    'check_new_listings': True,
    'check_price_drops': True,
    'minimum_price_drop_percentage': 10.0
}

# Reserved search limits
RESERVED_SEARCH_LIMITS = {
    'max_saved_searches': 20,
    'max_price_alerts': 50,
    'alert_cooldown_minutes': 60  # Don't spam notifications
}

# =============================================================================
# NOTIFICATION CONFIGURATION
# =============================================================================
# Desktop notifications
DESKTOP_NOTIFICATIONS = {
    'enabled': True,
    'timeout_seconds': 10,
    'show_thumbnails': True
}

# Discord notifications
DISCORD_NOTIFICATIONS = {
    'enabled': False,  # User needs to configure webhook
    'webhook_url': '',  # User must set this
    'include_images': True,
    'max_message_length': 2000
}

# Notification triggers
NOTIFICATION_TRIGGERS = {
    'new_listings': True,
    'price_drops': True,
    'deals_threshold_percentage': 20.0,  # Notify for deals 20% or better
    'keywords_alerts': []  # User can add specific keywords
}

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
DATABASE_CONFIG = {
    'vacuum_interval_days': 7,  # Clean up database weekly
    'backup_enabled': True,
    'backup_interval_days': 1,
    'max_backups': 7
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================
LOGGING_CONFIG = {
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    'file_logging': True,
    'console_logging': True,
    'max_log_size_mb': 10,
    'backup_count': 5,
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

# =============================================================================
# DEVELOPMENT AND DEBUG SETTINGS
# =============================================================================
DEBUG_CONFIG = {
    'debug_mode': False,
    'save_raw_html': False,
    'detailed_logging': False,
    'skip_image_loading': False,
    'mock_scrapers': False  # Use fake data for testing
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_enabled_sites():
    """Get list of currently enabled sites."""
    return [site_id for site_id, config in ALL_SITES.items() if config['enabled']]

def get_site_config(site_id):
    """Get configuration for a specific site."""
    return ALL_SITES.get(site_id, {})

def is_site_enabled(site_id):
    """Check if a site is enabled."""
    return ALL_SITES.get(site_id, {}).get('enabled', False)

def get_sites_by_priority():
    """Get enabled sites sorted by priority."""
    enabled_sites = [(site_id, config) for site_id, config in ALL_SITES.items() if config['enabled']]
    return sorted(enabled_sites, key=lambda x: x[1]['priority'])

def update_site_status(site_id, enabled):
    """Enable or disable a site."""
    if site_id in ALL_SITES:
        ALL_SITES[site_id]['enabled'] = enabled
        return True
    return False 