"""
Search Tab for Market Search Tool
CustomTkinter interface for searching marketplace sites.
"""

import customtkinter as ctk
import logging
from typing import List, Dict, Any
from core.database import DatabaseManager, get_search_results, get_database_stats, create_saved_search, add_saved_search_items
import threading
import subprocess
import sys
import os
from PIL import Image, ImageTk, ImageOps
import requests
from io import BytesIO
from customtkinter import CTkImage
from CTkMessagebox import CTkMessagebox
from customtkinter import CTkInputDialog

logger = logging.getLogger(__name__)

class SearchTab(ctk.CTkFrame):
    """Search tab with black and purple design."""
    
    def __init__(self, parent, font=None):
        """Initialize the search tab."""
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.font = font
        self.font_family = self.font.cget('family') if self.font else "Meiryo UI"
        logger.info(f"{self.__class__.__name__} initialized with font family: {self.font_family}")
        
        logger.info("Initializing Search tab...")
        
        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Search box (smaller)
        self.grid_rowconfigure(2, weight=1)  # Product/results area (bigger)
        
        # Initialize database manager
        self.db = DatabaseManager()
        
        # Define available sites
        self.available_sites = {
            'yahoo': {'name': 'Yahoo Auctions'},
            'rakuten': {'name': 'Rakuten'}
        }
        
        # Initialize pagination state
        self.current_page = 1
        self.items_per_page = 40  # 4 columns x 10 rows
        
        # Create the interface
        self.create_widgets()
        
        logger.info("Search tab initialized")
    
    def create_widgets(self):
        """Create the search interface with Spotify styling."""
        # Define fonts based on self.font_family for this method
        header_title_font = ctk.CTkFont(family=self.font_family, size=36, weight="bold")
        save_button_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")
        entry_font = ctk.CTkFont(family=self.font_family, size=15)
        price_entry_font = ctk.CTkFont(family=self.font_family, size=14)
        search_button_font = ctk.CTkFont(family=self.font_family, size=15, weight="bold")
        checkbox_font = ctk.CTkFont(family=self.font_family, size=14)

        self.create_header(header_title_font, save_button_font)
        self.create_content(entry_font, price_entry_font, search_button_font, checkbox_font)
    
    def create_header(self, title_font, button_font):
        """Create Spotify-style header."""
        self.header_frame = ctk.CTkFrame(self, height=100, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)
        # self.header_frame.grid_propagate(False) # Commented out, might not be needed / could affect layout
        
        self.title_label = ctk.CTkLabel(self.header_frame, text="マーケットサイト検索", font=title_font, text_color="#FFFFFF", anchor="w")
        self.title_label.grid(row=0, column=0, padx=30, pady=25, sticky="w")
        
        self.save_search_button = ctk.CTkButton(
            self.header_frame, text="💾 検索を保存", height=36, width=140, corner_radius=18,
            font=button_font, fg_color="#22c55e", hover_color="#16a34a",
            text_color="#FFFFFF", command=self.save_current_search
        )
        self.save_search_button.grid(row=0, column=1, padx=(0, 30), pady=(20, 0), sticky="e")
    
    def create_content(self, entry_font, price_font, search_btn_font, chkbox_font):
        """Create Spotify-style content area with a two-row search form."""
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Search container area
        self.content_frame.grid_rowconfigure(1, weight=1)  # Results area
        
        # Main search container (no fixed height, will auto-adjust)
        self.search_container = ctk.CTkFrame(self.content_frame, corner_radius=16, fg_color="#282828", border_width=0)
        self.search_container.grid(row=0, column=0, sticky="ew", pady=(0, 20)) # Increased bottom-padding for results separation
        self.search_container.grid_columnconfigure(0, weight=1)
        # Configure rows for top and bottom form parts
        self.search_container.grid_rowconfigure(0, weight=0)
        self.search_container.grid_rowconfigure(1, weight=0)

        # Top row of the form (keywords, prices, search button)
        self.top_form_frame = ctk.CTkFrame(self.search_container, fg_color="transparent")
        self.top_form_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5)) # pady top and bottom internal to search_container
        self.top_form_frame.grid_columnconfigure(0, weight=1) # Search entry expands
        self.top_form_frame.grid_columnconfigure(1, weight=0)
        self.top_form_frame.grid_columnconfigure(2, weight=0)
        self.top_form_frame.grid_columnconfigure(3, weight=0)
        
        self.search_entry = ctk.CTkEntry(
            self.top_form_frame, placeholder_text="検索したい商品名を入力してください...", height=40, corner_radius=20,
            font=entry_font, border_width=2, border_color="#535353", fg_color="#121212",
            text_color="#FFFFFF", placeholder_text_color="#B3B3B3"
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.min_price_entry = ctk.CTkEntry(
            self.top_form_frame, placeholder_text="最低価格", width=100, height=40, corner_radius=15, # Increased width slightly
            font=price_font, border_width=2, border_color="#535353", fg_color="#121212", text_color="#FFFFFF"
        )
        self.min_price_entry.grid(row=0, column=1, padx=(0, 5))
        
        self.max_price_entry = ctk.CTkEntry(
            self.top_form_frame, placeholder_text="最高価格", width=100, height=40, corner_radius=15, # Increased width slightly
            font=price_font, border_width=2, border_color="#535353", fg_color="#121212", text_color="#FFFFFF"
        )
        self.max_price_entry.grid(row=0, column=2, padx=(0, 10))
        
        self.search_button = ctk.CTkButton(
            self.top_form_frame, text="🔍  検索実行", height=40, width=130, corner_radius=20, # Increased width slightly
            font=search_btn_font, fg_color="#8B5CF6", hover_color="#A78BFA",
            text_color="#FFFFFF", command=self.perform_search
        )
        self.search_button.grid(row=0, column=3, padx=(0, 0)) # No right padx if it's the last element

        # Bottom row of the form (checkboxes)
        self.bottom_form_frame = ctk.CTkFrame(self.search_container, fg_color="transparent")
        self.bottom_form_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(5, 10)) # pady top and bottom internal
        # Configure columns for checkboxes, let them pack naturally or distribute as needed
        # For now, let them pack left

        self.site_vars = {}
        for i, (site_id, scraper_info) in enumerate(self.available_sites.items()):
            var = ctk.BooleanVar(value=True)
            self.site_vars[site_id] = var
            checkbox = ctk.CTkCheckBox(
                self.bottom_form_frame, text=scraper_info['name'], variable=var, font=chkbox_font,
                text_color="#FFFFFF", fg_color="#8B5CF6", hover_color="#A78BFA", border_color="#535353"
            )
            checkbox.pack(side="left", padx=5, pady=5) # Use pack for horizontal arrangement in bottom_form_frame
        
        # Results container (remains the same)
        self.results_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=20,
            fg_color="#282828",
            border_width=0
        )
        self.results_container.grid(row=1, column=0, sticky="nsew", pady=(10,0)) # Added top padding
        
        # Results scrollable frame (remains the same)
        self.results_frame = ctk.CTkScrollableFrame(
            self.results_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.results_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        for i in range(4):
            self.results_frame.grid_columnconfigure(i, weight=1, uniform="col")
    
    def perform_search(self):
        """Perform search with purple-style feedback."""
        # Get search parameters
        query = self.search_entry.get().strip()
        if not query:
            return
        
        # Get price range and convert to integers
        min_price = None
        max_price = None
        try:
            min_price_str = self.min_price_entry.get().strip()
            if min_price_str:
                min_price = int(min_price_str)
            max_price_str = self.max_price_entry.get().strip()
            if max_price_str:
                max_price = int(max_price_str)
        except ValueError:
            self.show_error("価格は整数で入力してください。")
            return
        
        # Get selected sites
        selected_sites = [
            site_id for site_id, var in self.site_vars.items()
            if var.get()
        ]
        
        if not selected_sites:
            return
        
        # Disable search button during search
        self.search_button.configure(state="disabled", text="🔍  検索中...")
        
        def search_thread():
            try:
                # Get the root directory path
                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                # Build command arguments with full path
                cmd = [sys.executable, os.path.join(root_dir, "test_scraper.py")]
                
                # Add sites
                cmd.extend(["--sites"] + selected_sites)
                
                # Add price range if specified
                if min_price is not None:
                    cmd.extend(["--min-price", str(min_price)])
                if max_price is not None:
                    cmd.extend(["--max-price", str(max_price)])
                
                # Add keywords
                cmd.extend(["--keywords"] + query.split())
                
                # Print command for debugging
                print("Running command:", " ".join(cmd))
                
                # Run the scraper with both stdout and stderr
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    cwd=root_dir,  # Set working directory to root
                    env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}  # Force UTF-8 encoding
                )
                
                # Print output for debugging
                print("Command output:", process.stdout)
                if process.stderr:
                    print("Command errors:", process.stderr)
                
                if process.returncode == 0:
                    # Get database stats filtered by current query - normalize query format
                    normalized_query = ' '.join(query.split())
                    stats = get_database_stats(query=normalized_query)
                    print("Database stats:", stats)  # Debug print
                    
                    # Update UI with results
                    self.after(0, lambda: self.display_search_results(stats))
                else:
                    error_msg = f"Error running scraper: {process.stderr}"
                    self.after(0, lambda: self.show_error(error_msg))
            
            except Exception as e:
                error_msg = f"Error during search: {str(e)}"
                self.after(0, lambda: self.show_error(error_msg))
            finally:
                # Re-enable search button
                self.after(0, lambda: self.search_button.configure(state="normal", text="🔍  検索実行"))
        
        # Start search in a separate thread
        threading.Thread(target=search_thread, daemon=True).start()
    
    def display_search_results(self, stats: Dict[str, int]):
        """Display search results statistics and items in a grid layout."""
        # Clear previous results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Create results header
        header = ctk.CTkLabel(
            self.results_frame,
            text="検索結果",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FFFFFF"
        )
        header.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 20))
        
        # Display total items
        total_label = ctk.CTkLabel(
            self.results_frame,
            text=f"総アイテム数: {stats['total_items']}",
            font=ctk.CTkFont(size=18),
            text_color="#FFFFFF"
        )
        total_label.grid(row=1, column=0, columnspan=4, sticky="w", pady=(0, 10))
        
        # Display items by site
        yahoo_label = ctk.CTkLabel(
            self.results_frame,
            text=f"Yahoo Auctions: {stats['yahoo_items']} アイテム",
            font=ctk.CTkFont(size=16),
            text_color="#FFFFFF"
        )
        yahoo_label.grid(row=2, column=0, columnspan=4, sticky="w", pady=(0, 5))
        
        rakuten_label = ctk.CTkLabel(
            self.results_frame,
            text=f"Rakuten: {stats['rakuten_items']} アイテム",
            font=ctk.CTkFont(size=16),
            text_color="#FFFFFF"
        )
        rakuten_label.grid(row=3, column=0, columnspan=4, sticky="w", pady=(0, 20))
        
        # Calculate offset for current page
        offset = (self.current_page - 1) * self.items_per_page
        
        # Get current search query - join keywords with spaces to match scraper format
        current_query = ' '.join(self.search_entry.get().strip().split())
        
        # Get search results from database, filtered by current query
        results = get_search_results(
            query=current_query,
            limit=self.items_per_page,
            offset=offset,
            sort_by="price_value",
            sort_order="asc"
        )
        
        if not results:
            no_results = ctk.CTkLabel(
                self.results_frame,
                text="検索結果が見つかりませんでした",
                font=ctk.CTkFont(size=16),
                text_color="#B3B3B3"
            )
            no_results.grid(row=4, column=0, columnspan=4, pady=50)
            return
        
        # Display items in a grid (4 items per row)
        for i, item in enumerate(results):
            row = (i // 4) + 4  # Start from row 4 (after stats)
            col = i % 4
            
            # Create product card
            card = ProductCard(self.results_frame, {
                'title': item['title'],
                'source': item['site'],
                'price': item['price_formatted'],
                'image_url': item.get('image_url'),
                'url': item['url']  # Add the URL
            }, self.font_family)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Add pagination if there are more than 40 items
        if stats['total_items'] > self.items_per_page:
            self.create_pagination(stats['total_items'])
    
    def create_pagination(self, total_items: int):
        """Create pagination controls."""
        total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        
        # Create pagination frame
        pagination_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        pagination_frame.grid(row=1000, column=0, columnspan=4, sticky="ew", pady=20)
        
        # Previous page button
        prev_button = ctk.CTkButton(
            pagination_frame,
            text="← 前へ",
            width=100,
            height=35,
            corner_radius=17,
            fg_color="#8B5CF6",
            hover_color="#A78BFA",
            text_color="#FFFFFF",
            command=lambda: self.change_page(self.current_page - 1),
            state="disabled" if self.current_page == 1 else "normal"
        )
        prev_button.pack(side="left", padx=10)
        
        # Page indicator
        page_label = ctk.CTkLabel(
            pagination_frame,
            text=f"ページ {self.current_page} / {total_pages}",
            font=ctk.CTkFont(size=14),
            text_color="#FFFFFF"
        )
        page_label.pack(side="left", padx=20)
        
        # Next page button
        next_button = ctk.CTkButton(
            pagination_frame,
            text="次へ →",
            width=100,
            height=35,
            corner_radius=17,
            fg_color="#8B5CF6",
            hover_color="#A78BFA",
            text_color="#FFFFFF",
            command=lambda: self.change_page(self.current_page + 1),
            state="disabled" if self.current_page == total_pages else "normal"
        )
        next_button.pack(side="left", padx=10)
    
    def change_page(self, new_page: int):
        """Change the current page of results."""
        if new_page < 1:
            return
            
        self.current_page = new_page
        
        # Get current search query
        current_query = self.search_entry.get().strip()
        
        # Get updated stats filtered by current query
        stats = get_database_stats(query=current_query)
        
        # Redisplay results with new page
        self.display_search_results(stats)
    
    def show_error(self, message: str):
        """Show error message."""
        error_label = ctk.CTkLabel(
            self.results_frame,
            text=f"エラー: {message}",
            font=ctk.CTkFont(size=16),
            text_color="#FF4444"
        )
        error_label.grid(row=0, column=0, columnspan=4, pady=50)
    
    def save_current_search(self):
        """Save the current search options and items to the database as a saved search."""
        # Gather current search options
        keywords = self.search_entry.get().strip().split()
        min_price = self.min_price_entry.get().strip()
        max_price = self.max_price_entry.get().strip()
        selected_sites = [site_id for site_id, var in self.site_vars.items() if var.get()]
        
        if not keywords:
            CTkMessagebox(title="エラー", message="キーワードを入力してください。", icon="cancel", font=(self.font_family, 12))
            return
        if not selected_sites:
            CTkMessagebox(title="エラー", message="検索サイトを少なくとも1つ選択してください。", icon="cancel", font=(self.font_family, 12))
            return

        options = {
            'keywords': keywords,
            'min_price': min_price,
            'max_price': max_price,
            'sites': selected_sites
        }
        
        # Prompt for a name using CTkInputDialog
        dialog = CTkInputDialog(text="この検索の名前を入力してください:", title="保存名", font=(self.font_family, 12))
        name = dialog.get_input()
        if not name:
            return  # User cancelled or left blank
            
        # Save search options with name
        saved_search_id = create_saved_search(options, name)
        
        if saved_search_id:
            # Get all items for the current search query
            current_query = ' '.join(keywords)
            all_items = get_search_results(
                query=current_query,
                limit=1000,  # Get all items
                offset=0,
                sort_by="price_value",
                sort_order="asc"
            )
            
            if all_items:
                add_saved_search_items(saved_search_id, all_items)
                CTkMessagebox(
                    title="保存完了", 
                    message=f"「{name}」が{len(all_items)}件のアイテムと共に保存されました。", 
                    icon="check", 
                    font=(self.font_family, 12)
                )
            else:
                CTkMessagebox(
                    title="保存完了", 
                    message=f"「{name}」が保存されました。(アイテムなし)", 
                    icon="check", 
                    font=(self.font_family, 12)
                )

            # Refresh the Saved Searches tab if possible
            main_window = self.winfo_toplevel()
            if hasattr(main_window, 'saved_searches_tab') and hasattr(main_window.saved_searches_tab, 'display_saved_searches'):
                # Access the font_family from the saved_searches_tab instance
                sst_font_family = main_window.saved_searches_tab.font_family
                # Define fonts as expected by display_saved_searches
                name_font = ctk.CTkFont(family=sst_font_family, size=18, weight="bold")
                opts_font = ctk.CTkFont(family=sst_font_family, size=14)
                count_font = ctk.CTkFont(family=sst_font_family, size=14, weight="bold")
                sw_font = ctk.CTkFont(family=sst_font_family, size=14)
                del_btn_font = ctk.CTkFont(family=sst_font_family, size=14, weight="bold")
                main_window.saved_searches_tab.display_saved_searches(name_font, opts_font, count_font, sw_font, del_btn_font)
        else:
            CTkMessagebox(
                title="保存失敗", 
                message="検索の保存中にエラーが発生しました。", 
                icon="cancel", 
                font=(self.font_family, 12)
            )

class ProductCard(ctk.CTkFrame):
    """Individual product card widget with black and purple design."""
    
    def __init__(self, parent, product_data: Dict[str, Any], font_family: str = "Meiryo UI"):
        super().__init__(parent, corner_radius=16, fg_color="#282828", border_width=0)
        self.product_data = product_data
        self.font_family = font_family
        self.create_card()
        
        # Add hover effect
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        # Add click event
        self.bind("<Button-1>", self.on_click)
        
        # Bind to all child widgets
        self.bind_all_children()
    
    def bind_all_children(self):
        """Bind hover and click events to all child widgets."""
        def bind_recursive(widget):
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)
            widget.bind("<Button-1>", self.on_click)
            for child in widget.winfo_children():
                bind_recursive(child)
        bind_recursive(self)
    
    def on_click(self, event):
        """Handle click event to open product URL."""
        url = self.product_data.get('url')
        if url:
            import webbrowser
            webbrowser.open(url)
    
    def create_card(self):
        """Create the product card layout."""
        # Configure grid for the card itself
        self.grid_rowconfigure(0, weight=1)  # Content area
        self.grid_rowconfigure(1, weight=0)  # Price/footer
        self.grid_columnconfigure(0, weight=1)
        
        # Content frame (image, title, source, spacer)
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=(0, 0))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # image
        self.content_frame.grid_rowconfigure(1, weight=0)  # title
        self.content_frame.grid_rowconfigure(2, weight=0)  # source
        self.content_frame.grid_rowconfigure(3, weight=1)  # spacer
        
        # Product image placeholder or real image
        self.image_frame = ctk.CTkFrame(
            self.content_frame, 
            height=150, 
            corner_radius=12,
            fg_color="#3E3E3E"
        )
        self.image_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 12))
        self.image_frame.grid_propagate(False)
        
        image_url = self.product_data.get('image_url')
        if image_url:
            try:
                response = requests.get(image_url, timeout=5)
                img_data = BytesIO(response.content)
                pil_image = Image.open(img_data).convert("RGBA")
                target_size = (220, 140)
                pil_image = ImageOps.contain(pil_image, target_size, method=Image.LANCZOS)
                background = Image.new("RGBA", target_size, (62, 62, 62, 255))
                background.paste(pil_image, ((target_size[0] - pil_image.width) // 2, (target_size[1] - pil_image.height) // 2))
                self.ctk_image = CTkImage(light_image=background, size=target_size)
                self.image_label = ctk.CTkLabel(
                    self.image_frame,
                    image=self.ctk_image,
                    text=""
                )
            except Exception as e:
                self.image_label = ctk.CTkLabel(
                    self.image_frame,
                    text="📷",
                    font=ctk.CTkFont(family=self.font_family, size=48),
                    text_color="#B3B3B3"
                )
        else:
            self.image_label = ctk.CTkLabel(
                self.image_frame,
                text="📷",
                font=ctk.CTkFont(family=self.font_family, size=48),
                text_color="#B3B3B3"
            )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Product title (truncate if too long)
        title = self.product_data.get('title', 'Product Title')
        max_chars = 50
        if len(title) > max_chars:
            title = title[:max_chars-3] + '...'
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text=title,
            font=ctk.CTkFont(family=self.font_family, size=12, weight="bold"),
            wraplength=160,
            anchor="w",
            justify="left",
            text_color="#FFFFFF"
        )
        self.title_label.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        
        # Product source
        source = self.product_data.get('source', 'Marketplace')
        self.source_label = ctk.CTkLabel(
            self.content_frame,
            text=source,
            font=ctk.CTkFont(family=self.font_family, size=12, weight="normal"),
            text_color="#B3B3B3",
            anchor="w"
        )
        self.source_label.grid(row=2, column=0, sticky="w")
        
        # Spacer to fill space above price
        self.spacer = ctk.CTkLabel(self.content_frame, text="", font=ctk.CTkFont(family=self.font_family, size=1))
        self.spacer.grid(row=3, column=0, sticky="nswe")
        
        # Price at the bottom/footer of the card
        price = self.product_data.get('price', '¥---')
        self.price_label = ctk.CTkLabel(
            self,
            text=price,
            font=ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
            text_color="#8B5CF6",
            anchor="e"
        )
        self.price_label.grid(row=1, column=0, sticky="sew", pady=(0, 8), padx=0)
        
        # Add cursor change on hover
        self.configure(cursor="hand2")
        self.content_frame.configure(cursor="hand2")
        self.image_frame.configure(cursor="hand2")
        self.image_label.configure(cursor="hand2")
        self.title_label.configure(cursor="hand2")
        self.source_label.configure(cursor="hand2")
        self.price_label.configure(cursor="hand2")
    
    def on_enter(self, event):
        """Hover effect."""
        self.configure(fg_color="#3E3E3E")
    
    def on_leave(self, event):
        """Reset hover effect."""
        self.configure(fg_color="#282828") 