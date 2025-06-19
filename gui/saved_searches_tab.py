import customtkinter as ctk
from core.database import get_saved_searches, get_saved_search_items, delete_saved_search, update_saved_search_notifications
import json
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)

class SavedSearchesTab(ctk.CTkFrame):
    def __init__(self, parent, font=None):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.font = font
        self.font_family = self.font.cget('family') if self.font else "Meiryo UI"
        logger.info(f"{self.__class__.__name__} initialized with font family: {self.font_family}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.create_widgets()

    def create_widgets(self):
        header_title_font = ctk.CTkFont(family=self.font_family, size=36, weight="bold")
        saved_search_name_font = ctk.CTkFont(family=self.font_family, size=18, weight="bold")
        options_font = ctk.CTkFont(family=self.font_family, size=14)
        item_count_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")
        switch_font = ctk.CTkFont(family=self.font_family, size=14)
        delete_button_font = ctk.CTkFont(family=self.font_family, size=14, weight="bold")

        self.header_frame = ctk.CTkFrame(self, height=100, corner_radius=0, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(0, weight=1)
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="保存された検索一覧",
            font=header_title_font,
            text_color="#FFFFFF",
            anchor="w"
        )
        self.title_label.grid(row=0, column=0, padx=30, pady=25, sticky="w")

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 30))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.scroll_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent", corner_radius=0)
        self.scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self.display_saved_searches(saved_search_name_font, options_font, item_count_font, switch_font, delete_button_font)

    def delete_saved_search(self, search_id, name):
        """Delete a saved search and all its associated items."""
        if messagebox.askyesno("確認", f"「{name}」を削除してもよろしいですか？"):
            try:
                # Delete the saved search (this will cascade delete all related items)
                if delete_saved_search(search_id):
                    # Refresh the display
                    self.display_saved_searches(
                        ctk.CTkFont(family=self.font_family, size=18, weight="bold"),
                        ctk.CTkFont(family=self.font_family, size=14),
                        ctk.CTkFont(family=self.font_family, size=14, weight="bold"),
                        ctk.CTkFont(family=self.font_family, size=14),
                        ctk.CTkFont(family=self.font_family, size=14, weight="bold")
                    )
            except Exception as e:
                logger.error(f"Error deleting saved search {search_id}: {e}")
                messagebox.showerror("エラー", "検索の削除中にエラーが発生しました。")

    def toggle_notifications(self, search_id, switch_widget):
        update_saved_search_notifications(search_id, bool(switch_widget.get()))

    def display_saved_searches(self, name_font, opts_font, count_font, sw_font, del_btn_font):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        saved_searches = get_saved_searches()
        if not saved_searches:
            empty_label = ctk.CTkLabel(self.scroll_frame, text="保存された検索はありません。", font=opts_font, text_color="#B3B3B3")
            empty_label.pack(padx=20, pady=20, anchor="center")
            return

        for i, search in enumerate(saved_searches):
            name = search.get('name', '(No Name)')
            # Get options directly from the search dictionary
            options = search.get('options', {})
            item_count = len(get_saved_search_items(search['id']))
            
            row_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#282828", corner_radius=12)
            row_frame.grid(row=i, column=0, sticky="ew", pady=8, padx=0)
            row_frame.grid_columnconfigure(1, weight=1)

            name_label = ctk.CTkLabel(row_frame, text=name, font=name_font, text_color="#8B5CF6")
            name_label.grid(row=0, column=0, sticky="w", padx=16, pady=(10,10))
            
            options_text = f"キーワード: {' '.join(options.get('keywords', []))}  価格: {options.get('min_price', '')} - {options.get('max_price', '')}  サイト: {', '.join(options.get('sites', []))}"
            options_label = ctk.CTkLabel(row_frame, text=options_text, font=opts_font, text_color="#FFFFFF", wraplength=500, justify="left")
            options_label.grid(row=0, column=1, sticky="w", padx=8, pady=(10,10))
            
            count_label = ctk.CTkLabel(row_frame, text=f"{item_count} アイテム", font=count_font, text_color="#22c55e")
            count_label.grid(row=0, column=2, sticky="e", padx=16, pady=(10,10))
            
            notifications_switch = ctk.CTkSwitch(
                row_frame, text="通知", font=sw_font, text_color="#FFFFFF",
                fg_color="#535353", progress_color="#8B5CF6"
            )
            notifications_switch.grid(row=0, column=3, sticky="e", padx=16, pady=(10,10))
            if search.get('notifications_enabled', False):
                notifications_switch.select()
            else:
                notifications_switch.deselect()
            notifications_switch.configure(command=lambda s_id=search['id'], sw=notifications_switch: self.toggle_notifications(s_id, sw))

            delete_button = ctk.CTkButton(
                row_frame, text="削除", width=60, height=30, corner_radius=15,
                font=del_btn_font, fg_color="#ef4444", hover_color="#dc2626", text_color="#FFFFFF",
                command=lambda s_id=search['id'], s_name=name: self.delete_saved_search(s_id, s_name)
            )
            delete_button.grid(row=0, column=4, sticky="e", padx=16, pady=(10,10)) 