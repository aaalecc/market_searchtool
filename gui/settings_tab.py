"""
Settings Tab for Market Search Tool
CustomTkinter interface for app configuration including Discord webhook.
"""

import customtkinter as ctk
import logging

logger = logging.getLogger(__name__)

class SettingsTab(ctk.CTkFrame):
    """Settings tab with black and purple design."""
    
    def __init__(self, parent, main_window=None, font=None):
        """Initialize the settings tab."""
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.main_window = main_window
        self.font = font
        self.font_family = self.font.cget('family') if self.font else "Meiryo UI"
        logger.info(f"{self.__class__.__name__} initialized with font family: {self.font_family}")
        
        # Configure layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create the interface
        self.create_widgets()
    
    def create_widgets(self):
        """Create the settings interface widgets with black and purple styling."""
        # Define fonts based on self.font_family
        header_title_font = ctk.CTkFont(family=self.font_family, size=36, weight="bold")
        save_button_font = ctk.CTkFont(family=self.font_family, size=15, weight="bold")
        placeholder_icon_font = ctk.CTkFont(family=self.font_family, size=80)
        placeholder_title_font = ctk.CTkFont(family=self.font_family, size=28, weight="bold")
        placeholder_subtitle_font = ctk.CTkFont(family=self.font_family, size=16, weight="normal")
        features_text_font = ctk.CTkFont(family=self.font_family, size=14, weight="normal")

        # Header section
        self.create_header(header_title_font, save_button_font)
        
        # Main content area
        self.create_content(placeholder_icon_font, placeholder_title_font, placeholder_subtitle_font, features_text_font)
    
    def create_header(self, title_font, button_font):
        """Create the header section with modern styling."""
        self.header_frame = ctk.CTkFrame(
            self, 
            height=100, 
            corner_radius=0, 
            fg_color="transparent"
        )
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_columnconfigure(1, weight=0)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="設定・環境設定",
            font=title_font,
            text_color="#FFFFFF",
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=25, sticky="w")
        
        self.save_button = ctk.CTkButton(
            self.header_frame,
            text="💾  保存",
            width=130,
            height=42,
            corner_radius=21,
            font=button_font,
            fg_color="#8B5CF6",
            hover_color="#A78BFA",
            text_color="#FFFFFF"
        )
        self.save_button.grid(row=0, column=1, padx=30, pady=25, sticky="e")
    
    def create_content(self, icon_font, title_font, subtitle_font, text_font):
        """Create the main content area with modern styling."""
        self.content_frame = ctk.CTkFrame(
            self,
            corner_radius=20,
            fg_color="#282828",
            border_width=0
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        
        placeholder_content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        placeholder_content.pack(expand=True, fill="both", padx=50, pady=50)
        
        icon_label = ctk.CTkLabel(
            placeholder_content,
            text="⚙️",
            font=icon_font,
            text_color="#B3B3B3"
        )
        icon_label.pack(pady=(30, 20))
        
        title_label = ctk.CTkLabel(
            placeholder_content,
            text="設定機能開発中",
            font=title_font,
            text_color="#FFFFFF"
        )
        title_label.pack(pady=(0, 12))
        
        subtitle_label = ctk.CTkLabel(
            placeholder_content,
            text="まもなく利用可能になります",
            font=subtitle_font,
            text_color="#B3B3B3"
        )
        subtitle_label.pack(pady=(0, 35))
        
        features_frame = ctk.CTkFrame(
            placeholder_content, 
            fg_color="#3E3E3E",
            corner_radius=16
        )
        features_frame.pack(fill="x", pady=15)
        
        features_text = """実装予定の機能:

• Discord Webhook URL設定
• 通知設定（Discord・デスクトップ）
• デフォルト有効サイト選択
• テーマ選択（ダーク・ライト）
• ページあたり結果数設定
• 接続テストボタン"""
        
        features_label = ctk.CTkLabel(
            features_frame,
            text=features_text,
            font=text_font,
            text_color="#FFFFFF",
            justify="left"
        )
        features_label.pack(padx=30, pady=25) 