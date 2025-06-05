"""
Main Window for Market Search Tool
CustomTkinter application with sidebar navigation: Search, Feed, Favorites, and Settings
"""

import customtkinter as ctk
import logging
from typing import Dict, Any

from config.settings import WINDOW_CONFIG, TAB_CONFIG
from core.database import get_setting, set_setting

# Import tab modules (we'll create these)
from gui.search_tab import SearchTab
from gui.feed_tab import FeedTab
from gui.favorites_tab import FavoritesTab
from gui.settings_tab import SettingsTab
from gui.saved_searches_tab import SavedSearchesTab

logger = logging.getLogger(__name__)

class MainWindow(ctk.CTk):
    """Main application window with sidebar navigation."""
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        logger.info("Initializing main window...")
        
        # Initialize window properties
        self.setup_window()
        
        # Setup CustomTkinter theming
        self.setup_theme()
        
        # Create the main interface
        self.create_widgets()
        
        # Setup event handlers
        self.setup_event_handlers()
        
        # Apply user settings
        self.apply_user_settings()
        
        # Set default tab
        self.show_feed_tab()
        
        logger.info("Main window initialized successfully")
    
    def setup_window(self):
        """Configure basic window properties."""
        # Window title and icon
        self.title(WINDOW_CONFIG['title'])
        
        # Start in fullscreen mode but keep window controls
        self.state('zoomed')  # Windows fullscreen
        self.attributes('-fullscreen', False)  # Disable true fullscreen to keep controls
        self.overrideredirect(False)  # Ensure window controls are visible
        
        # Window size and constraints for when not fullscreen
        self.geometry(f"{WINDOW_CONFIG['width']}x{WINDOW_CONFIG['height']}")
        self.minsize(WINDOW_CONFIG['min_width'], WINDOW_CONFIG['min_height'])
        
        # Window behavior
        self.resizable(WINDOW_CONFIG['resizable'], WINDOW_CONFIG['resizable'])
        
        # Configure window closing behavior
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        
        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - WINDOW_CONFIG['width']) // 2
        y = (screen_height - WINDOW_CONFIG['height']) // 2
        
        self.geometry(f"{WINDOW_CONFIG['width']}x{WINDOW_CONFIG['height']}+{x}+{y}")
    
    def setup_theme(self):
        """Setup CustomTkinter theme and appearance."""
        # Force dark theme for modern experience
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme("blue")
        
        logger.info(f"Applied theme: dark (Modern-style)")
    
    def create_widgets(self):
        """Create the main interface widgets."""
        # Configure main grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Initialize tab content
        self.init_tab_content()
    
    def create_sidebar(self):
        """Create the left sidebar navigation with Spotify-dark design."""
        self.sidebar_frame = ctk.CTkFrame(
            self, 
            width=260, 
            corner_radius=0, 
            fg_color="#000000"  # Pure black like Spotify
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        # App title/logo with modern styling and larger Japanese font
        self.logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(30, 25))
        
        self.logo_label = ctk.CTkLabel(
            self.logo_frame, 
            text="マーケットツール", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"  # Pure white for maximum contrast
        )
        self.logo_label.pack()
        
        self.subtitle_label = ctk.CTkLabel(
            self.logo_frame,
            text="商品検索ツール",
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color="#B3B3B3"  # Spotify's actual secondary text color
        )
        self.subtitle_label.pack(pady=(4, 0))
        
        # Navigation section with modern styling
        self.nav_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.nav_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(15, 0))
        
        self.nav_label = ctk.CTkLabel(
            self.nav_frame, 
            text="ナビゲーション", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#B3B3B3",  # Spotify's actual secondary text
            anchor="w"
        )
        self.nav_label.pack(anchor="w", pady=(0, 20))
        
        # Spotify-style navigation buttons
        button_style = {
            "corner_radius": 25,  # Very rounded like modern apps
            "height": 50,
            "border_spacing": 15,
            "fg_color": "transparent",
            "text_color": "#B3B3B3",  # Spotify's actual secondary text
            "hover_color": "#1A1A1A",  # Very dark gray on hover
            "anchor": "w",
            "font": ctk.CTkFont(size=16, weight="normal")
        }
        
        self.feed_button = ctk.CTkButton(
            self.sidebar_frame,
            text="🏠  フィード",
            command=self.show_feed_tab,
            **button_style
        )
        self.feed_button.grid(row=2, column=0, sticky="ew", padx=20, pady=3)
        
        self.search_button = ctk.CTkButton(
            self.sidebar_frame,
            text="🔍  検索",
            command=self.show_search_tab,
            **button_style
        )
        self.search_button.grid(row=3, column=0, sticky="ew", padx=20, pady=3)
        
        self.favorites_button = ctk.CTkButton(
            self.sidebar_frame,
            text="❤️  お気に入り",
            command=self.show_favorites_tab,
            **button_style
        )
        self.favorites_button.grid(row=4, column=0, sticky="ew", padx=20, pady=3)
        
        self.saved_searches_button = ctk.CTkButton(
            self.sidebar_frame,
            text="💾  保存検索",
            command=self.show_saved_searches_tab,
            **button_style
        )
        self.saved_searches_button.grid(row=5, column=0, sticky="ew", padx=20, pady=3)
        
        # Settings section at bottom with separator
        self.separator = ctk.CTkFrame(self.sidebar_frame, height=1, fg_color="#282828")
        self.separator.grid(row=6, column=0, sticky="ew", padx=30, pady=25)
        
        self.settings_button = ctk.CTkButton(
            self.sidebar_frame,
            text="⚙️  設定",
            command=self.show_settings_tab,
            **button_style
        )
        self.settings_button.grid(row=7, column=0, sticky="ew", padx=20, pady=(15, 25))
        
        # Purple-style theme toggle button (circular)
        self.theme_button = ctk.CTkButton(
            self.sidebar_frame,
            text="🌙",
            width=50,
            height=50,
            corner_radius=25,  # Perfect circle
            command=self.toggle_theme,
            fg_color="#8B5CF6",  # Purple accent
            hover_color="#A78BFA",  # Lighter purple on hover
            font=ctk.CTkFont(size=18),
            text_color="#FFFFFF"  # White text on purple
        )
        self.theme_button.grid(row=8, column=0, pady=(0, 30))
    
    def create_main_content(self):
        """Create the main content area with Spotify-dark styling."""
        self.main_content_frame = ctk.CTkFrame(
            self, 
            corner_radius=0, 
            fg_color="#121212"  # Spotify's actual main background
        )
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 0))
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        
        # Container for different tab contents with Spotify design
        self.content_container = ctk.CTkFrame(
            self.main_content_frame, 
            corner_radius=20,  # More rounded
            fg_color="#181818",  # Spotify's actual content background
            border_width=0  # No border for cleaner look
        )
        self.content_container.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
    
    def init_tab_content(self):
        """Initialize content for each tab."""
        try:
            # Initialize all tabs but don't show them yet
            self.search_tab = SearchTab(self.content_container)
            self.feed_tab = FeedTab(self.content_container)
            self.favorites_tab = FavoritesTab(self.content_container)
            self.settings_tab = SettingsTab(self.content_container, main_window=self)
            self.saved_searches_tab = SavedSearchesTab(self.content_container)
            
            # Hide all tabs initially
            self.search_tab.grid_remove()
            self.feed_tab.grid_remove()
            self.favorites_tab.grid_remove()
            self.settings_tab.grid_remove()
            self.saved_searches_tab.grid_remove()
            
            logger.info("All tabs initialized")
            
        except Exception as e:
            logger.error(f"Error initializing tab content: {e}")
            # Create placeholder content if tab modules aren't ready
            self.create_placeholder_content()
            # Initialize placeholder tabs to prevent attribute errors
            self.search_tab = self.placeholder_label
            self.feed_tab = self.placeholder_label
            self.favorites_tab = self.placeholder_label
            self.settings_tab = self.placeholder_label
            self.saved_searches_tab = self.placeholder_label
    
    def create_placeholder_content(self):
        """Create placeholder content for tabs during development."""
        logger.info("Creating placeholder tab content...")
        
        self.placeholder_label = ctk.CTkLabel(
            self.content_container,
            text="🔍 Tab content loading...",
            font=ctk.CTkFont(size=18)
        )
        self.placeholder_label.grid(row=0, column=0, sticky="nsew")
    
    def show_feed_tab(self):
        """Show the feed tab."""
        self.hide_all_tabs()
        self.feed_tab.grid(row=0, column=0, sticky="nsew")
        self.update_sidebar_selection("feed")
        self.current_tab = "feed"
        logger.info("Showing feed tab")
    
    def show_search_tab(self):
        """Show the search tab."""
        self.hide_all_tabs()
        self.search_tab.grid(row=0, column=0, sticky="nsew")
        self.update_sidebar_selection("search")
        self.current_tab = "search"
        logger.info("Showing search tab")
    
    def show_favorites_tab(self):
        """Show the favorites tab."""
        self.hide_all_tabs()
        self.favorites_tab.grid(row=0, column=0, sticky="nsew")
        self.update_sidebar_selection("favorites")
        self.current_tab = "favorites"
        logger.info("Showing favorites tab")
    
    def show_settings_tab(self):
        """Show the settings tab."""
        self.hide_all_tabs()
        self.settings_tab.grid(row=0, column=0, sticky="nsew")
        self.update_sidebar_selection("settings")
        self.current_tab = "settings"
        logger.info("Showing settings tab")
    
    def show_saved_searches_tab(self):
        """Show the saved searches tab."""
        self.hide_all_tabs()
        self.saved_searches_tab.grid(row=0, column=0, sticky="nsew")
        self.update_sidebar_selection("saved_searches")
        self.current_tab = "saved_searches"
        logger.info("Showing saved searches tab")
    
    def hide_all_tabs(self):
        """Hide all tab content."""
        if hasattr(self, 'search_tab'):
            self.search_tab.grid_remove()
        if hasattr(self, 'feed_tab'):
            self.feed_tab.grid_remove()
        if hasattr(self, 'favorites_tab'):
            self.favorites_tab.grid_remove()
        if hasattr(self, 'settings_tab'):
            self.settings_tab.grid_remove()
        if hasattr(self, 'saved_searches_tab'):
            self.saved_searches_tab.grid_remove()
    
    def update_sidebar_selection(self, selected_tab: str):
        """Update sidebar button appearance with purple accent selection."""
        # Reset all buttons to default appearance
        buttons = [self.feed_button, self.search_button, self.favorites_button, self.saved_searches_button, self.settings_button]
        for button in buttons:
            button.configure(
                fg_color="transparent",
                text_color="#B3B3B3"
            )
        
        # Highlight selected button with purple accent and white text
        if selected_tab == "feed":
            self.feed_button.configure(
                fg_color="#8B5CF6",  # Purple accent
                text_color="#FFFFFF"
            )
        elif selected_tab == "search":
            self.search_button.configure(
                fg_color="#8B5CF6",
                text_color="#FFFFFF"
            )
        elif selected_tab == "favorites":
            self.favorites_button.configure(
                fg_color="#8B5CF6",
                text_color="#FFFFFF"
            )
        elif selected_tab == "saved_searches":
            self.saved_searches_button.configure(
                fg_color="#8B5CF6",
                text_color="#FFFFFF"
            )
        elif selected_tab == "settings":
            self.settings_button.configure(
                fg_color="#8B5CF6",
                text_color="#FFFFFF"
            )
    
    def setup_event_handlers(self):
        """Setup event handlers for the window."""
        # Window state change handler
        self.bind("<Configure>", self.on_window_configure)
    
    def apply_user_settings(self):
        """Apply saved user settings to the interface."""
        try:
            # Apply window size if saved
            saved_width = get_setting('window_width')
            saved_height = get_setting('window_height')
            
            if saved_width and saved_height:
                self.geometry(f"{saved_width}x{saved_height}")
            
            # Apply last tab
            last_tab = get_setting('last_active_tab', 'feed')
            if last_tab == 'search':
                self.show_search_tab()
            elif last_tab == 'favorites':
                self.show_favorites_tab()
            elif last_tab == 'settings':
                self.show_settings_tab()
            elif last_tab == 'saved_searches':
                self.show_saved_searches_tab()
            else:
                self.show_feed_tab()
            
            logger.debug("User settings applied successfully")
            
        except Exception as e:
            logger.warning(f"Could not apply user settings: {e}")
    
    def toggle_theme(self):
        """Toggle theme with modern feedback."""
        # Keep dark theme but provide visual feedback
        self.theme_button.configure(text="✨")
        
        # Reset after delay
        self.after(1000, lambda: self.theme_button.configure(text="🌙"))
        
        logger.info("Theme toggle activated (staying in dark mode for modern experience)")
    
    def on_window_configure(self, event):
        """Handle window resize/move events."""
        if event.widget == self:
            # Save window size
            width = self.winfo_width()
            height = self.winfo_height()
            
            if width > 100 and height > 100:  # Valid sizes only
                set_setting('window_width', width)
                set_setting('window_height', height)
    
    def on_closing(self):
        """Handle window closing event."""
        logger.info("Application closing...")
        
        try:
            # Save current tab
            if hasattr(self, 'current_tab'):
                set_setting('last_active_tab', self.current_tab)
            
            # Save current window state
            self.apply_user_settings()
            
            # Close the application
            self.destroy()
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            self.destroy()  # Force close even if cleanup fails


# For testing the GUI independently
if __name__ == "__main__":
    # Setup basic logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Create and run the application
    app = MainWindow()
    app.mainloop() 