import customtkinter as ctk
from core.database import get_saved_searches, get_saved_search_items, delete_saved_search, update_saved_search_notifications
import json
from tkinter import messagebox

class SavedSearchesTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.create_widgets()

    def create_widgets(self):
        # Header
        self.header_frame = ctk.CTkFrame(self, height=100, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.header_frame.grid_propagate(False)
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="保存された検索一覧",
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="#FFFFFF",
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=25, sticky="w")

        # Content
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Scrollable area for saved searches
        self.scroll_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent", corner_radius=0)
        self.scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.display_saved_searches()

    def delete_saved_search(self, search_id, name):
        """Show confirmation dialog and delete saved search if confirmed."""
        if messagebox.askyesno("確認", f"「{name}」を削除してもよろしいですか？"):
            delete_saved_search(search_id)
            self.display_saved_searches()  # Refresh the display

    def toggle_notifications(self, search_id, enabled):
        """Handle notification toggle switch state change."""
        update_saved_search_notifications(search_id, enabled)

    def display_saved_searches(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        saved_searches = get_saved_searches()
        for i, search in enumerate(saved_searches):
            name = search.get('name', '(No Name)')
            options = json.loads(search['options_json'])
            item_count = len(get_saved_search_items(search['id']))
            # Row frame
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#282828", corner_radius=12)
            row_frame.grid(row=i, column=0, sticky="ew", pady=8, padx=0)
            row_frame.grid_columnconfigure(1, weight=1)
            # Name
            name_label = ctk.CTkLabel(row_frame, text=name, font=ctk.CTkFont(size=18, weight="bold"), text_color="#8B5CF6")
            name_label.grid(row=0, column=0, sticky="w", padx=16, pady=8)
            # Options
            options_text = f"キーワード: {' '.join(options.get('keywords', []))}  最低価格: {options.get('min_price', '')}  最高価格: {options.get('max_price', '')}  サイト: {', '.join(options.get('sites', []))}"
            options_label = ctk.CTkLabel(row_frame, text=options_text, font=ctk.CTkFont(size=14), text_color="#FFFFFF")
            options_label.grid(row=0, column=1, sticky="w", padx=8)
            # Item count
            count_label = ctk.CTkLabel(row_frame, text=f"{item_count}件のアイテム", font=ctk.CTkFont(size=14, weight="bold"), text_color="#22c55e")
            count_label.grid(row=0, column=2, sticky="e", padx=16)
            # Notifications toggle
            notifications_switch = ctk.CTkSwitch(
                row_frame,
                text="通知",
                font=ctk.CTkFont(size=14),
                command=lambda s=search['id']: self.toggle_notifications(s, notifications_switch.get())
            )
            notifications_switch.grid(row=0, column=3, sticky="e", padx=16)
            notifications_switch.select() if search.get('notifications_enabled', True) else notifications_switch.deselect()
            # Delete button
            delete_button = ctk.CTkButton(
                row_frame,
                text="✕",
                width=30,
                height=30,
                corner_radius=15,
                fg_color="#ef4444",  # Red color
                hover_color="#dc2626",  # Darker red on hover
                command=lambda s=search['id'], n=name: self.delete_saved_search(s, n)
            )
            delete_button.grid(row=0, column=4, sticky="e", padx=16, pady=8) 