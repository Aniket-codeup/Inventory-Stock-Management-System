from database.connection import get_db_connection
from models.supplier import Supplier

class SupplierRepository:
    @staticmethod
    def add(supplier: Supplier) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO suppliers (name, contact_person, phone, email, address, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                supplier.name.strip(),
                supplier.contact_person.strip() if supplier.contact_person else "",
                supplier.phone.strip() if supplier.phone else "",
                supplier.email.strip() if supplier.email else "",
                supplier.address.strip() if supplier.address else "",
                supplier.notes.strip() if supplier.notes else ""
            ))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE is_active = 1 ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [Supplier(**dict(row)) for row in rows]

    @staticmethod
    def get_by_id(supplier_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        row = cursor.fetchone()
        conn.close()
        return Supplier(**dict(row)) if row else None

    @staticmethod
    def update(supplier: Supplier):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE suppliers 
                SET name = ?, contact_person = ?, phone = ?, email = ?, address = ?, notes = ?
                WHERE id = ?
            """, (
                supplier.name.strip(),
                supplier.contact_person.strip() if supplier.contact_person else "",
                supplier.phone.strip() if supplier.phone else "",
                supplier.email.strip() if supplier.email else "",
                supplier.address.strip() if supplier.address else "",
                supplier.notes.strip() if supplier.notes else "",
                supplier.id
            ))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def deactivate(supplier_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE suppliers SET is_active = 0 WHERE id = ?", (supplier_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def search(query: str):
        conn = get_db_connection()
        cursor = conn.cursor()
        pattern = f"%{query.strip()}%"
        cursor.execute("""
            SELECT * FROM suppliers 
            WHERE is_active = 1 AND (
                name LIKE ? OR contact_person LIKE ? OR phone LIKE ? OR email LIKE ?
            )
            ORDER BY name ASC
        """, (pattern, pattern, pattern, pattern))
        rows = cursor.fetchall()
        conn.close()
        return [Supplier(**dict(row)) for row in rows]

    @staticmethod
    def has_purchases(supplier_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS cnt FROM purchases WHERE supplier_id = ?", (supplier_id,))
        count = cursor.fetchone()["cnt"]
        conn.close()
        return count > 0
