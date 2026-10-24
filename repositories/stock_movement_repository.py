import sqlite3
from database.connection import get_db_connection
from models.stock_movement import StockMovement

class StockMovementRepository:
    @staticmethod
    def add(movement: StockMovement, conn: sqlite3.Connection = None) -> int:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO stock_movements (
                    product_id, movement_type, quantity_change, 
                    previous_stock, resulting_stock, purchase_id, sale_id, reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                movement.product_id,
                movement.movement_type,
                movement.quantity_change,
                movement.previous_stock,
                movement.resulting_stock,
                movement.purchase_id,
                movement.sale_id,
                movement.reason.strip() if movement.reason else ""
            ))
            if close_conn:
                conn.commit()
            return cursor.lastrowid
        except Exception as e:
            if close_conn:
                conn.rollback()
            raise e
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def get_all(
        product_id: int = None, 
        movement_type: str = None, 
        start_date: str = None, 
        end_date: str = None, 
        limit: int = 200
    ):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            SELECT sm.*, pr.name AS product_name, pr.sku AS product_sku 
            FROM stock_movements sm
            LEFT JOIN products pr ON sm.product_id = pr.id
            WHERE 1=1
        """
        params = []
        if product_id and product_id > 0:
            sql += " AND sm.product_id = ?"
            params.append(product_id)
        if movement_type and movement_type.strip() and movement_type.strip().upper() != "ALL":
            sql += " AND UPPER(sm.movement_type) = UPPER(?)"
            params.append(movement_type.strip())
        if start_date and start_date.strip():
            sql += " AND sm.created_at >= ?"
            params.append(start_date.strip())
        if end_date and end_date.strip():
            sql += " AND sm.created_at <= ?"
            params.append(end_date.strip() + " 23:59:59")

        sql += " ORDER BY sm.created_at DESC, sm.id DESC"
        if limit:
            sql += f" LIMIT {int(limit)}"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        movements = []
        for r in rows:
            d = dict(r)
            p_name = d.pop("product_name", "")
            p_sku = d.pop("product_sku", "")
            sm = StockMovement(**d)
            sm.product_name = p_name or "Unknown Product"
            sm.product_sku = p_sku or ""
            movements.append(sm)
        return movements

    @staticmethod
    def get_recent(limit: int = 10):
        return StockMovementRepository.get_all(limit=limit)
