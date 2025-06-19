"""
Test script for image caching system.
"""

import os
import sys
from core.image_cache import get_image_cache, shutdown_image_cache
from core.database import DatabaseManager
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_image_cache():
    """Test the image caching system."""
    print("Testing image caching system...")
    
    # Initialize image cache
    image_cache = get_image_cache()
    
    # Test URLs (some sample product images)
    test_urls = [
        "https://httpbin.org/image/png",  # This should work
        "https://httpbin.org/image/jpeg",  # This should work
        "https://via.placeholder.com/300x200/FF0000/FFFFFF?text=Test+Image+1"  # This might fail
    ]
    
    print(f"Testing with {len(test_urls)} image URLs...")
    
    # Test synchronous caching
    for i, url in enumerate(test_urls):
        print(f"Testing image {i+1}: {url}")
        cached_path = image_cache.get_cached_image(url)
        if cached_path:
            print(f"  ✓ Cached successfully: {cached_path}")
            print(f"  ✓ File exists: {os.path.exists(cached_path)}")
        else:
            print(f"  ✗ Failed to cache: {url}")
    
    # Test preloading
    print("\nTesting preloading...")
    image_cache.preload_images(test_urls)
    
    # Test cache stats
    stats = image_cache.get_cache_stats()
    print(f"\nCache statistics:")
    print(f"  Files: {stats['file_count']}")
    print(f"  Size: {stats['total_size_mb']:.2f} MB")
    print(f"  Max size: {stats['max_size_mb']:.2f} MB")
    
    # Test with database integration
    print("\nTesting database integration...")
    db = DatabaseManager()
    
    # Create test items
    test_items = [
        {
            'title': 'Test Item 1',
            'price_value': 1000,
            'currency': 'JPY',
            'price_raw': '1000',
            'price_formatted': '¥1,000',
            'url': 'https://example.com/item1',
            'site': 'test',
            'image_url': test_urls[0],
            'seller': None,
            'location': None,
            'condition': None,
            'shipping_info': '{}'
        }
    ]
    
    # Process images for items
    from test_scraper import process_images_for_items
    processed_items = process_images_for_items(test_items, db)
    
    print(f"Processed {len(processed_items)} items")
    for item in processed_items:
        if item.get('cached_image_path'):
            print(f"  ✓ Item has cached image: {item['cached_image_path']}")
        else:
            print(f"  ✗ Item has no cached image")
    
    print("\nImage cache test completed!")

if __name__ == "__main__":
    try:
        test_image_cache()
    finally:
        shutdown_image_cache() 