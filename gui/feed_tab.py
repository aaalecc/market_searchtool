"""
Feed Tab for Market Search Tool
CustomTkinter interface for monitoring new listings.
"""

import customtkinter as ctk
import logging
from typing import List, Dict, Any

from core.database import get_new_items, get_saved_searches
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
        self.refresh_display()
    
    def refresh_display(self):
        """Re-fetches data and refreshes the feed interface."""
        # Clear existing widgets before redrawing
        for widget in self.winfo_children():
            widget.destroy()
        
        title_font = ctk.CTkFont(family=self.font_family, size=36, weight="bold")
        self.title_label = ctk.CTkLabel(self, text="フィード", font=title_font, text_color="#FFFFFF", anchor="w")
        self.title_label.pack(anchor="nw", padx=30, pady=25, fill="x")

        # Fetch the latest data
        all_new_items_by_search = get_new_items(limit=100)
        # Ensure we get the latest saved searches, especially their notification_enabled status
        saved_searches = [s for s in get_saved_searches() if s.get('notifications_enabled')]
        
        message_font = ctk.CTkFont(family=self.font_family, size=18)
        section_header_font = ctk.CTkFont(family=self.font_family, size=20, weight="bold")
        empty_item_font = ctk.CTkFont(family=self.font_family, size=16)

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
            
            section_label = ctk.CTkLabel(search_card_container, text=search_name, font=section_header_font, text_color="#8B5CF6", anchor="w")
            section_label.pack(anchor="nw", padx=15, pady=(10, 5), fill="x")
            
            items = all_new_items_by_search.get(search_name, [])
            items_display_frame = ctk.CTkFrame(search_card_container, fg_color="transparent")
            items_display_frame.pack(anchor="nw", fill="x", padx=15, pady=(0,10))

            if not items:
                empty_item_label = ctk.CTkLabel(items_display_frame, text="新規アイテムはありません", font=empty_item_font, text_color="#B3B3B3", anchor="w")
                empty_item_label.pack(anchor="nw", padx=0, pady=4, fill="x")
                continue
            
            found_items_for_any_search = True
            self._display_items_for_search(items_display_frame, search_name, items, initial_display=True)

        if not found_items_for_any_search and saved_searches:
            overall_empty_label = ctk.CTkLabel(self, text="全ての有効な検索に新規アイテムはありません。", font=message_font, text_color="#B3B3B3", anchor="center")
            overall_empty_label.pack(anchor="center", padx=40, pady=20, fill="x", expand=True)

    def _display_items_for_search(self, parent_frame: ctk.CTkFrame, search_name: str, all_items: List[Dict], initial_display: bool = True):
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        item_text_font = ctk.CTkFont(family=self.font_family, size=15)
        button_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")

        items_to_show = all_items[:4] if initial_display else all_items[:16]
        item_list_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        item_list_frame.pack(anchor="nw", fill="x", pady=(0,5))

        # Configure grid for 4 cards per row
        item_list_frame.grid_columnconfigure(0, weight=1)
        item_list_frame.grid_columnconfigure(1, weight=1)
        item_list_frame.grid_columnconfigure(2, weight=1)
        item_list_frame.grid_columnconfigure(3, weight=1)

        for i, item in enumerate(items_to_show):
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
            card = ProductCard(item_list_frame, product_data, font_family=self.font_family)
            row = i // 4
            col = i % 4
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        if initial_display and len(all_items) > 4:
            expand_button = ctk.CTkButton(parent_frame, text="もっと見る", width=100, font=button_font, command=lambda sf=parent_frame, sn=search_name, ai=all_items: self._display_items_for_search(sf, sn, ai, initial_display=False))
            expand_button.pack(anchor="ne", padx=0, pady=(5, 0))
        elif not initial_display and len(all_items) > 16:
            show_less_button = ctk.CTkButton(parent_frame, text="少なく表示", width=100, font=button_font, command=lambda sf=parent_frame, sn=search_name, ai=all_items: self._display_items_for_search(sf, sn, ai, initial_display=True))
            show_less_button.pack(anchor="ne", padx=0, pady=(5, 0))


    # Removed ProductCard class as it's not used in this minimal version
    # Removed on_enter, on_leave, bind_all_children, create_card from ProductCard
    # Removed original create_header and create_content_area from FeedTab
    # Removed original display_new_items as logic is now in create_widgets
    # Removed original expand_search_items as logic is now in _display_items_for_search
    # Removed refresh_feed and schedule_refresh and references to self.refresh_button
    # Removed open_item as item interaction is not part of this minimal design
    # The expand_search_items_simple is replaced by _display_items_for_search helper

