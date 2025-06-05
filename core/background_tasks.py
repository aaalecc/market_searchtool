"""
Background task manager for Market Search Tool
Handles periodic searches and other background tasks
"""

import threading
import time
import logging
import subprocess
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from core.database import get_saved_searches, add_new_items

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages background tasks like periodic searches."""
    
    def __init__(self):
        """Initialize the background task manager."""
        self.running = False
        self.thread = None
        self.search_interval = 300  # 5 minutes in seconds
        self.last_search_time = None
        logger.info("Background task manager initialized")
    
    def start(self):
        """Start the background task manager."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_periodic_tasks)
            self.thread.daemon = True
            self.thread.start()
            logger.info("Background task manager started")
            logger.info(f"Search interval set to {self.search_interval} seconds")
    
    def stop(self):
        """Stop the background task manager."""
        self.running = False
        if self.thread:
            self.thread.join()
            logger.info("Background task manager stopped")
    
    def _run_periodic_tasks(self):
        """Main loop for periodic tasks."""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check if it's time to run searches
                if (not self.last_search_time or 
                    (current_time - self.last_search_time) >= timedelta(seconds=self.search_interval)):
                    logger.info("=" * 50)
                    logger.info("Starting periodic search cycle")
                    logger.info(f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    self._run_saved_searches()
                    self.last_search_time = current_time
                    logger.info("Completed periodic search cycle")
                    logger.info("=" * 50)
                else:
                    time_until_next = timedelta(seconds=self.search_interval) - (current_time - self.last_search_time)
                    logger.debug(f"Next search in {time_until_next.total_seconds():.0f} seconds")
                
                # Sleep for a short time to prevent CPU overuse
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in background task: {e}")
                time.sleep(5)  # Sleep longer on error
    
    def _run_saved_searches(self):
        """Run all saved searches and check for new items."""
        logger.info("Running periodic saved searches...")
        
        saved_searches = get_saved_searches()
        logger.info(f"Found {len(saved_searches)} saved searches")
        
        new_items_by_search = {}  # Track new items by search
        total_new_items = 0
        
        for search in saved_searches:
            try:
                search_name = search.get('name', f'Search {search["id"]}')
                
                # Skip if notifications are disabled
                if not search.get('notifications_enabled', False):
                    logger.info(f"Skipping {search_name} (notifications disabled)")
                    continue
                
                logger.info(f"\nProcessing saved search: {search_name}")
                options = search['options']
                search_id = search['id']
                
                # Prepare sites list for test_scraper.py
                sites = []
                if 'Yahoo Auctions' in options.get('sites', []):
                    sites.append('yahoo')
                if 'Rakuten' in options.get('sites', []):
                    sites.append('rakuten')
                
                if not sites:
                    logger.info(f"No sites selected for {search_name}")
                    continue
                
                # Build command for test_scraper.py
                cmd = [
                    sys.executable,
                    "test_scraper.py",
                    "--sites",
                    *sites,
                    "--keywords",
                    *options.get('keywords', ['']),
                    "--min-price",
                    str(options.get('min_price', 0)),
                    "--max-price",
                    str(options.get('max_price', 1000000))
                ]
                
                logger.info(f"Running command: {' '.join(cmd)}")
                
                # Run test_scraper.py
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Log output
                if process.stdout:
                    logger.info("Test scraper output:")
                    for line in process.stdout.splitlines():
                        logger.info(line)
                
                if process.stderr:
                    logger.warning("Test scraper warnings/errors:")
                    for line in process.stderr.splitlines():
                        logger.warning(line)
                
                # Get database stats to determine new items
                from core.database import get_database_stats
                stats = get_database_stats()
                new_items = stats['total_items']
                
                if new_items > 0:
                    new_items_by_search[search_name] = new_items
                    total_new_items += new_items
                    logger.info(f"Found {new_items} new items for {search_name}")
                else:
                    logger.info(f"No new items found for {search_name}")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Error running test_scraper.py for {search_name}: {e}")
                if e.stdout:
                    logger.error(f"Output: {e.stdout}")
                if e.stderr:
                    logger.error(f"Errors: {e.stderr}")
            except Exception as e:
                logger.error(f"Error processing saved search {search_name}: {e}")
                continue
        
        # Report summary of new items by search
        if new_items_by_search:
            logger.info("\nSearch Summary:")
            logger.info("-" * 30)
            for search_name, count in new_items_by_search.items():
                logger.info(f"- {search_name}: {count} new items")
            logger.info("-" * 30)
            logger.info(f"Total new items found: {total_new_items}")
        else:
            logger.info("\nNo new items found in any saved searches")

# Create a global instance
task_manager = BackgroundTaskManager()

def start_background_tasks():
    """Start the background task manager."""
    task_manager.start()

def stop_background_tasks():
    """Stop the background task manager."""
    task_manager.stop() 