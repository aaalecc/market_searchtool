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
        logger.info("Starting to run saved searches...")
        all_saved_searches = get_saved_searches()
        active_searches = [s for s in all_saved_searches if s.get('notifications_enabled')]

        if not active_searches:
            logger.info("No saved searches with notifications enabled.")
            return

        total_items_added_to_feed_this_cycle = 0

        for search in active_searches:
            search_id = search['id']
            search_name = search.get('name', f"Search {search_id}")
            logger.info(f"\nProcessing saved search: {search_name} (ID: {search_id})")

            try:
                if 'options_json' not in search or not search['options_json']:
                    logger.warning(f"Search '{search_name}' (ID: {search_id}) has no options_json or it is empty. Skipping.")
                    continue
                options_data = json.loads(search['options_json'])

                keywords = options_data.get('keywords', [])
                min_price = options_data.get('min_price', '') # Ensure default is string for str()
                max_price = options_data.get('max_price', '') # Ensure default is string for str()
                sites = options_data.get('sites', [])

                if not keywords or not sites:
                    logger.warning(f"Search '{search_name}' (ID: {search_id}) is missing keywords or sites. Skipping.")
                    continue

                logger.info(f"  Parameters: Keywords={keywords}, Price={min_price}-{max_price}, Sites={sites}")

                cmd = [sys.executable, "test_scraper.py", "--sites", *sites, "--keywords", *keywords]
                if min_price: # Only add if not empty
                    cmd.extend(["--min-price", str(min_price)])
                if max_price: # Only add if not empty
                    cmd.extend(["--max-price", str(max_price)])
                
                logger.info(f"Running command: {' '.join(cmd)}")
                
                # Capture raw bytes, do not decode at subprocess level initially
                process = subprocess.run(cmd, capture_output=True) 

                stdout_text = None
                stderr_text = None

                # Attempt to decode stdout and stderr using multiple encodings
                encodings_to_try = ['utf-8', 'shift_jis', 'cp932']
                if process.stdout:
                    for enc in encodings_to_try:
                        try:
                            stdout_text = process.stdout.decode(enc)
                            logger.debug(f"Successfully decoded stdout with {enc}")
                            break
                        except UnicodeDecodeError:
                            logger.debug(f"Failed to decode stdout with {enc}")
                            continue
                    if not stdout_text:
                        logger.warning(f"Could not decode stdout for {search_name} with any attempted encoding. Raw: {process.stdout[:100]}")
                        # Fallback or decide how to handle undecodable stdout, for now treat as no JSON output

                if process.stderr:
                    for enc in encodings_to_try:
                        try:
                            stderr_text = process.stderr.decode(enc)
                            logger.debug(f"Successfully decoded stderr with {enc}")
                            break
                        except UnicodeDecodeError:
                            logger.debug(f"Failed to decode stderr with {enc}")
                            continue
                    if not stderr_text:
                         logger.warning(f"Could not decode stderr for {search_name} with any attempted encoding. Raw: {process.stderr[:100]}")

                if process.returncode != 0:
                    logger.error(f"Error running test_scraper.py for {search_name}. Return code: {process.returncode}")
                    if stdout_text:
                        logger.error(f"Scraper STDOUT: {stdout_text}")
                    if stderr_text:
                        logger.error(f"Scraper STDERR: {stderr_text}")
                    continue

                if stdout_text:
                    logger.info(f"Scraper stdout for {search_name}:\n{stdout_text[:500].strip()}...")
                    try:
                        scraped_items = json.loads(stdout_text)
                        if isinstance(scraped_items, list):
                            if scraped_items:
                                items_added_count = add_new_items(search_id, scraped_items)
                                if items_added_count > 0:
                                    logger.info(f"Successfully added {items_added_count} new items to the feed for {search_name}.")
                                    total_items_added_to_feed_this_cycle += items_added_count
                                else:
                                    logger.info(f"No genuinely new items to add to feed for {search_name} from this scrape (already exist or filtered).")
                            else:
                                logger.info(f"Scraper returned an empty list of items for {search_name}.")
                        else:
                            logger.warning(f"Scraper output for {search_name} was not a JSON list as expected. Output: {stdout_text[:500].strip()}")
                    except json.JSONDecodeError as je:
                        logger.error(f"Failed to decode JSON output from scraper for {search_name}: {je}. Output: {stdout_text[:500].strip()}")
                else:
                    logger.info(f"No decoded output (stdout) from scraper for {search_name}.")
                
                if stderr_text:
                    logger.info(f"Scraper stderr for {search_name}:\n{stderr_text.strip()}")

            except Exception as e:
                logger.error(f"Error processing saved search {search_name}: {e}", exc_info=True)
                continue
        
        if total_items_added_to_feed_this_cycle > 0:
            logger.info(f"\nTotal new items added to feed this cycle: {total_items_added_to_feed_this_cycle}")
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