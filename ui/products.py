import tkinter as tk
from tkinter import ttk, messagebox
from models.product import Product
from repositories.category_repository import CategoryRepository
from repositories.product_repository import ProductRepository
from services.product_service import ProductService
from ui.styles import (
    COLOR_BORDER, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, configure_treeview_tags
)

class ProductsView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.pack(fill=tk.BOTH, expand=True)

        self.create_widgets()
        self.refresh()

    def create_widgets(self):
        # Top banner
        header_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=16, highlightbackground=COLOR_BORDER, highlightthickness=1)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))

        title_lbl = tk.Label(header_frame, text="Product Catalog Management", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(header_frame, text="View, create, search, and manage products and pricing rules", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Filter & Action toolbar
        toolbar = tk.Frame(self, bg="#f8fafc")
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 12))

        # Search box
        tk.Label(toolbar, text="🔍 Search:", font=FONT_BODY_BOLD, bg="#f8fafc", fg=COLOR_TEXT_PRIMARY).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=22)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        # Category filter
        tk.Label(toolbar, text="Category:", font=FONT_BODY_BOLD, bg="#f8fafc", fg=COLOR_TEXT_PRIMARY).pack(side=tk.LEFT, padx=(0, 5))
        self.cat_filter_var = tk.StringVar(value="All Categories")
        self.cat_combobox = ttk.Combobox(toolbar, textvariable=self.cat_filter_var, state="readonly", width=18)
        self.cat_combobox.pack(side=tk.LEFT, padx=(0, 15))
        self.cat_combobox.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Stock Status filter
        tk.Label(toolbar, text="Status:", font=FONT_BODY_BOLD, bg="#f8fafc", fg=COLOR_TEXT_PRIMARY).pack(side=tk.LEFT, padx=(0, 5))
        self.status_filter_var = tk.StringVar(value="All Statuses")
        self.status_combobox = ttk.Combobox(
            toolbar, 
            textvariable=self.status_filter_var, 
            values=["All Statuses", "In Stock", "Low Stock", "Out of Stock"], 
            state="readonly", 
            width=14
        )
        self.status_combobox.pack(side=tk.LEFT, padx=(0, 15))
        self.status_combobox.bind("<<ComboboxSelected>>", lambda e: self.refresh())

        # Action Buttons
        ttk.Button(toolbar, text="➕ Add Product", style="Primary.TButton", command=self.open_add_dialog).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(toolbar, text="✏️ Edit Selected", style="Secondary.TButton", command=self.open_edit_dialog).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(toolbar, text="🚫 Deactivate", style="Danger.TButton", command=self.deactivate_selected).pack(side=tk.RIGHT)

        # Products Table Frame
        table_frame = tk.Frame(self, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        cols = ("id", "sku", "name", "category", "purchase_price", "selling_price", "stock", "min_stock", "status")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("name", text="Product Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("purchase_price", text="Cost (₹)")
        self.tree.heading("selling_price", text="Selling (₹)")
        self.tree.heading("stock", text="Current Stock")
        self.tree.heading("min_stock", text="Min Stock")
        self.tree.heading("status", text="Stock Status")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("sku", width=120, anchor="w")
        self.tree.column("name", width=220, anchor="w")
        self.tree.column("category", width=130, anchor="w")
        self.tree.column("purchase_price", width=95, anchor="e")
        self.tree.column("selling_price", width=95, anchor="e")
        self.tree.column("stock", width=95, anchor="center")
        self.tree.column("min_stock", width=80, anchor="center")
        self.tree.column("status", width=110, anchor="center")

        configure_treeview_tags(self.tree)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<Double-1>", lambda e: self.open_edit_dialog())

    def refresh(self):
        """Update category dropdown values and populate the product table."""
        # Refresh categories in dropdown
        categories = CategoryRepository.get_all(include_counts=False)
        self.category_map = {c.name: c.id for c in categories}
        cat_names = ["All Categories"] + [c.name for c in categories]
        self.cat_combobox["values"] = cat_names

        # Get filter values
        search_query = self.search_var.get().strip()
        selected_cat_name = self.cat_filter_var.get()
        cat_id = self.category_map.get(selected_cat_name, None) if selected_cat_name != "All Categories" else None

        selected_status = self.status_filter_var.get()
        status_filter = selected_status if selected_status != "All Statuses" else None

        # Fetch products
        products = ProductRepository.search(query=search_query, category_id=cat_id, stock_status=status_filter)

        self.tree.delete(*self.tree.get_children())
        for idx, p in enumerate(products):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            if p.is_out_of_stock:
                status_tag = "status_out_of_stock"
            elif p.is_low_stock:
                status_tag = "status_low_stock"
            else:
                status_tag = "status_in_stock"

            self.tree.insert(
                "",
                tk.END,
                values=(
                    p.id,
                    p.sku,
                    p.name,
                    p.category_name,
                    f"₹{p.purchase_price_rupees:,.2f}",
                    f"₹{p.selling_price_rupees:,.2f}",
                    p.current_stock,
                    p.minimum_stock,
                    p.stock_status
                ),
                tags=(row_tag, status_tag)
            )

    def _get_selected_product_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a product from the table first.")
            return None
        return int(self.tree.item(selected[0])["values"][0])

    def open_add_dialog(self):
        ProductFormDialog(self, title="Add New Product", on_save=self.refresh)

    def open_edit_dialog(self):
        prod_id = self._get_selected_product_id()
        if prod_id:
            product = ProductRepository.get_by_id(prod_id)
            if product:
                ProductFormDialog(self, title="Edit Product", product=product, on_save=self.refresh)

    def deactivate_selected(self):
        prod_id = self._get_selected_product_id()
        if not prod_id:
            return
        product = ProductRepository.get_by_id(prod_id)
        if not product:
            return

        confirm = messagebox.askyesno(
            "Confirm Deactivation",
            f"Are you sure you want to deactivate '{product.name}' (SKU: {product.sku})?\n\n"
            "This product will no longer appear in active selections, but historical transactions remain preserved."
        )
        if confirm:
            try:
                ProductService.deactivate_product(prod_id)
                messagebox.showinfo("Success", f"Product '{product.name}' deactivated successfully.")
                self.refresh()
                self.app.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to deactivate product: {e}")

class ProductFormDialog(tk.Toplevel):
    def __init__(self, parent, title: str, product: Product = None, on_save=None):
        super().__init__(parent)
        self.parent = parent
        self.product = product
        self.on_save = on_save

        self.title(title)
        self.geometry("520x560")
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

        header_lbl = tk.Label(pad_frame, text=self.title(), font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        header_lbl.pack(anchor="w", pady=(0, 16))

        # Categories
        categories = CategoryRepository.get_all(include_counts=False)
        self.cat_lookup = {c.name: c.id for c in categories}
        cat_names = [c.name for c in categories]

        form_grid = tk.Frame(pad_frame, bg="#ffffff")
        form_grid.pack(fill=tk.X)
        form_grid.grid_columnconfigure(1, weight=1)

        row = 0
        # SKU
        tk.Label(form_grid, text="SKU Code *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        self.sku_var = tk.StringVar(value=self.product.sku if self.product else "")
        self.sku_entry = ttk.Entry(form_grid, textvariable=self.sku_var)
        self.sku_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Product Name
        tk.Label(form_grid, text="Product Name *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        self.name_var = tk.StringVar(value=self.product.name if self.product else "")
        self.name_entry = ttk.Entry(form_grid, textvariable=self.name_var)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Category
        tk.Label(form_grid, text="Category *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        initial_cat = self.product.category_name if self.product and self.product.category_name else (cat_names[0] if cat_names else "")
        self.cat_var = tk.StringVar(value=initial_cat)
        self.cat_dropdown = ttk.Combobox(form_grid, textvariable=self.cat_var, values=cat_names, state="readonly")
        self.cat_dropdown.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Purchase Price
        tk.Label(form_grid, text="Purchase Price (₹) *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        init_purch = f"{self.product.purchase_price_rupees:.2f}" if self.product else "0.00"
        self.purch_var = tk.StringVar(value=init_purch)
        self.purch_entry = ttk.Entry(form_grid, textvariable=self.purch_var)
        self.purch_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Selling Price
        tk.Label(form_grid, text="Selling Price (₹) *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        init_sell = f"{self.product.selling_price_rupees:.2f}" if self.product else "0.00"
        self.sell_var = tk.StringVar(value=init_sell)
        self.sell_entry = ttk.Entry(form_grid, textvariable=self.sell_var)
        self.sell_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Minimum Stock
        tk.Label(form_grid, text="Min Stock Alert Level *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        init_min = str(self.product.minimum_stock) if self.product else "5"
        self.min_var = tk.StringVar(value=init_min)
        self.min_entry = ttk.Entry(form_grid, textvariable=self.min_var)
        self.min_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        # Initial Opening Stock (Only visible when adding new product)
        if not self.product:
            row += 1
            tk.Label(form_grid, text="Initial Stock Quantity:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
            self.init_stock_var = tk.StringVar(value="0")
            self.init_stock_entry = ttk.Entry(form_grid, textvariable=self.init_stock_var)
            self.init_stock_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))
        else:
            row += 1
            tk.Label(form_grid, text="Current Stock:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
            stk_info = tk.Label(
                form_grid, 
                text=f"{self.product.current_stock} units (Editable only via Purchases, Sales, or Adjustments)", 
                font=FONT_SMALL, 
                bg="#ffffff", 
                fg=COLOR_TEXT_SECONDARY
            )
            stk_info.grid(row=row, column=1, sticky="w", pady=6, padx=(10, 0))

        row += 1
        # Description
        tk.Label(form_grid, text="Description:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="nw", pady=6)
        self.desc_text = tk.Text(form_grid, height=3, width=28, font=FONT_BODY)
        if self.product and self.product.description:
            self.desc_text.insert("1.0", self.product.description)
        self.desc_text.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        # Buttons at bottom
        btn_bar = tk.Frame(pad_frame, bg="#ffffff")
        btn_bar.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_bar, text="Cancel", style="Secondary.TButton", command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_bar, text="Save Product", style="Primary.TButton", command=self.save_product).pack(side=tk.RIGHT)

    def save_product(self):
        sku = self.sku_var.get().strip()
        name = self.name_var.get().strip()
        cat_name = self.cat_var.get().strip()
        cat_id = self.cat_lookup.get(cat_name)
        purch_str = self.purch_var.get().strip()
        sell_str = self.sell_var.get().strip()
        min_str = self.min_var.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()

        if not cat_id:
            messagebox.showerror("Validation Error", "Please select a valid category.")
            return

        try:
            if not self.product:
                # Add mode
                init_stock = int(self.init_stock_var.get().strip()) if self.init_stock_var.get().strip() else 0
                ProductService.create_product(
                    sku=sku,
                    name=name,
                    category_id=cat_id,
                    purchase_price_rupees=purch_str,
                    selling_price_rupees=sell_str,
                    minimum_stock=int(min_str),
                    description=description,
                    initial_stock=init_stock
                )
                messagebox.showinfo("Success", f"Product '{name}' created successfully.")
            else:
                # Edit mode (preserves current stock)
                ProductService.update_product(
                    product_id=self.product.id,
                    sku=sku,
                    name=name,
                    category_id=cat_id,
                    purchase_price_rupees=purch_str,
                    selling_price_rupees=sell_str,
                    minimum_stock=int(min_str),
                    description=description
                )
                messagebox.showinfo("Success", f"Product '{name}' updated successfully.")

            if self.on_save:
                self.on_save()
            self.parent.app.refresh_dashboard()
            self.destroy()
        except ValueError as ex:
            messagebox.showerror("Validation Error", str(ex))
        except Exception as ex:
            messagebox.showerror("Database Error", f"An unexpected error occurred: {ex}")
