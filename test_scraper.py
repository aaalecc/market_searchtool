"""
Test script for Yahoo Auctions scraper.
"""

import json
from datetime import datetime
from scrapers.yahoo_auctions import YahooAuctionsScraper
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def format_price(price: float) -> str:
    """Format price with yen symbol and commas."""
    return f"¥{price:,.0f}"

def main():
    # Initialize scraper
    scraper = YahooAuctionsScraper()
    
    try:
        # Test search parameters
        keywords = ['ディグダ', 'カード']  # Example: Pokemon cards
        min_price = 1000  # ¥1,000
        max_price = 10000  # ¥10,000
        
        print(f"\nSearching Yahoo Auctions for: {', '.join(keywords)}")
        print(f"Price range: {format_price(min_price)} - {format_price(max_price)}")
        print("\nFetching results...\n")
        
        # Perform search
        results = scraper.search(
            keywords=keywords,
            min_price=min_price,
            max_price=max_price
        )
        
        # Display results
        if results:
            print(f"Found {len(results)} items:\n")
            
            for i, item in enumerate(results, 1):
                print(f"Item {i}:")
                print(f"Title: {item['title']}")
                print(f"Price: {format_price(item['price'])}")
                print(f"Bids: {item['bid_count']}")
                print(f"End Time: {item['end_time']}")
                print(f"URL: {item['url']}")
                if item['image_url']:
                    print(f"Image: {item['image_url']}")
                print("-" * 80)
            
            # Save results to JSON file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"yahoo_auctions_results_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\nResults saved to: {filename}")
            
        else:
            print("No results found.")
            
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    finally:
        # Cleanup
        scraper.cleanup()

if __name__ == "__main__":
    main() 