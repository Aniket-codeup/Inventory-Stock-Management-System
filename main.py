import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from database.schema import initialize_database
from database.connection import get_db_path
from ui.styles import (
    setup_modern_styles, COLOR_SIDEBAR_BG, COLOR_SIDEBAR_HEADER, COLOR_SIDEBAR_ACTIVE,
    COLOR_SIDEBAR_TEXT, COLOR_BORDER, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY_BOLD, FONT_SMALL
)
from ui.dashboard import DashboardView
from ui.products import ProductsView
from ui.categories import CategoriesView
from ui.suppliers import SuppliersView
from ui.purchases import PurchasesView
from ui.sales import SalesView
from ui.stock import StockView
from ui.reports import ReportsView
from ui.csv_view import CSVView
from ui.settings_view import SettingsView

class InventoryApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Inventory & Stock Management System")
        self.geometry("1280x800")
        self.minsize(1050, 680)

        # Center on screen
        self.center_window()

        # Initialize SQLite Database with PRAGMA foreign_keys = ON
        try:
            initialize_database()
        except Exception as e:
            messagebox.showerror("Database Initialization Error", f"Failed to initialize SQLite database:\n{e}")
            self.destroy()
            return

        # Setup modern TTK styles and custom theme
        setup_modern_styles(self)

        # Views management
        self.views = {}
        self.current_view_name = None
        self.nav_buttons = {}

        # Build Main UI Layout
        self.create_layout()

        # Navigate to Dashboard on initial load
        self.navigate_to("dashboard")

    def center_window(self):
        self.update_idletasks()
        w = 1280
        h = 800
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def create_layout(self):
        # Master Container
        self.master_frame = tk.Frame(self, bg="#f8fafc")
        self.master_frame.pack(fill=tk.BOTH, expand=True)

        # ==================== LEFT SIDEBAR ====================
        self.sidebar_frame = tk.Frame(self.master_frame, bg=COLOR_SIDEBAR_BG, width=240)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        # App Brand Header
        brand_frame = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR_HEADER, padx=18, pady=20)
        brand_frame.pack(fill=tk.X)

        brand_title = tk.Label(
            brand_frame,
            text="📦 INVENTORY PRO",
            font=("Segoe UI", 13, "bold"),
            bg=COLOR_SIDEBAR_HEADER,
            fg="#ffffff"
        )
        brand_title.pack(anchor="w")

        brand_sub = tk.Label(
            brand_frame,
            text="Stock & Sales Management",
            font=("Segoe UI", 8),
            bg=COLOR_SIDEBAR_HEADER,
            fg="#94a3b8"
        )
        brand_sub.pack(anchor="w", pady=(2, 0))

        # Navigation Menu List
        self.nav_menu_frame = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR_BG, pady=10)
        self.nav_menu_frame.pack(fill=tk.BOTH, expand=True)

        nav_items = [
            ("dashboard", "📊  Dashboard"),
            ("products", "📦  Products Catalog"),
            ("categories", "📁  Categories"),
            ("suppliers", "🏢  Suppliers"),
            ("purchases", "📥  Purchases (Stock-In)"),
            ("sales", "🛒  Sales (Stock-Out)"),
            ("stock", "⚖️  Stock Control & Audit"),
            ("reports", "📈  Business Reports"),
            ("csv", "📄  CSV Import / Export"),
            ("settings", "⚙️  Settings & Demo Data"),
        ]

        for key, label_text in nav_items:
            btn = tk.Button(
                self.nav_menu_frame,
                text=label_text,
                font=FONT_HEADING,
                bg=COLOR_SIDEBAR_BG,
                fg=COLOR_SIDEBAR_TEXT,
                activebackground=COLOR_SIDEBAR_ACTIVE,
                activeforeground="#ffffff",
                relief="flat",
                bd=0,
                anchor="w",
                padx=20,
                pady=9,
                cursor="hand2",
                command=lambda k=key: self.navigate_to(k)
            )
            btn.pack(fill=tk.X, pady=1)
            self.nav_buttons[key] = btn

        # Sidebar Footer
        sidebar_footer = tk.Frame(self.sidebar_frame, bg=COLOR_SIDEBAR_BG, padx=16, pady=12)
        sidebar_footer.pack(fill=tk.X, side=tk.BOTTOM)

        db_badge = tk.Label(
            sidebar_footer,
            text="● SQLite Connected (ACID)",
            font=("Segoe UI", 8, "bold"),
            bg=COLOR_SIDEBAR_BG,
            fg=COLOR_SUCCESS
        )
        db_badge.pack(anchor="w")

        ver_lbl = tk.Label(
            sidebar_footer,
            text="v1.0 Final-Year Project • Python 3",
            font=("Segoe UI", 8),
            bg=COLOR_SIDEBAR_BG,
            fg="#64748b"
        )
        ver_lbl.pack(anchor="w", pady=(2, 0))

        # ==================== MAIN CONTENT AREA ====================
        self.main_container = tk.Frame(self.master_frame, bg="#f8fafc")
        self.main_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Top Universal Status / Header Strip
        self.top_strip = tk.Frame(self.main_container, bg="#ffffff", height=48, padx=20, highlightbackground=COLOR_BORDER, highlightthickness=1)
        self.top_strip.pack(side=tk.TOP, fill=tk.X)
        self.top_strip.pack_propagate(False)

        self.breadcrumb_lbl = tk.Label(
            self.top_strip,
            text="Dashboard",
            font=FONT_BODY_BOLD,
            bg="#ffffff",
            fg=COLOR_TEXT_PRIMARY
        )
        self.breadcrumb_lbl.pack(side=tk.LEFT, pady=12)

        self.time_lbl = tk.Label(
            self.top_strip,
            text=datetime.datetime.now().strftime("%A, %d %B %Y"),
            font=FONT_SMALL,
            bg="#ffffff",
            fg=COLOR_TEXT_SECONDARY
        )
        self.time_lbl.pack(side=tk.RIGHT, pady=14)

        # Content Dynamic View Host Frame
        self.view_host = tk.Frame(self.main_container, bg="#f8fafc")
        self.view_host.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def navigate_to(self, view_name: str, **kwargs):
        """Switch active view and update sidebar selection states."""
        # Update sidebar button styles
        for key, btn in self.nav_buttons.items():
            if key == view_name:
                btn.config(bg=COLOR_SIDEBAR_ACTIVE, fg="#ffffff")
            else:
                btn.config(bg=COLOR_SIDEBAR_BG, fg=COLOR_SIDEBAR_TEXT)

        # Update breadcrumb title
        titles = {
            "dashboard": "Dashboard Overview",
            "products": "Product Catalog & Pricing",
            "categories": "Category Hierarchy",
            "suppliers": "Supplier Directory",
            "purchases": "Purchases & Inward Stock",
            "sales": "Sales Register & Outward Stock",
            "stock": "Stock Monitoring & Movement History",
            "reports": "Analytical Reports & Summaries",
            "csv": "CSV Import / Export Interchange",
            "settings": "System Settings & Demo Utilities",
        }
        self.breadcrumb_lbl.config(text=titles.get(view_name, view_name.capitalize()))

        # Destroy current view if present
        for child in self.view_host.winfo_children():
            child.destroy()

        # Instantiate selected view
        view_classes = {
            "dashboard": DashboardView,
            "products": ProductsView,
            "categories": CategoriesView,
            "suppliers": SuppliersView,
            "purchases": PurchasesView,
            "sales": SalesView,
            "stock": StockView,
            "reports": ReportsView,
            "csv": CSVView,
            "settings": SettingsView,
        }

        view_cls = view_classes.get(view_name)
        if view_cls:
            view_instance = view_cls(self.view_host, self)
            self.views[view_name] = view_instance
            self.current_view_name = view_name

            # Handle extra action requests (e.g. quick opening an add dialog)
            if kwargs.get("action") == "add" and hasattr(view_instance, "open_add_dialog"):
                self.after(50, view_instance.open_add_dialog)
            elif kwargs.get("action") == "adjust" and hasattr(view_instance, "open_adjustment_dialog"):
                self.after(50, view_instance.open_adjustment_dialog)
            elif "tab" in kwargs and hasattr(view_instance, "notebook"):
                view_instance.notebook.select(kwargs["tab"])

    def refresh_dashboard(self):
        """Helper to refresh dashboard metrics when products or transactions change."""
        if "dashboard" in self.views and self.current_view_name == "dashboard":
            self.views["dashboard"].refresh()

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()