import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from repositories.category_repository import CategoryRepository
from ui.styles import (
    COLOR_BORDER, COLOR_PRIMARY, COLOR_DANGER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, configure_treeview_tags
)

class CategoriesView(ttk.Frame):
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

        title_lbl = tk.Label(header_frame, text="Category Management", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(header_frame, text="Organize your product catalog into meaningful business departments", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Action Toolbar
        toolbar = tk.Frame(self, bg="#f8fafc")
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 12))

        # Add Category Input inline
        tk.Label(toolbar, text="New Category Name:", font=FONT_BODY_BOLD, bg="#f8fafc", fg=COLOR_TEXT_PRIMARY).pack(side=tk.LEFT, padx=(0, 6))
        self.new_cat_var = tk.StringVar()
        self.new_cat_entry = ttk.Entry(toolbar, textvariable=self.new_cat_var, width=25)
        self.new_cat_entry.pack(side=tk.LEFT, padx=(0, 8))
        self.new_cat_entry.bind("<Return>", lambda e: self.add_category())

        ttk.Button(toolbar, text="➕ Add Category", style="Primary.TButton", command=self.add_category).pack(side=tk.LEFT, padx=(0, 15))

        # Action buttons on right
        ttk.Button(toolbar, text="✏️ Rename Selected", style="Secondary.TButton", command=self.rename_selected).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(toolbar, text="🚫 Deactivate Category", style="Danger.TButton", command=self.deactivate_selected).pack(side=tk.RIGHT)

        # Categories Table Frame
        table_frame = tk.Frame(self, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        cols = ("id", "name", "product_count", "created_at")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="Category ID")
        self.tree.heading("name", text="Category Name")
        self.tree.heading("product_count", text="Active Products Linked")
        self.tree.heading("created_at", text="Creation Date")

        self.tree.column("id", width=90, anchor="center")
        self.tree.column("name", width=300, anchor="w")
        self.tree.column("product_count", width=160, anchor="center")
        self.tree.column("created_at", width=200, anchor="w")

        configure_treeview_tags(self.tree)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        categories = CategoryRepository.get_all(include_counts=True)
        for idx, c in enumerate(categories):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                tk.END,
                values=(c.id, c.name, f"{c.product_count} products", c.created_at[:19] if c.created_at else ""),
                tags=(row_tag,)
            )

    def _get_selected_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a category from the table first.")
            return None, None
        vals = self.tree.item(selected[0])["values"]
        return int(vals[0]), str(vals[1])

    def add_category(self):
        name = self.new_cat_var.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Category name cannot be empty.")
            return

        existing = CategoryRepository.get_by_name(name)
        if existing:
            messagebox.showerror("Validation Error", f"A category named '{name}' already exists.")
            return

        try:
            CategoryRepository.add(name)
            self.new_cat_var.set("")
            self.refresh()
            messagebox.showinfo("Success", f"Category '{name}' created successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create category: {e}")

    def rename_selected(self):
        cat_id, old_name = self._get_selected_category()
        if not cat_id:
            return

        new_name = simpledialog.askstring("Rename Category", f"Enter new name for category '{old_name}':", initialvalue=old_name)
        if new_name is not None:
            new_name = new_name.strip()
            if not new_name:
                messagebox.showerror("Validation Error", "Category name cannot be empty.")
                return
            if new_name.lower() == old_name.lower():
                return
            existing = CategoryRepository.get_by_name(new_name)
            if existing and existing.id != cat_id:
                messagebox.showerror("Validation Error", f"A category named '{new_name}' already exists.")
                return
            try:
                CategoryRepository.update(cat_id, new_name)
                self.refresh()
                messagebox.showinfo("Success", "Category renamed successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to rename category: {e}")

    def deactivate_selected(self):
        cat_id, cat_name = self._get_selected_category()
        if not cat_id:
            return

        # PRD 4.3 rule: Check if category is referenced by active products
        if CategoryRepository.has_active_products(cat_id):
            messagebox.showerror(
                "Cannot Deactivate Category",
                f"Category '{cat_name}' has active products assigned to it.\n\n"
                "Please reassign or deactivate the linked products before deactivating this category."
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Deactivation",
            f"Are you sure you want to deactivate category '{cat_name}'?"
        )
        if confirm:
            try:
                CategoryRepository.deactivate(cat_id)
                self.refresh()
                messagebox.showinfo("Success", f"Category '{cat_name}' deactivated successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to deactivate category: {e}")
