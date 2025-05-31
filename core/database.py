"""
Database module for Market Search Tool
SQLite database operations for storing scraped items.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for scraped items."""
    
    def __init__(self, db_path: str = "data/market_search.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.ensure_database_exists()
        self.create_tables()
    
    def ensure_database_exists(self):
        """Create database directory if it doesn't exist."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def create_tables(self):
        """Create the search results table."""
        with self.get_connection() as conn:
            # Create table without any UNIQUE constraints
            conn.execute('''
                CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price_value REAL,
                    currency TEXT DEFAULT 'JPY',
                    price_raw TEXT,
                    price_formatted TEXT,
                    url TEXT NOT NULL,
                    site TEXT NOT NULL,
                    image_url TEXT,
                    seller TEXT,
                    location TEXT,
                    condition TEXT,
                    shipping_info TEXT,
                    search_query TEXT,
                    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_available BOOLEAN DEFAULT 1
                )
            ''')
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_results_url ON search_results(url)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_results_site ON search_results(site)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_results_query ON search_results(search_query)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_results_price ON search_results(price_value)")
            
            conn.commit()
    
    def insert_items(self, items: List[Dict[str, Any]], search_query: str = None) -> int:
        """
        Insert multiple items into the database.
        All items will be inserted as new entries, even if they have the same URL.
        
        Args:
            items: List of item dictionaries
            search_query: Optional search query that found these items
            
        Returns:
            Number of items inserted
        """
        inserted_count = 0
        with self.get_connection() as conn:
            for item in items:
                try:
                    # Insert new item
                    conn.execute("""
                        INSERT INTO search_results (
                            title, price_value, currency, price_raw, price_formatted,
                            url, site, image_url, seller, location, condition,
                            shipping_info, search_query
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item['title'],
                        item['price_value'],
                        item.get('currency', 'JPY'),
                        item['price_raw'],
                        item['price_formatted'],
                        item['url'],
                        item['site'],
                        item.get('image_url'),
                        item.get('seller'),
                        item.get('location'),
                        item.get('condition'),
                        item.get('shipping_info', '{}'),
                        search_query
                    ))
                    inserted_count += 1
                    logger.debug(f"Inserted item: {item['url']}")
                        
                except Exception as e:
                    logger.warning(f"Failed to insert item {item.get('url')}: {e}")
                    continue
            
            conn.commit()
        return inserted_count
    
    def get_search_results(self, query: str = None, site: str = None, 
                          limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Get search results with optional filtering.
        
        Args:
            query: Filter by search query
            site: Filter by site
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of search result dictionaries
        """
        with self.get_connection() as conn:
            sql = "SELECT * FROM search_results WHERE 1=1"
            params = []
            
            if query:
                sql += " AND search_query = ?"
                params.append(query)
            
            if site:
                sql += " AND site = ?"
                params.append(site)
            
            sql += " ORDER BY found_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            rows = conn.execute(sql, params).fetchall()
            return [dict(row) for row in rows]
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        with self.get_connection() as conn:
            stats = {
                'total_items': conn.execute("SELECT COUNT(*) FROM search_results").fetchone()[0],
                'yahoo_items': conn.execute("SELECT COUNT(*) FROM search_results WHERE site = 'Yahoo Auctions'").fetchone()[0],
                'rakuten_items': conn.execute("SELECT COUNT(*) FROM search_results WHERE site = 'Rakuten'").fetchone()[0]
            }
            return stats

# Create a global instance for easy access
db = DatabaseManager()

# Convenience functions
def insert_items(*args, **kwargs):
    return db.insert_items(*args, **kwargs)

def get_search_results(*args, **kwargs):
    return db.get_search_results(*args, **kwargs)

def get_database_stats():
    return db.get_database_stats() 