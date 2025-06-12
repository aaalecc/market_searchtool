# Japanese Market Scraper - Project Context for AI Assistant

## Project Overview
**Project Name:** Japanese Market Scraper Desktop App
**Description:** A desktop application that scrapes multiple Japanese and international marketplace websites (Yahoo Auctions/Flea Market, Rakuten Market, Mercari, Grailed, Sneaker Dunk) to find items based on user criteria and provides notifications for new listings
**Main Language:** Python
**GUI Framework:** CustomTkinter
**Web Scraping:** BeautifulSoup4 (bs4) + requests
**Database:** SQLite (`market_search.db`)
**Notification Systems:** Desktop notifications + Discord webhooks
**Target Markets:** Yahoo Auctions, Yahoo Flea Market, Rakuten Market, Mercari, Grailed, Sneaker Dunk

## Project Architecture

### Core Components
1. **GUI Application** (CustomTkinter)
   - Main search interface
   - Results display
   - Saved searches management tab
   - New items feed tab

2. **Web Scraping Engine**
   - `test_scraper.py` - Base scraper file
   - Site-specific scrapers for each marketplace
   - Handles search parameters and filtering

3. **Database Layer** (SQLite)
   - Items database (search results)
   - Saved searches database (search parameters + items)
   - New items database (notifications feed)

4. **Periodic Monitoring System**
   - Runs every 30 minutes
   - Monitors saved searches with notifications enabled
   - Detects new items and adds to feed

## Current File Structure
```
project_root/
├── main.py                   # [Status: ?] Main GUI application entry point
├── test_scraper.py          # [Status: ?] Base scraper with argument handling
├── clear_database.py        # [Status: ?] Database maintenance utility
├── show_database.py         # [Status: ?] Database viewing utility
├── notes.txt                # [Status: ?] Development notes/todo
├── requirements.txt         # [Status: ?] Project dependencies
├── README.md               # [Status: ?] Project documentation
├── .gitignore              # [Status: ?] Git ignore rules
├── __pycache__/            # Python cache files
├── cache/                  # [Status: ?] Scraping cache storage
├── config/                 # [Status: ?] Configuration management
│   ├── __init__.py         # [Status: ?] Package initializer
│   ├── scraping_config.py  # [Status: ?] Scraping settings and parameters
│   └── settings.py         # [Status: ?] General application settings
├── core/                   # [Status: ?] Core application logic
│   ├── __init__.py         # [Status: ?] Package initializer
│   ├── background_tasks.py # [Status: ?] Periodic scraping and monitoring
│   └── database.py         # [Status: ?] Database operations and management
├── data/                   # [Status: ?] Data storage
│   └── market_search.db    # [Status: ?] SQLite database file
├── gui/                    # [Status: ?] CustomTkinter GUI components
│   ├── __init__.py         # [Status: ?] Package initializer
│   ├── favorites_tab.py    # [Status: ?] Favorites/bookmarks interface
│   ├── feed_tab.py         # [Status: ?] New items feed display
│   ├── main_window.py      # [Status: ?] Main application window
│   ├── saved_searches_tab.py # [Status: ?] Saved searches management
│   ├── search_tab.py       # [Status: ?] Search input and results
│   └── settings_tab.py     # [Status: ?] Application settings interface
├── logs/                   # [Status: ?] Application logging
├── notifications/          # [Status: ?] Notification system
│   ├── __init__.py         # [Status: ?] Package initializer
│   ├── desktop_notifier.py # [Status: ?] Desktop notifications
│   └── discord_notifier.py # [Status: ?] Discord webhook notifications
├── scrapers/              # [Status: ?] Web scraping modules
│   ├── __init__.py         # [Status: ?] Package initializer
│   ├── grailed.py          # [Status: ?] Grailed marketplace scraper
│   ├── mercari.py          # [Status: ?] Mercari marketplace scraper
│   ├── rakuten.py          # [Status: ?] Rakuten Market scraper
│   ├── sneaker_dunk.py     # [Status: ?] Sneaker Dunk marketplace scraper
│   ├── yahoo_auctions.py   # [Status: ?] Yahoo Auctions scraper
│   └── yahoo_flea_market.py # [Status: ?] Yahoo Flea Market scraper
├── snapshots/             # [Status: ?] Data snapshots/backups
└── venv/                  # Virtual environment
```

## Implementation Status

### ✅ Completed Features
- [x] **Core Scraping System:**
  - Yahoo Auctions scraper (`yahoo_auctions.py`) - **Complete & Working**
  - Rakuten Market scraper (`rakuten.py`) - **Complete & Working**
  - Central scraper coordinator (`test_scraper.py`) - **Complete & Working**
  - Scraping environment configuration (`config/scraping_config.py`) - **Complete**

- [x] **GUI Components (Fully Functional):**
  - Main window with tabbed interface (`main_window.py`) - **Complete**
  - **Search Tab** (`search_tab.py`) - **Complete & Working**
    - Search input with filters (keywords, price range, site selection)
    - Displays all available items from database
    - Results sorted by price (low to high)
  - **Saved Searches Tab** (`saved_searches_tab.py`) - **Complete & Working**
    - Shows all current saved searches
    - Ability to enable/disable notifications per search
  - **Feed Tab** (`feed_tab.py`) - **Complete & Working**
    - Displays containers for saved searches with notifications enabled
    - Shows all items from new_items database for each saved search
    - "View Items" button to display all items for corresponding saved search

- [x] **Database & Storage:**
  - SQLite database operations (`market_search.db`) - **Complete & Working**
  - Database functions (`core/database.py`) - **Complete & Working**
  - Save search functionality - **Complete & Working**
  - New items database tracking - **Complete & Working**
  - Database utilities (`clear_database.py`, `show_database.py`) - **Complete**

- [x] **Background Processing System:**
  - Periodic scraper (`core/background_tasks.py`) - **Complete & Working**
  - Runs on app launch + every 30 minutes automatically
  - Scrapes all saved searches with notifications enabled
  - Adds new items to new_items database for corresponding saved searches
  - Integrates with notification system

- [x] **Notifications:**
  - Desktop notifications (`desktop_notifier.py`) - **Complete & Working**
  - Provides summary of how many new items were added to each saved search
  - Triggered after each periodic scraping cycle

### 🚧 In Progress
- [ ] *Currently no active development tasks*

### 📋 Planned/Todo
- [ ] **Priority 1: Additional Scrapers**
  - Mercari scraper (`mercari.py`) - *Placeholder file exists*
  - Sneaker Dunk scraper (`sneaker_dunk.py`) - *Placeholder file exists*  
  - Grailed scraper (`grailed.py`) - *Placeholder file exists*
  
- [ ] **Priority 2: UI/UX Improvements**
  - Modernize user interface design and aesthetics
  - Improve UI smoothness and responsiveness
  - Enhance visual design with modern styling
  - Better user experience and interface flow
  - Optimize CustomTkinter components for smoother interactions
  
- [ ] **Priority 3: Performance Optimization**
  - Speed up individual scrapers (Yahoo Auctions, Rakuten, future scrapers)
  - Optimize GUI loading times and responsiveness
  - Improve background task execution speed
  - Database query optimization for faster operations
  - Reduce memory usage and improve overall efficiency
  - Implement better caching mechanisms
  
- [ ] **Priority 4: Discord Integration**
  - Complete Discord webhook notifications (`discord_notifier.py`)
  - Integrate Discord notifications with periodic scraper
  - Add Discord configuration in settings
  - Test and implement Discord notification formatting
  
- [ ] **Secondary Features:**
  - Settings tab functionality (`settings_tab.py`) - *Currently empty*
  - Favorites tab functionality (`favorites_tab.py`) - *Status unknown*
  - Yahoo Flea Market scraper (`yahoo_flea_market.py`) - *Lower priority*
  
- [ ] **Future Enhancements:**
  - Error handling improvements for network issues
  - Search result caching optimization
  - Export functionality for results
  - Advanced filtering options
  - Decide on `settings.py` future (may be deleted)

## Key Workflow

### 1. User Search Process
1. User inputs search criteria in GUI:
   - Keywords
   - Min/max price range
   - Website selection (Yahoo, Rakuten, or both)
2. User clicks search button
3. GUI calls `test_scraper.py` with arguments
4. Scraper runs site-specific scrapers with filters
5. Results stored in items SQLite database
6. GUI displays results sorted by price (low to high)

### 2. Save Search Process
1. User clicks "Save Search" button
2. Search parameters + current results saved to saved_searches database
3. Search appears in saved_searches tab
4. User can enable/disable notifications for each saved search

### 3. Periodic Monitoring Process
1. Runs every 30 minutes automatically
2. Checks saved_searches database for notification-enabled searches
3. For each enabled search:
   - Runs `test_scraper.py` with saved parameters
   - Compares new results with saved results
   - Identifies non-duplicate items
   - Adds new items to new_items database
4. New items appear in feed tab

## Database Schema

### Items Database
- Item details from search results
- Price, title, URL, image, marketplace source
- Timestamp of when scraped

### Saved Searches Database
- Search parameters (keywords, price range, sites)
- Associated items from original search
- Notification enabled/disabled flag
- Timestamp of original search

### New Items Database
- Items found during periodic monitoring
- References to which saved search triggered the finding
- Timestamp of discovery

## Dependencies
```
customtkinter>=5.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0
sqlite3 (built-in)
threading (built-in)
schedule>=1.2.0  # For periodic scraping
```

## Technical Implementation Notes

### Scraping Strategy
- **Yahoo Auctions** (`yahoo_auctions.py`) - **✅ Complete** - Fully implemented with filtering
- **Rakuten Market** (`rakuten.py`) - **✅ Complete** - Fully implemented with filtering  
- **Yahoo Flea Market** (`yahoo_flea_market.py`) - **❌ Not started** - Placeholder file
- **Mercari** (`mercari.py`) - **❌ Not started** - Placeholder file
- **Grailed** (`grailed.py`) - **❌ Not started** - Fashion marketplace scraping planned
- **Sneaker Dunk** (`sneaker_dunk.py`) - **❌ Not started** - Sneaker marketplace scraping planned
- Rate limiting and respectful scraping practices via `scraping_config.py`
- User agent rotation and scraping environment setup
- Error handling for blocked requests or site changes

### Background Processing System
- **Periodic Execution**: Runs on app launch + every 30 minutes via `background_tasks.py`
- **Automated Search Updates**: Executes `test_scraper.py` for all saved searches
- **Database Updates**: Updates SQL databases with new findings automatically
- **Notification Triggers**: Calls desktop notifier with summary of new items found
- **Integration**: Seamlessly works with GUI and database systems

### Notification System
- **Desktop Notifications** (`desktop_notifier.py`) - **✅ Working** - Sends summary of new items from periodic scraping
- **Discord Notifications** (`discord_notifier.py`) - **❌ Not implemented** - Webhook integration planned
- **Configuration**: Discord URL can be set in `settings.py` (when implemented)
- **Trigger**: Notifications sent after each periodic scraping cycle with new items

### Database Operations
- **Single Database**: `market_search.db` handles all data storage
- **Core Functions**: `database.py` provides all insert/retrieve operations
- **Integration**: Called by GUI files and scraper files for data operations
- **Utilities**: `clear_database.py` and `show_database.py` for maintenance and debugging
- **Efficient Processing**: Duplicate detection, proper indexing, automated cleanup

## Current Development Focus
**Last Updated:** June 12, 2025
**Current Status:** Core application is **fully functional** with 2 marketplace scrapers

### Application Status: WORKING ✅
- **Search System:** Fully operational with Yahoo Auctions + Rakuten
- **GUI:** All main tabs functional (Search, Saved Searches, Feed)
- **Background Processing:** Automatic 30-minute scraping cycles working
- **Notifications:** Desktop notifications working with item count summaries
- **Database:** All data operations working (save searches, new items tracking)

### Immediate Development Priority
**Next Goals in Order:**
1. **Expand Marketplace Coverage** - Implement remaining scrapers (Mercari, Sneaker Dunk, Grailed)
2. **UI/UX Modernization** - Make interface smoother, more modern, and visually appealing
3. **Performance Optimization** - Speed up all components (scrapers, GUI, background tasks)
4. **Discord Integration** - Complete Discord notification system implementation

### Development Areas Needing Attention

#### 🎨 UI/UX Improvements Needed
- **Modern Design**: Update visual aesthetics to contemporary standards
- **Smooth Interactions**: Eliminate lag and improve responsiveness
- **Better Layout**: Optimize spacing, typography, and visual hierarchy
- **Enhanced User Experience**: Streamline workflow and improve usability
- **CustomTkinter Optimization**: Leverage advanced styling features

#### ⚡ Performance Optimization Required
- **Scraper Speed**: Optimize individual scraper execution time
- **GUI Performance**: Reduce loading times and improve responsiveness
- **Background Tasks**: Speed up periodic scraping cycles
- **Database Efficiency**: Optimize queries and reduce overhead
- **Memory Management**: Reduce RAM usage and improve resource handling
- **Caching Strategy**: Implement better caching for frequently accessed data

#### 🔔 Discord Integration Goals
- **Complete Implementation**: Finish `discord_notifier.py` functionality
- **Webhook Integration**: Set up Discord webhook system
- **Message Formatting**: Design notification message templates
- **Configuration**: Add Discord settings to configuration system
- **Testing**: Ensure reliable delivery and formatting

### Recent Achievements
- Completed core scraping and GUI infrastructure
- Successfully implemented periodic background scraping
- Working notification system with desktop alerts
- Functional saved searches with new items tracking
- Stable database operations for all core features

### Known Issues & Technical Debt
- [ ] **Performance Issues:**
  - Individual scrapers may be slower than optimal
  - GUI loading and responsiveness could be improved
  - Background task execution needs speed optimization
  - Database operations could be more efficient
  
- [ ] **UI/UX Issues:**
  - Interface design needs modernization
  - User interactions could be smoother
  - Visual aesthetics need contemporary update
  - CustomTkinter styling not fully leveraged
  
- [ ] **Incomplete Features:**
  - Discord notifications (`discord_notifier.py`) - File exists but not implemented
  - Settings tab (`settings_tab.py`) - Currently empty
  - Several scraper placeholders need implementation
  
- [ ] **Technical Debt:**
  - Caching mechanisms could be more sophisticated
  - Error handling for network issues needs improvement
  - Memory usage optimization opportunities exist
  - Code organization and documentation could be enhanced

### Next Steps
1. **Scraper Expansion** - Implement Mercari, Sneaker Dunk, and Grailed scrapers using existing patterns
2. **UI Modernization** - Redesign interface with modern CustomTkinter styling and smooth animations
3. **Performance Tuning** - Profile and optimize scraper speed, GUI responsiveness, and background tasks
4. **Discord Integration** - Complete webhook notification system with proper formatting and configuration
5. **Settings Implementation** - Build functional settings tab for user preferences and Discord configuration
6. **Testing & Optimization** - Comprehensive testing of new features and performance improvements

---
**Instructions for AI Assistant:**
- This is a **working application** in expansion phase, not initial development
- Core infrastructure is solid - focus on enhancement and expansion
- **Priority areas**: Additional scrapers → UI improvements → Performance → Discord integration
- When suggesting improvements, consider impact on existing working functionality
- Performance optimization should target: scraper speed, GUI responsiveness, background task efficiency
- UI improvements should focus on modern design, smooth interactions, and better user experience
- Maintain consistency with existing code patterns and structure
- Be mindful of Japanese text encoding and marketplace-specific requirements
- Consider scalability when suggesting performance improvements