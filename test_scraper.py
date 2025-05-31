"""
Test script for Yahoo Auctions scraper.
"""

from datetime import datetime
from scrapers.yahoo_auctions import YahooAuctionsScraper
import logging
import argparse
from core.database import insert_items, get_database_stats

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def format_price(price: float) -> str:
    """Format price with yen symbol and commas."""
    return f"¥{price:,.0f}"

def main():
    parser = argparse.ArgumentParser(description="Test script for market scrapers.")
    parser.add_argument('--sites', nargs='+', choices=['yahoo', 'rakuten'], required=True, help='Sites to scrape (yahoo, rakuten)')
    args = parser.parse_args()

    # Set search parameters directly here
    keywords = ['ディグダ', 'カード']
    min_price = 50
    max_price = 1000
    search_query = ' '.join(keywords)

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
            print(f"\nSearching Yahoo Auctions for: {', '.join(keywords)}")
            print(f"Price range: {format_price(min_price)} - {format_price(max_price)}")
            print("\nFetching results...\n")
            results = scraper.search(**search_options)
            if results['items']:
                print(f"Yahoo Auctions: Found {len(results['items'])} items")
                print(f"Search URL: {results['search_url']}")
                
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
                        'site': 'Yahoo Auctions',
                        'image_url': item.get('image_url'),
                        'seller': None,
                        'location': None,
                        'condition': None,
                        'shipping_info': '{}'
                    }
                    db_items.append(db_item)
                
                # Insert items into database
                inserted_count = insert_items(db_items, search_query=search_query)
                print(f"Yahoo Auctions: Inserted {inserted_count} new items into database")
                
                site_results['yahoo'] = results['items']
                results_all.extend(results['items'])
            else:
                print("Yahoo Auctions: No results found.")
        except Exception as e:
            print(f"Error during Yahoo Auctions scraping: {e}")
        finally:
            scraper.cleanup()

    if 'rakuten' in args.sites:
        from scrapers.rakuten import RakutenScraper
        scraper = RakutenScraper()
        try:
            print(f"\nSearching Rakuten for: {', '.join(keywords)}")
            print(f"Price range: {format_price(min_price)} - {format_price(max_price)}")
            print("\nFetching results...\n")
            results = scraper.search(**search_options)
            if results['items']:
                print(f"Rakuten: Found {len(results['items'])} items")
                print(f"Search URL: {results['search_url']}")
                
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
                        'site': 'Rakuten',
                        'image_url': item.get('image_url'),
                        'seller': None,
                        'location': None,
                        'condition': None,
                        'shipping_info': '{}'
                    }
                    db_items.append(db_item)
                
                # Insert items into database
                inserted_count = insert_items(db_items, search_query=search_query)
                print(f"Rakuten: Inserted {inserted_count} new items into database")
                
                site_results['rakuten'] = results['items']
                results_all.extend(results['items'])
            else:
                print("Rakuten: No results found.")
        except Exception as e:
            print(f"Error during Rakuten scraping: {e}")
        finally:
            scraper.cleanup()

    # Print database statistics
    stats = get_database_stats()
    print("\nDatabase Statistics:")
    print(f"Total items: {stats['total_items']}")
    print(f"Yahoo Auctions items: {stats['yahoo_items']}")
    print(f"Rakuten items: {stats['rakuten_items']}")

if __name__ == "__main__":
    main() 