from datetime import datetime
from database.connection import get_db_connection
from models.product import Product
from models.purchase import Purchase, PurchaseItem
from repositories.supplier_repository import SupplierRepository
from repositories.purchase_repository import PurchaseRepository

class PurchaseService:
    @staticmethod
    def record_purchase(
        supplier_id: int,
        items: list[dict],
        purchase_date: str = None,
        reference_number: str = "",
        notes: str = ""
    ) -> int:
        """
        Record a purchase transaction atomically:
        - Validates supplier & items
        - Inserts purchase & purchase items
        - Increases stock quantities for each product
        - Records stock movement audit log
        - Commits all changes or rolls back on any error
        """
        if not supplier_id or int(supplier_id) <= 0:
            raise ValueError("A valid supplier must be selected.")

        supplier = SupplierRepository.get_by_id(int(supplier_id))
        if not supplier or not supplier.is_active:
            raise ValueError("Supplier not found or is inactive.")

        if not items or len(items) == 0:
            raise ValueError("A purchase must contain at least one item.")

        if not purchase_date or not purchase_date.strip():
            purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Prepare and validate items
        validated_items = []
        total_amount_paise = 0

        for idx, item in enumerate(items, start=1):
            prod_id = int(item.get("product_id", 0))
            if prod_id <= 0:
                raise ValueError(f"Item #{idx}: Invalid product ID.")

            try:
                qty = int(item.get("quantity", 0))
                if qty <= 0:
                    raise ValueError(f"Item #{idx}: Quantity must be greater than zero.")
            except Exception:
                raise ValueError(f"Item #{idx}: Invalid quantity value.")

            unit_price_val = item.get("unit_price", 0)
            # If unit_price is already in paise or rupees:
            if isinstance(unit_price_val, (float, str)):
                unit_price_paise = Product.rupees_to_paise(unit_price_val)
            else:
                unit_price_paise = int(unit_price_val)

            if unit_price_paise < 0:
                raise ValueError(f"Item #{idx}: Purchase price cannot be negative.")

            line_total_paise = qty * unit_price_paise
            total_amount_paise += line_total_paise

            validated_items.append({
                "product_id": prod_id,
                "quantity": qty,
                "unit_price": unit_price_paise,
                "line_total": line_total_paise
            })

        # Atomic transaction
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # 1. Insert Purchase Header
            cursor.execute("""
                INSERT INTO purchases (supplier_id, purchase_date, total_amount, reference_number, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                int(supplier_id),
                purchase_date.strip(),
                total_amount_paise,
                reference_number.strip(),
                notes.strip()
            ))
            purchase_id = cursor.lastrowid

            # 2. Process each item: insert purchase_item, update product stock, insert stock_movement
            for v_item in validated_items:
                cursor.execute("""
                    INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_price, line_total)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    purchase_id,
                    v_item["product_id"],
                    v_item["quantity"],
                    v_item["unit_price"],
                    v_item["line_total"]
                ))

                # Check product existence & fetch current stock
                cursor.execute("SELECT current_stock, is_active FROM products WHERE id = ?", (v_item["product_id"],))
                p_row = cursor.fetchone()
                if not p_row:
                    raise ValueError(f"Product ID {v_item['product_id']} not found.")

                prev_stock = p_row["current_stock"]
                new_stock = prev_stock + v_item["quantity"]

                # Update current stock
                cursor.execute("""
                    UPDATE products 
                    SET current_stock = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (new_stock, v_item["product_id"]))

                # Record stock movement
                cursor.execute("""
                    INSERT INTO stock_movements (
                        product_id, movement_type, quantity_change, 
                        previous_stock, resulting_stock, purchase_id, reason
                    )
                    VALUES (?, 'PURCHASE', ?, ?, ?, ?, ?)
                """, (
                    v_item["product_id"],
                    v_item["quantity"],
                    prev_stock,
                    new_stock,
                    purchase_id,
                    f"Purchase ID #{purchase_id}"
                ))

            conn.commit()
            return purchase_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def list_purchases(supplier_id: int = None, start_date: str = None, end_date: str = None):
        return PurchaseRepository.get_all(supplier_id=supplier_id, start_date=start_date, end_date=end_date)

    @staticmethod
    def get_purchase(purchase_id: int):
        return PurchaseRepository.get_by_id(purchase_id)
