import tkinter as tk
from tkinter import ttk, messagebox
import os
import sqlite3
from database.connection import get_db_path, get_db_connection
from services.sample_data_service import SampleDataService
from ui.styles import (
    COLOR_BORDER, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, FONT_STAT_NUM
)

class SettingsView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)

        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=16, highlightbackground=COLOR_BORDER, highlightthickness=1)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))

        title_lbl = tk.Label(header_frame, text="System Configuration & Demonstration Utilities", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(header_frame, text="Database diagnostic statistics, data seeding utilities, and system information", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        content = tk.Frame(self, bg="#f8fafc", padx=20, pady=5)
        content.pack(fill=tk.BOTH, expand=True)

        # Left / Right layout
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        # Left Card: Demonstration & Test Data Seeding
        demo_card = tk.Frame(content, bg="#ffffff", padx=20, pady=18, highlightbackground=COLOR_BORDER, highlightthickness=1)
        demo_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

        tk.Label(demo_card, text="⚡ Viva & Demonstration Utilities", font=FONT_HEADING, bg="#ffffff", fg=COLOR_PRIMARY).pack(anchor="w")
        tk.Label(
            demo_card,
            text="Populate the system with a complete set of realistic business records (categories, suppliers, active inventory with low-stock alerts, purchase orders, and sales receipts) for instant viva examination demonstration.",
            font=FONT_SMALL,
            bg="#ffffff",
            fg=COLOR_TEXT_SECONDARY,
            wraplength=380,
            justify=tk.LEFT
        ).pack(anchor="w", pady=(6, 16))

        ttk.Button(demo_card, text="✨ Load Sample Demonstration Data", style="Primary.TButton", command=self.seed_sample_data).pack(anchor="w", pady=(0, 15))

        # Reset Card separator
        ttk.Separator(demo_card, orient="horizontal").pack(fill=tk.X, pady=12)

        tk.Label(demo_card, text="🗑️ Factory Reset / Purge Database", font=FONT_HEADING, bg="#ffffff", fg=COLOR_DANGER).pack(anchor="w")
        tk.Label(
            demo_card,
            text="Permanently clear all products, categories, suppliers, sales, purchases, and stock movement logs. Use with caution.",
            font=FONT_SMALL,
            bg="#ffffff",
            fg=COLOR_TEXT_SECONDARY,
            wraplength=380,
            justify=tk.LEFT
        ).pack(anchor="w", pady=(6, 16))

        ttk.Button(demo_card, text="Purge All Records", style="Danger.TButton", command=self.reset_database).pack(anchor="w")

        # Right Card: Database & Environment Statistics
        stats_card = tk.Frame(content, bg="#ffffff", padx=20, pady=18, highlightbackground=COLOR_BORDER, highlightthickness=1)
        stats_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)

        tk.Label(stats_card, text="📁 Database Diagnostics", font=FONT_HEADING, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(anchor="w")

        self.db_path_lbl = tk.Label(stats_card, text="Path: Loading...", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY, wraplength=380, justify=tk.LEFT)
        self.db_path_lbl.pack(anchor="w", pady=(6, 2))

        self.db_size_lbl = tk.Label(stats_card, text="Size: Loading...", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        self.db_size_lbl.pack(anchor="w", pady=(0, 12))

        ttk.Separator(stats_card, orient="horizontal").pack(fill=tk.X, pady=8)

        tk.Label(stats_card, text="Current Table Row Counts:", font=FONT_BODY_BOLD, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(anchor="w", pady=(0, 6))

        self.counts_frame = tk.Frame(stats_card, bg="#ffffff")
        self.counts_frame.pack(fill=tk.X)

        # Tech Stack summary at bottom of Right Card
        ttk.Separator(stats_card, orient="horizontal").pack(fill=tk.X, pady=12)
        tk.Label(stats_card, text="Project Technology Stack:", font=FONT_BODY_BOLD, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(anchor="w")
        tech_info = (
            "• Python 3 Standard Library (Zero external dependencies)\n"
            "• Object-Oriented Architecture (Data models, Services, Repositories)\n"
            "• SQLite Database with PRAGMA foreign_keys = ON & ACID transactions\n"
            "• Exact Currency: Integer Paise storage to eliminate float rounding\n"
            "• CSV Import/Export with data validation and error reporting\n"
            "• Tkinter & Modern TTK Desktop Graphical User Interface"
        )
        tk.Label(stats_card, text=tech_info, font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY, justify=tk.LEFT).pack(anchor="w", pady=(4, 0))

    def refresh(self):
        db_path = get_db_path()
        self.db_path_lbl.config(text=f"Location: {db_path}")

        if os.path.exists(db_path):
            size_kb = os.path.getsize(db_path) / 1024.0
            self.db_size_lbl.config(text=f"Database File Size: {size_kb:,.2f} KB")
        else:
            self.db_size_lbl.config(text="Database File Size: Not yet initialized")

        # Query row counts
        for widget in self.counts_frame.winfo_children():
            widget.destroy()

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            tables = [
                ("Products", "products"),
                ("Categories", "categories"),
                ("Suppliers", "suppliers"),
                ("Purchase Orders", "purchases"),
                ("Purchase Items", "purchase_items"),
                ("Sales Transactions", "sales"),
                ("Sale Items", "sale_items"),
                ("Stock Movements", "stock_movements")
            ]

            row = 0
            for name, tbl in tables:
                cursor.execute(f"SELECT COUNT(*) AS cnt FROM {tbl}")
                cnt = cursor.fetchone()["cnt"]
                tk.Label(self.counts_frame, text=f"{name}:", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY).grid(row=row, column=0, sticky="w", pady=2)
                tk.Label(self.counts_frame, text=f"{cnt:,} records", font=FONT_BODY_BOLD, bg="#ffffff", fg=COLOR_PRIMARY).grid(row=row, column=1, sticky="e", padx=(20, 0), pady=2)
                row += 1
            conn.close()
        except Exception as e:
            tk.Label(self.counts_frame, text=f"Error querying table counts: {e}", font=FONT_SMALL, bg="#ffffff", fg=COLOR_DANGER).pack()

    def seed_sample_data(self):
        confirm = messagebox.askyesno(
            "Load Sample Demo Data",
            "This will seed categories, suppliers, inventory products, purchases, and sales into the database.\n\nProceed?"
        )
        if confirm:
            try:
                SampleDataService.seed_data()
                messagebox.showinfo("Success", "Sample demonstration data loaded successfully!\nDashboard and inventory tables updated.")
                self.refresh()
                self.app.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to seed data: {e}")

    def reset_database(self):
        confirm = messagebox.askyesno(
            "Confirm Database Reset",
            "WARNING: This will permanently purge ALL records from the database.\n\nAre you sure you want to proceed?"
        )
        if confirm:
            try:
                SampleDataService.reset_database()
                messagebox.showinfo("Reset Complete", "All database tables have been purged.")
                self.refresh()
                self.app.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset database: {e}")
