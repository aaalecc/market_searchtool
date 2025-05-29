"""
Favorites Tab for Market Search Tool
CustomTkinter interface for managing saved listings.
"""

import customtkinter as ctk
import logging

logger = logging.getLogger(__name__)

class FavoritesTab(ctk.CTkFrame):
    """Favorites tab with black and purple design."""
    
    def __init__(self, parent):
        """Initialize the favorites tab."""
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        logger.info("Initializing Favorites tab...")
        
        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create the interface
        self.create_widgets()
        
        logger.info("Favorites tab initialized")
    
    def create_widgets(self):
        """Create the favorites interface widgets with black and purple styling."""
        # Header section
        self.create_header()
        
        # Main content area
        self.create_content()
    
    def create_header(self):
        """Create the header section with modern styling."""
        self.header_frame = ctk.CTkFrame(
            self, 
            height=100, 
            corner_radius=0, 
            fg_color="transparent"
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_propagate(False)
        
        # Title with larger Japanese font
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="お気に入り - 保存済み商品",
            font=ctk.CTkFont(size=36, weight="bold"),  # Larger for consistency
            text_color="#FFFFFF",  # Pure white
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=25, sticky="w")
        
        # Purple management button
        self.manage_button = ctk.CTkButton(
            self.header_frame,
            text="🗂️  管理",
            width=130,
            height=42,
            corner_radius=21,  # Very rounded
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#8B5CF6",  # Purple accent
            hover_color="#A78BFA",
            text_color="#FFFFFF"  # White text on purple
        )
        self.manage_button.grid(row=0, column=2, padx=30, pady=25, sticky="e")
    
    def create_content(self):
        """Create the main content area with modern styling."""
        # Content frame with Spotify-style background
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color="#282828",  # Spotify card background
            border_width=0
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        
        # Placeholder content with modern styling
        placeholder_content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        placeholder_content.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Large icon
        icon_label = ctk.CTkLabel(
            placeholder_content,
            text="❤️",
            font=ctk.CTkFont(size=80),
            text_color="#B3B3B3"
        )
        icon_label.pack(pady=(30, 20))
        
        # Main title
        title_label = ctk.CTkLabel(
            placeholder_content,
            text="お気に入り管理機能開発中",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFFFFF"
        )
        title_label.pack(pady=(0, 12))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            placeholder_content,
            text="まもなく利用可能になります",
            font=ctk.CTkFont(size=16, weight="normal"),
            text_color="#B3B3B3"
        )
        subtitle_label.pack(pady=(0, 35))
        
        # Feature list with modern styling
        features_frame = ctk.CTkFrame(
            placeholder_content, 
            fg_color="#3E3E3E",  # Slightly lighter than card
            corner_radius=16
        )
        features_frame.pack(fill="x", pady=15)
        
        features_text = """実装予定の機能:

• 保存した商品のグリッド表示
• 保存商品の価格追跡
• 「まだ販売中？」ステータス確認
• お気に入りから削除
• 「購入済み」アーカイブへ移動
• 各商品のメモ・タグ機能"""
        
        features_label = ctk.CTkLabel(
            features_frame,
            text=features_text,
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color="#FFFFFF",
            justify="left"
        )
        features_label.pack(padx=30, pady=25) 