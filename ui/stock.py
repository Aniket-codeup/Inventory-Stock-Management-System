import tkinter as tk
from tkinter import ttk, messagebox
from repositories.category_repository import CategoryRepository
from repositories.product_repository import ProductRepository
from repositories.stock_movement_repository import StockMovementRepository
from services.inventory_service import InventoryService
from ui.styles import (
    COLOR_BORDER, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, FONT_STAT_NUM, configure_treeview_tags
)

class StockView(ttk.Frame):
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

        title_lbl = tk.Label(header_frame, text="Stock Control & Movement Auditing", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(header_frame, text="Monitor real-time warehouse inventory, trace every stock movement, and perform authorized adjustments", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.tab_levels = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_levels, text="📦 Current Stock Levels")

        self.tab_movements = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_movements, text="🔄 Movement History & Audit Trail")

        self._build_levels_tab()
        self._build_movements_tab()

    def _build_levels_tab(self):
        container = tk.Frame(self.tab_levels, bg="#f8fafc", padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Toolbar
        toolbar = tk.Frame(container, bg="#f8fafc")
        toolbar.pack(fill=tk.X, pady=(0, 12))

        tk.Label(toolbar, text="🔍 Search:", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_levels())

        tk.Label(toolbar, text="Category:", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 5))
        self.cat_var = tk.StringVar(value="All Categories")
        self.cat_combo = ttk.Combobox(toolbar, textvariable=self.cat_var, state="readonly", width=16)
        self.cat_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_levels())

        tk.Label(toolbar, text="Status:", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 5))
        self.status_var = tk.StringVar(value="All Statuses")
        self.status_combo = ttk.Combobox(
            toolbar, 
            textvariable=self.status_var, 
            values=["All Statuses", "In Stock", "Low Stock", "Out of Stock"], 
            state="readonly", 
            width=14
        )
        self.status_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.status_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_levels())

        ttk.Button(toolbar, text="⚖️ Stock Adjustment", style="Primary.TButton", command=self.open_adjustment_dialog).pack(side=tk.RIGHT)
        ttk.Button(toolbar, text="🔄 Refresh", style="Secondary.TButton", command=self.refresh_levels).pack(side=tk.RIGHT, padx=(0, 10))

        # Stock Levels Table
        table_frame = tk.Frame(container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "sku", "name", "category", "stock", "min_stock", "status")
        self.tree_levels = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.tree_levels.heading("id", text="ID")
        self.tree_levels.heading("sku", text="SKU")
        self.tree_levels.heading("name", text="Product Name")
        self.tree_levels.heading("category", text="Category")
        self.tree_levels.heading("stock", text="Available Stock")
        self.tree_levels.heading("min_stock", text="Min Threshold")
        self.tree_levels.heading("status", text="Stock Health Status")

        self.tree_levels.column("id", width=50, anchor="center")
        self.tree_levels.column("sku", width=120, anchor="w")
        self.tree_levels.column("name", width=250, anchor="w")
        self.tree_levels.column("category", width=140, anchor="w")
        self.tree_levels.column("stock", width=110, anchor="center")
        self.tree_levels.column("min_stock", width=100, anchor="center")
        self.tree_levels.column("status", width=130, anchor="center")

        configure_treeview_tags(self.tree_levels)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_levels.yview)
        self.tree_levels.configure(yscrollcommand=scroll_y.set)

        self.tree_levels.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_levels.bind("<Double-1>", lambda e: self.open_adjustment_dialog())

    def _build_movements_tab(self):
        container = tk.Frame(self.tab_movements, bg="#f8fafc", padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(container, bg="#f8fafc")
        toolbar.pack(fill=tk.X, pady=(0, 12))

        tk.Label(toolbar, text="Movement Type:", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 6))
        self.mov_type_var = tk.StringVar(value="All")
        self.mov_type_combo = ttk.Combobox(
            toolbar, 
            textvariable=self.mov_type_var, 
            values=["All", "PURCHASE", "SALE", "ADJUSTMENT", "OPENING_STOCK"], 
            state="readonly", 
            width=16
        )
        self.mov_type_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.mov_type_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_movements())

        ttk.Button(toolbar, text="🔄 Refresh Log", style="Secondary.TButton", command=self.refresh_movements).pack(side=tk.LEFT)

        # Movements Table
        table_frame = tk.Frame(container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "time", "sku", "product", "type", "change", "prev", "result", "reason")
        self.tree_movements = ttk.Treeview(table_frame, columns=cols, show="headings")

        self.tree_movements.heading("id", text="ID")
        self.tree_movements.heading("time", text="Date & Time")
        self.tree_movements.heading("sku", text="SKU")
        self.tree_movements.heading("product", text="Product Name")
        self.tree_movements.heading("type", text="Type")
        self.tree_movements.heading("change", text="Change")
        self.tree_movements.heading("prev", text="Prev Stock")
        self.tree_movements.heading("result", text="Result Stock")
        self.tree_movements.heading("reason", text="Audit Reason / Reference")

        self.tree_movements.column("id", width=50, anchor="center")
        self.tree_movements.column("time", width=140, anchor="w")
        self.tree_movements.column("sku", width=100, anchor="w")
        self.tree_movements.column("product", width=180, anchor="w")
        self.tree_movements.column("type", width=100, anchor="center")
        self.tree_movements.column("change", width=70, anchor="center")
        self.tree_movements.column("prev", width=80, anchor="center")
        self.tree_movements.column("result", width=80, anchor="center")
        self.tree_movements.column("reason", width=220, anchor="w")

        configure_treeview_tags(self.tree_movements)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_movements.yview)
        self.tree_movements.configure(yscrollcommand=scroll_y.set)

        self.tree_movements.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        categories = CategoryRepository.get_all(include_counts=False)
        self.cat_lookup = {c.name: c.id for c in categories}
        self.cat_combo["values"] = ["All Categories"] + [c.name for c in categories]

        self.refresh_levels()
        self.refresh_movements()

    def refresh_levels(self):
        query = self.search_var.get().strip()
        cat_name = self.cat_var.get()
        cat_id = self.cat_lookup.get(cat_name, None) if cat_name != "All Categories" else None

        status_name = self.status_var.get()
        status_filter = status_name if status_name != "All Statuses" else None

        products = ProductRepository.search(query=query, category_id=cat_id, stock_status=status_filter)

        self.tree_levels.delete(*self.tree_levels.get_children())
        for idx, p in enumerate(products):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            if p.is_out_of_stock:
                status_tag = "status_out_of_stock"
            elif p.is_low_stock:
                status_tag = "status_low_stock"
            else:
                status_tag = "status_in_stock"

            self.tree_levels.insert(
                "",
                tk.END,
                values=(p.id, p.sku, p.name, p.category_name, p.current_stock, p.minimum_stock, p.stock_status),
                tags=(row_tag, status_tag)
            )

    def refresh_movements(self):
        mov_type = self.mov_type_var.get()
        movements = StockMovementRepository.get_all(movement_type=mov_type, limit=200)

        self.tree_movements.delete(*self.tree_movements.get_children())
        for idx, m in enumerate(movements):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            chg_str = f"+{m.quantity_change}" if m.quantity_change > 0 else str(m.quantity_change)
            ref_str = f"Purchase #{m.purchase_id}" if m.purchase_id else (f"Sale #{m.sale_id}" if m.sale_id else m.reason)
            self.tree_movements.insert(
                "",
                tk.END,
                values=(
                    m.id,
                    m.created_at[:16] if m.created_at else "",
                    m.product_sku,
                    m.product_name,
                    m.movement_type,
                    chg_str,
                    m.previous_stock,
                    m.resulting_stock,
                    ref_str
                ),
                tags=(row_tag,)
            )

    def open_adjustment_dialog(self):
        selected = self.tree_levels.selection()
        selected_prod_id = None
        if selected:
            selected_prod_id = int(self.tree_levels.item(selected[0])["values"][0])
        StockAdjustmentDialog(self, selected_prod_id=selected_prod_id, on_save=self.refresh)

class StockAdjustmentDialog(tk.Toplevel):
    def __init__(self, parent, selected_prod_id=None, on_save=None):
        super().__init__(parent)
        self.parent = parent
        self.selected_prod_id = selected_prod_id
        self.on_save = on_save

        self.title("Manual Stock Adjustment")
        self.geometry("480x440")
        self.resizable(False, False)
        self.configure(bg="#ffffff")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        pad_frame = tk.Frame(self, bg="#ffffff", padx=24, pady=20)
        pad_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(pad_frame, text="Manual Stock Adjustment", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(anchor="w")
        tk.Label(pad_frame, text="Apply authorized stock changes with mandatory audit reason", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY).pack(anchor="w", pady=(2, 16))

        # Products list
        products = ProductRepository.get_all()
        self.prod_map = {}
        prod_names = []
        initial_idx = 0
        for idx, p in enumerate(products):
            label = f"{p.sku} - {p.name} (Current: {p.current_stock})"
            self.prod_map[label] = p
            prod_names.append(label)
            if self.selected_prod_id and p.id == self.selected_prod_id:
                initial_idx = idx

        form_grid = tk.Frame(pad_frame, bg="#ffffff")
        form_grid.pack(fill=tk.X)
        form_grid.grid_columnconfigure(1, weight=1)

        row = 0
        tk.Label(form_grid, text="Select Product *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        self.prod_var = tk.StringVar()
        self.prod_combo = ttk.Combobox(form_grid, textvariable=self.prod_var, values=prod_names, state="readonly", width=30)
        self.prod_combo.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))
        if prod_names:
            self.prod_combo.current(initial_idx)

        row += 1
        tk.Label(form_grid, text="Action Type *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        self.direction_var = tk.StringVar(value="Add Stock (+)")
        self.dir_combo = ttk.Combobox(
            form_grid, 
            textvariable=self.direction_var, 
            values=["Add Stock (+)", "Deduct Stock (-)", "Found in Audit (+)", "Damaged / Expired (-)", "Customer Return (+)"], 
            state="readonly"
        )
        self.dir_combo.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        tk.Label(form_grid, text="Quantity *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        self.qty_var = tk.StringVar(value="1")
        self.qty_entry = ttk.Entry(form_grid, textvariable=self.qty_var)
        self.qty_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        tk.Label(form_grid, text="Audit Reason *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="nw", pady=6)
        self.reason_text = tk.Text(form_grid, height=4, font=FONT_BODY)
        self.reason_text.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        btn_bar = tk.Frame(pad_frame, bg="#ffffff")
        btn_bar.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_bar, text="Cancel", style="Secondary.TButton", command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_bar, text="Apply Adjustment", style="Primary.TButton", command=self.apply_adjustment).pack(side=tk.RIGHT)

    def apply_adjustment(self):
        prod_label = self.prod_var.get()
        product = self.prod_map.get(prod_label)
        if not product:
            messagebox.showerror("Validation Error", "Please select a product.")
            return

        try:
            qty = int(self.qty_var.get().strip())
            if qty <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Validation Error", "Quantity must be a positive integer.")
            return

        direction = self.direction_var.get()
        change = qty if ("+" in direction) else -qty

        reason = self.reason_text.get("1.0", tk.END).strip()
        if not reason:
            messagebox.showerror("Validation Error", "Please enter an audit reason for this adjustment.")
            return

        m_type = "DAMAGE" if "Damaged" in direction else ("RETURN" if "Return" in direction else "ADJUSTMENT")

        try:
            res = InventoryService.adjust_stock(
                product_id=product.id,
                quantity_change=change,
                movement_type=m_type,
                reason=reason
            )
            messagebox.showinfo(
                "Adjustment Complete",
                f"Stock successfully adjusted for '{product.name}'.\n\n"
                f"Previous: {res['previous_stock']} units\n"
                f"Change: {res['quantity_change']} units\n"
                f"New Stock: {res['resulting_stock']} units"
            )
            if self.on_save:
                self.on_save()
            self.parent.app.refresh_dashboard()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Adjustment Failed", str(e))
