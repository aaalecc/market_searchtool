"""
Script to display database contents and statistics.
"""

from core.database import get_search_results, get_database_stats

def main():
    # Get database statistics
    stats = get_database_stats()
    print("\nDatabase Statistics:")
    print(f"Total items: {stats['total_items']}")
    print(f"Yahoo Auctions items: {stats['yahoo_items']}")
    print(f"Rakuten items: {stats['rakuten_items']}")
    
    # Get and display recent items
    print("\nRecent Items:")
    items = get_search_results(limit=10)  # Get 10 most recent items
    
    for item in items:
        print("\n" + "="*80)
        print(f"Title: {item['title']}")
        print(f"Price: {item['price_formatted']}")
        print(f"Site: {item['site']}")
        print(f"URL: {item['url']}")
        print(f"Found at: {item['found_at']}")
        print(f"Last seen: {item['last_seen']}")

if __name__ == "__main__":
    main() 