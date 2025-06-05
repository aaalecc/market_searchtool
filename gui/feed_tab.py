"""
Feed Tab for Market Search Tool
CustomTkinter interface for monitoring new listings.
"""

import customtkinter as ctk
import logging
from typing import List, Dict, Any

from core.database import get_new_items, get_saved_searches

logger = logging.getLogger(__name__)

class FeedTab(ctk.CTkFrame):
    """Feed tab with a minimal design, showing saved searches and their items."""
    
    def __init__(self, parent):
        """Initialize the feed tab."""
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        logger.info("Initializing Feed tab...")
        
        # Configure layout (important for .pack to work as expected)
        self.grid_columnconfigure(0, weight=1) 
        # self.grid_rowconfigure(0, weight=0) # For title
        # self.grid_rowconfigure(1, weight=1) # For scrollable content area if we add it back

        self.create_widgets()
        logger.info("Feed tab initialized")
    
    def create_widgets(self):
        """Create a minimal feed interface: just a title and a list of saved searches with notifications enabled and their items."""
        # Clear all widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Title (like other tabs)
        self.title_label = ctk.CTkLabel(
            self,
            text="フィード",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        self.title_label.pack(anchor="nw", padx=30, pady=25, fill="x")

        # Fetch all new items once
        all_new_items_by_search = get_new_items(limit=100)
        
        # List saved searches with notifications enabled
        saved_searches = [s for s in get_saved_searches() if s.get('notifications_enabled')]
        
        if not saved_searches:
            empty_label = ctk.CTkLabel(
                self,
                text="有効な通知設定の保存済み検索はありません。", # Changed message
                font=ctk.CTkFont(size=18),
                text_color="#B3B3B3",
                anchor="w"
            )
            empty_label.pack(anchor="nw", padx=40, pady=8, fill="x")
            return
        
        found_items_for_any_search = False
        for search in saved_searches:
            search_id = search['id']
            search_name = search.get('name', f"Search {search_id}")
            
            # Section header for the saved search
            section_label = ctk.CTkLabel(
                self,
                text=search_name,
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#8B5CF6",
                anchor="w"
            )
            section_label.pack(anchor="nw", padx=40, pady=(16, 4), fill="x")
            
            items = all_new_items_by_search.get(search_name, [])
            
            if not items:
                empty_item_label = ctk.CTkLabel(
                    self,
                    text="新規アイテムはありません",
                    font=ctk.CTkFont(size=16),
                    text_color="#B3B3B3",
                    anchor="w"
                )
                empty_item_label.pack(anchor="nw", padx=60, pady=4, fill="x")
                continue # Move to the next search
            
            found_items_for_any_search = True
            # Container for items and expand button for this search
            # This helps in expand_search_items_simple to target removal
            search_items_frame = ctk.CTkFrame(self, fg_color="transparent")
            search_items_frame.pack(anchor="nw", fill="x", padx=0, pady=0)
            search_items_frame.search_name_ref = search_name # Store reference for expand

            self._display_items_for_search(search_items_frame, search_name, items, initial_display=True)

        if not found_items_for_any_search and saved_searches:
             # This message appears if there are enabled searches, but NONE of them have items.
            overall_empty_label = ctk.CTkLabel(
                self,
                text="全ての有効な検索に新規アイテムはありません。",
                font=ctk.CTkFont(size=18),
                text_color="#B3B3B3",
                anchor="w"
            )
            overall_empty_label.pack(anchor="nw", padx=40, pady=8, fill="x")


    def _display_items_for_search(self, parent_frame: ctk.CTkFrame, search_name: str, all_items: List[Dict], initial_display: bool = True):
        """Helper to display items for a given search, either initially (10) or expanded (100)."""
        for widget in parent_frame.winfo_children(): # Clear previous items/button in this frame
            widget.destroy()

        items_to_show = all_items[:10] if initial_display else all_items

        for item in items_to_show:
            item_label = ctk.CTkLabel(
                parent_frame,
                text=item['title'], # Simple display, just title
                font=ctk.CTkFont(size=15),
                text_color="#FFFFFF",
                anchor="w"
            )
            item_label.pack(anchor="nw", padx=60, pady=2, fill="x")
            
        if initial_display and len(all_items) > 10:
            expand_button = ctk.CTkButton(
                parent_frame,
                text="もっと見る",
                width=100,
                command=lambda sf=parent_frame, sn=search_name, ai=all_items: self._display_items_for_search(sf, sn, ai, initial_display=False)
            )
            expand_button.pack(anchor="nw", padx=60, pady=(2, 8))
        elif not initial_display and len(all_items) > 10: # Optionally, show a "show less" or just leave it expanded
            # You could add a "show less" button here if desired
            pass


    # Removed ProductCard class as it's not used in this minimal version
    # Removed on_enter, on_leave, bind_all_children, create_card from ProductCard
    # Removed original create_header and create_content_area from FeedTab
    # Removed original display_new_items as logic is now in create_widgets
    # Removed original expand_search_items as logic is now in _display_items_for_search
    # Removed refresh_feed and schedule_refresh and references to self.refresh_button
    # Removed open_item as item interaction is not part of this minimal design
    # The expand_search_items_simple is replaced by _display_items_for_search helper

