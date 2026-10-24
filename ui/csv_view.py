import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import csv
from datetime import datetime
from services.csv_service import CSVService
from ui.styles import (
    COLOR_BORDER, COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, FONT_STAT_NUM, configure_treeview_tags
)

class CSVView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.selected_file_path = None
        self.pack(fill=tk.BOTH, expand=True)

        self.create_widgets()

    def create_widgets(self):
        # Header banner
        header_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=16, highlightbackground=COLOR_BORDER, highlightthickness=1)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 15))

        title_lbl = tk.Label(header_frame, text="CSV Data Interchange & Migration", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(header_frame, text="Import product catalogs and export transactional ledgers using standard CSV files", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        self.tab_import = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_import, text="📥 Import Products from CSV")

        self.tab_export = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_export, text="📤 Export Data to CSV")

        self._build_import_tab()
        self._build_export_tab()

    def _build_import_tab(self):
        container = tk.Frame(self.tab_import, bg="#f8fafc", padx=15, pady=15)
        container.pack(fill=tk.BOTH, expand=True)

        # Instructions / Template Card
        inst_card = tk.Frame(container, bg="#ffffff", padx=16, pady=14, highlightbackground=COLOR_BORDER, highlightthickness=1)
        inst_card.pack(fill=tk.X, pady=(0, 15))

        tk.Label(inst_card, text="Product CSV Import Guidelines", font=FONT_HEADING, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(anchor="w")
        guidelines_text = (
            "• Required columns: SKU, Product Name, Category, Purchase Price, Selling Price\n"
            "• Optional columns: Current Stock (opening stock), Minimum Stock, Description\n"
            "• New categories found in the CSV will be automatically registered in the system.\n"
            "• Duplicate SKUs will be safely identified and reported without crashing the import."
        )
        tk.Label(inst_card, text=guidelines_text, font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY, justify=tk.LEFT).pack(anchor="w", pady=(4, 10))

        ttk.Button(inst_card, text="📄 Download Sample CSV Template", style="Secondary.TButton", command=self.download_template).pack(anchor="w")

        # File Selector Card
        select_card = tk.Frame(container, bg="#ffffff", padx=16, pady=14, highlightbackground=COLOR_BORDER, highlightthickness=1)
        select_card.pack(fill=tk.X, pady=(0, 15))

        tk.Label(select_card, text="Select CSV File to Import:", font=FONT_BODY_BOLD, bg="#ffffff").pack(side=tk.LEFT, padx=(0, 10))
        self.file_lbl = tk.Label(select_card, text="No file selected", font=FONT_BODY, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        self.file_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))

        ttk.Button(select_card, text="📂 Browse CSV File...", style="Secondary.TButton", command=self.browse_csv).pack(side=tk.LEFT, padx=(0, 10))
        self.import_btn = ttk.Button(select_card, text="🚀 Process Import", style="Primary.TButton", state="disabled", command=self.run_import)
        self.import_btn.pack(side=tk.LEFT)

        # Preview Table Card
        preview_card = tk.Frame(container, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        preview_card.pack(fill=tk.BOTH, expand=True)

        prev_header = tk.Frame(preview_card, bg="#ffffff", padx=15, pady=10)
        prev_header.pack(fill=tk.X)
        tk.Label(prev_header, text="CSV File Data Preview", font=FONT_HEADING, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(side=tk.LEFT)

        self.tree_preview = ttk.Treeview(preview_card, show="headings")
        configure_treeview_tags(self.tree_preview)

        scroll_y = ttk.Scrollbar(preview_card, orient="vertical", command=self.tree_preview.yview)
        scroll_x = ttk.Scrollbar(preview_card, orient="horizontal", command=self.tree_preview.xview)
        self.tree_preview.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_export_tab(self):
        container = tk.Frame(self.tab_export, bg="#f8fafc", padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        grid = tk.Frame(container, bg="#f8fafc")
        grid.pack(fill=tk.X)
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        # 1. Products Export Card
        c1 = self._create_export_action_card(
            grid, 0, 0,
            title="📦 Products Catalog Export",
            desc="Export active products including SKUs, category links, purchase/selling prices, and stock balances.",
            btn_text="Export Products CSV",
            command=self.export_products
        )

        # 2. Sales Export Card
        c2 = self._create_export_action_card(
            grid, 0, 1,
            title="🛒 Sales Transactions Register",
            desc="Export complete sales transaction log with customer references, item quantities, and revenues.",
            btn_text="Export Sales CSV",
            command=self.export_sales
        )

        # 3. Purchases Export Card
        c3 = self._create_export_action_card(
            grid, 1, 0,
            title="📥 Purchase Orders Register",
            desc="Export complete procurement history with vendor details, purchase orders, and expenditure totals.",
            btn_text="Export Purchases CSV",
            command=self.export_purchases
        )

        # 4. Stock Movements Export Card
        c4 = self._create_export_action_card(
            grid, 1, 1,
            title="🔄 Stock Movements Audit Trail",
            desc="Export complete traceable history of stock increases, decreases, sales, deliveries, and adjustments.",
            btn_text="Export Movements CSV",
            command=self.export_movements
        )

    def _create_export_action_card(self, parent, row, col, title, desc, btn_text, command):
        card = tk.Frame(parent, bg="#ffffff", padx=20, pady=18, highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        tk.Label(card, text=title, font=FONT_HEADING, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(anchor="w")
        tk.Label(card, text=desc, font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY, wraplength=340, justify=tk.LEFT).pack(anchor="w", pady=(6, 16))

        ttk.Button(card, text=btn_text, style="Primary.TButton", command=command).pack(anchor="w")
        return card

    def download_template(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="products_import_template.csv"
        )
        if not file_path:
            return
        try:
            CSVService.generate_sample_csv(file_path)
            messagebox.showinfo("Template Saved", f"Sample CSV template successfully saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {e}")

    def browse_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        self.selected_file_path = file_path
        self.file_lbl.config(text=os.path.basename(file_path), fg=COLOR_PRIMARY)
        self.import_btn.config(state="normal")
        self._load_preview(file_path)

    def _load_preview(self, file_path):
        self.tree_preview.delete(*self.tree_preview.get_children())
        try:
            with open(file_path, mode="r", newline="", encoding="utf-8-sig") as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                if not headers:
                    messagebox.showwarning("Empty File", "The selected file is empty.")
                    return

                self.tree_preview["columns"] = headers
                for h in headers:
                    self.tree_preview.heading(h, text=h)
                    self.tree_preview.column(h, width=120, anchor="w")

                for idx, row in enumerate(reader):
                    if idx >= 12:  # Preview first 12 rows
                        break
                    row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
                    self.tree_preview.insert("", tk.END, values=row, tags=(row_tag,))
        except Exception as e:
            messagebox.showerror("Read Error", f"Failed to read file preview: {e}")

    def run_import(self):
        if not self.selected_file_path:
            return

        confirm = messagebox.askyesno(
            "Confirm Import",
            f"Are you ready to import products from:\n{os.path.basename(self.selected_file_path)}?\n\n"
            "Valid products will be added to the database with opening inventory tracked."
        )
        if not confirm:
            return

        try:
            summary = CSVService.import_products(self.selected_file_path)
            ImportResultDialog(self, summary)
            self.app.refresh_dashboard()
        except Exception as e:
            messagebox.showerror("Import Error", f"Import process encountered an error: {e}")

    def export_products(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"products_export_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not file_path:
            return
        try:
            count = CSVService.export_products(file_path)
            messagebox.showinfo("Export Successful", f"Exported {count} product(s) to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def export_sales(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"sales_ledger_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not file_path:
            return
        try:
            count = CSVService.export_sales(file_path)
            messagebox.showinfo("Export Successful", f"Exported {count} sale transaction(s) to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def export_purchases(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"purchases_register_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not file_path:
            return
        try:
            count = CSVService.export_purchases(file_path)
            messagebox.showinfo("Export Successful", f"Exported {count} purchase order(s) to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    def export_movements(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"stock_movements_audit_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if not file_path:
            return
        try:
            count = CSVService.export_stock_movements(file_path)
            messagebox.showinfo("Export Successful", f"Exported {count} stock movement audit record(s) to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

class ImportResultDialog(tk.Toplevel):
    def __init__(self, parent, summary):
        super().__init__(parent)
        self.title("CSV Import Results Summary")
        self.geometry("540x440")
        self.configure(bg="#ffffff")
        self.transient(parent)
        self.grab_set()

        pad = tk.Frame(self, bg="#ffffff", padx=22, pady=18)
        pad.pack(fill=tk.BOTH, expand=True)

        tk.Label(pad, text="Import Execution Summary", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY).pack(anchor="w")

        # Stats Cards
        stats_frame = tk.Frame(pad, bg="#ffffff", pady=10)
        stats_frame.pack(fill=tk.X)

        self._stat_box(stats_frame, "Total Rows Analyzed", str(summary["total"]), COLOR_PRIMARY).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))
        self._stat_box(stats_frame, "Successfully Imported", str(summary["imported"]), COLOR_SUCCESS).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=3)
        self._stat_box(stats_frame, "Skipped / Rejected", str(summary["skipped"]), COLOR_DANGER if summary["skipped"] > 0 else COLOR_TEXT_SECONDARY).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(6, 0))

        # Errors list
        tk.Label(pad, text="Error Log / Skipped Reasons:", font=FONT_BODY_BOLD, bg="#ffffff").pack(anchor="w", pady=(10, 4))
        err_box = tk.Text(pad, height=8, font=FONT_SMALL, bg="#f8fafc", relief="solid", borderwidth=1)
        err_box.pack(fill=tk.BOTH, expand=True)

        if summary["errors"]:
            for err in summary["errors"]:
                err_box.insert(tk.END, f"• {err}\n")
        else:
            err_box.insert(tk.END, "✓ All rows passed validation and were imported with zero errors!")
        err_box.config(state="disabled")

        ttk.Button(pad, text="Close", style="Primary.TButton", command=self.destroy).pack(anchor="e", pady=(15, 0))

    def _stat_box(self, parent, title, val, color):
        box = tk.Frame(parent, bg="#f8fafc", padx=10, pady=8, highlightbackground=COLOR_BORDER, highlightthickness=1)
        tk.Label(box, text=title, font=("Segoe UI", 8), bg="#f8fafc", fg=COLOR_TEXT_SECONDARY).pack(anchor="w")
        tk.Label(box, text=val, font=FONT_STAT_NUM, bg="#f8fafc", fg=color).pack(anchor="w")
        return box
