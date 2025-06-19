"""
Test script for cache cleanup when saved searches are deleted.
"""

import os
import sys
from core.image_cache import get_image_cache, shutdown_image_cache, cleanup_orphaned_cache_files
from core.database import DatabaseManager, delete_saved_search, create_saved_search, add_saved_search_items
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cache_cleanup():
    """Test cache cleanup when saved searches are deleted."""
    print("Testing cache cleanup functionality...")
    
    # Initialize image cache and database
    image_cache = get_image_cache()
    db = DatabaseManager()
    
    # Create a test saved search
    test_options = {
        'keywords': ['test', 'cache', 'cleanup'],
        'min_price': '1000',
        'max_price': '5000',
        'sites': ['yahoo']
    }
    
    saved_search_id = create_saved_search(test_options, "Test Cache Cleanup Search")
    print(f"Created test saved search with ID: {saved_search_id}")
    
    # Create test items with cached image paths
    test_items = [
        {
            'title': 'Test Item 1',
            'price_value': 1000,
            'currency': 'JPY',
            'price_raw': '1000',
            'price_formatted': '¥1,000',
            'url': 'https://example.com/item1',
            'site': 'test',
            'image_url': 'https://httpbin.org/image/png',
            'cached_image_path': 'data/image_cache/test_item_1.png',
            'seller': None,
            'location': None,
            'condition': None,
            'shipping_info': '{}'
        },
        {
            'title': 'Test Item 2',
            'price_value': 2000,
            'currency': 'JPY',
            'price_raw': '2000',
            'price_formatted': '¥2,000',
            'url': 'https://example.com/item2',
            'site': 'test',
            'image_url': 'https://httpbin.org/image/jpeg',
            'cached_image_path': 'data/image_cache/test_item_2.png',
            'seller': None,
            'location': None,
            'condition': None,
            'shipping_info': '{}'
        }
    ]
    
    # Add items to saved search
    added_count = add_saved_search_items(saved_search_id, test_items)
    print(f"Added {added_count} test items to saved search")
    
    # Create some fake cache files
    cache_dir = "data/image_cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    fake_cache_files = [
        'data/image_cache/test_item_1.png',
        'data/image_cache/test_item_2.png',
        'data/image_cache/orphaned_file.png'  # This should be cleaned up
    ]
    
    for cache_file in fake_cache_files:
        with open(cache_file, 'w') as f:
            f.write("fake image data")
        print(f"Created fake cache file: {cache_file}")
    
    # Check initial cache stats
    stats = image_cache.get_cache_stats()
    print(f"Initial cache stats: {stats}")
    
    # Delete the saved search
    print(f"\nDeleting saved search {saved_search_id}...")
    success = delete_saved_search(saved_search_id)
    print(f"Delete operation successful: {success}")
    
    # Check cache stats after deletion
    stats = image_cache.get_cache_stats()
    print(f"Cache stats after deletion: {stats}")
    
    # Test orphaned file cleanup
    print("\nTesting orphaned file cleanup...")
    orphaned_count = cleanup_orphaned_cache_files(db)
    print(f"Cleaned up {orphaned_count} orphaned files")
    
    # Final cache stats
    stats = image_cache.get_cache_stats()
    print(f"Final cache stats: {stats}")
    
    print("\nCache cleanup test completed!")

if __name__ == "__main__":
    try:
        test_cache_cleanup()
    finally:
        shutdown_image_cache() 