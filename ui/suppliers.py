import tkinter as tk
from tkinter import ttk, messagebox
from models.supplier import Supplier
from repositories.supplier_repository import SupplierRepository
from services.supplier_service import SupplierService
from ui.styles import (
    COLOR_BORDER, COLOR_PRIMARY, COLOR_DANGER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, FONT_TITLE, FONT_HEADING, FONT_BODY,
    FONT_BODY_BOLD, FONT_SMALL, configure_treeview_tags
)

class SuppliersView(ttk.Frame):
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

        title_lbl = tk.Label(header_frame, text="Supplier Directory", font=FONT_TITLE, bg="#ffffff", fg=COLOR_TEXT_PRIMARY)
        title_lbl.pack(anchor="w")
        sub_lbl = tk.Label(header_frame, text="Maintain supplier contacts and vendor profiles for inventory purchases", font=FONT_SMALL, bg="#ffffff", fg=COLOR_TEXT_SECONDARY)
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Toolbar
        toolbar = tk.Frame(self, bg="#f8fafc")
        toolbar.pack(fill=tk.X, padx=20, pady=(0, 12))

        tk.Label(toolbar, text="🔍 Search Suppliers:", font=FONT_BODY_BOLD, bg="#f8fafc", fg=COLOR_TEXT_PRIMARY).pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 15))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh())

        ttk.Button(toolbar, text="➕ Add Supplier", style="Primary.TButton", command=self.open_add_dialog).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(toolbar, text="✏️ Edit Selected", style="Secondary.TButton", command=self.open_edit_dialog).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(toolbar, text="🚫 Deactivate", style="Danger.TButton", command=self.deactivate_selected).pack(side=tk.RIGHT)

        # Table Frame
        table_frame = tk.Frame(self, bg="#ffffff", highlightbackground=COLOR_BORDER, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        cols = ("id", "name", "contact", "phone", "email", "address")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Supplier / Vendor Company")
        self.tree.heading("contact", text="Contact Person")
        self.tree.heading("phone", text="Phone Number")
        self.tree.heading("email", text="Email Address")
        self.tree.heading("address", text="Physical Address")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("name", width=200, anchor="w")
        self.tree.column("contact", width=140, anchor="w")
        self.tree.column("phone", width=130, anchor="w")
        self.tree.column("email", width=170, anchor="w")
        self.tree.column("address", width=220, anchor="w")

        configure_treeview_tags(self.tree)

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<Double-1>", lambda e: self.open_edit_dialog())

    def refresh(self):
        query = self.search_var.get().strip()
        suppliers = SupplierService.list_suppliers(query=query)
        self.tree.delete(*self.tree.get_children())
        for idx, s in enumerate(suppliers):
            row_tag = "evenrow" if idx % 2 == 0 else "oddrow"
            self.tree.insert(
                "",
                tk.END,
                values=(s.id, s.name, s.contact_person, s.phone, s.email, s.address),
                tags=(row_tag,)
            )

    def _get_selected_supplier_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a supplier from the table first.")
            return None
        return int(self.tree.item(selected[0])["values"][0])

    def open_add_dialog(self):
        SupplierFormDialog(self, title="Add New Supplier", on_save=self.refresh)

    def open_edit_dialog(self):
        sup_id = self._get_selected_supplier_id()
        if sup_id:
            supplier = SupplierService.get_supplier(sup_id)
            if supplier:
                SupplierFormDialog(self, title="Edit Supplier", supplier=supplier, on_save=self.refresh)

    def deactivate_selected(self):
        sup_id = self._get_selected_supplier_id()
        if not sup_id:
            return
        supplier = SupplierService.get_supplier(sup_id)
        if not supplier:
            return

        confirm = messagebox.askyesno(
            "Confirm Deactivation",
            f"Are you sure you want to deactivate supplier '{supplier.name}'?\n\n"
            "Historical purchase orders will remain associated with this supplier."
        )
        if confirm:
            try:
                SupplierService.deactivate_supplier(sup_id)
                messagebox.showinfo("Success", f"Supplier '{supplier.name}' deactivated successfully.")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to deactivate supplier: {e}")

class SupplierFormDialog(tk.Toplevel):
    def __init__(self, parent, title: str, supplier: Supplier = None, on_save=None):
        super().__init__(parent)
        self.parent = parent
        self.supplier = supplier
        self.on_save = on_save

        self.title(title)
        self.geometry("480x500")
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

        form_grid = tk.Frame(pad_frame, bg="#ffffff")
        form_grid.pack(fill=tk.X)
        form_grid.grid_columnconfigure(1, weight=1)

        row = 0
        # Company Name
        tk.Label(form_grid, text="Supplier Company *:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        self.name_var = tk.StringVar(value=self.supplier.name if self.supplier else "")
        self.name_entry = ttk.Entry(form_grid, textvariable=self.name_var)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Contact Person
        tk.Label(form_grid, text="Contact Person:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        self.contact_var = tk.StringVar(value=self.supplier.contact_person if self.supplier else "")
        self.contact_entry = ttk.Entry(form_grid, textvariable=self.contact_var)
        self.contact_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Phone
        tk.Label(form_grid, text="Phone Number:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        self.phone_var = tk.StringVar(value=self.supplier.phone if self.supplier else "")
        self.phone_entry = ttk.Entry(form_grid, textvariable=self.phone_var)
        self.phone_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Email
        tk.Label(form_grid, text="Email Address:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="w", pady=6)
        self.email_var = tk.StringVar(value=self.supplier.email if self.supplier else "")
        self.email_entry = ttk.Entry(form_grid, textvariable=self.email_var)
        self.email_entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Address
        tk.Label(form_grid, text="Address:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="nw", pady=6)
        self.address_text = tk.Text(form_grid, height=2, width=25, font=FONT_BODY)
        if self.supplier and self.supplier.address:
            self.address_text.insert("1.0", self.supplier.address)
        self.address_text.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        row += 1
        # Notes
        tk.Label(form_grid, text="Notes:", font=FONT_BODY_BOLD, bg="#ffffff").grid(row=row, column=0, sticky="nw", pady=6)
        self.notes_text = tk.Text(form_grid, height=2, width=25, font=FONT_BODY)
        if self.supplier and self.supplier.notes:
            self.notes_text.insert("1.0", self.supplier.notes)
        self.notes_text.grid(row=row, column=1, sticky="ew", pady=6, padx=(10, 0))

        # Bottom Action Buttons
        btn_bar = tk.Frame(pad_frame, bg="#ffffff")
        btn_bar.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(btn_bar, text="Cancel", style="Secondary.TButton", command=self.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(btn_bar, text="Save Supplier", style="Primary.TButton", command=self.save_supplier).pack(side=tk.RIGHT)

    def save_supplier(self):
        name = self.name_var.get().strip()
        contact = self.contact_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        address = self.address_text.get("1.0", tk.END).strip()
        notes = self.notes_text.get("1.0", tk.END).strip()

        try:
            if not self.supplier:
                SupplierService.create_supplier(
                    name=name,
                    contact_person=contact,
                    phone=phone,
                    email=email,
                    address=address,
                    notes=notes
                )
                messagebox.showinfo("Success", f"Supplier '{name}' created successfully.")
            else:
                SupplierService.update_supplier(
                    supplier_id=self.supplier.id,
                    name=name,
                    contact_person=contact,
                    phone=phone,
                    email=email,
                    address=address,
                    notes=notes
                )
                messagebox.showinfo("Success", f"Supplier '{name}' updated successfully.")

            if self.on_save:
                self.on_save()
            self.destroy()
        except ValueError as ex:
            messagebox.showerror("Validation Error", str(ex))
        except Exception as ex:
            messagebox.showerror("Database Error", f"An unexpected error occurred: {ex}")
