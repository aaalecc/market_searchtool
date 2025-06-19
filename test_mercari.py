#!/usr/bin/env python3
"""
Test script for Mercari scraper
Simple test to verify the Mercari scraper works correctly.
"""

import sys
import os
import logging
from scrapers.mercari import MercariScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_mercari_scraper():
    """Test the Mercari scraper with a simple search."""
    print("Testing Mercari scraper...")
    
    # Create scraper instance
    scraper = MercariScraper(headless=True)
    
    try:
        # Test search
        results = scraper.search(
            keywords=['iPhone'],
            min_price=10000,
            max_price=50000
        )
        
        print(f"\nSearch completed!")
        print(f"Search URL: {results['search_url']}")
        print(f"Found {len(results['items'])} items")
        
        # Display first few items
        for i, item in enumerate(results['items'][:5]):
            print(f"\nItem {i+1}:")
            print(f"  Title: {item['title']}")
            print(f"  Price: ¥{item['price']:,}")
            print(f"  URL: {item['url']}")
            if item.get('image_url'):
                print(f"  Image: {item['image_url']}")
        
        if len(results['items']) > 5:
            print(f"\n... and {len(results['items']) - 5} more items")
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.cleanup()
        print("\nScraper cleanup completed")

if __name__ == "__main__":
    test_mercari_scraper() 