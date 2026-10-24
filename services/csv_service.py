import csv
import os
from decimal import Decimal
from models.product import Product
from repositories.product_repository import ProductRepository
from repositories.category_repository import CategoryRepository
from repositories.purchase_repository import PurchaseRepository
from repositories.sale_repository import SaleRepository
from repositories.stock_movement_repository import StockMovementRepository
from services.product_service import ProductService

class CSVService:
    @staticmethod
    def export_products(file_path: str, category_id: int = None) -> int:
        """
        Export products to a CSV file.
        Returns the number of exported rows.
        """
        products = ProductRepository.search(category_id=category_id)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        fieldnames = [
            "SKU",
            "Product Name",
            "Category",
            "Description",
            "Purchase Price (INR)",
            "Selling Price (INR)",
            "Current Stock",
            "Minimum Stock",
            "Status"
        ]

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in products:
                writer.writerow({
                    "SKU": p.sku,
                    "Product Name": p.name,
                    "Category": p.category_name,
                    "Description": p.description,
                    "Purchase Price (INR)": f"{p.purchase_price_rupees:.2f}",
                    "Selling Price (INR)": f"{p.selling_price_rupees:.2f}",
                    "Current Stock": p.current_stock,
                    "Minimum Stock": p.minimum_stock,
                    "Status": p.stock_status
                })
        return len(products)

    @staticmethod
    def import_products(file_path: str) -> dict:
        """
        Import products from a CSV file.
        Enforces validation rules:
        - Required headers: SKU, Product Name, Category, Purchase Price, Selling Price, Minimum Stock
        - Validates numeric prices and non-negative stock
        - Checks for duplicate SKUs within the file and active database
        - Creates categories on the fly if they don't exist
        - Records initial stock movements for positive opening stock
        - Returns a detailed summary: { total, imported, skipped, errors }
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        summary = {
            "total": 0,
            "imported": 0,
            "skipped": 0,
            "errors": []
        }

        with open(file_path, mode="r", newline="", encoding="utf-8-sig") as f:
            # Check for empty file
            first_line = f.readline()
            if not first_line.strip():
                raise ValueError("The provided CSV file is empty.")
            f.seek(0)

            reader = csv.reader(f)
            raw_headers = next(reader, None)
            if not raw_headers:
                raise ValueError("Missing CSV header row.")

            # Normalize header mapping (case-insensitive and trimmed)
            header_map = {}
            for idx, h in enumerate(raw_headers):
                normalized = h.strip().lower()
                header_map[normalized] = idx

            # Helper to find column by aliases
            def get_col_val(row_list, aliases, default=""):
                for a in aliases:
                    if a in header_map:
                        idx = header_map[a]
                        if idx < len(row_list):
                            return row_list[idx].strip()
                return default

            sku_aliases = ["sku", "product sku", "item code"]
            name_aliases = ["product name", "name", "item name", "title"]
            cat_aliases = ["category", "category name"]
            desc_aliases = ["description", "desc"]
            purch_aliases = ["purchase price (inr)", "purchase price", "cost price", "purchase_price", "cost"]
            sell_aliases = ["selling price (inr)", "selling price", "retail price", "selling_price", "price"]
            stock_aliases = ["current stock", "stock", "quantity", "initial stock", "current_stock"]
            min_stock_aliases = ["minimum stock", "min stock", "reorder level", "minimum_stock"]

            # Validate that minimum required columns exist
            has_sku = any(a in header_map for a in sku_aliases)
            has_name = any(a in header_map for a in name_aliases)
            has_purch = any(a in header_map for a in purch_aliases)
            has_sell = any(a in header_map for a in sell_aliases)

            if not (has_sku and has_name and has_purch and has_sell):
                missing = []
                if not has_sku: missing.append("SKU")
                if not has_name: missing.append("Product Name")
                if not has_purch: missing.append("Purchase Price")
                if not has_sell: missing.append("Selling Price")
                raise ValueError(f"Missing required CSV column(s): {', '.join(missing)}")

            seen_skus_in_file = set()

            # Process each row
            for row_num, row in enumerate(reader, start=2):
                if not row or not any(field.strip() for field in row):
                    continue  # Skip blank lines

                summary["total"] += 1
                sku = get_col_val(row, sku_aliases)
                name = get_col_val(row, name_aliases)
                category_name = get_col_val(row, cat_aliases, default="General")
                description = get_col_val(row, desc_aliases, default="")
                purch_str = get_col_val(row, purch_aliases)
                sell_str = get_col_val(row, sell_aliases)
                stock_str = get_col_val(row, stock_aliases, default="0")
                min_stock_str = get_col_val(row, min_stock_aliases, default="5")

                # Validation checks
                if not sku:
                    summary["skipped"] += 1
                    summary["errors"].append(f"Row {row_num}: SKU cannot be empty.")
                    continue

                sku_upper = sku.upper()
                if sku_upper in seen_skus_in_file:
                    summary["skipped"] += 1
                    summary["errors"].append(f"Row {row_num}: Duplicate SKU '{sku}' found within file.")
                    continue
                seen_skus_in_file.add(sku_upper)

                if not name:
                    summary["skipped"] += 1
                    summary["errors"].append(f"Row {row_num}: Product Name cannot be empty.")
                    continue

                try:
                    # Clean currency symbols if user included ₹ or $
                    clean_purch = purch_str.replace("₹", "").replace("$", "").replace(",", "").strip()
                    clean_sell = sell_str.replace("₹", "").replace("$", "").replace(",", "").strip()
                    purch_val = float(clean_purch)
                    sell_val = float(clean_sell)
                    if purch_val < 0 or sell_val < 0:
                        raise ValueError()
                except Exception:
                    summary["skipped"] += 1
                    summary["errors"].append(f"Row {row_num}: Invalid price values ('{purch_str}', '{sell_str}').")
                    continue

                try:
                    current_stock = int(float(stock_str)) if stock_str else 0
                    min_stock = int(float(min_stock_str)) if min_stock_str else 0
                    if current_stock < 0 or min_stock < 0:
                        raise ValueError()
                except Exception:
                    summary["skipped"] += 1
                    summary["errors"].append(f"Row {row_num}: Stock quantities must be non-negative integers.")
                    continue

                # Resolve or auto-create category
                category = CategoryRepository.get_by_name(category_name)
                if not category:
                    try:
                        cat_id = CategoryRepository.add(category_name)
                    except Exception:
                        cat_id = 1
                else:
                    cat_id = category.id

                # Attempt creation
                try:
                    ProductService.create_product(
                        sku=sku,
                        name=name,
                        category_id=cat_id,
                        purchase_price_rupees=purch_val,
                        selling_price_rupees=sell_val,
                        minimum_stock=min_stock,
                        description=description,
                        initial_stock=current_stock
                    )
                    summary["imported"] += 1
                except Exception as ex:
                    summary["skipped"] += 1
                    summary["errors"].append(f"Row {row_num} (SKU: {sku}): {str(ex)}")

        return summary

    @staticmethod
    def export_sales(file_path: str, start_date: str = None, end_date: str = None) -> int:
        """Export sales transactions to a CSV file."""
        sales = SaleRepository.get_all(start_date=start_date, end_date=end_date)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        fieldnames = ["Sale ID", "Date", "Total Amount (INR)", "Items Summary", "Notes"]
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for s in sales:
                detailed = SaleRepository.get_by_id(s.id)
                summary_str = "; ".join([f"{it.product_name} x {it.quantity} @ ₹{it.unit_price_rupees:.2f}" for it in detailed.items])
                writer.writerow({
                    "Sale ID": s.id,
                    "Date": s.sale_date,
                    "Total Amount (INR)": f"{s.total_amount_rupees:.2f}",
                    "Items Summary": summary_str,
                    "Notes": s.notes or ""
                })
        return len(sales)

    @staticmethod
    def export_purchases(file_path: str, start_date: str = None, end_date: str = None) -> int:
        """Export purchase transactions to a CSV file."""
        purchases = PurchaseRepository.get_all(start_date=start_date, end_date=end_date)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        fieldnames = ["Purchase ID", "Date", "Supplier", "Reference No", "Total Amount (INR)", "Items Summary", "Notes"]
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in purchases:
                detailed = PurchaseRepository.get_by_id(p.id)
                summary_str = "; ".join([f"{it.product_name} x {it.quantity} @ ₹{it.unit_price_rupees:.2f}" for it in detailed.items])
                writer.writerow({
                    "Purchase ID": p.id,
                    "Date": p.purchase_date,
                    "Supplier": p.supplier_name,
                    "Reference No": p.reference_number or "",
                    "Total Amount (INR)": f"{p.total_amount_rupees:.2f}",
                    "Items Summary": summary_str,
                    "Notes": p.notes or ""
                })
        return len(purchases)

    @staticmethod
    def export_stock_movements(file_path: str, start_date: str = None, end_date: str = None) -> int:
        """Export stock movements audit history to a CSV file."""
        movements = StockMovementRepository.get_all(start_date=start_date, end_date=end_date, limit=1000)
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        fieldnames = [
            "Movement ID",
            "Timestamp",
            "SKU",
            "Product Name",
            "Movement Type",
            "Quantity Change",
            "Previous Stock",
            "Resulting Stock",
            "Reference / Reason"
        ]
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for m in movements:
                ref = f"Purchase #{m.purchase_id}" if m.purchase_id else (f"Sale #{m.sale_id}" if m.sale_id else m.reason)
                writer.writerow({
                    "Movement ID": m.id,
                    "Timestamp": m.created_at,
                    "SKU": m.product_sku,
                    "Product Name": m.product_name,
                    "Movement Type": m.movement_type,
                    "Quantity Change": m.quantity_change,
                    "Previous Stock": m.previous_stock,
                    "Resulting Stock": m.resulting_stock,
                    "Reference / Reason": ref
                })
        return len(movements)

    @staticmethod
    def generate_sample_csv(file_path: str):
        """Create a template CSV file for users to easily fill and import."""
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        fieldnames = [
            "SKU",
            "Product Name",
            "Category",
            "Description",
            "Purchase Price (INR)",
            "Selling Price (INR)",
            "Current Stock",
            "Minimum Stock"
        ]
        sample_rows = [
            {
                "SKU": "STAT-PEN-01",
                "Product Name": "Gel Pen (Blue)",
                "Category": "Stationery",
                "Description": "Smooth flow 0.7mm blue gel pen",
                "Purchase Price (INR)": "15.00",
                "Selling Price (INR)": "25.00",
                "Current Stock": "50",
                "Minimum Stock": "10"
            },
            {
                "SKU": "ELEC-USB-02",
                "Product Name": "USB-C Fast Charging Cable",
                "Category": "Electronics",
                "Description": "1.2m nylon braided cable",
                "Purchase Price (INR)": "120.00",
                "Selling Price (INR)": "250.00",
                "Current Stock": "20",
                "Minimum Stock": "5"
            },
            {
                "SKU": "GROC-TEA-03",
                "Product Name": "Assam Green Tea 250g",
                "Category": "Groceries",
                "Description": "Organic whole leaf green tea",
                "Purchase Price (INR)": "180.00",
                "Selling Price (INR)": "260.00",
                "Current Stock": "15",
                "Minimum Stock": "5"
            }
        ]
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_rows)
