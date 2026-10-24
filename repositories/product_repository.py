import sqlite3
from database.connection import get_db_connection
from models.product import Product

class ProductRepository:
    @staticmethod
    def _row_to_product(row) -> Product:
        if not row:
            return None
        data = dict(row)
        cat_name = data.pop("category_name", "")
        prod = Product(**data)
        prod.category_name = cat_name or ""
        return prod

    @staticmethod
    def add(product: Product, conn: sqlite3.Connection = None) -> int:
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO products (
                    sku, name, category_id, description, 
                    purchase_price, selling_price, current_stock, minimum_stock
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product.sku.strip(),
                product.name.strip(),
                product.category_id,
                product.description.strip() if product.description else "",
                product.purchase_price,
                product.selling_price,
                product.current_stock,
                product.minimum_stock
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
    def get_all(include_inactive: bool = False):
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT p.*, c.name AS category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
        """
        if not include_inactive:
            query += " WHERE p.is_active = 1"
        query += " ORDER BY p.name ASC"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return [ProductRepository._row_to_product(r) for r in rows]

    @staticmethod
    def get_by_id(product_id: int, conn: sqlite3.Connection = None):
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, c.name AS category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        """, (product_id,))
        row = cursor.fetchone()
        if close_conn:
            conn.close()
        return ProductRepository._row_to_product(row)

    @staticmethod
    def get_by_sku(sku: str, conn: sqlite3.Connection = None):
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, c.name AS category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE LOWER(p.sku) = LOWER(?)
        """, (sku.strip(),))
        row = cursor.fetchone()
        if close_conn:
            conn.close()
        return ProductRepository._row_to_product(row)

    @staticmethod
    def update(product: Product):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE products 
                SET sku = ?, name = ?, category_id = ?, description = ?, 
                    purchase_price = ?, selling_price = ?, minimum_stock = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                product.sku.strip(),
                product.name.strip(),
                product.category_id,
                product.description.strip() if product.description else "",
                product.purchase_price,
                product.selling_price,
                product.minimum_stock,
                product.id
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_stock(product_id: int, new_stock: int, conn: sqlite3.Connection = None):
        """Update current_stock for a product within an active or new transaction."""
        close_conn = False
        if conn is None:
            conn = get_db_connection()
            close_conn = True
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE products 
                SET current_stock = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (new_stock, product_id))
            if close_conn:
                conn.commit()
        except Exception as e:
            if close_conn:
                conn.rollback()
            raise e
        finally:
            if close_conn:
                conn.close()

    @staticmethod
    def deactivate(product_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE products SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (product_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def search(query: str = None, category_id: int = None, stock_status: str = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            SELECT p.*, c.name AS category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1
        """
        params = []
        if query and query.strip():
            pat = f"%{query.strip()}%"
            sql += " AND (p.sku LIKE ? OR p.name LIKE ? OR p.description LIKE ?)"
            params.extend([pat, pat, pat])
        if category_id and category_id > 0:
            sql += " AND p.category_id = ?"
            params.append(category_id)

        sql += " ORDER BY p.name ASC"
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()

        products = [ProductRepository._row_to_product(r) for r in rows]
        if stock_status:
            target = stock_status.strip().lower()
            if target in ["low", "low stock"]:
                products = [p for p in products if p.is_low_stock]
            elif target in ["out", "out of stock"]:
                products = [p for p in products if p.is_out_of_stock]
            elif target in ["in", "in stock"]:
                products = [p for p in products if not p.is_low_stock and not p.is_out_of_stock]
        return products

    @staticmethod
    def get_low_stock():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, c.name AS category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1 AND p.current_stock > 0 AND p.current_stock <= p.minimum_stock
            ORDER BY p.current_stock ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [ProductRepository._row_to_product(r) for r in rows]

    @staticmethod
    def get_out_of_stock():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, c.name AS category_name 
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.is_active = 1 AND p.current_stock <= 0
            ORDER BY p.name ASC
        """)
        rows = cursor.fetchall()
        conn.close()
        return [ProductRepository._row_to_product(r) for r in rows]