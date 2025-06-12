"""
Database module for Market Search Tool
SQLite database operations for storing scraped items.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from contextlib import contextmanager
import json

# Configure logging
logger = logging.getLogger(__name__)

# SQL Query Constants
CREATE_TABLES = {
    'search_results': '''
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
    ''',
    'saved_searches': '''
        CREATE TABLE IF NOT EXISTS saved_searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            options_json TEXT NOT NULL,
            name TEXT,
            notifications_enabled BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    'saved_search_items': '''
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
    ''',
    'new_items': '''
        CREATE TABLE IF NOT EXISTS new_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            saved_search_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            price_value REAL,
            currency TEXT DEFAULT 'JPY',
            price_formatted TEXT,
            url TEXT NOT NULL,
            site TEXT NOT NULL,
            image_url TEXT,
            seller TEXT,
            location TEXT,
            condition TEXT,
            shipping_info TEXT,
            found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_viewed BOOLEAN DEFAULT 0,
            FOREIGN KEY(saved_search_id) REFERENCES saved_searches(id) ON DELETE CASCADE
        )
    ''',
    'settings': '''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    '''
}

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_search_results_url ON search_results(url)",
    "CREATE INDEX IF NOT EXISTS idx_search_results_site ON search_results(site)",
    "CREATE INDEX IF NOT EXISTS idx_search_results_query ON search_results(search_query)",
    "CREATE INDEX IF NOT EXISTS idx_search_results_price ON search_results(price_value)",
    "CREATE INDEX IF NOT EXISTS idx_new_items_saved_search ON new_items(saved_search_id)",
    "CREATE INDEX IF NOT EXISTS idx_new_items_found_at ON new_items(found_at)"
]

class QueryBuilder:
    """Helper class for building SQL queries with proper parameter handling."""
    
    def __init__(self, base_query: str):
        self.query = base_query
        self.params: List[Any] = []
        self.where_clauses: List[str] = []
        self.order_by: Optional[str] = None
        self.limit: Optional[int] = None
        self.offset: Optional[int] = None
    
    def add_where(self, condition: str, *params: Any) -> 'QueryBuilder':
        """Add a WHERE clause to the query."""
        self.where_clauses.append(condition)
        self.params.extend(params)
        return self
    
    def add_order_by(self, column: str, order: str = "ASC") -> 'QueryBuilder':
        """Add ORDER BY clause to the query."""
        if column in {"price_value", "found_at", "title", "site"}:
            order = order.upper() if order.upper() in {"ASC", "DESC"} else "ASC"
            self.order_by = f"ORDER BY {column} {order}"
        return self
    
    def add_pagination(self, limit: int, offset: int = 0) -> 'QueryBuilder':
        """Add LIMIT and OFFSET to the query."""
        self.limit = limit
        self.offset = offset
        return self
    
    def build(self) -> tuple[str, List[Any]]:
        """Build the final query with all clauses."""
        query = self.query
        
        if self.where_clauses:
            query += " WHERE " + " AND ".join(self.where_clauses)
        
        if self.order_by:
            query += f" {self.order_by}"
        
        if self.limit is not None:
            query += f" LIMIT {self.limit}"
            if self.offset is not None:
                query += f" OFFSET {self.offset}"
        
        return query, self.params

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
            # Create all tables
            for table_name, create_sql in CREATE_TABLES.items():
                conn.execute(create_sql)
            
            # Create all indexes
            for index_sql in CREATE_INDEXES:
                conn.execute(index_sql)
            
            # Add notifications_enabled column if it doesn't exist
            try:
                conn.execute("ALTER TABLE saved_searches ADD COLUMN notifications_enabled BOOLEAN DEFAULT 0")
                logger.info("Added notifications_enabled column to saved_searches table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e):
                    raise
                logger.debug("notifications_enabled column already exists")
            
            conn.commit()
    
    def insert_items(self, items: List[Dict[str, Any]], search_query: str = None) -> int:
        """
        Insert multiple items into the database using batch operations.
        All items will be inserted as new entries, even if they have the same URL.
        
        Args:
            items: List of item dictionaries
            search_query: Optional search query that found these items
            
        Returns:
            Number of items inserted
        """
        if not items:
            return 0
            
        with self.get_connection() as conn:
            try:
                # Prepare batch insert
                values = []
                for item in items:
                    values.append((
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
                
                # Execute batch insert
                conn.executemany("""
                    INSERT INTO search_results (
                        title, price_value, currency, price_raw, price_formatted,
                        url, site, image_url, seller, location, condition,
                        shipping_info, search_query
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)
                
                inserted_count = len(items)
                logger.debug(f"Batch inserted {inserted_count} items")
                conn.commit()
                return inserted_count
                    
            except Exception as e:
                logger.error(f"Failed to batch insert items: {e}")
                conn.rollback()
                return 0
    
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
            # Build query using QueryBuilder
            query_builder = QueryBuilder("SELECT * FROM search_results")
            
            if query:
                query_builder.add_where("search_query = ?", query)
            
            if site:
                query_builder.add_where("site = ?", site)
            
            if sort_by:
                query_builder.add_order_by(sort_by, sort_order)
            else:
                query_builder.add_order_by("found_at", "DESC")
            
            query_builder.add_pagination(limit, offset)
            
            # Execute query
            sql, params = query_builder.build()
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
        """
        Create a new saved search.
        
        Args:
            options: Search options dictionary
            name: Optional name for the saved search
            
        Returns:
            ID of the created saved search
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.execute(
                    "INSERT INTO saved_searches (options_json, name) VALUES (?, ?)",
                    (json.dumps(options), name)
                )
                saved_search_id = cursor.lastrowid
                conn.commit()
                return saved_search_id
            except Exception as e:
                logger.error(f"Failed to create saved search: {e}")
                conn.rollback()
                return -1
    
    def update_saved_search_notifications(self, saved_search_id: int, enabled: bool) -> bool:
        """
        Update notification settings for a saved search.
        
        Args:
            saved_search_id: ID of the saved search
            enabled: Whether notifications should be enabled
            
        Returns:
            True if update was successful
        """
        with self.get_connection() as conn:
            try:
                conn.execute(
                    "UPDATE saved_searches SET notifications_enabled = ? WHERE id = ?",
                    (enabled, saved_search_id)
                )
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to update saved search notifications: {e}")
                conn.rollback()
                return False
    
    def add_saved_search_items(self, saved_search_id: int, items: list) -> int:
        """
        Add items to a saved search using batch operations.
        
        Args:
            saved_search_id: ID of the saved search
            items: List of item dictionaries
            
        Returns:
            Number of items added
        """
        if not items:
            return 0
            
        with self.get_connection() as conn:
            try:
                # Prepare batch insert
                values = []
                for item in items:
                    values.append((
                        saved_search_id,
                        item['title'],
                        item['price_value'],
                        item['url'],
                        item['site'],
                        item.get('image_url')
                    ))
                
                # Execute batch insert
                conn.executemany("""
                    INSERT OR IGNORE INTO saved_search_items 
                    (saved_search_id, title, price_value, url, site, image_url)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, values)
                
                added_count = len(items)
                logger.debug(f"Batch added {added_count} items to saved search {saved_search_id}")
                conn.commit()
                return added_count
                    
            except Exception as e:
                logger.error(f"Failed to batch add items to saved search: {e}")
                conn.rollback()
                return 0
    
    def get_saved_searches(self) -> List[Dict]:
        """
        Get all saved searches.
        
        Returns:
            List of saved search dictionaries
        """
        with self.get_connection() as conn:
            query_builder = QueryBuilder("SELECT * FROM saved_searches")
            query_builder.add_order_by("created_at", "DESC")
            
            sql, params = query_builder.build()
            rows = conn.execute(sql, params).fetchall()
            
            # Parse JSON options for each saved search
            saved_searches = []
            for row in rows:
                search = dict(row)
                search['options'] = json.loads(search['options_json'])
                del search['options_json']
                saved_searches.append(search)
            
            return saved_searches
    
    def get_saved_search_items(self, saved_search_id: int) -> List[Dict]:
        """
        Get items for a specific saved search.
        
        Args:
            saved_search_id: ID of the saved search
            
        Returns:
            List of item dictionaries
        """
        with self.get_connection() as conn:
            query_builder = QueryBuilder("SELECT * FROM saved_search_items")
            query_builder.add_where("saved_search_id = ?", saved_search_id)
            query_builder.add_order_by("found_at", "DESC")
            
            sql, params = query_builder.build()
            rows = conn.execute(sql, params).fetchall()
            return [dict(row) for row in rows]
    
    def delete_saved_search(self, saved_search_id: int) -> bool:
        """
        Delete a saved search and all its items.
        
        Args:
            saved_search_id: ID of the saved search to delete
            
        Returns:
            True if deletion was successful
        """
        with self.get_connection() as conn:
            try:
                # Delete will cascade to saved_search_items due to foreign key
                conn.execute("DELETE FROM saved_searches WHERE id = ?", (saved_search_id,))
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to delete saved search: {e}")
                conn.rollback()
                return False

    def add_new_items(self, saved_search_id: int, items: List[Dict[str, Any]]) -> int:
        """
        Add new items to the feed using batch operations.
        
        Args:
            saved_search_id: ID of the saved search that found these items
            items: List of item dictionaries
            
        Returns:
            Number of items added
        """
        if not items:
            return 0
            
        with self.get_connection() as conn:
            try:
                # Prepare batch insert
                values = []
                for item in items:
                    values.append((
                        saved_search_id,
                        item['title'],
                        item['price_value'],
                        item.get('currency', 'JPY'),
                        item['price_formatted'],
                        item['url'],
                        item['site'],
                        item.get('image_url'),
                        item.get('seller'),
                        item.get('location'),
                        item.get('condition'),
                        item.get('shipping_info', '{}')
                    ))
                
                # Execute batch insert
                conn.executemany("""
                    INSERT INTO new_items (
                        saved_search_id, title, price_value, currency, price_formatted,
                        url, site, image_url, seller, location, condition, shipping_info
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)
                
                added_count = len(items)
                logger.debug(f"Batch added {added_count} new items for saved search {saved_search_id}")
                conn.commit()
                return added_count
                    
            except Exception as e:
                logger.error(f"Failed to batch add new items: {e}")
                conn.rollback()
                return 0
    
    def get_new_items(self, limit: int = 10, offset: int = 0, site: str = None) -> Dict[str, List[Dict]]:
        """
        Get new items grouped by saved search.
        
        Args:
            limit: Maximum number of items per saved search
            offset: Number of items to skip
            site: Optional site filter
            
        Returns:
            Dictionary mapping saved search names to lists of items
        """
        with self.get_connection() as conn:
            # First get all saved searches with new items
            query_builder = QueryBuilder("""
                SELECT DISTINCT n.saved_search_id, COALESCE(s.name, 'Unnamed Search ' || s.id) as search_name
                FROM new_items n
                JOIN saved_searches s ON n.saved_search_id = s.id
                WHERE n.is_viewed = 0
            """)
            
            if site:
                query_builder.add_where("n.site = ?", site)
            
            sql, params = query_builder.build()
            saved_searches = [(row[0], row[1]) for row in conn.execute(sql, params).fetchall()]
            
            # Then get items for each saved search
            result = {}
            for saved_search_id, search_name in saved_searches:
                query_builder = QueryBuilder("""
                    SELECT * FROM new_items 
                    WHERE saved_search_id = ? AND is_viewed = 0
                """)
                
                if site:
                    query_builder.add_where("site = ?", site)
                
                query_builder.add_order_by("found_at", "DESC")
                query_builder.add_pagination(limit, offset)
                
                sql, params = query_builder.build()
                items = [dict(row) for row in conn.execute(sql, [saved_search_id] + params).fetchall()]
                
                if items:
                    result[search_name] = items
            
            return result
    
    def mark_items_as_viewed(self, item_ids: List[int]) -> None:
        """
        Mark items as viewed in the feed.
        
        Args:
            item_ids: List of item IDs to mark as viewed
        """
        if not item_ids:
            return
            
        with self.get_connection() as conn:
            try:
                # Use batch update for better performance
                placeholders = ','.join('?' * len(item_ids))
                conn.execute(
                    f"UPDATE new_items SET is_viewed = 1 WHERE id IN ({placeholders})",
                    item_ids
                )
                conn.commit()
            except Exception as e:
                logger.error(f"Failed to mark items as viewed: {e}")
                conn.rollback()
    
    def get_new_items_count(self, site: str = None) -> Dict[str, int]:
        """
        Get count of new items per saved search.
        
        Args:
            site: Optional site filter
            
        Returns:
            Dictionary mapping saved search names to item counts
        """
        with self.get_connection() as conn:
            query_builder = QueryBuilder("""
                SELECT COALESCE(s.name, 'Unnamed Search ' || s.id) as search_name, COUNT(*) as count 
                FROM new_items n
                JOIN saved_searches s ON n.saved_search_id = s.id
                WHERE n.is_viewed = 0
            """)
            
            if site:
                query_builder.add_where("n.site = ?", site)
            
            query_builder.add_where("GROUP BY s.id, s.name")
            
            sql, params = query_builder.build()
            rows = conn.execute(sql, params).fetchall()
            
            return {row['search_name']: row['count'] for row in rows}

# Create a global instance for easy access
db = DatabaseManager()

# Type aliases for better readability
ItemDict = Dict[str, Any]
ItemList = List[ItemDict]
SavedSearchDict = Dict[str, Any]
SavedSearchList = List[SavedSearchDict]

def insert_items(items: ItemList, search_query: Optional[str] = None) -> int:
    """
    Insert multiple items into the database.
    
    Args:
        items: List of item dictionaries
        search_query: Optional search query that found these items
        
    Returns:
        Number of items inserted
    """
    return db.insert_items(items, search_query)

def get_search_results(
    query: Optional[str] = None,
    site: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> ItemList:
    """
    Get search results with optional filtering and sorting.
    
    Args:
        query: Filter by search query
        site: Filter by site
        limit: Maximum number of results
        offset: Number of results to skip
        sort_by: Column to sort by
        sort_order: Sort order ('asc' or 'desc')
        
    Returns:
        List of search result dictionaries
    """
    return db.get_search_results(query, site, limit, offset, sort_by, sort_order)

def get_database_stats() -> Dict[str, int]:
    """
    Get database statistics.
    
    Returns:
        Dictionary of database statistics
    """
    return db.get_database_stats()

def get_setting(key: str, default: Any = None) -> Any:
    """
    Get a setting value.
    
    Args:
        key: Setting key
        default: Default value if setting not found
        
    Returns:
        Setting value or default
    """
    return db.get_setting(key, default)

def set_setting(key: str, value: Any) -> None:
    """
    Set a setting value.
    
    Args:
        key: Setting key
        value: Setting value
    """
    db.set_setting(key, value)

def item_exists(title: str, price_value: float) -> bool:
    """
    Check if an item exists in the database.
    
    Args:
        title: Item title
        price_value: Item price
        
    Returns:
        True if item exists
    """
    return db.item_exists(title, price_value)

def create_saved_search(options: Dict[str, Any], name: Optional[str] = None) -> int:
    """
    Create a new saved search.
    
    Args:
        options: Search options dictionary
        name: Optional name for the saved search
        
    Returns:
        ID of the created saved search
    """
    return db.create_saved_search(options, name)

def update_saved_search_notifications(saved_search_id: int, enabled: bool) -> bool:
    """
    Update notification settings for a saved search.
    
    Args:
        saved_search_id: ID of the saved search
        enabled: Whether notifications should be enabled
        
    Returns:
        True if update was successful
    """
    return db.update_saved_search_notifications(saved_search_id, enabled)

def add_saved_search_items(saved_search_id: int, items: ItemList) -> int:
    """
    Add items to a saved search.
    
    Args:
        saved_search_id: ID of the saved search
        items: List of item dictionaries
        
    Returns:
        Number of items added
    """
    return db.add_saved_search_items(saved_search_id, items)

def get_saved_searches() -> SavedSearchList:
    """
    Get all saved searches.
    
    Returns:
        List of saved search dictionaries
    """
    return db.get_saved_searches()

def get_saved_search_items(saved_search_id: int) -> ItemList:
    """
    Get items for a specific saved search.
    
    Args:
        saved_search_id: ID of the saved search
        
    Returns:
        List of item dictionaries
    """
    return db.get_saved_search_items(saved_search_id)

def delete_saved_search(saved_search_id: int) -> bool:
    """
    Delete a saved search and all its items.
    
    Args:
        saved_search_id: ID of the saved search to delete
        
    Returns:
        True if deletion was successful
    """
    return db.delete_saved_search(saved_search_id)

def get_new_items(
    limit: int = 10,
    offset: int = 0,
    site: Optional[str] = None
) -> Dict[str, ItemList]:
    """
    Get new items grouped by saved search.
    
    Args:
        limit: Maximum number of items per saved search
        offset: Number of items to skip
        site: Optional site filter
        
    Returns:
        Dictionary mapping saved search names to lists of items
    """
    return db.get_new_items(limit, offset, site)

def mark_items_as_viewed(item_ids: List[int]) -> None:
    """
    Mark items as viewed in the feed.
    
    Args:
        item_ids: List of item IDs to mark as viewed
    """
    db.mark_items_as_viewed(item_ids)

def get_new_items_count(site: Optional[str] = None) -> Dict[str, int]:
    """
    Get count of new items per saved search.
    
    Args:
        site: Optional site filter
        
    Returns:
        Dictionary mapping saved search names to item counts
    """
    return db.get_new_items_count(site)

def add_new_items(saved_search_id: int, items: ItemList) -> int:
    """
    Add new items to the feed.
    
    Args:
        saved_search_id: ID of the saved search that found these items
        items: List of item dictionaries
        
    Returns:
        Number of items added
    """
    return db.add_new_items(saved_search_id, items) 