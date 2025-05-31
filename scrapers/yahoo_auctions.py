"""
Yahoo Auctions scraper with exact keyword matching and date filtering.
"""

import logging
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib.parse
import re
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config.scraping_config import (
    get_request_headers,
    SESSION_CONFIG,
    POOL_CONFIG,
    BURST_PROTECTION
)

logger = logging.getLogger(__name__)

class YahooAuctionsScraper:
    """Scraper for Yahoo Auctions with exact keyword matching."""
    
    BASE_URL = "https://auctions.yahoo.co.jp/search/search"
    
    def __init__(self):
        """Initialize the scraper with session and headers."""
        self.session = requests.Session()
        
        # Configure session with retry strategy
        retry_strategy = Retry(
            total=SESSION_CONFIG['max_retries'],
            backoff_factor=SESSION_CONFIG['backoff_factor'],
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=POOL_CONFIG['pool_connections'],
            pool_maxsize=POOL_CONFIG['pool_maxsize']
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set session timeout
        self.session.timeout = SESSION_CONFIG['timeout']
        
        # Track request timing for rate limiting
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()
    
    def _respect_rate_limits(self):
        """Implement rate limiting and burst protection."""
        current_time = time.time()
        
        # Check if we need to reset the request window
        if current_time - self.request_window_start >= 60:
            self.request_count = 0
            self.request_window_start = current_time
        
        # Check if we've exceeded the rate limit
        if self.request_count >= BURST_PROTECTION['max_requests_per_minute']:
            sleep_time = 60 - (current_time - self.request_window_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.request_count = 0
                self.request_window_start = time.time()
        
        # Ensure minimum delay between requests
        time_since_last = current_time - self.last_request_time
        if time_since_last < 3:  # Minimum 3 seconds between requests
            time.sleep(3 - time_since_last)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def search(self, keywords: List[str], min_price: Optional[int] = None, max_price: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search Yahoo Auctions for all listings, no time or category restrictions, both auction and set price.
        """
        try:
            self._respect_rate_limits()
            params = {
                'p': ' '.join(keywords),
                'va': ' '.join(keywords),
                'b': 1,
                'n': 100,
                'fixed': 3,  # Both auction and set price
                's1': 'new'  # Sort by newest listings
            }
            if min_price:
                params['aucminprice'] = str(min_price)
            if max_price:
                params['aucmaxprice'] = str(max_price)
            headers = get_request_headers(site_id='yahoo_auctions')
            response = self.session.get(
                self.BASE_URL,
                params=params,
                headers=headers,
                allow_redirects=SESSION_CONFIG['allow_redirects'],
                verify=SESSION_CONFIG['verify_ssl']
            )
            response.raise_for_status()
            search_url = response.url
            soup = BeautifulSoup(response.text, 'html.parser')
            items = []
            page = 1
            while True:
                for item in soup.select('li.Product'):
                    try:
                        title = item.select_one('.Product__title').text.strip()
                        price_text = item.select_one('.Product__price').text.strip()
                        price = self._normalize_price(price_text)
                        url = item.select_one('a')['href']
                        if not url.startswith('http'):
                            url = 'https://auctions.yahoo.co.jp' + url
                        img = item.select_one('img')
                        image_url = img['src'] if img else None
                        bid_count = 0
                        bid_text = item.select_one('.Product__bid')
                        if bid_text:
                            bid_match = re.search(r'(\d+)', bid_text.text)
                            if bid_match:
                                bid_count = int(bid_match.group(1))
                        # Get end time from the search results page
                        end_time = ''
                        end_time_elem = item.select_one('.Product__time')
                        if end_time_elem:
                            end_time = end_time_elem.text.strip()
                        # Determine if item is fixed price
                        is_fixed_price = end_time == ''
                        item_data = {
                            'id': url.split('/')[-1],
                            'title': title,
                            'price': price,
                            'url': url,
                            'image_url': image_url,
                            'end_time': end_time,
                            'bid_count': bid_count,
                            'is_fixed_price': is_fixed_price,
                            'source': 'Yahoo Auctions',
                            'timestamp': datetime.now().isoformat()
                        }
                        items.append(item_data)
                    except Exception as e:
                        logger.error(f"Error parsing item: {e}")
                        continue
                if not soup.select('li.Product'):
                    break
                page += 1
                params['b'] = (page - 1) * 100 + 1
                self._respect_rate_limits()
                response = self.session.get(
                    self.BASE_URL,
                    params=params,
                    headers=headers,
                    allow_redirects=SESSION_CONFIG['allow_redirects'],
                    verify=SESSION_CONFIG['verify_ssl']
                )
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
            return {
                'items': items,
                'search_url': search_url
            }
            
        except Exception as e:
            logger.error(f"Error in Yahoo Auctions search: {e}")
            if hasattr(e, 'response') and e.response.status_code == 429:
                # Rate limit hit, wait longer
                time.sleep(BURST_PROTECTION['cooldown_after_error'])
            return []
    
    def _normalize_price(self, price_str: str) -> float:
        """Convert price string to float value."""
        try:
            # Remove currency symbols, commas, and '円'
            price_str = price_str.replace('¥', '').replace(',', '').replace('円', '').strip()
            
            # Handle "現在" (current bid) format
            if '現在' in price_str:
                # Extract the number after "現在"
                price_match = re.search(r'現在\s*(\d+)', price_str)
                if price_match:
                    return float(price_match.group(1))
                return 0.0
            
            # Handle regular price format
            return float(price_str)
        except (ValueError, AttributeError) as e:
            logger.error(f"Error normalizing price '{price_str}': {e}")
            return 0.0
    
    def _parse_end_time(self, time_str: str) -> datetime:
        """Parse Japanese time format to datetime."""
        try:
            now = datetime.now()
            
            # Handle "X時間" format (X hours remaining)
            if '時間' in time_str:
                hours = int(re.search(r'(\d+)時間', time_str).group(1))
                return now + timedelta(hours=hours)
            
            # Handle "X分" format (X minutes remaining)
            if '分' in time_str:
                minutes = int(re.search(r'(\d+)分', time_str).group(1))
                return now + timedelta(minutes=minutes)
            
            # Handle "X日" format (X days remaining)
            if '日' in time_str:
                days = int(re.search(r'(\d+)日', time_str).group(1))
                return now + timedelta(days=days)
            
            # Handle "X月X日" format (specific date)
            if '月' in time_str and '日' in time_str:
                month = int(re.search(r'(\d+)月', time_str).group(1))
                day = int(re.search(r'(\d+)日', time_str).group(1))
                return datetime(now.year, month, day)
            
            # If no format matches, return current time
            return now
            
        except Exception as e:
            logger.error(f"Error parsing end time '{time_str}': {e}")
            return datetime.now()
    
    def cleanup(self):
        """Clean up resources."""
        if self.session:
            self.session.close() 