import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from repositories.supplier_repository import SupplierRepository
from repositories.product_repository import ProductRepository
from services.purchase_service import PurchaseService
from ui.styles import (
    COLOR_BORDER, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, FONT_STAT_NUM, configure_treeview_tags
)

class PurchasesView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)

        self.cart_items = []  # list of dicts: product_id, sku, name, quantity, unit_price_rupees, line_total_rupees

        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=16, highlightbackground=COLOR_BORDER, highlightthickness=1)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))

        title_lbl = tk.Label(header_frame, text="Purchase Management & Stock Replenishment", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(header_frame, text="Record vendor deliveries, track purchase orders, and automatically increase stock levels", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Tab 1: Record Purchase
        self.tab_record = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_record, text="📥 Record New Purchase")

        # Tab 2: Purchase History
        self.tab_history = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_history, text="📜 Purchase History & Audit")

        self._build_record_tab()
        self._build_history_tab()

    def _build_record_tab(self):
        container = tk.Frame(self.tab_record, bg="#f8fafc", padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Top section: Supplier & Order metadata card
        meta_card = tk.Frame(container, bg="#ffffff", padx=15, pady=12, highlightbackground=COLOR_BORDER, highlightthickness=1)
        meta_card.pack(fill=tk.X, pady=(0, 15))

        meta_grid = tk.Frame(meta_card, bg="#ffffff")
        meta_grid.pack(fill=tk.X)

        # Supplier
        tk.Label(meta_grid, text="Supplier *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.sup_var = tk.StringVar()
        self.sup_combo = ttk.Combobox(meta_grid, textvariable=self.sup_var, state="readonly", width=26)
        self.sup_combo.grid(row=0, column=1, sticky="w", padx=(0, 20))

        # Date
        tk.Label(meta_grid, text="Date:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=0, column=2, sticky="w", padx=(0, 8))
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.date_entry = ttk.Entry(meta_grid, textvariable=self.date_var, width=18)
        self.date_entry.grid(row=0, column=3, sticky="w", padx=(0, 20))

        # Reference No
        tk.Label(meta_grid, text="Ref / Invoice #:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=0, column=4, sticky="w", padx=(0, 8))
        self.ref_var = tk.StringVar()
        self.ref_entry = ttk.Entry(meta_grid, textvariable=self.ref_var, width=16)
        self.ref_entry.grid(row=0, column=5, sticky="w")

        # Middle: Add Item Bar
        item_bar = tk.Frame(container, bg="#ffffff", padx=15, pady=12, highlightbackground=COLOR_BORDER, highlightthickness=1)
        item_bar.pack(fill=tk.X, pady=(0, 15))

        tk.Label(item_bar, text="Select Product *:", font=FONT_BODY_BOLD, bg="#ffffff").pack(side=tk.LEFT, padx=(0, 6))
        self.item_prod_var = tk.StringVar()
        self.item_prod_combo = ttk.Combobox(item_bar, textvariable=self.item_prod_var, state="readonly", width=28)
        self.item_prod_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.item_prod_combo.bind("<<ComboboxSelected>>", self._on_product_selected)

        tk.Label(item_bar, text="Cost Price (₹) *:", font=FONT_BODY_BOLD, bg="#ffffff").pack(side=tk.LEFT, padx=(0, 6))
        self.item_price_var = tk.StringVar(value="0.00")
        self.item_price_entry = ttk.Entry(item_bar, textvariable=self.item_price_var, width=10)
        self.item_price_entry.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(item_bar, text="Quantity *:", font=FONT_BODY_BOLD, bg="#ffffff").pack(side=tk.LEFT, padx=(0, 6))
        self.item_qty_var = tk.StringVar(value="1")
        self.item_qty_entry = ttk.Entry(item_bar, textvariable=self.item_qty_var, width=8)
        self.item_qty_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.item_qty_entry.bind("<Return>", lambda e: self.add_item_to_cart())

        ttk.Button(item_bar, text="➕ Add to Order", style="Primary.TButton", command=self.add_item_to_cart).pack(side=tk.LEFT)

        # Cart Table & Summary Split
        cart_split = tk.Frame(container, bg="#f8fafc")
        cart_split.pack(fill=tk.BOTH, expand=True)

        # Left: Items Cart Table
        cart_frame = tk.Frame(cart_split, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        cart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        cols = ("sku", "name", "price", "qty", "line_total")
        self.tree_cart = ttk.Treeview(cart_frame, columns=cols, show="headings", height=8)
        self.tree_cart.heading("sku", text="SKU")
        self.tree_cart.heading("name", text="Product Name")
        self.tree_cart.heading("price", text="Unit Cost (₹)")
        self.tree_cart.heading("qty", text="Quantity")
        self.tree_cart.heading("line_total", text="Line Total (₹)")

        self.tree_cart.column("sku", width=100, anchor="w")
        self.tree_cart.column("name", width=220, anchor="w")
        self.tree_cart.column("price", width=100, anchor="e")
        self.tree_cart.column("qty", width=80, anchor="center")
        self.tree_cart.column("line_total", width=110, anchor="e")

        configure_treeview_tags(self.tree_cart)
        self.tree_cart.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cart toolbar
        cart_tools = tk.Frame(cart_frame, bg="#ffffff", padx=10, pady=5)
        cart_tools.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(cart_tools, text="❌ Remove Selected Item", style="Secondary.TButton", command=self.remove_item_from_cart).pack(side=tk.LEFT)
        ttk.Button(cart_tools, text="🧹 Clear All Items", style="Secondary.TButton", command=self.clear_cart).pack(side=tk.LEFT, padx=(10, 0))

        # Right: Total & Order Checkout Card
        checkout_card = tk.Frame(cart_split, bg="#ffffff", width=260, padx=18, pady=18, highlightbackground=COLOR_BORDER, highlightthickness=1)
        checkout_card.pack(side=tk.RIGHT, fill=tk.Y)
        checkout_card.pack_propagate(False)

        tk.Label(checkout_card, text="Order Summary", font=FONT_HEADING, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(anchor="w")
        tk.Label(checkout_card, text="Grand Total Payable", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY).pack(anchor="w", pady=(12, 0))

        self.total_lbl = tk.Label(checkout_card, text="₹0.00", font=FONT_STAT_NUM, bg="#ffffff", fg=COLOR_PRIMARY)
        self.total_lbl.pack(anchor="w", pady=(2, 10))

        self.items_count_lbl = tk.Label(checkout_card, text="0 items in order", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        self.items_count_lbl.pack(anchor="w", pady=(0, 15))

        tk.Label(checkout_card, text="Order Notes / PO Ref:", font=FONT_BODY_BOLD, bg="#ffffff").pack(anchor="w")
        self.notes_text = tk.Text(checkout_card, height=4, font=FONT_BODY)
        self.notes_text.pack(fill=tk.X, pady=(4, 15))

        ttk.Button(checkout_card, text="💾 Save Purchase & Update Stock", style="Success.TButton", command=self.submit_purchase).pack(fill=tk.X)

    def _build_history_tab(self):
        container = tk.Frame(self.tab_history, bg="#f8fafc", padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Filter bar
        filt_bar = tk.Frame(container, bg="#f8fafc")
        filt_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(filt_bar, text="Filter by Supplier:", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 6))
        self.hist_sup_var = tk.StringVar(value="All Suppliers")
        self.hist_sup_combo = ttk.Combobox(filt_bar, textvariable=self.hist_sup_var, state="readonly", width=22)
        self.hist_sup_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.hist_sup_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_history())

        ttk.Button(filt_bar, text="🔄 Refresh History", style="Secondary.TButton", command=self.refresh_history).pack(side=tk.LEFT)
        ttk.Button(filt_bar, text="🔍 View Selected Order Details", style="Primary.TButton", command=self.view_selected_order).pack(side=tk.RIGHT)

        # History Table
        hist_frame = tk.Frame(container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        hist_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "date", "supplier", "ref", "amount", "notes")
        self.tree_hist = ttk.Treeview(hist_frame, columns=cols, show="headings", selectmode="browse")
        self.tree_hist.heading("id", text="Purchase ID")
        self.tree_hist.heading("date", text="Date & Time")
        self.tree_hist.heading("supplier", text="Supplier")
        self.tree_hist.heading("ref", text="Reference / Invoice #")
        self.tree_hist.heading("amount", text="Total Paid (₹)")
        self.tree_hist.heading("notes", text="Notes")

        self.tree_hist.column("id", width=90, anchor="center")
        self.tree_hist.column("date", width=140, anchor="w")
        self.tree_hist.column("supplier", width=180, anchor="w")
        self.tree_hist.column("ref", width=130, anchor="w")
        self.tree_hist.column("amount", width=120, anchor="e")
        self.tree_hist.column("notes", width=220, anchor="w")

        configure_treeview_tags(self.tree_hist)

        scroll_y = ttk.Scrollbar(hist_frame, orient="vertical", command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=scroll_y.set)

        self.tree_hist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree_hist.bind("<Double-1>", lambda e: self.view_selected_order())

    def refresh(self):
        # Refresh suppliers dropdown
        suppliers = SupplierRepository.get_all()
        self.supplier_map = {s.name: s.id for s in suppliers}
        sup_names = [s.name for s in suppliers]
        self.sup_combo["values"] = sup_names
        if sup_names and not self.sup_var.get():
            self.sup_combo.current(0)

        # Refresh supplier history dropdown
        self.hist_sup_combo["values"] = ["All Suppliers"] + sup_names

        # Refresh products dropdown
        products = ProductRepository.get_all()
        self.product_lookup = {}
        prod_displays = []
        for p in products:
            label = f"{p.sku} - {p.name}"
            self.product_lookup[label] = p
            prod_displays.append(label)
        self.item_prod_combo["values"] = prod_displays
        if prod_displays and not self.item_prod_var.get():
            self.item_prod_combo.current(0)
            self._on_product_selected(None)

        self.refresh_history()

    def _on_product_selected(self, event):
        selected_label = self.item_prod_var.get()
        product = self.product_lookup.get(selected_label)
        if product:
            self.item_price_var.set(f"{product.purchase_price_rupees:.2f}")

    def add_item_to_cart(self):
        label = self.item_prod_var.get()
        product = self.product_lookup.get(label)
        if not product:
            messagebox.showerror("Error", "Please select a product.")
            return

        try:
            qty = int(self.item_qty_var.get().strip())
            if qty <= 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Validation Error", "Quantity must be a positive integer.")
            return

        try:
            price = float(self.item_price_var.get().strip())
            if price < 0:
                raise ValueError()
        except Exception:
            messagebox.showerror("Validation Error", "Unit price must be a valid positive number.")
            return

        # Check if already in cart, if so update quantity
        for item in self.cart_items:
            if item["product_id"] == product.id:
                item["quantity"] += qty
                item["unit_price_rupees"] = price
                item["line_total_rupees"] = round(item["quantity"] * price, 2)
                self._update_cart_display()
                return

        line_total = round(qty * price, 2)
        self.cart_items.append({
            "product_id": product.id,
            "sku": product.sku,
            "name": product.name,
            "quantity": qty,
            "unit_price_rupees": price,
            "line_total_rupees": line_total
        })
        self._update_cart_display()

    def remove_item_from_cart(self):
        selected = self.tree_cart.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Select an item from the cart to remove.")
            return
        idx = self.tree_cart.index(selected[0])
        del self.cart_items[idx]
        self._update_cart_display()

    def clear_cart(self):
        self.cart_items.clear()
        self._update_cart_display()

    def _update_cart_display(self):
        self.tree_cart.delete(*self.tree_cart.get_children())
        grand_total = 0.0
        total_qty = 0
        for idx, item in enumerate(self.cart_items):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_cart.insert(
                "",
                tk.END,
                values=(
                    item["sku"],
                    item["name"],
                    f"₹{item['unit_price_rupees']:,.2f}",
                    item["quantity"],
                    f"₹{item['line_total_rupees']:,.2f}"
                ),
                tags=(row_tag,)
            )
            grand_total += item["line_total_rupees"]
            total_qty += item["quantity"]

        self.total_lbl.config(text=f"₹{grand_total:,.2f}")
        self.items_count_lbl.config(text=f"{len(self.cart_items)} item(s) • {total_qty} total units")

    def submit_purchase(self):
        sup_name = self.sup_var.get().strip()
        sup_id = self.supplier_map.get(sup_name)
        if not sup_id:
            messagebox.showerror("Validation Error", "Please select a valid supplier.")
            return

        if not self.cart_items:
            messagebox.showerror("Validation Error", "Please add at least one product to the purchase order.")
            return

        date_val = self.date_var.get().strip()
        ref_no = self.ref_var.get().strip()
        notes = self.notes_text.get("1.0", tk.END).strip()

        # Format items for service
        service_items = [
            {
                "product_id": it["product_id"],
                "quantity": it["quantity"],
                "unit_price": it["unit_price_rupees"]
            }
            for it in self.cart_items
        ]

        try:
            pid = PurchaseService.record_purchase(
                supplier_id=sup_id,
                items=service_items,
                purchase_date=date_val,
                reference_number=ref_no,
                notes=notes
            )
            messagebox.showinfo("Success", f"Purchase Order #{pid} saved successfully!\nStock levels have been updated.")
            self.clear_cart()
            self.ref_var.set("")
            self.notes_text.delete("1.0", tk.END)
            self.refresh()
            self.app.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Purchase Failed", f"Failed to record purchase: {e}")

    def refresh_history(self):
        sup_filter_name = self.hist_sup_var.get()
        sup_id = self.supplier_map.get(sup_filter_name, None) if sup_filter_name != "All Suppliers" else None
        purchases = PurchaseService.list_purchases(supplier_id=sup_id)

        self.tree_hist.delete(*self.tree_hist.get_children())
        for idx, p in enumerate(purchases):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_hist.insert(
                "",
                tk.END,
                values=(
                    p.id,
                    p.purchase_date[:16] if p.purchase_date else "",
                    p.supplier_name,
                    p.reference_number or "-",
                    f"₹{p.total_amount_rupees:,.2f}",
                    p.notes or ""
                ),
                tags=(row_tag,)
            )

    def view_selected_order(self):
        selected = self.tree_hist.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a purchase order from the history table.")
            return
        pid = int(self.tree_hist.item(selected[0])["values"][0])
        purchase = PurchaseService.get_purchase(pid)
        if purchase:
            PurchaseDetailDialog(self, purchase)

class PurchaseDetailDialog(tk.Toplevel):
    def __init__(self, parent, purchase):
        super().__init__(parent)
        self.title(f"Purchase Order Details — #{purchase.id}")
        self.geometry("600x460")
        self.configure(bg="#ffffff")
        self.transient(parent)
        self.grab_set()

        pad = tk.Frame(self, bg="#ffffff", padx=20, pady=16)
        pad.pack(fill=tk.BOTH, expand=True)

        tk.Label(pad, text=f"Purchase Order #{purchase.id}", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(anchor="w")
        tk.Label(pad, text=f"Supplier: {purchase.supplier_name}  |  Date: {purchase.purchase_date}", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY).pack(anchor="w", pady=(2, 12))

        # Items Table
        cols = ("sku", "name", "price", "qty", "total")
        tree = ttk.Treeview(pad, columns=cols, show="headings", height=8)
        tree.heading("sku", text="SKU")
        tree.heading("name", text="Product")
        tree.heading("price", text="Unit Cost (₹)")
        tree.heading("qty", text="Quantity")
        tree.heading("total", text="Line Total (₹)")

        tree.column("sku", width=90, anchor="w")
        tree.column("name", width=200, anchor="w")
        tree.column("price", width=95, anchor="e")
        tree.column("qty", width=70, anchor="center")
        tree.column("total", width=100, anchor="e")

        configure_treeview_tags(tree)
        for idx, it in enumerate(purchase.items):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            tree.insert("", tk.END, values=(it.product_sku, it.product_name, f"₹{it.unit_price_rupees:,.2f}", it.quantity, f"₹{it.line_total_rupees:,.2f}"), tags=(row_tag,))
        tree.pack(fill=tk.BOTH, expand=True)

        # Footer
        footer = tk.Frame(pad, bg="#ffffff", pady=10)
        footer.pack(fill=tk.X)
        tk.Label(footer, text=f"Total Paid: ₹{purchase.total_amount_rupees:,.2f}", font=FONT_HEADING, bg="#ffffff", fg=COLOR_PRIMARY).pack(side=tk.LEFT)
        ttk.Button(footer, text="Close", style="Secondary.TButton", command=self.destroy).pack(side=tk.RIGHT)
