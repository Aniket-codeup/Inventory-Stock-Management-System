import sqlite3
from database.connection import get_db_connection
from models.purchase import Purchase, PurchaseItem

class PurchaseRepository:
    @staticmethod
    def create(purchase: Purchase, items: list[PurchaseItem], conn: sqlite3.Connection = None) -> int:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO purchases (supplier_id, purchase_date, total_amount, reference_number, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (
                purchase.supplier_id,
                purchase.purchase_date,
                purchase.total_amount,
                purchase.reference_number.strip() if purchase.reference_number else "",
                purchase.notes.strip() if purchase.notes else ""
            ))
            purchase_id = cursor.lastrowid

            for item in items:
                cursor.execute("""
                    INSERT INTO purchase_items (purchase_id, product_id, quantity, unit_price, line_total)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    purchase_id,
                    item.product_id,
                    item.quantity,
                    item.unit_price,
                    item.line_total
                ))

            if close_conn:
                conn.commit()
            return purchase_id
        except Exception as e:
            if close_conn:
                conn.rollback()
            raise e
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def get_all(supplier_id: int = None, start_date: str = None, end_date: str = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            SELECT p.*, s.name AS supplier_name 
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE 1=1
        """
        params = []
        if supplier_id and supplier_id > 0:
            sql += " AND p.supplier_id = ?"
            params.append(supplier_id)
        if start_date and start_date.strip():
            sql += " AND p.purchase_date >= ?"
            params.append(start_date.strip())
        if end_date and end_date.strip():
            sql += " AND p.purchase_date <= ?"
            params.append(end_date.strip() + " 23:59:59")

        sql += " ORDER BY p.purchase_date DESC, p.id DESC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        purchases = []
        for r in rows:
            d = dict(r)
            sup_name = d.pop("supplier_name", "")
            p = Purchase(**d)
            p.supplier_name = sup_name or "Unknown Supplier"
            purchases.append(p)
        return purchases

    @staticmethod
    def get_by_id(purchase_id: int) -> Purchase:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, s.name AS supplier_name 
            FROM purchases p
            LEFT JOIN suppliers s ON p.supplier_id = s.id
            WHERE p.id = ?
        """, (purchase_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        d = dict(row)
        sup_name = d.pop("supplier_name", "")
        purchase = Purchase(**d)
        purchase.supplier_name = sup_name or "Unknown Supplier"

        # Load purchase items
        cursor.execute("""
            SELECT pi.*, pr.name AS product_name, pr.sku AS product_sku 
            FROM purchase_items pi
            LEFT JOIN products pr ON pi.product_id = pr.id
            WHERE pi.purchase_id = ?
            ORDER BY pi.id ASC
        """, (purchase_id,))
        item_rows = cursor.fetchall()
        conn.close()

        items = []
        for ir in item_rows:
            idict = dict(ir)
            p_name = idict.pop("product_name", "")
            p_sku = idict.pop("product_sku", "")
            item = PurchaseItem(**idict)
            item.product_name = p_name or "Unknown Product"
            item.product_sku = p_sku or ""
            items.append(item)

        purchase.items = items
        return purchase
