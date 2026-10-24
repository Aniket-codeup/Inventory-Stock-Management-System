import sqlite3
from database.connection import get_db_connection
from models.stock_movement import StockMovement
from repositories.product_repository import ProductRepository
from repositories.stock_movement_repository import StockMovementRepository

class InventoryService:
    @staticmethod
    def adjust_stock(product_id: int, quantity_change: int, movement_type: str, reason: str) -> dict:
        """
        Manually adjust stock for a product (e.g., damaged goods, audit adjustment, opening stock).
        Runs inside an atomic transaction to guarantee stock integrity.
        """
        if quantity_change == 0:
            raise ValueError("Quantity change cannot be zero.")
        if not reason or not reason.strip():
            raise ValueError("A reason must be provided for stock adjustments.")

        valid_types = ["ADJUSTMENT", "OPENING_STOCK", "DAMAGE", "RETURN"]
        m_type = movement_type.strip().upper()
        if m_type not in valid_types:
            m_type = "ADJUSTMENT"

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Fetch product with row-level integrity
            cursor.execute("SELECT * FROM products WHERE id = ? AND is_active = 1", (product_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Active product with ID {product_id} does not exist.")

            previous_stock = row["current_stock"]
            resulting_stock = previous_stock + quantity_change

            if resulting_stock < 0:
                raise ValueError(
                    f"Stock adjustment would result in negative stock ({resulting_stock}). "
                    f"Current stock is {previous_stock}."
                )

            # 1. Update product stock
            cursor.execute("""
                UPDATE products 
                SET current_stock = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (resulting_stock, product_id))

            # 2. Record stock movement
            cursor.execute("""
                INSERT INTO stock_movements (
                    product_id, movement_type, quantity_change, 
                    previous_stock, resulting_stock, reason
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                product_id,
                m_type,
                quantity_change,
                previous_stock,
                resulting_stock,
                reason.strip()
            ))

            conn.commit()
            return {
                "product_id": product_id,
                "previous_stock": previous_stock,
                "quantity_change": quantity_change,
                "resulting_stock": resulting_stock
            }
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_stock_summary() -> dict:
        """Calculate high-level stock statistics for dashboard and reporting."""
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) AS total_products FROM products WHERE is_active = 1")
        total_products = cursor.fetchone()["total_products"]

        cursor.execute("SELECT COALESCE(SUM(current_stock), 0) AS total_units FROM products WHERE is_active = 1")
        total_units = cursor.fetchone()["total_units"]

        cursor.execute("""
            SELECT COUNT(*) AS low_stock_count 
            FROM products 
            WHERE is_active = 1 AND current_stock > 0 AND current_stock <= minimum_stock
        """)
        low_stock_count = cursor.fetchone()["low_stock_count"]

        cursor.execute("""
            SELECT COUNT(*) AS out_of_stock_count 
            FROM products 
            WHERE is_active = 1 AND current_stock <= 0
        """)
        out_of_stock_count = cursor.fetchone()["out_of_stock_count"]

        cursor.execute("""
            SELECT COALESCE(SUM(current_stock * purchase_price), 0) AS total_valuation_paise,
                   COALESCE(SUM(current_stock * selling_price), 0) AS total_retail_valuation_paise
            FROM products 
            WHERE is_active = 1
        """)
        val_row = cursor.fetchone()
        valuation_paise = val_row["total_valuation_paise"]
        retail_valuation_paise = val_row["total_retail_valuation_paise"]

        conn.close()

        return {
            "total_products": total_products,
            "total_units": total_units,
            "low_stock_count": low_stock_count,
            "out_of_stock_count": out_of_stock_count,
            "in_stock_count": total_products - (low_stock_count + out_of_stock_count),
            "total_valuation_paise": valuation_paise,
            "total_valuation_rupees": round(valuation_paise / 100.0, 2),
            "retail_valuation_rupees": round(retail_valuation_paise / 100.0, 2),
        }

    @staticmethod
    def get_stock_levels(search: str = None, category_id: int = None, status_filter: str = None):
        """Retrieve stock levels with filtering."""
        return ProductRepository.search(query=search, category_id=category_id, stock_status=status_filter)

    @staticmethod
    def get_movements(product_id: int = None, movement_type: str = None, limit: int = 200):
        """Retrieve stock movement history."""
        return StockMovementRepository.get_all(product_id=product_id, movement_type=movement_type, limit=limit)
