"""
Test script for Yahoo Auctions scraper.
"""

from datetime import datetime
from scrapers.yahoo_auctions import YahooAuctionsScraper
import logging
import argparse
from core.database import DatabaseManager, item_exists, get_database_stats
from core.image_cache import get_image_cache
import subprocess
import sys
import os
import time
from PIL import Image, ImageTk
import requests
from io import BytesIO

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def format_price(price: float) -> str:
    """Format price with yen symbol and commas."""
    return f"¥{price:,.0f}"

def process_images_for_items(items: list, db: DatabaseManager) -> list:
    """Pre-process images for items and update cached_image_path."""
    image_cache = get_image_cache()
    processed_items = []
    
    # Collect all image URLs for preloading
    image_urls = [item.get('image_url') for item in items if item.get('image_url')]
    if image_urls:
        print(f"Preloading {len(image_urls)} images...", file=sys.stderr)
        image_cache.preload_images(image_urls)
    
    for item in items:
        processed_item = item.copy()
        image_url = item.get('image_url')
        
        if image_url:
            # Try to get cached image path
            cached_path = image_cache.get_cached_image(image_url)
            if cached_path:
                processed_item['cached_image_path'] = cached_path
                print(f"Cached image: {image_url} -> {cached_path}", file=sys.stderr)
        
        processed_items.append(processed_item)
    
    return processed_items

def main():
    parser = argparse.ArgumentParser(description="Test script for market scrapers.")
    parser.add_argument('--sites', nargs='+', choices=['yahoo', 'rakuten', 'mercari'], required=True, help='Sites to scrape (yahoo, rakuten, mercari)')
    parser.add_argument('--min-price', type=int, default=0, help='Minimum price in JPY')
    parser.add_argument('--max-price', type=int, default=1000000, help='Maximum price in JPY')
    parser.add_argument('--keywords', nargs='+', default=[''], help='Search keywords')
    parser.add_argument('--db', type=str, default='data/market_search.db', help='Output database file')
    args = parser.parse_args()

    # Use command line arguments
    keywords = args.keywords
    min_price = args.min_price
    max_price = args.max_price
    search_query = ' '.join(keywords)
    db_path = args.db

    # Log search parameters
    print(f"\nSearch Parameters:", file=sys.stderr)
    print(f"Query: {search_query}", file=sys.stderr)
    print(f"Price Range: {format_price(min_price)} - {format_price(max_price)}", file=sys.stderr)
    print(f"Sites: {', '.join(args.sites)}", file=sys.stderr)
    print(f"Database: {db_path}\n", file=sys.stderr)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Use the specified database file
    db = DatabaseManager(db_path)

    # Clear old search results before starting any scraping
    print("Clearing old search results...", file=sys.stderr)
    db.clear_old_search_results()

    # Verify database is empty after clearing
    stats = db.get_database_stats()
    print(f"Database after clearing: {stats}", file=sys.stderr)

    search_options = {
        'keywords': keywords,
        'min_price': min_price,
        'max_price': max_price
    }

    results_all = []
    site_results = {}

    if 'yahoo' in args.sites:
        scraper = YahooAuctionsScraper()
        try:
            results = scraper.search(**search_options)
            if results['items']:
                print(f"Yahoo Auctions: Found {len(results['items'])} items", file=sys.stderr)
                print(f"Search URL: {results['search_url']}", file=sys.stderr)
                
                # Process images for Yahoo items
                processed_items = process_images_for_items(results['items'], db)
                
                # Convert items to database format
                db_items = []
                for item in processed_items:
                    db_item = {
                        'title': item['title'],
                        'price_value': item['price'],
                        'currency': 'JPY',
                        'price_raw': str(item['price']),
                        'price_formatted': format_price(item['price']),
                        'url': item['url'],
                        'site': item.get('source', 'yahoo'),
                        'image_url': item.get('image_url'),
                        'cached_image_path': item.get('cached_image_path'),
                        'seller': None,
                        'location': None,
                        'condition': None,
                        'shipping_info': '{}'
                    }
                    if not db.item_exists(db_item['title'], db_item['price_value']):
                        db_items.append(db_item)
                
                if db_items:
                    inserted_count = db.insert_items(db_items, search_query=search_query)
                    print(f"Yahoo Auctions: Inserted {inserted_count} new items into database", file=sys.stderr)
                    # Verify items were inserted
                    stats = db.get_database_stats()
                    print(f"Database after Yahoo insert: {stats}", file=sys.stderr)
                site_results['yahoo'] = results['items']
                results_all.extend(results['items'])
            else:
                print("Yahoo Auctions: No results found.", file=sys.stderr)
        except Exception as e:
            print(f"Error during Yahoo Auctions scraping: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        finally:
            scraper.cleanup()

    if 'rakuten' in args.sites:
        from scrapers.rakuten import RakutenScraper
        scraper = RakutenScraper()
        try:
            results = scraper.search(**search_options)
            if results['items']:
                print(f"Rakuten: Found {len(results['items'])} items", file=sys.stderr)
                print(f"Search URL: {results['search_url']}", file=sys.stderr)
                
                # Process images for Rakuten items
                processed_items = process_images_for_items(results['items'], db)
                
                db_items = []
                for item in processed_items:
                    db_item = {
                        'title': item['title'],
                        'price_value': item['price'],
                        'currency': 'JPY',
                        'price_raw': str(item['price']),
                        'price_formatted': format_price(item['price']),
                        'url': item['url'],
                        'site': 'rakuten',
                        'image_url': item.get('image_url'),
                        'cached_image_path': item.get('cached_image_path'),
                        'seller': None,
                        'location': None,
                        'condition': None,
                        'shipping_info': '{}'
                    }
                    if not db.item_exists(db_item['title'], db_item['price_value']):
                        db_items.append(db_item)
                if db_items:
                    inserted_count = db.insert_items(db_items, search_query=search_query)
                    print(f"Rakuten: Inserted {inserted_count} new items into database", file=sys.stderr)
                    # Verify items were inserted
                    stats = db.get_database_stats()
                    print(f"Database after Rakuten insert: {stats}", file=sys.stderr)
                site_results['rakuten'] = results['items']
                results_all.extend(results['items'])
            else:
                print("Rakuten: No results found.", file=sys.stderr)
        except Exception as e:
            print(f"Error during Rakuten scraping: {e}", file=sys.stderr)
        finally:
            scraper.cleanup()

    if 'mercari' in args.sites:
        from scrapers.mercari import MercariScraper
        print("Starting Mercari block...", file=sys.stderr)
        scraper = MercariScraper()
        try:
            print("Mercari: Starting Selenium-based scraping...", file=sys.stderr)
            results = scraper.search(**search_options)
            print(f"Mercari: Search finished, found {len(results['items']) if results and 'items' in results else 'NO RESULTS'} items", file=sys.stderr)
            if results['items']:
                print(f"Mercari: Found {len(results['items'])} items", file=sys.stderr)
                print(f"Search URL: {results['search_url']}", file=sys.stderr)
                print(f"---", file=sys.stderr)
                
                # Process images for Mercari items
                processed_items = process_images_for_items(results['items'], db)
                
                db_items = []
                for item in processed_items:
                    db_item = {
                        'title': item['title'],
                        'price_value': item['price'],
                        'currency': 'JPY',
                        'price_raw': str(item['price']),
                        'price_formatted': format_price(item['price']),
                        'url': item['url'],
                        'site': 'mercari',
                        'image_url': item.get('image_url'),
                        'cached_image_path': item.get('cached_image_path'),
                        'seller': None,
                        'location': None,
                        'condition': None,
                        'shipping_info': '{}'
                    }
                    if not db.item_exists(db_item['title'], db_item['price_value']):
                        db_items.append(db_item)
                if db_items:
                    inserted_count = db.insert_items(db_items, search_query=search_query)
                    print(f"Mercari: Inserted {inserted_count} new items into database", file=sys.stderr)
                    # Verify items were inserted
                    stats = db.get_database_stats()
                    print(f"Database after Mercari insert: {stats}", file=sys.stderr)
                site_results['mercari'] = results['items']
                results_all.extend(results['items'])
            else:
                print("Mercari: No results found.", file=sys.stderr)
        except Exception as e:
            print(f"Error during Mercari scraping: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
        finally:
            scraper.cleanup()
            print("Finished Mercari block.", file=sys.stderr)

    # Summary of all results
    print(f"\nSearch Results:", file=sys.stderr)
    print(f"Total items found: {len(results_all)}", file=sys.stderr)
    for site, items in site_results.items():
        print(f"{site.capitalize()}: {len(items)} items", file=sys.stderr)
    
    print(f"\nDatabase Statistics:", file=sys.stderr)
    stats = db.get_database_stats()
    print(f"Total items in database: {stats['total_items']}", file=sys.stderr)
    print(f"Yahoo items: {stats['yahoo_items']}", file=sys.stderr)
    print(f"Rakuten items: {stats['rakuten_items']}", file=sys.stderr)
    print(f"Mercari items: {stats['mercari_items']}", file=sys.stderr)

if __name__ == "__main__":
    main() 