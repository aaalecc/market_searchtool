"""
Search Tab for Market Search Tool
CustomTkinter interface for searching marketplace sites.
"""

import customtkinter as ctk
import logging
from typing import List, Dict, Any
from core.database import DatabaseManager, get_search_results
from core.scrapers import get_available_scrapers
import threading

logger = logging.getLogger(__name__)

class SearchTab(ctk.CTkFrame):
    """Search tab with black and purple design."""
    
    def __init__(self, parent):
        """Initialize the search tab."""
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        logger.info("Initializing Search tab...")
        
        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Initialize database manager
        self.db = DatabaseManager()
        
        # Get available scrapers
        self.available_scrapers = get_available_scrapers()
        
        # Create the interface
        self.create_widgets()
        
        logger.info("Search tab initialized")
    
    def create_widgets(self):
        """Create the search interface with Spotify styling."""
        # Header section
        self.create_header()
        
        # Main content area
        self.create_content()
    
    def create_header(self):
        """Create Spotify-style header."""
        self.header_frame = ctk.CTkFrame(
            self, 
            height=100, 
            corner_radius=0, 
            fg_color="transparent"
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_propagate(False)
        
        # Title with Spotify typography and larger Japanese font
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="マーケットサイト検索",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=25, sticky="w")
    
    def create_content(self):
        """Create Spotify-style content area."""
        # Content frame
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(1, weight=1)
        
        # Search container
        self.search_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=20,
            fg_color="#282828",
            border_width=0
        )
        self.search_container.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        
        # Search form
        self.form_frame = ctk.CTkFrame(self.search_container, fg_color="transparent")
        self.form_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=25)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        # Search label
        search_label = ctk.CTkLabel(
            self.form_frame,
            text="検索キーワード",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        )
        search_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="検索したい商品名を入力してください...",
            height=50,
            width=500,
            corner_radius=25,
            font=ctk.CTkFont(size=16),
            border_width=2,
            border_color="#535353",
            fg_color="#121212",
            text_color="#FFFFFF",
            placeholder_text_color="#B3B3B3"
        )
        self.search_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 20), pady=(0, 0))
        
        # Search button
        self.search_button = ctk.CTkButton(
            self.form_frame,
            text="🔍  検索実行",
            height=50,
            width=150,
            corner_radius=25,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#8B5CF6",
            hover_color="#A78BFA",
            text_color="#FFFFFF",
            command=self.perform_search
        )
        self.search_button.grid(row=1, column=2, sticky="e")
        
        # Price range frame
        self.price_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.price_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(15, 0))
        
        # Min price
        min_price_label = ctk.CTkLabel(
            self.price_frame,
            text="最低価格:",
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF"
        )
        min_price_label.grid(row=0, column=0, padx=(0, 10))
        
        self.min_price_entry = ctk.CTkEntry(
            self.price_frame,
            placeholder_text="¥",
            width=120,
            height=35,
            corner_radius=17,
            font=ctk.CTkFont(size=14),
            border_width=2,
            border_color="#535353",
            fg_color="#121212",
            text_color="#FFFFFF"
        )
        self.min_price_entry.grid(row=0, column=1, padx=(0, 20))
        
        # Max price
        max_price_label = ctk.CTkLabel(
            self.price_frame,
            text="最高価格:",
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF"
        )
        max_price_label.grid(row=0, column=2, padx=(0, 10))
        
        self.max_price_entry = ctk.CTkEntry(
            self.price_frame,
            placeholder_text="¥",
            width=120,
            height=35,
            corner_radius=17,
            font=ctk.CTkFont(size=14),
            border_width=2,
            border_color="#535353",
            fg_color="#121212",
            text_color="#FFFFFF"
        )
        self.max_price_entry.grid(row=0, column=3)
        
        # Site selection frame
        self.sites_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.sites_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(15, 0))
        
        # Site selection label
        sites_label = ctk.CTkLabel(
            self.sites_frame,
            text="検索サイト:",
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF"
        )
        sites_label.grid(row=0, column=0, padx=(0, 10))
        
        # Site checkboxes
        self.site_vars = {}
        for i, (site_id, scraper) in enumerate(self.available_scrapers.items()):
            var = ctk.BooleanVar(value=True)
            self.site_vars[site_id] = var
            checkbox = ctk.CTkCheckBox(
                self.sites_frame,
                text=scraper.name,
                variable=var,
                font=ctk.CTkFont(size=14),
                text_color="#FFFFFF",
                fg_color="#8B5CF6",
                hover_color="#A78BFA",
                border_color="#535353"
            )
            checkbox.grid(row=0, column=i+1, padx=10)
        
        # Results container
        self.results_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=20,
            fg_color="#282828",
            border_width=0
        )
        self.results_container.grid(row=1, column=0, sticky="nsew")
        
        # Results scrollable frame
        self.results_frame = ctk.CTkScrollableFrame(
            self.results_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.results_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Configure grid columns for results
        for i in range(4):
            self.results_frame.grid_columnconfigure(i, weight=1, uniform="col")
    
    def perform_search(self):
        """Perform search with purple-style feedback."""
        # Get search parameters
        query = self.search_entry.get().strip()
        if not query:
            return
        
        # Get price range
        min_price = self.min_price_entry.get().strip()
        max_price = self.max_price_entry.get().strip()
        
        # Get selected sites
        selected_sites = [
            site_id for site_id, var in self.site_vars.items()
            if var.get()
        ]
        
        if not selected_sites:
            return
        
        # Update UI to show loading state
        self.search_button.configure(
            text="⟳  検索中...",
            state="disabled",
            fg_color="#535353"
        )
        
        # Clear existing results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Run search in a separate thread
        def search_thread():
            try:
                # Clear database
                self.db.clear_all_items()
                
                # Run scrapers for selected sites
                for site_id in selected_sites:
                    scraper = self.available_scrapers[site_id]
                    items = scraper.search(
                        query=query,
                        min_price=min_price if min_price else None,
                        max_price=max_price if max_price else None
                    )
                    if items:
                        self.db.insert_items(items)
                
                # Get results sorted by price
                results = get_search_results(
                    query=query,
                    site=None,  # Get from all sites
                    sort_by="price_value",
                    sort_order="asc"
                )
                
                # Update UI with results
                self.after(0, lambda: self.display_results(results))
                
            except Exception as e:
                logger.error(f"Search error: {str(e)}")
                self.after(0, lambda: self.show_error(str(e)))
            finally:
                self.after(0, lambda: self.search_button.configure(
                    text="🔍  検索実行",
                    state="normal",
                    fg_color="#8B5CF6"
                ))
        
        # Start search thread
        threading.Thread(target=search_thread, daemon=True).start()
    
    def display_results(self, results: List[Dict[str, Any]]):
        """Display search results in a grid."""
        if not results:
            # Show no results message
            no_results = ctk.CTkLabel(
                self.results_frame,
                text="検索結果が見つかりませんでした",
                font=ctk.CTkFont(size=16),
                text_color="#B3B3B3"
            )
            no_results.grid(row=0, column=0, columnspan=4, pady=50)
            return
        
        # Display results in a grid
        for i, item in enumerate(results):
            row = i // 4
            col = i % 4
            
            # Create product card
            card = ProductCard(self.results_frame, {
                'title': item['title'],
                'source': item['site'],
                'price': f"¥{item['price_value']:,}",
                'image_url': item.get('image_url')
            })
            card.grid(row=row, column=col, padx=15, pady=15, sticky="ew")
    
    def show_error(self, message: str):
        """Show error message."""
        error_label = ctk.CTkLabel(
            self.results_frame,
            text=f"エラー: {message}",
            font=ctk.CTkFont(size=16),
            text_color="#FF4444"
        )
        error_label.grid(row=0, column=0, columnspan=4, pady=50)

class ProductCard(ctk.CTkFrame):
    """Individual product card widget with black and purple design."""
    
    def __init__(self, parent, product_data: Dict[str, Any]):
        super().__init__(
            parent, 
            corner_radius=16,
            fg_color="#282828",
            border_width=0
        )
        
        self.product_data = product_data
        self.create_card()
        
        # Add hover effect
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        # Bind to all child widgets
        self.bind_all_children()
    
    def bind_all_children(self):
        """Bind hover events to all child widgets."""
        def bind_recursive(widget):
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            for child in widget.winfo_children():
                bind_recursive(child)
        bind_recursive(self)
    
    def create_card(self):
        """Create the product card layout."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Product image placeholder
        self.image_frame = ctk.CTkFrame(
            self, 
            height=200, 
            corner_radius=12,
            fg_color="#3E3E3E"
        )
        self.image_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 12))
        self.image_frame.grid_propagate(False)
        
        # Image placeholder
        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="📷",
            font=ctk.CTkFont(size=56),
            text_color="#B3B3B3"
        )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 16))
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Product title
        title = self.product_data.get('title', 'Product Title')
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=220,
            anchor="w",
            justify="left",
            text_color="#FFFFFF"
        )
        self.title_label.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        
        # Source and price layout
        self.info_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.info_frame.grid(row=1, column=0, sticky="ew")
        self.info_frame.grid_columnconfigure(0, weight=1)
        
        # Product source
        source = self.product_data.get('source', 'Marketplace')
        self.source_label = ctk.CTkLabel(
            self.info_frame,
            text=source,
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#B3B3B3",
            anchor="w"
        )
        self.source_label.grid(row=0, column=0, sticky="w")
        
        # Price
        price = self.product_data.get('price', '¥---')
        self.price_label = ctk.CTkLabel(
            self.info_frame,
            text=price,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#8B5CF6",
            anchor="e"
        )
        self.price_label.grid(row=0, column=1, sticky="e")
        
        # Favorite button
        self.fav_button = ctk.CTkButton(
            self.content_frame,
            text="♡",
            width=30,
            height=30,
            corner_radius=15,
            fg_color="transparent",
            text_color="#B3B3B3",
            hover_color="#8B5CF6",
            font=ctk.CTkFont(size=14)
        )
        self.fav_button.grid(row=0, column=1, sticky="ne", padx=(8, 0))
    
    def on_enter(self, event):
        """Hover effect."""
        self.configure(fg_color="#3E3E3E")
    
    def on_leave(self, event):
        """Reset hover effect."""
        self.configure(fg_color="#282828") 