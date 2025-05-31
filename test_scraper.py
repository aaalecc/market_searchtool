"""
Test script for Yahoo Auctions scraper.
"""

import json
from datetime import datetime
from scrapers.yahoo_auctions import YahooAuctionsScraper
import logging
import argparse

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
                site_results['rakuten'] = results['items']
                results_all.extend(results['items'])
            else:
                print("Rakuten: No results found.")
        except Exception as e:
            print(f"Error during Rakuten scraping: {e}")
        finally:
            scraper.cleanup()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if len(args.sites) == 1:
        site = args.sites[0]
        filename = f"{site}_results_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(site_results[site], f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {filename}")
    else:
        filename = f"combined_results_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_all, f, ensure_ascii=False, indent=2)
        print(f"\nResults saved to: {filename}")

    # Print summary
    print("\nSummary:")
    total = 0
    for site in args.sites:
        count = len(site_results.get(site, []))
        print(f"{site.capitalize()}: {count} items")
        total += count
    print(f"Total: {total} items")

if __name__ == "__main__":
    main() 