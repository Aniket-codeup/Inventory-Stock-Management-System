import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import datetime
from repositories.category_repository import CategoryRepository
from services.report_service import ReportService
from ui.styles import (
    COLOR_BORDER, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, configure_treeview_tags
)

class ReportsView(ttk.Frame):
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

        title_lbl = tk.Label(header_frame, text="Business Reports & Analytical Exports", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(header_frame, text="Generate detailed valuation, replenishment, sales, purchase, and stock audit statements", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.tab_inv = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_inv, text="📊 Inventory Valuation")

        self.tab_low = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_low, text="⚠️ Low-Stock & Replenishment")

        self.tab_sales = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sales, text="📈 Sales Performance")

        self.tab_purch = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_purch, text="📥 Procurement & Purchases")

        self._build_inventory_report()
        self._build_low_stock_report()
        self._build_sales_report()
        self._build_purchases_report()

    def _build_inventory_report(self):
        container = tk.Frame(self.tab_inv, bg="#f8fafc", padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(container, bg="#f8fafc")
        toolbar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(toolbar, text="Category Filter:", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 6))
        self.inv_cat_var = tk.StringVar(value="All Categories")
        self.inv_cat_combo = ttk.Combobox(toolbar, textvariable=self.inv_cat_var, state="readonly", width=18)
        self.inv_cat_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.inv_cat_combo.bind("<<ComboboxSelected>>", lambda e: self.load_inventory_report())

        ttk.Button(toolbar, text="🔄 Generate Report", style="Secondary.TButton", command=self.load_inventory_report).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="📥 Export to CSV", style="Primary.TButton", command=self.export_inventory_csv).pack(side=tk.RIGHT)

        table_frame = tk.Frame(container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("sku", "name", "category", "stock", "min", "cost", "sell", "cost_val", "retail_val", "status")
        self.tree_inv = ttk.Treeview(table_frame, columns=cols, show="headings")
        self.tree_inv.heading("sku", text="SKU")
        self.tree_inv.heading("name", text="Product Name")
        self.tree_inv.heading("category", text="Category")
        self.tree_inv.heading("stock", text="Stock")
        self.tree_inv.heading("min", text="Min")
        self.tree_inv.heading("cost", text="Cost (₹)")
        self.tree_inv.heading("sell", text="Selling (₹)")
        self.tree_inv.heading("cost_val", text="Cost Valuation (₹)")
        self.tree_inv.heading("retail_val", text="Retail Valuation (₹)")
        self.tree_inv.heading("status", text="Status")

        self.tree_inv.column("sku", width=90, anchor="w")
        self.tree_inv.column("name", width=180, anchor="w")
        self.tree_inv.column("category", width=120, anchor="w")
        self.tree_inv.column("stock", width=60, anchor="center")
        self.tree_inv.column("min", width=50, anchor="center")
        self.tree_inv.column("cost", width=80, anchor="e")
        self.tree_inv.column("sell", width=80, anchor="e")
        self.tree_inv.column("cost_val", width=115, anchor="e")
        self.tree_inv.column("retail_val", width=115, anchor="e")
        self.tree_inv.column("status", width=95, anchor="center")

        configure_treeview_tags(self.tree_inv)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_inv.yview)
        self.tree_inv.configure(yscrollcommand=scroll_y.set)

        self.tree_inv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_low_stock_report(self):
        container = tk.Frame(self.tab_low, bg="#f8fafc", padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(container, bg="#f8fafc")
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="🔄 Refresh Alert List", style="Secondary.TButton", command=self.load_low_stock_report).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="📥 Export Replenishment List to CSV", style="Primary.TButton", command=self.export_low_stock_csv).pack(side=tk.RIGHT)

        table_frame = tk.Frame(container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("sku", "name", "category", "current", "min", "reorder", "cost", "status")
        self.tree_low = ttk.Treeview(table_frame, columns=cols, show="headings")
        self.tree_low.heading("sku", text="SKU")
        self.tree_low.heading("name", text="Product Name")
        self.tree_low.heading("category", text="Category")
        self.tree_low.heading("current", text="Current Stock")
        self.tree_low.heading("min", text="Min Level")
        self.tree_low.heading("reorder", text="Suggested Reorder Qty")
        self.tree_low.heading("cost", text="Unit Cost (₹)")
        self.tree_low.heading("status", text="Stock Status")

        self.tree_low.column("sku", width=100, anchor="w")
        self.tree_low.column("name", width=220, anchor="w")
        self.tree_low.column("category", width=140, anchor="w")
        self.tree_low.column("current", width=90, anchor="center")
        self.tree_low.column("min", width=90, anchor="center")
        self.tree_low.column("reorder", width=140, anchor="center")
        self.tree_low.column("cost", width=95, anchor="e")
        self.tree_low.column("status", width=110, anchor="center")

        configure_treeview_tags(self.tree_low)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_low.yview)
        self.tree_low.configure(yscrollcommand=scroll_y.set)

        self.tree_low.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_sales_report(self):
        container = tk.Frame(self.tab_sales, bg="#f8fafc", padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(container, bg="#f8fafc")
        toolbar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(toolbar, text="From Date (YYYY-MM-DD):", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 4))
        self.sales_from_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.sales_from_var, width=12).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(toolbar, text="To Date:", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 4))
        self.sales_to_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.sales_to_var, width=12).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Button(toolbar, text="🔄 Filter Sales", style="Secondary.TButton", command=self.load_sales_report).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="📥 Export Sales to CSV", style="Primary.TButton", command=self.export_sales_csv).pack(side=tk.RIGHT)

        table_frame = tk.Frame(container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "date", "items", "amount", "notes")
        self.tree_sales = ttk.Treeview(table_frame, columns=cols, show="headings")
        self.tree_sales.heading("id", text="Sale ID")
        self.tree_sales.heading("date", text="Date & Time")
        self.tree_sales.heading("items", text="Products Sold")
        self.tree_sales.heading("amount", text="Total Revenue (₹)")
        self.tree_sales.heading("notes", text="Customer Notes")

        self.tree_sales.column("id", width=80, anchor="center")
        self.tree_sales.column("date", width=140, anchor="w")
        self.tree_sales.column("items", width=360, anchor="w")
        self.tree_sales.column("amount", width=130, anchor="e")
        self.tree_sales.column("notes", width=200, anchor="w")

        configure_treeview_tags(self.tree_sales)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_sales.yview)
        self.tree_sales.configure(yscrollcommand=scroll_y.set)

        self.tree_sales.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_purchases_report(self):
        container = tk.Frame(self.tab_purch, bg="#f8fafc", padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        toolbar = tk.Frame(container, bg="#f8fafc")
        toolbar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(toolbar, text="From Date (YYYY-MM-DD):", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 4))
        self.purch_from_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.purch_from_var, width=12).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(toolbar, text="To Date:", font=FONT_BODY_BOLD, bg="#f8fafc").pack(side=tk.LEFT, padx=(0, 4))
        self.purch_to_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.purch_to_var, width=12).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Button(toolbar, text="🔄 Filter Purchases", style="Secondary.TButton", command=self.load_purchases_report).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="📥 Export Purchases to CSV", style="Primary.TButton", command=self.export_purchases_csv).pack(side=tk.RIGHT)

        table_frame = tk.Frame(container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        cols = ("id", "date", "supplier", "items", "amount", "ref")
        self.tree_purch = ttk.Treeview(table_frame, columns=cols, show="headings")
        self.tree_purch.heading("id", text="PO ID")
        self.tree_purch.heading("date", text="Date & Time")
        self.tree_purch.heading("supplier", text="Supplier")
        self.tree_purch.heading("items", text="Products Purchased")
        self.tree_purch.heading("amount", text="Total Paid (₹)")
        self.tree_purch.heading("ref", text="Reference #")

        self.tree_purch.column("id", width=70, anchor="center")
        self.tree_purch.column("date", width=140, anchor="w")
        self.tree_purch.column("supplier", width=180, anchor="w")
        self.tree_purch.column("items", width=300, anchor="w")
        self.tree_purch.column("amount", width=120, anchor="e")
        self.tree_purch.column("ref", width=110, anchor="w")

        configure_treeview_tags(self.tree_purch)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_purch.yview)
        self.tree_purch.configure(yscrollcommand=scroll_y.set)

        self.tree_purch.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        categories = CategoryRepository.get_all(include_counts=False)
        self.cat_lookup = {c.name: c.id for c in categories}
        self.inv_cat_combo["values"] = ["All Categories"] + [c.name for c in categories]

        self.load_inventory_report()
        self.load_low_stock_report()
        self.load_sales_report()
        self.load_purchases_report()

    def load_inventory_report(self):
        cat_name = self.inv_cat_var.get()
        cat_id = self.cat_lookup.get(cat_name, None) if cat_name != "All Categories" else None
        data = ReportService.get_inventory_report(category_id=cat_id)

        self.tree_inv.delete(*self.tree_inv.get_children())
        for idx, row in enumerate(data):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            tag = "status_out_of_stock" if row["status"] == "Out of Stock" else ("status_low_stock" if row["status"] == "Low Stock" else "status_in_stock")
            self.tree_inv.insert(
                "",
                tk.END,
                values=(
                    row["sku"], row["name"], row["category"],
                    row["current_stock"], row["minimum_stock"],
                    f"₹{row['purchase_price']:,.2f}", f"₹{row['selling_price']:,.2f}",
                    f"₹{row['cost_valuation']:,.2f}", f"₹{row['retail_valuation']:,.2f}",
                    row["status"]
                ),
                tags=(row_tag, tag)
            )

    def load_low_stock_report(self):
        data = ReportService.get_low_stock_report()
        self.tree_low.delete(*self.tree_low.get_children())
        for idx, row in enumerate(data):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            tag = "status_out_of_stock" if row["status"] == "Out of Stock" else "status_low_stock"
            self.tree_low.insert(
                "",
                tk.END,
                values=(
                    row["sku"], row["name"], row["category"],
                    row["current_stock"], row["minimum_stock"],
                    f"{row['suggested_reorder']} units",
                    f"₹{row['purchase_price']:,.2f}",
                    row["status"]
                ),
                tags=(row_tag, tag)
            )

    def load_sales_report(self):
        s_from = self.sales_from_var.get().strip() or None
        s_to = self.sales_to_var.get().strip() or None
        data = ReportService.get_sales_report(start_date=s_from, end_date=s_to)
        self.tree_sales.delete(*self.tree_sales.get_children())
        for idx, row in enumerate(data):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_sales.insert(
                "",
                tk.END,
                values=(row["sale_id"], row["sale_date"][:16], row["items_summary"], f"₹{row['total_amount']:,.2f}", row["notes"]),
                tags=(row_tag,)
            )

    def load_purchases_report(self):
        p_from = self.purch_from_var.get().strip() or None
        p_to = self.purch_to_var.get().strip() or None
        data = ReportService.get_purchases_report(start_date=p_from, end_date=p_to)
        self.tree_purch.delete(*self.tree_purch.get_children())
        for idx, row in enumerate(data):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree_purch.insert(
                "",
                tk.END,
                values=(row["purchase_id"], row["purchase_date"][:16], row["supplier"], row["items_summary"], f"₹{row['total_amount']:,.2f}", row["reference_number"]),
                tags=(row_tag,)
            )

    def _export_tree_to_csv(self, tree: ttk.Treeview, default_filename: str):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename
        )
        if not file_path:
            return

        columns = tree["columns"]
        headers = [tree.heading(col)["text"] for col in columns]

        rows = []
        for item in tree.get_children():
            rows.append(tree.item(item)["values"])

        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
            messagebox.showinfo("Export Successful", f"Report exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export CSV: {e}")

    def export_inventory_csv(self):
        self._export_tree_to_csv(self.tree_inv, f"inventory_report_{datetime.now().strftime('%Y%m%d')}.csv")

    def export_low_stock_csv(self):
        self._export_tree_to_csv(self.tree_low, f"low_stock_report_{datetime.now().strftime('%Y%m%d')}.csv")

    def export_sales_csv(self):
        self._export_tree_to_csv(self.tree_sales, f"sales_report_{datetime.now().strftime('%Y%m%d')}.csv")

    def export_purchases_csv(self):
        self._export_tree_to_csv(self.tree_purch, f"purchases_report_{datetime.now().strftime('%Y%m%d')}.csv")
