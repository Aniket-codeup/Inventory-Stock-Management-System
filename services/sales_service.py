from datetime import datetime
from database.connection import get_db_connection
from models.product import Product
from models.sale import Sale, SaleItem
from repositories.sale_repository import SaleRepository

class SalesService:
    @staticmethod
    def record_sale(
        items: list[dict],
        sale_date: str = None,
        notes: str = ""
    ) -> int:
        """
        Record a sales transaction atomically:
        - Validates items
        - Enforces stock availability (cannot sell more than current_stock)
        - Rejects inactive products
        - Inserts sale and sale items
        - Decreases stock quantities
        - Records stock movement audit log
        - Commits all changes or rolls back on failure
        """
        if not items or len(items) == 0:
            raise ValueError("A sale must contain at least one item.")

        if not sale_date or not sale_date.strip():
            sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        validated_items = []
        total_amount_paise = 0

        # Validate items structure
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
            if isinstance(unit_price_val, (float, str)):
                unit_price_paise = Product.rupees_to_paise(unit_price_val)
            else:
                unit_price_paise = int(unit_price_val)

            if unit_price_paise < 0:
                raise ValueError(f"Item #{idx}: Selling price cannot be negative.")

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

            # Pre-validate stock levels and active status with row locking / checks
            for v_item in validated_items:
                cursor.execute("""
                    SELECT id, name, sku, current_stock, is_active 
                    FROM products 
                    WHERE id = ?
                """, (v_item["product_id"],))
                p_row = cursor.fetchone()
                if not p_row:
                    raise ValueError(f"Product ID {v_item['product_id']} not found.")
                if not p_row["is_active"]:
                    raise ValueError(f"Cannot sell inactive product '{p_row['name']}' (SKU: {p_row['sku']}).")

                avail_stock = p_row["current_stock"]
                req_qty = v_item["quantity"]
                if req_qty > avail_stock:
                    raise ValueError(
                        f"Insufficient stock for '{p_row['name']}' (SKU: {p_row['sku']}). "
                        f"Available: {avail_stock}, Requested: {req_qty}."
                    )
                v_item["product_name"] = p_row["name"]
                v_item["prev_stock"] = avail_stock

            # 1. Insert Sale Header
            cursor.execute("""
                INSERT INTO sales (sale_date, total_amount, notes)
                VALUES (?, ?, ?)
            """, (
                sale_date.strip(),
                total_amount_paise,
                notes.strip()
            ))
            sale_id = cursor.lastrowid

            # 2. Process items
            for v_item in validated_items:
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, line_total)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    sale_id,
                    v_item["product_id"],
                    v_item["quantity"],
                    v_item["unit_price"],
                    v_item["line_total"]
                ))

                prev_stock = v_item["prev_stock"]
                new_stock = prev_stock - v_item["quantity"]

                # Update product current_stock
                cursor.execute("""
                    UPDATE products 
                    SET current_stock = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (new_stock, v_item["product_id"]))

                # Record stock movement
                cursor.execute("""
                    INSERT INTO stock_movements (
                        product_id, movement_type, quantity_change, 
                        previous_stock, resulting_stock, sale_id, reason
                    )
                    VALUES (?, 'SALE', ?, ?, ?, ?, ?)
                """, (
                    v_item["product_id"],
                    -v_item["quantity"],
                    prev_stock,
                    new_stock,
                    sale_id,
                    f"Sale ID #{sale_id}"
                ))

            conn.commit()
            return sale_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def list_sales(start_date: str = None, end_date: str = None):
        return SaleRepository.get_all(start_date=start_date, end_date=end_date)

    @staticmethod
    def get_sale(sale_id: int):
        return SaleRepository.get_by_id(sale_id)
