"""
Desktop notifications using plyer
Handles system notifications for the Market Search Tool
"""

import logging
from plyer import notification
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def notify_scraper_results(search_results: List[Dict[str, Any]], total_new_items: int):
    """
    Send a desktop notification about scraper results.
    
    Args:
        search_results: List of dictionaries containing search results
            Each dict should have: search_name, items_added, current_total
        total_new_items: Total number of items in the new_items database
    """
    try:
        # Create notification title
        title = "Market Search Tool - スクレイピング完了"
        
        # Create notification message
        message_parts = []
        for result in search_results:
            search_name = result.get('search_name', 'Unknown Search')
            items_added = result.get('items_added', 0)
            current_total = result.get('current_total', 0)
            message_parts.append(
                f"{search_name}:\n"
                f"  新規追加: {items_added}件\n"
                f"  現在の総数: {current_total}件"
            )
        
        # Add total items count
        message_parts.append(f"\n全検索の新規アイテム総数: {total_new_items}件")
        
        # Join all parts with newlines
        message = "\n".join(message_parts)
        
        # Send notification
        notification.notify(
            title=title,
            message=message,
            app_name="Market Search Tool",
            timeout=15  # Show notification for 15 seconds
        )
        
        logger.info(f"Desktop notification sent: {title}")
        logger.debug(f"Notification details: {message}")
        
    except Exception as e:
        logger.error(f"Failed to send desktop notification: {e}") 