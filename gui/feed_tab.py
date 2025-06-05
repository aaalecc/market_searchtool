"""
Feed Tab for Market Search Tool
CustomTkinter interface for monitoring new listings with a modern grid layout.
"""

import customtkinter as ctk
import logging
from PIL import Image, ImageTk, ImageOps
import requests
from io import BytesIO
from typing import List, Dict, Any
from customtkinter import CTkImage
from datetime import datetime
import webbrowser

from core.database import get_new_items, mark_items_as_viewed, get_new_items_count, get_saved_searches

logger = logging.getLogger(__name__)

class ProductCard(ctk.CTkFrame):
    """Individual product card widget with black and purple design."""
    
    def __init__(self, parent, product_data: Dict[str, Any]):
        super().__init__(
            parent, 
            corner_radius=16,  # More rounded like Spotify
            fg_color="#282828",  # Spotify's actual card background
            border_width=0  # No border for cleaner look
        )
        
        self.product_data = product_data
        self.create_card()
        
        # Add Spotify-style hover effect
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        
        # Bind to all child widgets for better hover experience
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
        """Create the product card layout with Spotify-style design."""
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
            height=200, 
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
                    font=ctk.CTkFont(size=56),
                    text_color="#B3B3B3"
                )
        else:
            self.image_label = ctk.CTkLabel(
                self.image_frame,
                text="📷",
                font=ctk.CTkFont(size=56),
                text_color="#B3B3B3"
            )
        self.image_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Product title (truncate if too long)
        title = self.product_data.get('title', 'Product Title')
        max_chars = 60
        if len(title) > max_chars:
            title = title[:max_chars-3] + '...'
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            wraplength=180,
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
            font=ctk.CTkFont(size=12, weight="normal"),
            text_color="#B3B3B3",
            anchor="w"
        )
        self.source_label.grid(row=2, column=0, sticky="w")
        
        # Spacer to fill space above price
        self.spacer = ctk.CTkLabel(self.content_frame, text="", font=ctk.CTkFont(size=1))
        self.spacer.grid(row=3, column=0, sticky="nswe")
        
        # Price at the bottom/footer of the card
        price = self.product_data.get('price', '¥---')
        self.price_label = ctk.CTkLabel(
            self,
            text=price,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#8B5CF6",
            anchor="e"
        )
        self.price_label.grid(row=1, column=0, sticky="sew", pady=(0, 8), padx=0)
    
    def on_enter(self, event):
        """Spotify-style hover effect."""
        self.configure(fg_color="#3E3E3E")  # Lighter on hover
    
    def on_leave(self, event):
        """Reset hover effect."""
        self.configure(fg_color="#282828")  # Back to normal

class FeedTab(ctk.CTkFrame):
    """Feed tab with black and purple design."""
    
    def __init__(self, parent):
        """Initialize the feed tab."""
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        logger.info("Initializing Feed tab...")
        
        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create the interface
        self.create_widgets()
        
        self.refresh_interval = 30000  # 30 seconds
        self.schedule_refresh()
        
        logger.info("Feed tab initialized")
    
    def create_widgets(self):
        """Create the feed interface with modern design."""
        # Header section
        self.create_header()
        
        # Create scrollable content area
        self.create_content_area()
        
        # Initial display
        self.display_new_items()
    
    def create_header(self):
        """Create modern header."""
        self.header_frame = ctk.CTkFrame(
            self, 
            height=100, 
            corner_radius=0, 
            fg_color="transparent"
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="新着アイテム",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=25, sticky="w")
        
        # Subtitle with item count
        self.filter_label = ctk.CTkLabel(
            self.header_frame,
            text="新着順 • 8件の商品が見つかりました",
            font=ctk.CTkFont(size=15, weight="normal"),  # Fixed font weight
            text_color="#B3B3B3",  # Spotify secondary text
            anchor="w"
        )
        self.filter_label.pack(anchor="w", pady=(4, 0))
        
        # Purple-style refresh button
        self.refresh_button = ctk.CTkButton(
            self.header_frame,
            text="🔄  更新",
            width=130,
            height=42,
            corner_radius=21,  # Very rounded
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#8B5CF6",  # Purple accent
            hover_color="#A78BFA",
            text_color="#FFFFFF",  # White text on purple
            command=self.refresh_feed
        )
        self.refresh_button.grid(row=0, column=2, padx=30, pady=25, sticky="e")
    
    def create_content_area(self):
        """Create Spotify-style scrollable area."""
        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            corner_radius=0,
            fg_color="transparent",
            scrollbar_button_color="#B3B3B3",
            scrollbar_button_hover_color="#FFFFFF"
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Responsive grid (3-4 columns)
        for i in range(4):
            self.scroll_frame.grid_columnconfigure(i, weight=1, uniform="col")
    
    def display_new_items(self):
        """Display new items in the feed, grouped by saved search with notifications enabled only."""
        # Clear existing items
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Get saved searches with notifications enabled
        saved_searches = [s for s in get_saved_searches() if s.get('notifications_enabled')]
        if not saved_searches:
            return  # No searches to show
        
        # Get new items for all searches (limit 100 for expand, but show only 10 by default)
        items_by_search = get_new_items(limit=100)
        
        row = 0
        for search in saved_searches:
            search_name = search.get('name', f"Search {search['id']}")
            items = items_by_search.get(search_name, [])
            if not items:
                continue  # Skip if no items for this search
            
            # Only show the top 10 by default
            items_to_show = items[:10]
            
            # Create expandable section for each saved search
            section_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#282828", corner_radius=12)
            section_frame.grid(row=row, column=0, sticky="ew", padx=0, pady=(20, 10))
            section_frame.grid_columnconfigure(0, weight=1)
            
            # Header with search name and expand button
            header_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, sticky="ew", padx=16, pady=12)
            header_frame.grid_columnconfigure(0, weight=1)
            
            # Search name and item count
            title_text = f"{search_name} ({len(items)}件)"
            title_label = ctk.CTkLabel(
                header_frame,
                text=title_text,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#8B5CF6"
            )
            title_label.grid(row=0, column=0, sticky="w")
            
            # Expand button
            expand_button = ctk.CTkButton(
                header_frame,
                text="もっと見る",
                width=100,
                command=lambda s=search_name: self.expand_search_items(s)
            )
            expand_button.grid(row=0, column=1, padx=(16, 0))
            
            # Items container
            items_container = ctk.CTkFrame(section_frame, fg_color="transparent")
            items_container.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))
            items_container.grid_columnconfigure(0, weight=1)
            
            # Display items (top 10)
            for i, item in enumerate(items_to_show):
                item_frame = ctk.CTkFrame(items_container, fg_color="#3E3E3E", corner_radius=8)
                item_frame.grid(row=i, column=0, sticky="ew", pady=4)
                item_frame.grid_columnconfigure(1, weight=1)
                
                # Image (if available)
                if item.get('image_url'):
                    try:
                        response = requests.get(item['image_url'], timeout=5)
                        img_data = BytesIO(response.content)
                        pil_image = Image.open(img_data).convert("RGBA")
                        target_size = (80, 80)
                        pil_image = ImageOps.contain(pil_image, target_size, method=Image.LANCZOS)
                        background = Image.new("RGBA", target_size, (62, 62, 62, 255))
                        background.paste(pil_image, ((target_size[0] - pil_image.width) // 2, (target_size[1] - pil_image.height) // 2))
                        ctk_image = CTkImage(light_image=background, size=target_size)
                        image_label = ctk.CTkLabel(
                            item_frame,
                            image=ctk_image,
                            text=""
                        )
                    except Exception:
                        image_label = ctk.CTkLabel(
                            item_frame,
                            text="📷",
                            font=ctk.CTkFont(size=24)
                        )
                else:
                    image_label = ctk.CTkLabel(
                        item_frame,
                        text="📷",
                        font=ctk.CTkFont(size=24)
                    )
                image_label.grid(row=0, column=0, padx=12, pady=12)
                
                # Item details
                details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                details_frame.grid(row=0, column=1, sticky="ew", padx=8, pady=8)
                details_frame.grid_columnconfigure(0, weight=1)
                
                # Title
                title_label = ctk.CTkLabel(
                    details_frame,
                    text=item['title'],
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#FFFFFF",
                    anchor="w"
                )
                title_label.grid(row=0, column=0, sticky="ew", pady=(0, 4))
                
                # Price and site
                info_text = f"¥{item.get('price_formatted', 'N/A')} • {item['site']}"
                info_label = ctk.CTkLabel(
                    details_frame,
                    text=info_text,
                    font=ctk.CTkFont(size=14),
                    text_color="#B3B3B3"
                )
                info_label.grid(row=1, column=0, sticky="ew")
                
                # Open button
                open_button = ctk.CTkButton(
                    item_frame,
                    text="開く",
                    width=60,
                    command=lambda url=item['url']: self.open_item(url)
                )
                open_button.grid(row=0, column=2, padx=12, pady=12)
            
            row += 1

    def expand_search_items(self, search_name: str):
        """Expand a saved search to show up to 100 items."""
        items_by_search = get_new_items(limit=100)
        items = items_by_search.get(search_name, [])
        
        # Find the section for this search
        for widget in self.scroll_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkFrame):  # header_frame
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, ctk.CTkLabel) and search_name in grandchild.cget("text"):
                                # Found the section, update the items
                                items_container = widget.winfo_children()[1]  # Get the items container
                                
                                # Clear existing items
                                for item in items_container.winfo_children():
                                    item.destroy()
                                
                                # Add all items
                                for i, item in enumerate(items):
                                    item_frame = ctk.CTkFrame(items_container, fg_color="#3E3E3E", corner_radius=8)
                                    item_frame.grid(row=i, column=0, sticky="ew", pady=4)
                                    item_frame.grid_columnconfigure(1, weight=1)
                                    
                                    # Image (if available)
                                    if item.get('image_url'):
                                        try:
                                            response = requests.get(item['image_url'], timeout=5)
                                            img_data = BytesIO(response.content)
                                            pil_image = Image.open(img_data).convert("RGBA")
                                            target_size = (80, 80)
                                            pil_image = ImageOps.contain(pil_image, target_size, method=Image.LANCZOS)
                                            background = Image.new("RGBA", target_size, (62, 62, 62, 255))
                                            background.paste(pil_image, ((target_size[0] - pil_image.width) // 2, (target_size[1] - pil_image.height) // 2))
                                            ctk_image = CTkImage(light_image=background, size=target_size)
                                            image_label = ctk.CTkLabel(
                                                item_frame,
                                                image=ctk_image,
                                                text=""
                                            )
                                        except Exception:
                                            image_label = ctk.CTkLabel(
                                                item_frame,
                                                text="📷",
                                                font=ctk.CTkFont(size=24)
                                            )
                                    else:
                                        image_label = ctk.CTkLabel(
                                            item_frame,
                                            text="📷",
                                            font=ctk.CTkFont(size=24)
                                        )
                                    image_label.grid(row=0, column=0, padx=12, pady=12)
                                    
                                    # Item details
                                    details_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                                    details_frame.grid(row=0, column=1, sticky="ew", padx=8, pady=8)
                                    details_frame.grid_columnconfigure(0, weight=1)
                                    
                                    # Title
                                    title_label = ctk.CTkLabel(
                                        details_frame,
                                        text=item['title'],
                                        font=ctk.CTkFont(size=16, weight="bold"),
                                        text_color="#FFFFFF",
                                        anchor="w"
                                    )
                                    title_label.grid(row=0, column=0, sticky="ew", pady=(0, 4))
                                    
                                    # Price and site
                                    info_text = f"¥{item.get('price_formatted', 'N/A')} • {item['site']}"
                                    info_label = ctk.CTkLabel(
                                        details_frame,
                                        text=info_text,
                                        font=ctk.CTkFont(size=14),
                                        text_color="#B3B3B3"
                                    )
                                    info_label.grid(row=1, column=0, sticky="ew")
                                    
                                    # Open button
                                    open_button = ctk.CTkButton(
                                        item_frame,
                                        text="開く",
                                        width=60,
                                        command=lambda url=item['url']: self.open_item(url)
                                    )
                                    open_button.grid(row=0, column=2, padx=12, pady=12)
                                
                                # Update the header to show total count
                                for child in child.winfo_children():
                                    if isinstance(child, ctk.CTkLabel):
                                        child.configure(text=f"{search_name} ({len(items)}件)")
                                
                                return

    def open_item(self, url: str):
        """Open item URL in default browser."""
        webbrowser.open(url)

    def refresh_feed(self):
        """Purple-style refresh with smooth animations."""
        logger.info("Refreshing feed...")
        
        # Purple-style loading
        self.refresh_button.configure(
            text="⟳  更新中...",
            state="disabled",
            fg_color="#535353"  # Disabled gray
        )
        
        def complete_refresh():
            self.refresh_button.configure(
                text="✓  完了",
                fg_color="#8B5CF6",
                state="normal"
            )
            # Reset after delay
            self.after(1200, lambda: self.refresh_button.configure(
                text="🔄  更新",
                fg_color="#8B5CF6"
            ))
        
        # Simulate refresh
        self.display_new_items()
        self.after(900, complete_refresh)
    
    def schedule_refresh(self):
        """Schedule periodic refresh of the feed."""
        self.display_new_items()
        self.after(self.refresh_interval, self.schedule_refresh) 