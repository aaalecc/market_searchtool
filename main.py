"""
Market Search Tool - Main Application Entry Point
Initializes the application and starts the GUI.
"""

import sys
import os
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Add the project root to the path so we can import our modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our modules
from config.settings import (
    APP_NAME, APP_VERSION, LOGGING_CONFIG, DEBUG_CONFIG,
    WINDOW_CONFIG, DATABASE_CONFIG
)
from core.database import db
from core.image_cache import get_image_cache, shutdown_image_cache
from gui.main_window import MainWindow

def setup_logging():
    """Configure application logging."""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    log_filename = f"market_search_{datetime.now().strftime('%Y%m%d')}.log"
    log_file = log_dir / log_filename
    
    # Configure logging
    log_level = getattr(logging, LOGGING_CONFIG['level'].upper())
    
    # Create formatters
    formatter = logging.Formatter(LOGGING_CONFIG['log_format'])
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if LOGGING_CONFIG['console_logging']:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        # Attempt to set encoding for the stream if possible (Python 3.7+ for StreamHandler)
        try:
            console_handler.stream.reconfigure(encoding='utf-8')
        except AttributeError:
            # Fallback for older versions or if reconfigure is not available
            # This might mean console encoding issues persist on some systems
            pass 
        root_logger.addHandler(console_handler)
    
    # File handler
    if LOGGING_CONFIG['file_logging']:
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=LOGGING_CONFIG['max_log_size_mb'] * 1024 * 1024,
            backupCount=LOGGING_CONFIG['backup_count'],
            encoding='utf-8'  # Explicitly set UTF-8 for file handler too
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"=== {APP_NAME} v{APP_VERSION} Starting ===")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Project root: {project_root}")
    
    return logger

def check_dependencies():
    """Check if all required dependencies are available."""
    logger = logging.getLogger(__name__)
    
    required_packages = [
        'requests', 'beautifulsoup4', 'lxml', 'selenium', 
        'webdriver_manager', 'APScheduler', 'plyer', 
        'discord_webhook', 'customtkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'discord_webhook':
                import discord_webhook
            elif package == 'webdriver_manager':
                import webdriver_manager
            elif package == 'beautifulsoup4':
                import bs4
            elif package == 'APScheduler':
                import apscheduler
            else:
                __import__(package)
            logger.debug(f"✓ {package} is available")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"✗ {package} is missing")
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.error("Please install them with: pip install -r requirements.txt")
        return False
    
    logger.info("All required dependencies are available")
    return True

def initialize_database():
    """Initialize the database and perform any necessary migrations."""
    logger = logging.getLogger(__name__)
    
    try:
        # Database is automatically initialized when imported
        stats = db.get_database_stats()
        logger.info(f"Database initialized successfully: {stats}")
        return True
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

def initialize_image_cache():
    """Initialize the image cache system."""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize image cache
        image_cache = get_image_cache()
        stats = image_cache.get_cache_stats()
        logger.info(f"Image cache initialized successfully: {stats}")
        return True
    except Exception as e:
        logger.error(f"Image cache initialization failed: {e}")
        return False

def setup_default_settings():
    """Setup default application settings if they don't exist."""
    logger = logging.getLogger(__name__)
    
    try:
        from core.database import get_setting, set_setting
        
        # Check if this is first run
        first_run = get_setting('first_run', True)
        
        if first_run:
            logger.info("First run detected, setting up default settings...")
            
            # Set default settings
            default_settings = {
                'first_run': False,
                'theme': WINDOW_CONFIG['theme'],
                'discord_notifications_enabled': False,
                'desktop_notifications_enabled': True,
                'default_enabled_sites': ['yahoo_auctions', 'yahoo_flea_market', 'rakuten', 'mercari'],
                'results_per_page': 20,
                'auto_refresh_interval': 300,
                'last_cleanup': datetime.now().isoformat()
            }
            
            for key, value in default_settings.items():
                set_setting(key, value)
                logger.debug(f"Set default setting: {key} = {value}")
            
            logger.info("Default settings configured successfully")
        else:
            logger.info("Existing settings found, skipping default setup")
            
        return True
    except Exception as e:
        logger.error(f"Failed to setup default settings: {e}")
        return False

def create_application():
    """Create and configure the main application."""
    logger = logging.getLogger(__name__)
    
    try:
        # Create the main window
        logger.info("Creating main application window...")
        app = MainWindow()
        
        # Configure window properties from settings
        app.title(WINDOW_CONFIG['title'])
        app.geometry(f"{WINDOW_CONFIG['width']}x{WINDOW_CONFIG['height']}")
        app.minsize(WINDOW_CONFIG['min_width'], WINDOW_CONFIG['min_height'])
        app.resizable(WINDOW_CONFIG['resizable'], WINDOW_CONFIG['resizable'])
        
        logger.info("Application window created successfully")
        return app
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        return None

def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=f"{APP_NAME} v{APP_VERSION}")
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug mode')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
                       default=LOGGING_CONFIG['level'],
                       help='Set logging level')
    parser.add_argument('--no-gui', action='store_true',
                       help='Run in headless mode (for testing)')
    parser.add_argument('--version', action='version', 
                       version=f'{APP_NAME} {APP_VERSION}')
    
    args = parser.parse_args()
    
    # Override settings based on command line arguments
    if args.debug:
        DEBUG_CONFIG['debug_mode'] = True
        LOGGING_CONFIG['level'] = 'DEBUG'
    
    if args.log_level:
        LOGGING_CONFIG['level'] = args.log_level
    
    # Setup logging first
    logger = setup_logging()
    
    try:
        logger.info("Starting application initialization...")
        
        # Check dependencies
        if not check_dependencies():
            logger.error("Dependency check failed, exiting...")
            return 1
        
        # Initialize database
        if not initialize_database():
            logger.error("Database initialization failed, exiting...")
            return 1
        
        # Initialize image cache
        if not initialize_image_cache():
            logger.error("Image cache initialization failed, exiting...")
            return 1
        
        # Setup default settings
        if not setup_default_settings():
            logger.error("Settings initialization failed, exiting...")
            return 1
        
        # Create and start the application
        if args.no_gui:
            logger.info("Running in headless mode")
            # Could add CLI interface here for testing
            logger.info("Headless mode completed successfully")
            return 0
        else:
            app = create_application()
            if not app:
                logger.error("Application creation failed, exiting...")
                return 1
            
            logger.info("Starting GUI application...")
            
            # Start the application main loop
            app.mainloop()
            
            logger.info("Application closed successfully")
            return 0
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    finally:
        # Cleanup operations
        logger.info("Performing cleanup operations...")
        
        # Shutdown image cache
        try:
            shutdown_image_cache()
            logger.info("Image cache shutdown completed")
        except Exception as e:
            logger.error(f"Error during image cache shutdown: {e}")
        
        # You could add cleanup code here:
        # - Close database connections
        # - Stop background threads
        # - Save final settings
        
        logger.info(f"=== {APP_NAME} Shutdown Complete ===")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
