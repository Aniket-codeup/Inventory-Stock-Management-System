import tkinter as tk
from tkinter import ttk
from services.report_service import ReportService
from ui.styles import (
    COLOR_CARD_BG, COLOR_BORDER, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_PURPLE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY,
    FONT_STAT_NUM, FONT_SMALL, configure_treeview_tags
)

class DashboardView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)

        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        # Main scrollable canvas container if window is small
        self.canvas = tk.Canvas(self, background="#f8fafc", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content_frame = ttk.Frame(self.canvas)

        self.content_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=None, yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Title & Subtitle banner
        header_frame = tk.Frame(self.content_frame, bg="#ffffff", padx=20, pady=16, highlightbackground=COLOR_BORDER, highlightthickness=1)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))

        title_lbl = tk.Label(header_frame, text="Executive Inventory Dashboard", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(header_frame, text="Real-time operational overview, stock health, and recent movements", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Quick Actions Bar
        actions_bar = tk.Frame(self.content_frame, bg="#f8fafc")
        actions_bar.pack(fill=tk.X, padx=20, pady=(0, 15))

        ttk.Button(actions_bar, text="➕ Add Product", style="Primary.TButton", command=lambda: self.app.navigate_to("products", action="add")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_bar, text="📥 Record Purchase", style="Success.TButton", command=lambda: self.app.navigate_to("purchases")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_bar, text="🛒 Record Sale", style="Primary.TButton", command=lambda: self.app.navigate_to("sales")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_bar, text="⚖️ Stock Adjustment", style="Secondary.TButton", command=lambda: self.app.navigate_to("stock", action="adjust")).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_bar, text="🔄 Refresh Data", style="Secondary.TButton", command=self.refresh).pack(side=tk.RIGHT)

        # KPI Summary Cards Grid
        self.cards_frame = tk.Frame(self.content_frame, bg="#f8fafc")
        self.cards_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        for col in range(4):
            self.cards_frame.grid_columnconfigure(col, weight=1, uniform="kpi")

        self.card_active_prods = self._create_kpi_card(self.cards_frame, 0, 0, "Active Products", "0", COLOR_PRIMARY, "📦 In catalog")
        self.card_total_units = self._create_kpi_card(self.cards_frame, 0, 1, "Total Stock Units", "0", COLOR_SUCCESS, "🏢 Warehouse stock")
        self.card_low_stock = self._create_kpi_card(self.cards_frame, 0, 2, "Low-Stock Alerts", "0", COLOR_WARNING, "⚠️ Below minimum threshold")
        self.card_out_of_stock = self._create_kpi_card(self.cards_frame, 0, 3, "Out of Stock", "0", COLOR_DANGER, "🚫 Zero inventory remaining")

        self.card_sales_today = self._create_kpi_card(self.cards_frame, 1, 0, "Today's Sales", "₹0.00", COLOR_PRIMARY, "🛒 Daily revenue")
        self.card_purchases_today = self._create_kpi_card(self.cards_frame, 1, 1, "Today's Purchases", "₹0.00", COLOR_PURPLE, "📥 Daily stock purchases")
        self.card_total_sales = self._create_kpi_card(self.cards_frame, 1, 2, "Total All-Time Sales", "₹0.00", COLOR_PRIMARY, "📈 Cumulative revenue")
        self.card_inventory_val = self._create_kpi_card(self.cards_frame, 1, 3, "Inventory Valuation", "₹0.00", COLOR_SUCCESS, "💰 Asset value at cost")

        # Two Columns for Tables: Left: Low-Stock Alerts | Right: Recent Movements
        tables_container = tk.Frame(self.content_frame, bg="#f8fafc")
        tables_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 25))
        tables_container.grid_columnconfigure(0, weight=1, uniform="tab")
        tables_container.grid_columnconfigure(1, weight=1, uniform="tab")

        # --- Low Stock Alert Panel ---
        low_stock_frame = tk.Frame(tables_container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        low_stock_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        low_header = tk.Frame(low_stock_frame, bg="#ffffff", padx=15, pady=12)
        low_header.pack(fill=tk.X)
        tk.Label(low_header, text="⚠️ Low-Stock & Depleted Items", font=FONT_HEADING, bg="#ffffff", fg="#b45309").pack(side=tk.LEFT)
        ttk.Button(low_header, text="View All", style="Secondary.TButton", command=lambda: self.app.navigate_to("stock")).pack(side=tk.RIGHT)

        cols_low = ("sku", "name", "stock", "min_stock", "status")
        self.tree_low = ttk.Treeview(low_stock_frame, columns=cols_low, show="headings", height=7)
        self.tree_low.heading("sku", text="SKU")
        self.tree_low.heading("name", text="Product Name")
        self.tree_low.heading("stock", text="Stock")
        self.tree_low.heading("min_stock", text="Min")
        self.tree_low.heading("status", text="Status")

        self.tree_low.column("sku", width=90, anchor="w")
        self.tree_low.column("name", width=160, anchor="w")
        self.tree_low.column("stock", width=60, anchor="center")
        self.tree_low.column("min_stock", width=50, anchor="center")
        self.tree_low.column("status", width=90, anchor="center")

        configure_treeview_tags(self.tree_low)
        self.tree_low.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # --- Recent Transactions / Movements Panel ---
        movements_frame = tk.Frame(tables_container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        movements_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        mov_header = tk.Frame(movements_frame, bg="#ffffff", padx=15, pady=12)
        mov_header.pack(fill=tk.X)
        tk.Label(mov_header, text="🕒 Recent Stock Movements", font=FONT_HEADING, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(side=tk.LEFT)
        ttk.Button(mov_header, text="Full Audit Log", style="Secondary.TButton", command=lambda: self.app.navigate_to("stock", tab=1)).pack(side=tk.RIGHT)

        cols_mov = ("time", "product", "type", "change", "resulting")
        self.tree_mov = ttk.Treeview(movements_frame, columns=cols_mov, show="headings", height=7)
        self.tree_mov.heading("time", text="Date/Time")
        self.tree_mov.heading("product", text="Product")
        self.tree_mov.heading("type", text="Type")
        self.tree_mov.heading("change", text="Change")
        self.tree_mov.heading("resulting", text="Resulting")

        self.tree_mov.column("time", width=110, anchor="w")
        self.tree_mov.column("product", width=140, anchor="w")
        self.tree_mov.column("type", width=80, anchor="center")
        self.tree_mov.column("change", width=60, anchor="center")
        self.tree_mov.column("resulting", width=60, anchor="center")

        configure_treeview_tags(self.tree_mov)
        self.tree_mov.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _create_kpi_card(self, parent, row, col, title, initial_val, accent_color, subtitle):
        card = tk.Frame(parent, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        # Accent top bar
        accent = tk.Frame(card, bg=accent_color, height=4)
        accent.pack(fill=tk.X)

        pad_frame = tk.Frame(card, bg="#ffffff", padx=14, pady=12)
        pad_frame.pack(fill=tk.BOTH, expand=True)

        t_lbl = tk.Label(pad_frame, text=title, font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        t_lbl.pack(anchor="w")

        val_lbl = tk.Label(pad_frame, text=initial_val, font=FONT_STAT_NUM, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        val_lbl.pack(anchor="w", pady=(4, 2))

        sub_lbl = tk.Label(pad_frame, text=subtitle, font=("Segoe UI", 8), bg="#ffffff", fg="#94a3b8")
        sub_lbl.pack(anchor="w")

        return val_lbl

    def refresh(self):
        """Reload metrics from database and update all dashboard widgets."""
        try:
            metrics = ReportService.get_dashboard_metrics()
        except Exception as e:
            print("Dashboard refresh error:", e)
            return

        self.card_active_prods.config(text=str(metrics["total_products"]))
        self.card_total_units.config(text=f"{metrics['total_units']:,}")
        self.card_low_stock.config(text=str(metrics["low_stock_count"]))
        self.card_out_of_stock.config(text=str(metrics["out_of_stock_count"]))

        self.card_sales_today.config(text=f"₹{metrics['today_sales_rupees']:,.2f}")
        self.card_purchases_today.config(text=f"₹{metrics['today_purchases_rupees']:,.2f}")
        self.card_total_sales.config(text=f"₹{metrics['total_sales_rupees']:,.2f}")
        self.card_inventory_val.config(text=f"₹{metrics['total_valuation_rupees']:,.2f}")

        # Update Low Stock table
        self.tree_low.delete(*self.tree_low.get_children())
        combined_alerts = metrics["out_of_stock_products"] + metrics["low_stock_products"]
        for idx, p in enumerate(combined_alerts[:15]):
            tag = "status_out_of_stock" if p.is_out_of_stock else "status_low_stock"
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_low.insert(
                "",
                tk.END,
                values=(p.sku, p.name, p.current_stock, p.minimum_stock, p.stock_status),
                tags=(row_tag, tag)
            )

        # Update Recent Movements table
        self.tree_mov.delete(*self.tree_mov.get_children())
        for idx, m in enumerate(metrics["recent_movements"]):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            date_display = m.created_at[:16] if m.created_at else ""
            chg_display = f"+{m.quantity_change}" if m.quantity_change > 0 else str(m.quantity_change)
            self.tree_mov.insert(
                "",
                tk.END,
                values=(date_display, m.product_name, m.movement_type, chg_display, m.resulting_stock),
                tags=(row_tag,)
            )
