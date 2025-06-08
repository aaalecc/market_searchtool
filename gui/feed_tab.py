"""
Feed Tab for Market Search Tool
CustomTkinter interface for monitoring new listings.
"""

import customtkinter as ctk
import logging
from typing import List, Dict, Any
from datetime import datetime

from core.database import get_new_items, get_saved_searches, get_new_items_count
from gui.search_tab import ProductCard

logger = logging.getLogger(__name__)

class FeedTab(ctk.CTkFrame):
    """Feed tab with a minimal design, showing saved searches and their items."""
    
    def __init__(self, parent, font=None):
        """Initialize the feed tab."""
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.font = font
        self.font_family = self.font.cget('family') if self.font else "Meiryo UI"
        logger.info(f"{self.__class__.__name__} initialized with font family: {self.font_family}")
        
        self.grid_columnconfigure(0, weight=1)
        self.current_view = "feed"  # Track current view: "feed" or "items"
        self.current_search_name = None
        self.current_items = None
        self.refresh_display()
    
    def refresh_display(self):
        """Re-fetches data and refreshes the feed interface."""
        # Clear existing widgets before redrawing
        for widget in self.winfo_children():
            widget.destroy()
        
        if self.current_view == "feed":
            self._show_feed_view()
        else:
            self._show_items_view(self.current_search_name, self.current_items)
    
    def _show_feed_view(self):
        """Show the main feed view with saved searches."""
        title_font = ctk.CTkFont(family=self.font_family, size=36, weight="bold")
        self.title_label = ctk.CTkLabel(self, text="フィード", font=title_font, text_color="#FFFFFF", anchor="w")
        self.title_label.pack(anchor="nw", padx=30, pady=25, fill="x")

        # Fetch the latest data
        all_new_items_by_search = get_new_items(limit=100)
        # Ensure we get the latest saved searches, especially their notification_enabled status
        saved_searches = [s for s in get_saved_searches() if s.get('notifications_enabled')]
        
        message_font = ctk.CTkFont(family=self.font_family, size=18)
        section_header_font = ctk.CTkFont(family=self.font_family, size=20, weight="bold")
        info_font = ctk.CTkFont(family=self.font_family, size=16)
        button_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")

        if not saved_searches:
            empty_label = ctk.CTkLabel(self, text="有効な通知設定の保存済み検索はありません。", font=message_font, text_color="#B3B3B3", anchor="center")
            empty_label.pack(anchor="center", padx=40, pady=20, fill="x", expand=True)
            return
        
        found_items_for_any_search = False
        for search in saved_searches:
            search_id = search['id']
            search_name = search.get('name', f"Search {search_id}")
            
            search_card_container = ctk.CTkFrame(self, fg_color="#282828", border_width=1, border_color="#404040", corner_radius=12)
            search_card_container.pack(anchor="nw", fill="x", padx=30, pady=(10, 5))
            
            # Header with search name
            header_frame = ctk.CTkFrame(search_card_container, fg_color="transparent")
            header_frame.pack(fill="x", padx=15, pady=(10, 5))
            
            section_label = ctk.CTkLabel(header_frame, text=search_name, font=section_header_font, text_color="#8B5CF6", anchor="w")
            section_label.pack(side="left", padx=0, pady=0)
            
            # Get item counts
            items = all_new_items_by_search.get(search_name, [])
            if not items:
                empty_item_label = ctk.CTkLabel(search_card_container, text="新規アイテムはありません", font=info_font, text_color="#B3B3B3", anchor="w")
                empty_item_label.pack(anchor="nw", padx=15, pady=(0, 10), fill="x")
                continue
            
            found_items_for_any_search = True
            
            # Count items by site
            site_counts = {}
            for item in items:
                site = item.get('site', 'Unknown')
                site_counts[site] = site_counts.get(site, 0) + 1
            
            # Create info frame
            info_frame = ctk.CTkFrame(search_card_container, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            # Total items count
            total_count_label = ctk.CTkLabel(info_frame, 
                text=f"合計: {len(items)}件の新規アイテム", 
                font=info_font, 
                text_color="#FFFFFF"
            )
            total_count_label.pack(anchor="w", pady=(0, 5))
            
            # Site-specific counts
            for site, count in site_counts.items():
                site_label = ctk.CTkLabel(info_frame,
                    text=f"{site}: {count}件",
                    font=info_font,
                    text_color="#B3B3B3"
                )
                site_label.pack(anchor="w", pady=(0, 2))
            
            # View button
            view_button = ctk.CTkButton(
                search_card_container,
                text="アイテムを表示",
                font=button_font,
                command=lambda s=search_name, i=items: self._show_items_view(s, i)
            )
            view_button.pack(anchor="e", padx=15, pady=(0, 10))

        if not found_items_for_any_search and saved_searches:
            overall_empty_label = ctk.CTkLabel(self, text="全ての有効な検索に新規アイテムはありません。", font=message_font, text_color="#B3B3B3", anchor="center")
            overall_empty_label.pack(anchor="center", padx=40, pady=20, fill="x", expand=True)

    def _show_items_view(self, search_name: str, items: List[Dict]):
        """Show items view in the current window."""
        # Store current state
        self.current_view = "items"
        self.current_search_name = search_name
        self.current_items = items
        
        # Clear existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Header with title and back button
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_font = ctk.CTkFont(family=self.font_family, size=24, weight="bold")
        title_label = ctk.CTkLabel(header_frame, text=search_name, font=title_font, text_color="#FFFFFF")
        title_label.pack(side="left")
        
        back_button = ctk.CTkButton(
            header_frame,
            text="戻る",
            font=ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
            command=self._go_back_to_feed
        )
        back_button.pack(side="right")
        
        # Create scrollable frame for items
        items_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        items_frame.pack(fill="both", expand=True)
        
        # Configure grid for 4 cards per row
        items_frame.grid_columnconfigure(0, weight=1)
        items_frame.grid_columnconfigure(1, weight=1)
        items_frame.grid_columnconfigure(2, weight=1)
        items_frame.grid_columnconfigure(3, weight=1)
        
        # Sort items by price
        sorted_items = sorted(items, key=lambda x: x.get('price_value', float('inf')))
        
        # Add product cards
        for i, item in enumerate(sorted_items):
            # Format price
            price_value = item.get('price_value', 0)
            price_formatted = item.get('price_formatted', '')
            if not price_formatted and price_value:
                price_formatted = f"¥{price_value:,.0f}"
            
            # Prepare product_data for ProductCard
            product_data = {
                'title': item.get('title', ''),
                'image_url': item.get('image_url', None),
                'price': price_formatted,
                'source': item.get('site', item.get('source', '')),
                'url': item.get('url', '')
            }
            
            card = ProductCard(items_frame, product_data, font_family=self.font_family)
            row = i // 4
            col = i % 4
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    def _go_back_to_feed(self):
        """Return to the feed view."""
        self.current_view = "feed"
        self.current_search_name = None
        self.current_items = None
        self.refresh_display()

