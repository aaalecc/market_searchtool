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
        
        # Enhanced sample data
        self.sample_products = [
            {
                'title': 'ユニクロ プレミアムTシャツ',
                'source': 'ヤフオク',
                'price': '¥2,500',
                'image_url': None
            },
            {
                'title': 'ナイキ ベースボールキャップ',
                'source': 'メルカリ',
                'price': '¥1,800',
                'image_url': None
            },
            {
                'title': 'リーバイス ヴィンテージデニム',
                'source': 'ヤフーフリマ',
                'price': '¥4,200',
                'image_url': None
            },
            {
                'title': 'ポケモンカード リザードン GX',
                'source': '楽天',
                'price': '¥15,000',
                'image_url': None
            },
            {
                'title': 'ナイキ エアジョーダン1 レトロ',
                'source': 'Grailed',
                'price': '¥22,000',
                'image_url': None
            },
            {
                'title': 'シュプリーム ボックスロゴTシャツ',
                'source': 'メルカリ',
                'price': '¥35,000',
                'image_url': None
            },
            {
                'title': 'アップル Watch Series 9',
                'source': '楽天',
                'price': '¥45,000',
                'image_url': None
            },
            {
                'title': 'ストーンアイランド ジャケット',
                'source': 'Grailed',
                'price': '¥28,000',
                'image_url': None
            }
        ]
        
        # Create the interface
        self.create_widgets()
        
        logger.info("Feed tab initialized")
    
    def create_widgets(self):
        """Create the feed interface with modern design."""
        # Header section
        self.create_header()
        
        # Create scrollable content area
        self.create_content_area()
        
        # Load sample products
        self.load_products()
    
    def create_header(self):
        """Create modern header."""
        self.header_frame = ctk.CTkFrame(
            self, 
            height=100, 
            corner_radius=0, 
            fg_color="transparent"
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_propagate(False)
        
        # Title section with modern typography
        self.title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=0, sticky="w", padx=30, pady=25)
        
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text="あなたのフィード",
            font=ctk.CTkFont(size=36, weight="bold"),  # Larger Japanese font
            text_color="#FFFFFF",  # Pure white
            anchor="w"
        )
        self.title_label.pack(anchor="w")
        
        # Subtitle with item count
        self.filter_label = ctk.CTkLabel(
            self.title_frame,
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
    
    def load_products(self):
        """Load products with Spotify-style grid."""
        # Clear existing
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        
        # Create Spotify-style product cards
        for index, product in enumerate(self.sample_products):
            row = index // 4
            col = index % 4
            
            # Create Spotify-style card
            card = ProductCard(self.scroll_frame, product)
            card.grid(
                row=row, 
                column=col, 
                padx=15, 
                pady=15, 
                sticky="ew"
            )
        
        # Bottom spacing
        spacer_frame = ctk.CTkFrame(self.scroll_frame, height=50, fg_color="transparent")
        spacer_frame.grid(row=(len(self.sample_products)//4) + 1, column=0, columnspan=4, pady=25)
    
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
        self.load_products()
        self.after(900, complete_refresh)
    
    def add_product(self, product_data: Dict[str, Any]):
        """Add a new product to the feed."""
        self.sample_products.insert(0, product_data)
        self.load_products()
    
    def clear_feed(self):
        """Clear all products from the feed."""
        self.sample_products.clear()
        self.load_products() 