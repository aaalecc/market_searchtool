"""
Background task manager for Market Search Tool
Handles periodic searches and other background tasks
"""

import threading
import time
import logging
import subprocess
import sys
import json
import os
import shutil
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from core.database import get_saved_searches, get_saved_search_items, add_new_items, get_new_items_count
from notifications.desktop_notifier import notify_scraper_results

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

SNAPSHOT_DIR = 'snapshots'
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

class BackgroundTaskManager:
    """Manages background tasks like periodic searches."""
    
    def __init__(self):
        """Initialize the background task manager."""
        self.running = False
        self.thread = None
        self.search_interval = 1800  # 30 minutes in seconds
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
                logger.error(f"Error in background task: {e}", exc_info=True)
                time.sleep(5)  # Sleep longer on error
    
    def _read_items_from_db(self, db_path):
        items = []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM search_results").fetchall()
            for row in rows:
                items.append(dict(row))
            conn.close()
        except Exception as e:
            logger.error(f"Failed to read items from {db_path}: {e}")
        return items

    def _run_saved_searches(self):
        """Run all saved searches and check for new items."""
        logger.info("Starting to run saved searches...")
        all_saved_searches = get_saved_searches()
        active_searches = [s for s in all_saved_searches if s.get('notifications_enabled')]

        if not active_searches:
            logger.info("No saved searches with notifications enabled.")
            return

        search_results = []
        for search in active_searches:
            search_id = search['id']
            search_name = search.get('name', f"Search {search_id}")
            logger.info(f"\nProcessing saved search: {search_name} (ID: {search_id})")

            try:
                # Prepare snapshot db paths
                current_db = os.path.join(SNAPSHOT_DIR, f"saved_search_{search_id}_current.db")
                prev_db = os.path.join(SNAPSHOT_DIR, f"saved_search_{search_id}_prev.db")
                # Remove current_db if it exists
                if os.path.exists(current_db):
                    os.remove(current_db)
                
                # Get options directly from the search dictionary
                options = search.get('options', {})
                keywords = options.get('keywords', [])
                min_price = options.get('min_price', '')
                max_price = options.get('max_price', '')
                sites = options.get('sites', [])
                
                # Build command
                cmd = [sys.executable, "test_scraper.py", "--sites", *sites, "--keywords", *keywords]
                
                # Only add price parameters if they have values
                if min_price and min_price.strip():
                    cmd.extend(["--min-price", str(min_price)])
                if max_price and max_price.strip():
                    cmd.extend(["--max-price", str(max_price)])
                
                cmd.extend(["--db", current_db])
                
                logger.info(f"Running command: {' '.join(cmd)}")
                process = subprocess.run(cmd, capture_output=True)
                if process.returncode != 0:
                    logger.error(f"Scraper failed for {search_name}. STDERR: {process.stderr.decode(errors='replace')}")
                    continue
                # Read items from new snapshot db
                current_items = self._read_items_from_db(current_db)
                logger.info(f"Found {len(current_items)} items in current snapshot for {search_name}")
                # Read items from previous snapshot db or from saved_search_items if first run
                if os.path.exists(prev_db):
                    prev_items = self._read_items_from_db(prev_db)
                else:
                    prev_items = get_saved_search_items(search_id)
                prev_urls = {item['url'] for item in prev_items}
                new_items = [item for item in current_items if item['url'] not in prev_urls]
                logger.info(f"Detected {len(new_items)} new items for {search_name}")
                
                # Log the URLs of new items for debugging
                if new_items:
                    logger.info("New item URLs:")
                    for item in new_items:
                        logger.info(f"  - {item['url']}")
                
                # Add new items to feed
                if new_items:
                    added_count = add_new_items(search_id, new_items)
                    logger.info(f"Added {added_count} new items to feed for {search_name}")
                    # Get current total for this search
                    current_total = len(get_saved_search_items(search_id))
                    search_results.append({
                        'search_name': search_name,
                        'items_added': added_count,
                        'current_total': current_total
                    })
                # Replace previous snapshot
                if os.path.exists(prev_db):
                    os.remove(prev_db)
                shutil.move(current_db, prev_db)
            except Exception as e:
                logger.error(f"Error processing saved search {search_name}: {e}", exc_info=True)
                continue
        
        # Get total items count and send notification
        if search_results:
            total_items = sum(count['current_total'] for count in search_results)
            notify_scraper_results(search_results, total_items)
        else:
            logger.info("\nNo new items were added to the feed in any saved searches this cycle.")

# Create a global instance
task_manager = BackgroundTaskManager()

def start_background_tasks():
    """Start the background task manager."""
    task_manager.start()

def stop_background_tasks():
    """Stop the background task manager."""
    task_manager.stop() 