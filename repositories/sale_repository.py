import sqlite3
from database.connection import get_db_connection
from models.sale import Sale, SaleItem

class SaleRepository:
    @staticmethod
    def create(sale: Sale, items: list[SaleItem], conn: sqlite3.Connection = None) -> int:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO sales (sale_date, total_amount, notes)
                VALUES (?, ?, ?)
            """, (
                sale.sale_date,
                sale.total_amount,
                sale.notes.strip() if sale.notes else ""
            ))
            sale_id = cursor.lastrowid

            for item in items:
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, line_total)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    sale_id,
                    item.product_id,
                    item.quantity,
                    item.unit_price,
                    item.line_total
                ))

            if close_conn:
                conn.commit()
            return sale_id
        except Exception as e:
            if close_conn:
                conn.rollback()
            raise e
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def get_all(start_date: str = None, end_date: str = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "SELECT * FROM sales WHERE 1=1"
        params = []
        if start_date and start_date.strip():
            sql += " AND sale_date >= ?"
            params.append(start_date.strip())
        if end_date and end_date.strip():
            sql += " AND sale_date <= ?"
            params.append(end_date.strip() + " 23:59:59")

        sql += " ORDER BY sale_date DESC, id DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        return [Sale(**dict(r)) for r in rows]

    @staticmethod
    def get_by_id(sale_id: int) -> Sale:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sales WHERE id = ?", (sale_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        sale = Sale(**dict(row))

        # Load sale items
        cursor.execute("""
            SELECT si.*, pr.name AS product_name, pr.sku AS product_sku 
            FROM sale_items si
            LEFT JOIN products pr ON si.product_id = pr.id
            WHERE si.sale_id = ?
            ORDER BY si.id ASC
        """, (sale_id,))
        item_rows = cursor.fetchall()
        conn.close()

        items = []
        for ir in item_rows:
            idict = dict(ir)
            p_name = idict.pop("product_name", "")
            p_sku = idict.pop("product_sku", "")
            item = SaleItem(**idict)
            item.product_name = p_name or "Unknown Product"
            item.product_sku = p_sku or ""
            items.append(item)

        sale.items = items
        return sale
