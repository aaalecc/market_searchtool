"""
Database module for Market Search Tool
SQLite database operations for storing scraped items.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import json

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
        """Create the search results table and saved search tables."""
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
            
            # Create saved_searches table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS saved_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    options_json TEXT NOT NULL,
                    name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create saved_search_items table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS saved_search_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    saved_search_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    price_value REAL,
                    url TEXT NOT NULL,
                    site TEXT NOT NULL,
                    image_url TEXT,
                    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(saved_search_id, title, price_value),
                    FOREIGN KEY(saved_search_id) REFERENCES saved_searches(id) ON DELETE CASCADE
                )
            ''')
            
            # Create settings table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                          limit: int = 50, offset: int = 0, sort_by: str = None, sort_order: str = "asc") -> List[Dict]:
        """
        Get search results with optional filtering and sorting.
        
        Args:
            query: Filter by search query
            site: Filter by site
            limit: Maximum number of results
            offset: Number of results to skip
            sort_by: Column to sort by (e.g., 'price_value')
            sort_order: 'asc' or 'desc'
        
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
            
            # Add sorting
            if sort_by in {"price_value", "found_at", "title", "site"}:
                order = sort_order.lower() if sort_order and sort_order.lower() in {"asc", "desc"} else "asc"
                sql += f" ORDER BY {sort_by} {order}"
            else:
                sql += " ORDER BY found_at DESC"
            
            sql += " LIMIT ? OFFSET ?"
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
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value from the database.
        
        Args:
            key: Setting key
            default: Default value if setting doesn't exist
            
        Returns:
            Setting value or default
        """
        with self.get_connection() as conn:
            result = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            if result:
                return result['value']
            return default
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a setting value in the database.
        
        Args:
            key: Setting key
            value: Setting value
        """
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, str(value)))
            conn.commit()
    
    def item_exists(self, title: str, price_value: float) -> bool:
        normalized_title = title.strip().lower()
        rounded_price = round(price_value, 2) if price_value is not None else None
        with self.get_connection() as conn:
            result = conn.execute(
                "SELECT 1 FROM search_results WHERE LOWER(TRIM(title)) = ? AND ROUND(price_value, 2) = ? LIMIT 1",
                (normalized_title, rounded_price)
            ).fetchone()
            return result is not None

    def create_saved_search(self, options: dict, name: str = None) -> int:
        """Create a new saved search and return its ID."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO saved_searches (options_json, name) VALUES (?, ?)",
                (json.dumps(options, ensure_ascii=False), name)
            )
            conn.commit()
            logger.info(f"Saved search inserted: name={name}, options={options}, id={cursor.lastrowid}")
            return cursor.lastrowid

    def add_saved_search_items(self, saved_search_id: int, items: list):
        """Add items to a saved search, skipping duplicates by title and price_value."""
        with self.get_connection() as conn:
            for item in items:
                try:
                    conn.execute(
                        """INSERT OR IGNORE INTO saved_search_items
                           (saved_search_id, title, price_value, url, site, image_url)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (
                            saved_search_id,
                            item['title'],
                            item.get('price_value'),
                            item['url'],
                            item['site'],
                            item.get('image_url')
                        )
                    )
                except Exception as e:
                    continue
            conn.commit()

    def get_saved_searches(self):
        """Return all saved searches."""
        with self.get_connection() as conn:
            rows = conn.execute("SELECT * FROM saved_searches ORDER BY created_at DESC").fetchall()
            return [dict(row) for row in rows]

    def get_saved_search_items(self, saved_search_id: int):
        """Get all items for a saved search."""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM saved_search_items WHERE saved_search_id = ?",
                (saved_search_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def delete_saved_search(self, saved_search_id: int) -> bool:
        """
        Delete a saved search and its associated items.
        
        Args:
            saved_search_id: ID of the saved search to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                # The ON DELETE CASCADE in the saved_search_items table will automatically
                # delete associated items when the saved search is deleted
                conn.execute("DELETE FROM saved_searches WHERE id = ?", (saved_search_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to delete saved search {saved_search_id}: {e}")
            return False

# Create a global instance for easy access
db = DatabaseManager()

# Convenience functions
def insert_items(*args, **kwargs):
    return db.insert_items(*args, **kwargs)

def get_search_results(*args, **kwargs):
    return db.get_search_results(*args, **kwargs)

def get_database_stats():
    return db.get_database_stats() 

def get_setting(key: str, default: Any = None) -> Any:
    return db.get_setting(key, default)

def set_setting(key: str, value: Any) -> None:
    return db.set_setting(key, value)

def item_exists(title: str, price_value: float) -> bool:
    normalized_title = title.strip().lower()
    rounded_price = round(price_value, 2) if price_value is not None else None
    return db.item_exists(normalized_title, rounded_price)

def create_saved_search(options, name=None):
    return db.create_saved_search(options, name)

def add_saved_search_items(saved_search_id, items):
    return db.add_saved_search_items(saved_search_id, items)

def get_saved_searches():
    return db.get_saved_searches()

def get_saved_search_items(saved_search_id):
    """Get all items for a saved search."""
    return db.get_saved_search_items(saved_search_id)

def delete_saved_search(saved_search_id: int) -> bool:
    """Delete a saved search and its associated items."""
    return db.delete_saved_search(saved_search_id) 