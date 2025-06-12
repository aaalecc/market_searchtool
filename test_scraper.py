"""
Test script for Yahoo Auctions scraper.
"""

from datetime import datetime
from scrapers.yahoo_auctions import YahooAuctionsScraper
import logging
import argparse
from core.database import DatabaseManager, item_exists, get_database_stats
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

def main():
    parser = argparse.ArgumentParser(description="Test script for market scrapers.")
    parser.add_argument('--sites', nargs='+', choices=['yahoo', 'rakuten'], required=True, help='Sites to scrape (yahoo, rakuten)')
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
                
                # Convert items to database format
                db_items = []
                for item in results['items']:
                    db_item = {
                        'title': item['title'],
                        'price_value': item['price'],
                        'currency': 'JPY',
                        'price_raw': str(item['price']),
                        'price_formatted': format_price(item['price']),
                        'url': item['url'],
                        'site': item.get('source', 'yahoo'),
                        'image_url': item.get('image_url'),
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
                db_items = []
                for item in results['items']:
                    db_item = {
                        'title': item['title'],
                        'price_value': item['price'],
                        'currency': 'JPY',
                        'price_raw': str(item['price']),
                        'price_formatted': format_price(item['price']),
                        'url': item['url'],
                        'site': 'rakuten',
                        'image_url': item.get('image_url'),
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

if __name__ == "__main__":
    main() 