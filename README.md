# Japanese Market Search Tool

A desktop application for searching multiple Japanese marketplace websites with real-time monitoring and notifications.

## Features

- **Multi-site Search**: Search across Yahoo Auctions, Rakuten Market, and Mercari
- **Price Filtering**: Set minimum and maximum price ranges
- **Saved Searches**: Save search criteria for repeated use
- **Real-time Monitoring**: Automatic background monitoring every 30 minutes
- **Desktop Notifications**: Get notified when new items are found
- **Modern GUI**: Clean, intuitive interface built with CustomTkinter

## Supported Marketplaces

- **Yahoo Auctions** - Traditional auction site with both auction and fixed-price items
- **Rakuten Market** - Large e-commerce marketplace
- **Mercari** - Popular C2C marketplace (uses Selenium for anti-detection)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. **Search**: Enter keywords, set price range, and select marketplaces
2. **Save Searches**: Click "Save Search" to store your criteria
3. **Monitor**: Enable notifications for saved searches to get alerts for new items
4. **View Results**: Check the Feed tab for new items from your saved searches

## Technical Details

- **Language**: Python 3.8+
- **GUI Framework**: CustomTkinter
- **Web Scraping**: BeautifulSoup4 + requests (Yahoo/Rakuten), Selenium (Mercari)
- **Database**: SQLite
- **Background Processing**: Threading with periodic execution

## Anti-Detection Measures

The Mercari scraper uses advanced anti-detection techniques:
- Selenium WebDriver with stealth mode
- Human-like delays and scrolling
- Random user agent rotation
- Popup and cookie handling
- Fallback selectors for dynamic content

## Configuration

Edit `config/settings.py` to customize:
- Search intervals
- Price ranges
- Enabled marketplaces
- GUI appearance

## License

This project is for educational purposes. Please respect website terms of service and rate limits.