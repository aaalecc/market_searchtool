"""
Mercari scraper using Selenium for anti-bot protection handling.
Mercari has extremely strict anti-scraping measures requiring browser automation.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

from config.scraping_config import (
    get_chrome_options,
    get_selenium_driver_config,
    get_random_user_agent,
    SELENIUM_TIMEOUTS
)

logger = logging.getLogger(__name__)

class MercariScraper:
    """Selenium-based scraper for Mercari with anti-detection measures."""
    
    BASE_URL = "https://jp.mercari.com"
    SEARCH_URL = "https://jp.mercari.com/search"
    
    def __init__(self, headless: bool = True):
        """
        Initialize the Mercari scraper with Selenium WebDriver.
        
        Args:
            headless: Run browser in headless mode (default: True)
        """
        self.headless = headless
        self.driver = None
        self.wait = None
        self.last_request_time = 0
        
        # Mercari-specific selectors
        self.selectors = {
            'search_input': 'input[data-testid="search-input"]',
            'search_button': 'button[data-testid="search-button"]',
            'product_cards': '[data-testid="item-cell"]',
            'product_title': '[data-testid="item-name"]',
            'product_price': '[data-testid="price"]',
            'product_image': 'img[data-testid="item-image"]',
            'product_link': 'a[data-testid="item-link"]',
            'load_more': 'button[data-testid="load-more"]',
            'price_filter_min': 'input[data-testid="price-min"]',
            'price_filter_max': 'input[data-testid="price-max"]',
            'sort_dropdown': 'select[data-testid="sort-select"]',
            'category_filter': 'button[data-testid="category-filter"]',
            'condition_filter': 'button[data-testid="condition-filter"]',
            'location_filter': 'button[data-testid="location-filter"]',
            'results_count': '[data-testid="results-count"]',
            'no_results': '[data-testid="no-results"]',
            'loading_spinner': '[data-testid="loading-spinner"]',
            'cookie_accept': 'button[data-testid="cookie-accept"]',
            'popup_close': 'button[data-testid="popup-close"]',
            'modal_close': 'button[data-testid="modal-close"]'
        }
        
        # Fallback selectors for when data-testid attributes change
        self.fallback_selectors = {
            'search_input': ['input[type="search"]', 'input[name="q"]', 'input[placeholder*="検索"]'],
            'search_button': ['button[type="submit"]', 'input[type="submit"]', '.search-button'],
            'product_cards': ['.item-cell', '.product-card', '[class*="item"]', '[class*="product"]'],
            'product_title': ['.item-name', '.product-title', 'h3', 'h4', '[class*="title"]'],
            'product_price': ['.price', '.cost', '[class*="price"]', '[data-price]'],
            'product_image': ['img[src*="jpg"]', 'img[src*="jpeg"]', 'img[src*="png"]', 'img[src*="webp"]'],
            'product_link': ['a[href*="/item/"]', 'a[href*="/product/"]', '.item-link']
        }
        
        logger.info("Mercari scraper initialized")
    
    def _setup_driver(self):
        """Set up Chrome WebDriver with anti-detection measures and resource blocking."""
        try:
            # Get Chrome options with stealth mode
            chrome_options = Options()
            options_list = get_chrome_options(stealth_mode=True, headless=self.headless)
            
            for option in options_list:
                chrome_options.add_argument(option)
            
            # Additional anti-detection measures
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Additional speed optimizations
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--blink-settings=imagesEnabled=false')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-background-networking')
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-translate')
            chrome_options.add_argument('--disable-notifications')
            chrome_options.add_argument('--disable-popup-blocking')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            
            # Set up Chrome service
            service = Service(ChromeDriverManager().install())
            
            # Create driver
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Block CSS and font files using DevTools Protocol
            try:
                self.driver.execute_cdp_cmd('Network.enable', {})
                self.driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["*.css", "*.woff", "*.woff2", "*.ttf", "*.otf"]})
            except Exception as e:
                logger.debug(f"Failed to block CSS/fonts: {e}")
            
            # Execute stealth script
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set lower timeouts
            self.driver.implicitly_wait(2)
            self.driver.set_page_load_timeout(8)
            self.driver.set_script_timeout(8)
            
            # Create wait object
            self.wait = WebDriverWait(self.driver, 4)
            
            logger.info("Chrome WebDriver setup complete")
        except Exception as e:
            logger.error(f"Failed to setup Chrome WebDriver: {e}")
            raise
    
    def _human_like_delay(self, min_delay: float = 0.1, max_delay: float = 0.3):
        """Add minimal human-like random delays between actions."""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _scroll_randomly(self):
        """Perform minimal random scrolling to simulate human behavior."""
        try:
            scroll_amount = random.randint(50, 200)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            self._human_like_delay(0.1, 0.2)
        except Exception as e:
            logger.debug(f"Scroll failed: {e}")
    
    def _handle_popups_and_cookies(self):
        """Handle various popups, cookies, and modals that might appear."""
        popup_selectors = [
            self.selectors['cookie_accept'],
            self.selectors['popup_close'],
            self.selectors['modal_close']
        ]
        
        for selector in popup_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    element.click()
                    self._human_like_delay(0.1, 0.2)
                    logger.debug(f"Closed popup with selector: {selector}")
            except NoSuchElementException:
                continue
            except Exception as e:
                logger.debug(f"Failed to close popup {selector}: {e}")
    
    def _wait_for_page_load(self):
        """Wait for page to fully load with reduced timeouts."""
        try:
            # Wait for loading spinner to disappear with shorter timeout
            self.wait.until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['loading_spinner']))
            )
        except TimeoutException:
            logger.debug("Loading spinner timeout - continuing anyway")
        
        # Wait for content to be present with shorter timeout
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['product_cards']))
            )
        except TimeoutException:
            logger.debug("Product cards not found - might be no results")
    
    def _find_element_with_fallback(self, primary_selector: str, fallback_selectors: List[str]):
        """Find element using primary selector with fallback options."""
        try:
            return self.driver.find_element(By.CSS_SELECTOR, primary_selector)
        except NoSuchElementException:
            for fallback in fallback_selectors:
                try:
                    return self.driver.find_element(By.CSS_SELECTOR, fallback)
                except NoSuchElementException:
                    continue
        return None
    
    def _extract_price(self, price_element) -> float:
        """Extract and normalize price from price element."""
        try:
            price_text = price_element.text.strip()
            # Remove currency symbols, commas, and '円'
            price_text = re.sub(r'[¥,円\s]', '', price_text)
            # Extract numeric value
            price_match = re.search(r'(\d+)', price_text)
            if price_match:
                return float(price_match.group(1))
            return 0.0
        except Exception as e:
            logger.debug(f"Price extraction failed: {e}")
            return 0.0
    
    def _extract_product_data(self, product_element) -> Optional[Dict[str, Any]]:
        """Extract product data from a product card element."""
        try:
            # Extract title
            title_element = self._find_element_with_fallback(
                self.selectors['product_title'],
                self.fallback_selectors['product_title']
            )
            if not title_element:
                return None
            title = title_element.text.strip()
            
            # Extract price
            price_element = self._find_element_with_fallback(
                self.selectors['product_price'],
                self.fallback_selectors['product_price']
            )
            if not price_element:
                return None
            price = self._extract_price(price_element)
            
            # Extract URL
            link_element = self._find_element_with_fallback(
                self.selectors['product_link'],
                self.fallback_selectors['product_link']
            )
            if not link_element:
                return None
            url = link_element.get_attribute('href')
            if not url.startswith('http'):
                url = self.BASE_URL + url
            
            # Extract image
            image_element = self._find_element_with_fallback(
                self.selectors['product_image'],
                self.fallback_selectors['product_image']
            )
            image_url = None
            if image_element:
                image_url = image_element.get_attribute('src')
            
            # Extract item ID from URL
            item_id = url.split('/')[-1] if url else f"mercari_{int(time.time())}"
            
            return {
                'id': item_id,
                'title': title,
                'price': price,
                'url': url,
                'image_url': image_url,
                'end_time': '',  # Mercari is fixed price
                'bid_count': 0,
                'is_fixed_price': True,
                'source': 'mercari',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.debug(f"Failed to extract product data: {e}")
            return None
    
    def search(self, keywords: List[str], min_price: Optional[int] = None, max_price: Optional[int] = None) -> Dict[str, Any]:
        """
        Search Mercari for items matching the criteria.
        
        Args:
            keywords: List of search keywords
            min_price: Minimum price filter
            max_price: Maximum price filter
            
        Returns:
            Dictionary with 'items' list and 'search_url' string
        """
        logger.info(f"Starting Mercari search for keywords: {keywords}")
        
        if not self.driver:
            self._setup_driver()
        
        items = []
        search_url = ""
        
        try:
            # Build search URL with query parameters
            search_query = ' '.join(keywords)
            search_url = f"{self.SEARCH_URL}?keyword={search_query}"
            
            # Add price filters if specified
            if min_price is not None:
                search_url += f"&price_min={min_price}"
            if max_price is not None:
                search_url += f"&price_max={max_price}"
            
            logger.info(f"Navigating to search URL: {search_url}")
            self.driver.get(search_url)
            self._human_like_delay(0.5, 1.0)
            
            # Handle any popups or cookies
            self._handle_popups_and_cookies()
            
            # Wait for page to load
            self._wait_for_page_load()

            # Check the '販売中のみ表示' (on sale only) checkbox if present
            try:
                checkbox = self.driver.find_element(By.CSS_SELECTOR, 'input[data-testid="on-sale-condition-checkbox"]')
                if not checkbox.is_selected():
                    checkbox.click()
                    self._human_like_delay(1.0, 2.0)  # Wait for page to refresh
            except Exception as e:
                logger.debug(f"Could not check 'on sale only' checkbox: {e}")
            
            # Scroll and collect items
            items = self._collect_items()
            
            logger.info(f"Mercari search completed. Found {len(items)} items")
            
        except Exception as e:
            logger.error(f"Error during Mercari search: {e}")
            import traceback
            traceback.print_exc()
        
        return {
            'items': items,
            'search_url': search_url
        }
    
    def _collect_items(self) -> List[Dict[str, Any]]:
        """Slowly scrolls down to the bottom and back to the top to load all items, then collects all visible items from the search results."""
        items = []
        try:
            # Slowly scroll down to the bottom
            scroll_pause = 0.2
            scroll_step = 300
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            current_position = 0
            while current_position < last_height:
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                self._human_like_delay(scroll_pause, scroll_pause + 0.1)
                current_position += scroll_step
                last_height = self.driver.execute_script("return document.body.scrollHeight")
            # Ensure we're at the very bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self._human_like_delay(0.5, 0.7)
            # Slowly scroll back up to the top
            while current_position > 0:
                current_position -= scroll_step
                if current_position < 0:
                    current_position = 0
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                self._human_like_delay(scroll_pause, scroll_pause + 0.1)
            # After scrolling, collect all loaded items
            product_elements = self.driver.find_elements(By.CSS_SELECTOR, 'li[data-testid="item-cell"]')
            for element in product_elements:
                try:
                    # URL and ID
                    link_elem = element.find_element(By.CSS_SELECTOR, 'a[data-testid="thumbnail-link"]')
                    href = link_elem.get_attribute('href')
                    url = href if href.startswith('http') else 'https://jp.mercari.com' + href
                    item_id = href.split('/')[-1]

                    # Title
                    img_div = link_elem.find_element(By.CSS_SELECTOR, 'div[role="img"]')
                    title = img_div.get_attribute('aria-label')

                    # Image
                    img_tag = element.find_element(By.CSS_SELECTOR, 'picture img')
                    image_url = img_tag.get_attribute('src')

                    # Price
                    price_span = element.find_element(By.CSS_SELECTOR, 'span[class*="merPrice"] span[class*="number__"]')
                    price_text = price_span.text.replace(',', '').replace('¥', '').strip()
                    price = int(price_text)

                    item_data = {
                        'id': item_id,
                        'title': title,
                        'price': price,
                        'url': url,
                        'image_url': image_url,
                        'end_time': '',  # Mercari is fixed price
                        'bid_count': 0,
                        'is_fixed_price': True,
                        'source': 'mercari',
                        'timestamp': datetime.now().isoformat()
                    }
                    items.append(item_data)
                except Exception as e:
                    logger.debug(f"Failed to extract product: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error collecting items: {e}")
        return items
    
    def cleanup(self):
        """Clean up resources and close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Mercari scraper WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None
                self.wait = None 