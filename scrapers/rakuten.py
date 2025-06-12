"""
Rakuten scraper with robust anti-detection and standardized output, matching Yahoo Auctions scraper format.
"""

import logging
from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
from datetime import datetime
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

class RakutenScraper:
    """Scraper for Rakuten marketplace, matching Yahoo Auctions scraper format."""
    BASE_URL = "https://search.rakuten.co.jp/search/mall/"

    def __init__(self):
        self.session = requests.Session()
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
        self.session.timeout = SESSION_CONFIG['timeout']
        self.last_request_time = 0
        self.request_count = 0
        self.request_window_start = time.time()

    def _respect_rate_limits(self):
        current_time = time.time()
        if current_time - self.request_window_start >= 60:
            self.request_count = 0
            self.request_window_start = current_time
        if self.request_count >= BURST_PROTECTION['max_requests_per_minute']:
            sleep_time = 60 - (current_time - self.request_window_start)
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.request_count = 0
                self.request_window_start = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 1:
            time.sleep(1 - time_since_last)
        self.last_request_time = time.time()
        self.request_count += 1

    def search(self, keywords: List[str], min_price: Optional[int] = None, max_price: Optional[int] = None) -> Dict[str, Any]:
        """
        Search Rakuten for all listings matching the parameters, outputting standardized item dicts.
        """
        try:
            self._respect_rate_limits()
            # Join keywords with a full-width space
            query = '\u3000'.join(keywords)
            url = self.BASE_URL + query + '/'
            params = {
                'p': 1,
                's': 4  # Always sort by newest
            }
            if min_price is not None:
                url = url.rstrip('/') + f'/?min={int(min_price)}'
                logger.info(f"Rakuten: Setting min price filter: {min_price}")
            if max_price is not None:
                url = url.rstrip('/') + f'&max={int(max_price)}'
                logger.info(f"Rakuten: Setting max price filter: {max_price}")
            headers = get_request_headers(site_id='rakuten')
            logger.info(f"Rakuten: Search URL with params: {url}")
            response = self.session.get(url, params=params, headers=headers, allow_redirects=SESSION_CONFIG['allow_redirects'], verify=SESSION_CONFIG['verify_ssl'])
            response.raise_for_status()
            search_url = response.url
            soup = BeautifulSoup(response.text, 'html.parser')
            items = []

            # Find total number of pages
            pagination = soup.select_one('div.dui-pagination')
            total_pages = 1
            if pagination:
                page_links = pagination.find_all('a', class_=lambda c: c and 'item' in c)
                page_numbers = []
                for link in page_links:
                    try:
                        num = int(link.text.strip())
                        page_numbers.append(num)
                    except Exception:
                        continue
                if page_numbers:
                    total_pages = max(page_numbers)
            print(f"[DEBUG] Total pages detected: {total_pages}")
            logger.info(f"Rakuten: Total pages detected: {total_pages}")

            for page in range(1, total_pages + 1):
                params['p'] = page
                self._respect_rate_limits()
                response = self.session.get(search_url, params=params, headers=headers, allow_redirects=SESSION_CONFIG['allow_redirects'], verify=SESSION_CONFIG['verify_ssl'])
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                print(f"[DEBUG] Fetching page {page}")
                logger.info(f"Rakuten: Fetching page {page}/{total_pages}")
                page_item_count = 0
                for item in soup.select('div.searchresultitem, div.searchresultitem--grid, div.searchresultitem--list, div.dui-card'):
                    try:
                        # Title extraction (from <a> inside h2.title-link-wrapper--25--s)
                        title_elem = item.select_one('h2.title-link-wrapper--25--s a')
                        title = title_elem.text.strip() if title_elem else ''
                        # Robust price extraction: try multiple selectors
                        price = 0.0
                        price_selectors = [
                            'div.price--3zUvK.price-with-price-plus-shipping--Bmgz2',
                            'div.price--3zUvK',
                            'div.price-wrapper--10cCL'
                        ]
                        for sel in price_selectors:
                            price_elem = item.select_one(sel)
                            if price_elem:
                                price_text = price_elem.text.strip()
                                price = self._normalize_price(price_text)
                                if price > 0:
                                    break
                                    
                        # Skip items that don't match price criteria
                        if min_price is not None and price < min_price:
                            continue
                        if max_price is not None and price > max_price:
                            continue
                            
                        # URL and ID extraction
                        url_elem = item.select_one('h2.title-link-wrapper--25--s a')
                        url = url_elem['href'] if url_elem and url_elem.has_attr('href') else ''
                        if url and not url.startswith('http'):
                            url = 'https://search.rakuten.co.jp' + url
                        # Extract ID from data-item-id attribute if available, otherwise from URL
                        item_id = ''
                        data_item_id = item.get('data-item-id')
                        if data_item_id:
                            item_id = data_item_id
                        else:
                            id_match = re.search(r'/([0-9]+)(?:-[0-9]+)?/', url)
                            item_id = id_match.group(1) if id_match else ''
                        # Image extraction
                        img_elem = item.select_one('img')
                        image_url = img_elem['src'] if img_elem else None

                        item_data = {
                            'id': item_id,
                            'title': title,
                            'price': price,
                            'url': url,
                            'image_url': image_url,
                            'end_time': '',  # Rakuten is fixed price
                            'bid_count': 0,
                            'is_fixed_price': True,
                            'source': 'Rakuten',
                            'timestamp': datetime.now().isoformat()
                        }
                        items.append(item_data)
                        page_item_count += 1
                    except Exception as e:
                        logger.error(f"Error parsing item: {e}")
                        continue
                logger.info(f"Rakuten: Page {page} - {page_item_count} items scraped (total so far: {len(items)})")
            return {
                'items': items,
                'search_url': search_url
            }
        except Exception as e:
            logger.error(f"Error in Rakuten search: {e}")
            if hasattr(e, 'response') and e.response.status_code == 429:
                time.sleep(BURST_PROTECTION['cooldown_after_error'])
            return []

    def _normalize_price(self, price_str: str) -> float:
        try:
            price_str = price_str.replace('¥', '').replace(',', '').replace('円', '').strip()
            price_match = re.search(r'(\d+)', price_str)
            if price_match:
                return float(price_match.group(1))
            return 0.0
        except (ValueError, AttributeError) as e:
            logger.error(f"Error normalizing price '{price_str}': {e}")
            return 0.0

    def cleanup(self):
        if self.session:
            self.session.close() 