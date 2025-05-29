"""
Database module for Market Search Tool
SQLite database operations and schema management.
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager

from config.settings import DATABASE_PATH, DATABASE_CONFIG

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for the Market Search Tool."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path or DATABASE_PATH
        self.ensure_database_exists()
        self.create_tables()
        self.create_indexes()
    
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
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
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
        """Create all database tables."""
        with self.get_connection() as conn:
            # Search results table - stores all found items
            conn.execute('''
                CREATE TABLE IF NOT EXISTS search_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price_value REAL,
                    currency TEXT DEFAULT 'JPY',
                    price_raw TEXT,
                    price_formatted TEXT,
                    url TEXT UNIQUE NOT NULL,
                    site TEXT NOT NULL,
                    image_url TEXT,
                    seller TEXT,
                    location TEXT,
                    condition TEXT,
                    shipping_info TEXT,  -- JSON string
                    search_query TEXT,   -- What search found this
                    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_available BOOLEAN DEFAULT 1,
                    hash TEXT  -- For duplicate detection
                )
            ''')
            
            # User favorites table - saved items
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id INTEGER NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    price_alert_threshold REAL,
                    is_purchased BOOLEAN DEFAULT 0,
                    FOREIGN KEY (result_id) REFERENCES search_results (id)
                        ON DELETE CASCADE
                )
            ''')
            
            # Saved searches table - feed monitoring
            conn.execute('''
                CREATE TABLE IF NOT EXISTS saved_searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,  -- User-friendly name
                    search_query TEXT NOT NULL,
                    enabled_sites TEXT,  -- JSON array of site IDs
                    min_price REAL,
                    max_price REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_run TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    notification_enabled BOOLEAN DEFAULT 1,
                    check_interval_minutes INTEGER DEFAULT 15
                )
            ''')
            
            # User settings table - app preferences
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    value_type TEXT DEFAULT 'string',  -- string, integer, boolean, json
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Price history table - track price changes
            conn.execute('''
                CREATE TABLE IF NOT EXISTS price_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id INTEGER NOT NULL,
                    price_value REAL NOT NULL,
                    currency TEXT DEFAULT 'JPY',
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (result_id) REFERENCES search_results (id)
                        ON DELETE CASCADE
                )
            ''')
            
            # Feed items table - new items from saved searches
            conn.execute('''
                CREATE TABLE IF NOT EXISTS feed_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    result_id INTEGER NOT NULL,
                    saved_search_id INTEGER NOT NULL,
                    is_new BOOLEAN DEFAULT 1,
                    is_price_drop BOOLEAN DEFAULT 0,
                    price_drop_percentage REAL,
                    added_to_feed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_read BOOLEAN DEFAULT 0,
                    FOREIGN KEY (result_id) REFERENCES search_results (id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (saved_search_id) REFERENCES saved_searches (id)
                        ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
    
    def create_indexes(self):
        """Create database indexes for performance."""
        with self.get_connection() as conn:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_search_results_query ON search_results(search_query)",
                "CREATE INDEX IF NOT EXISTS idx_search_results_site ON search_results(site)",
                "CREATE INDEX IF NOT EXISTS idx_search_results_price ON search_results(price_value)",
                "CREATE INDEX IF NOT EXISTS idx_search_results_found_at ON search_results(found_at)",
                "CREATE INDEX IF NOT EXISTS idx_search_results_url ON search_results(url)",
                "CREATE INDEX IF NOT EXISTS idx_search_results_hash ON search_results(hash)",
                "CREATE INDEX IF NOT EXISTS idx_price_history_result_id ON price_history(result_id)",
                "CREATE INDEX IF NOT EXISTS idx_price_history_recorded_at ON price_history(recorded_at)",
                "CREATE INDEX IF NOT EXISTS idx_user_favorites_result_id ON user_favorites(result_id)",
                "CREATE INDEX IF NOT EXISTS idx_feed_items_saved_search_id ON feed_items(saved_search_id)",
                "CREATE INDEX IF NOT EXISTS idx_feed_items_is_new ON feed_items(is_new)",
                "CREATE INDEX IF NOT EXISTS idx_saved_searches_is_active ON saved_searches(is_active)"
            ]
            
            for index_sql in indexes:
                conn.execute(index_sql)
            
            conn.commit()
    
    # =============================================================================
    # SEARCH RESULTS OPERATIONS
    # =============================================================================
    
    def insert_search_result(self, item: Dict[str, Any]) -> int:
        """
        Insert a search result into the database.
        
        Args:
            item: Standardized item dictionary
            
        Returns:
            ID of inserted item, or existing ID if duplicate
        """
        with self.get_connection() as conn:
            # Generate hash for duplicate detection
            item_hash = self._generate_item_hash(item)
            
            # Check if item already exists
            existing = conn.execute(
                "SELECT id FROM search_results WHERE url = ? OR hash = ?",
                (item['url'], item_hash)
            ).fetchone()
            
            if existing:
                # Update last_seen timestamp
                conn.execute(
                    "UPDATE search_results SET last_seen = CURRENT_TIMESTAMP WHERE id = ?",
                    (existing['id'],)
                )
                conn.commit()
                return existing['id']
            
            # Insert new item
            cursor = conn.execute('''
                INSERT INTO search_results 
                (title, price_value, currency, price_raw, price_formatted, url, site, 
                 image_url, seller, location, condition, shipping_info, search_query, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('title', ''),
                item.get('price_value'),
                item.get('currency', 'JPY'),
                item.get('price_raw', ''),
                item.get('price_formatted', ''),
                item['url'],
                item['site'],
                item.get('image_url', ''),
                item.get('seller', ''),
                item.get('location', ''),
                item.get('condition', ''),
                json.dumps(item.get('shipping', {})),
                item.get('search_query', ''),
                item_hash
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_search_results(self, query: str = None, site: str = None, 
                          limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        Get search results with optional filtering.
        
        Args:
            query: Filter by search query
            site: Filter by site
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of search result dictionaries
        """
        with self.get_connection() as conn:
            sql = "SELECT * FROM search_results WHERE is_available = 1"
            params = []
            
            if query:
                sql += " AND search_query LIKE ?"
                params.append(f"%{query}%")
            
            if site:
                sql += " AND site = ?"
                params.append(site)
            
            sql += " ORDER BY found_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            rows = conn.execute(sql, params).fetchall()
            return [dict(row) for row in rows]
    
    def update_item_availability(self, item_id: int, is_available: bool):
        """Update item availability status."""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE search_results SET is_available = ? WHERE id = ?",
                (is_available, item_id)
            )
            conn.commit()
    
    # =============================================================================
    # FAVORITES OPERATIONS
    # =============================================================================
    
    def add_to_favorites(self, result_id: int, notes: str = None, 
                        price_alert_threshold: float = None) -> int:
        """
        Add item to user favorites.
        
        Args:
            result_id: ID of search result
            notes: User notes
            price_alert_threshold: Price alert threshold
            
        Returns:
            ID of favorite entry
        """
        with self.get_connection() as conn:
            # Check if already favorited
            existing = conn.execute(
                "SELECT id FROM user_favorites WHERE result_id = ?",
                (result_id,)
            ).fetchone()
            
            if existing:
                return existing['id']
            
            cursor = conn.execute('''
                INSERT INTO user_favorites (result_id, notes, price_alert_threshold)
                VALUES (?, ?, ?)
            ''', (result_id, notes, price_alert_threshold))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_favorites(self) -> List[Dict]:
        """Get all user favorites with item details."""
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT f.*, r.title, r.price_value, r.price_formatted, r.url, 
                       r.site, r.image_url, r.is_available
                FROM user_favorites f
                JOIN search_results r ON f.result_id = r.id
                ORDER BY f.added_at DESC
            ''').fetchall()
            
            return [dict(row) for row in rows]
    
    def remove_from_favorites(self, favorite_id: int):
        """Remove item from favorites."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM user_favorites WHERE id = ?", (favorite_id,))
            conn.commit()
    
    def mark_as_purchased(self, favorite_id: int):
        """Mark favorite item as purchased."""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE user_favorites SET is_purchased = 1 WHERE id = ?",
                (favorite_id,)
            )
            conn.commit()
    
    # =============================================================================
    # SAVED SEARCHES OPERATIONS
    # =============================================================================
    
    def save_search(self, name: str, query: str, enabled_sites: List[str],
                   min_price: float = None, max_price: float = None) -> int:
        """
        Save a search for monitoring.
        
        Args:
            name: User-friendly name for the search
            query: Search query
            enabled_sites: List of site IDs to search
            min_price: Minimum price filter
            max_price: Maximum price filter
            
        Returns:
            ID of saved search
        """
        with self.get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO saved_searches 
                (name, search_query, enabled_sites, min_price, max_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, query, json.dumps(enabled_sites), min_price, max_price))
            
            conn.commit()
            return cursor.lastrowid
    
    def get_saved_searches(self, active_only: bool = True) -> List[Dict]:
        """Get saved searches."""
        with self.get_connection() as conn:
            sql = "SELECT * FROM saved_searches"
            if active_only:
                sql += " WHERE is_active = 1"
            sql += " ORDER BY created_at DESC"
            
            rows = conn.execute(sql).fetchall()
            searches = []
            
            for row in rows:
                search = dict(row)
                search['enabled_sites'] = json.loads(search['enabled_sites'])
                searches.append(search)
            
            return searches
    
    def update_saved_search_last_run(self, search_id: int):
        """Update last run timestamp for saved search."""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE saved_searches SET last_run = CURRENT_TIMESTAMP WHERE id = ?",
                (search_id,)
            )
            conn.commit()
    
    def delete_saved_search(self, search_id: int):
        """Delete a saved search."""
        with self.get_connection() as conn:
            conn.execute("DELETE FROM saved_searches WHERE id = ?", (search_id,))
            conn.commit()
    
    # =============================================================================
    # USER SETTINGS OPERATIONS
    # =============================================================================
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get user setting value."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT value, value_type FROM user_settings WHERE key = ?",
                (key,)
            ).fetchone()
            
            if not row:
                return default
            
            value, value_type = row['value'], row['value_type']
            
            # Convert based on type
            if value_type == 'boolean':
                return value.lower() == 'true'
            elif value_type == 'integer':
                return int(value)
            elif value_type == 'json':
                return json.loads(value)
            else:
                return value
    
    def set_setting(self, key: str, value: Any):
        """Set user setting value."""
        with self.get_connection() as conn:
            # Determine value type
            if isinstance(value, bool):
                value_type = 'boolean'
                value_str = str(value).lower()
            elif isinstance(value, int):
                value_type = 'integer'
                value_str = str(value)
            elif isinstance(value, (dict, list)):
                value_type = 'json'
                value_str = json.dumps(value)
            else:
                value_type = 'string'
                value_str = str(value)
            
            conn.execute('''
                INSERT OR REPLACE INTO user_settings (key, value, value_type, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (key, value_str, value_type))
            
            conn.commit()
    
    # =============================================================================
    # PRICE HISTORY OPERATIONS
    # =============================================================================
    
    def record_price_history(self, result_id: int, price_value: float, currency: str = 'JPY'):
        """Record price history for an item."""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO price_history (result_id, price_value, currency)
                VALUES (?, ?, ?)
            ''', (result_id, price_value, currency))
            conn.commit()
    
    def get_price_history(self, result_id: int) -> List[Dict]:
        """Get price history for an item."""
        with self.get_connection() as conn:
            rows = conn.execute('''
                SELECT * FROM price_history 
                WHERE result_id = ? 
                ORDER BY recorded_at ASC
            ''', (result_id,)).fetchall()
            
            return [dict(row) for row in rows]
    
    # =============================================================================
    # FEED OPERATIONS
    # =============================================================================
    
    def add_to_feed(self, result_id: int, saved_search_id: int, 
                   is_price_drop: bool = False, price_drop_percentage: float = None):
        """Add item to feed."""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO feed_items 
                (result_id, saved_search_id, is_price_drop, price_drop_percentage)
                VALUES (?, ?, ?, ?)
            ''', (result_id, saved_search_id, is_price_drop, price_drop_percentage))
            conn.commit()
    
    def get_feed_items(self, unread_only: bool = False, limit: int = 50) -> List[Dict]:
        """Get feed items with item details."""
        with self.get_connection() as conn:
            sql = '''
                SELECT f.*, r.title, r.price_value, r.price_formatted, r.url, 
                       r.site, r.image_url, s.name as search_name
                FROM feed_items f
                JOIN search_results r ON f.result_id = r.id
                JOIN saved_searches s ON f.saved_search_id = s.id
            '''
            
            if unread_only:
                sql += " WHERE f.is_read = 0"
            
            sql += " ORDER BY f.added_to_feed DESC LIMIT ?"
            
            rows = conn.execute(sql, (limit,)).fetchall()
            return [dict(row) for row in rows]
    
    def mark_feed_item_read(self, feed_item_id: int):
        """Mark feed item as read."""
        with self.get_connection() as conn:
            conn.execute(
                "UPDATE feed_items SET is_read = 1 WHERE id = ?",
                (feed_item_id,)
            )
            conn.commit()
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def _generate_item_hash(self, item: Dict[str, Any]) -> str:
        """Generate hash for duplicate detection."""
        import hashlib
        
        # Use title, site, and price for hash (normalize for comparison)
        title = item.get('title', '').lower().strip()
        site = item.get('site', '')
        price = str(item.get('price_value', ''))
        
        hash_string = f"{title}|{site}|{price}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def cleanup_old_data(self, days: int = 30):
        """Clean up old data from database."""
        with self.get_connection() as conn:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Remove old search results that aren't favorited
            conn.execute('''
                DELETE FROM search_results 
                WHERE found_at < ? 
                AND id NOT IN (SELECT result_id FROM user_favorites)
            ''', (cutoff_date,))
            
            # Remove old feed items
            conn.execute('''
                DELETE FROM feed_items 
                WHERE added_to_feed < ?
            ''', (cutoff_date,))
            
            # Clean up price history older than 90 days
            old_cutoff = datetime.now() - timedelta(days=90)
            conn.execute('''
                DELETE FROM price_history 
                WHERE recorded_at < ?
            ''', (old_cutoff,))
            
            conn.commit()
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics."""
        with self.get_connection() as conn:
            stats = {}
            
            tables = ['search_results', 'user_favorites', 'saved_searches', 
                     'user_settings', 'price_history', 'feed_items']
            
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                stats[table] = count
            
            return stats
    
    def vacuum_database(self):
        """Optimize database by running VACUUM."""
        with self.get_connection() as conn:
            conn.execute("VACUUM")


# Global database instance
db = DatabaseManager()

# Convenience functions for easy access
def get_search_results(*args, **kwargs):
    return db.get_search_results(*args, **kwargs)

def insert_search_result(*args, **kwargs):
    return db.insert_search_result(*args, **kwargs)

def add_to_favorites(*args, **kwargs):
    return db.add_to_favorites(*args, **kwargs)

def get_favorites(*args, **kwargs):
    return db.get_favorites(*args, **kwargs)

def save_search(*args, **kwargs):
    return db.save_search(*args, **kwargs)

def get_saved_searches(*args, **kwargs):
    return db.get_saved_searches(*args, **kwargs)

def get_setting(*args, **kwargs):
    return db.get_setting(*args, **kwargs)

def set_setting(*args, **kwargs):
    return db.set_setting(*args, **kwargs) 