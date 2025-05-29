"""
Search Tab for Market Search Tool
CustomTkinter interface for searching marketplace sites.
"""

import customtkinter as ctk
import logging

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
            font=ctk.CTkFont(size=36, weight="bold"),  # Larger for better Japanese readability
            text_color="#FFFFFF",  # Pure white
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
        
        # Spotify-style search section
        self.search_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=20,  # More rounded like Spotify
            fg_color="#282828",  # Spotify card background
            border_width=0
        )
        self.search_container.grid(row=0, column=0, sticky="ew", pady=(0, 25))
        
        # Search form with Spotify styling
        self.form_frame = ctk.CTkFrame(self.search_container, fg_color="transparent")
        self.form_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=25)
        self.form_frame.grid_columnconfigure(1, weight=1)
        
        # Search label with larger Japanese font
        search_label = ctk.CTkLabel(
            self.form_frame,
            text="検索キーワード",
            font=ctk.CTkFont(size=18, weight="bold"),  # Larger
            text_color="#FFFFFF"  # Pure white
        )
        search_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))
        
        # Spotify-style search entry
        self.search_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="検索したい商品名を入力してください...",
            height=50,  # Taller
            width=500,
            corner_radius=25,  # Very rounded like Spotify
            font=ctk.CTkFont(size=16),  # Larger font
            border_width=2,
            border_color="#535353",
            fg_color="#121212",  # Darker background
            text_color="#FFFFFF",
            placeholder_text_color="#B3B3B3"
        )
        self.search_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(0, 20), pady=(0, 0))
        
        # Purple-style search button
        self.search_button = ctk.CTkButton(
            self.form_frame,
            text="🔍  検索実行",
            height=50,
            width=150,
            corner_radius=25,  # Very rounded
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#8B5CF6",  # Purple accent
            hover_color="#A78BFA",
            text_color="#FFFFFF",  # White text on purple
            command=self.perform_search
        )
        self.search_button.grid(row=1, column=2, sticky="e")
        
        # Filter info with Spotify styling
        self.filter_info = ctk.CTkLabel(
            self.form_frame,
            text="💡 すべてのサイト • 全価格帯 • 新着順で検索します",
            font=ctk.CTkFont(size=13, weight="normal"),  # Fixed font weight
            text_color="#B3B3B3"  # Spotify secondary
        )
        self.filter_info.grid(row=2, column=0, columnspan=3, sticky="w", pady=(18, 0))
        
        # Results placeholder with Spotify design
        self.results_container = ctk.CTkFrame(
            self.content_frame,
            corner_radius=20,
            fg_color="#282828",  # Spotify card background
            border_width=0
        )
        self.results_container.grid(row=1, column=0, sticky="nsew")
        
        # Placeholder with Spotify styling
        self.placeholder_frame = ctk.CTkFrame(self.results_container, fg_color="transparent")
        self.placeholder_frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        # Large icon
        self.placeholder_icon = ctk.CTkLabel(
            self.placeholder_frame,
            text="🔍",
            font=ctk.CTkFont(size=80),  # Larger icon
            text_color="#B3B3B3"
        )
        self.placeholder_icon.pack(pady=(30, 20))
        
        # Main title with larger Japanese font
        self.placeholder_title = ctk.CTkLabel(
            self.placeholder_frame,
            text="検索機能開発中",
            font=ctk.CTkFont(size=28, weight="bold"),  # Larger
            text_color="#FFFFFF"  # Pure white
        )
        self.placeholder_title.pack(pady=(0, 12))
        
        # Subtitle
        self.placeholder_subtitle = ctk.CTkLabel(
            self.placeholder_frame,
            text="まもなく利用可能になります",
            font=ctk.CTkFont(size=16, weight="normal"),  # Fixed font weight
            text_color="#B3B3B3"
        )
        self.placeholder_subtitle.pack(pady=(0, 35))
        
        # Feature list with Spotify styling
        self.features_frame = ctk.CTkFrame(
            self.placeholder_frame, 
            fg_color="#3E3E3E",  # Slightly lighter than card
            corner_radius=16
        )
        self.features_frame.pack(fill="x", pady=15)
        
        features_text = """実装予定の機能:

✓ サイト選択チェックボックス
✓ 価格帯フィルター設定  
✓ 検索結果のグリッド表示
✓ お気に入り追加ボタン
✓ 検索条件の保存機能
✓ 並び替えオプション"""
        
        self.features_label = ctk.CTkLabel(
            self.features_frame,
            text=features_text,
            font=ctk.CTkFont(size=14, weight="normal"),  # Fixed font weight
            text_color="#FFFFFF",  # White text for better contrast
            justify="left"
        )
        self.features_label.pack(padx=30, pady=25)
    
    def perform_search(self):
        """Perform search with purple-style feedback."""
        query = self.search_entry.get().strip()
        
        if not query:
            # Purple-style validation feedback
            self.search_entry.configure(border_color="#E22134")  # Red error
            self.after(2500, lambda: self.search_entry.configure(border_color="#535353"))
            return
        
        logger.info(f"Performing search for: {query}")
        
        # Purple-style loading state
        self.search_button.configure(
            text="⟳  検索中...",
            state="disabled",
            fg_color="#535353"  # Disabled gray
        )
        
        # Success feedback
        def complete_search():
            self.search_button.configure(
                text="✓  検索完了",
                fg_color="#8B5CF6",
                state="normal"
            )
            # Reset button
            self.after(1500, lambda: self.search_button.configure(
                text="🔍  検索実行",
                fg_color="#8B5CF6"
            ))
        
        # Simulate search delay
        self.after(1200, complete_search) 