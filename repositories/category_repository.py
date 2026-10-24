from database.connection import get_db_connection
from models.category import Category

class CategoryRepository:
    @staticmethod
    def add(name: str) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name.strip(),))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_all(include_counts: bool = True):
        conn = get_db_connection()
        cursor = conn.cursor()
        if include_counts:
            cursor.execute("""
                SELECT c.*, 
                       (SELECT COUNT(*) FROM products p WHERE p.category_id = c.id AND p.is_active = 1) AS product_count
                FROM categories c 
                WHERE c.is_active = 1 
                ORDER BY c.name ASC
            """)
        else:
            cursor.execute("SELECT *, 0 AS product_count FROM categories WHERE is_active = 1 ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [Category(**dict(row)) for row in rows]

    @staticmethod
    def get_by_id(category_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT *, 0 AS product_count FROM categories WHERE id = ?", (category_id,))
        row = cursor.fetchone()
        conn.close()
        return Category(**dict(row)) if row else None

    @staticmethod
    def get_by_name(name: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT *, 0 AS product_count FROM categories WHERE LOWER(name) = LOWER(?) AND is_active = 1", (name.strip(),))
        row = cursor.fetchone()
        conn.close()
        return Category(**dict(row)) if row else None

    @staticmethod
    def update(category_id: int, name: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE categories SET name = ? WHERE id = ?", (name.strip(), category_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def deactivate(category_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE categories SET is_active = 0 WHERE id = ?", (category_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def has_active_products(category_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM products WHERE category_id = ? AND is_active = 1", (category_id,))
        count = cursor.fetchone()["cnt"]
        conn.close()
        return count > 0