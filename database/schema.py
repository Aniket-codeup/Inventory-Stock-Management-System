import sqlite3
from database.connection import get_db_connection

def initialize_database(conn: sqlite3.Connection = None, db_path: str = None):
    """Initialize the SQLite database schema with all required tables and indexes."""
    close_when_done = False
    if conn is None:
        conn = get_db_connection(db_path=db_path)
        close_when_done = True

    cursor = conn.cursor()

    # 1. Categories Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Suppliers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            notes TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3. Products Table (Prices stored in integer paise)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            description TEXT,
            purchase_price INTEGER NOT NULL,
            selling_price INTEGER NOT NULL,
            current_stock INTEGER DEFAULT 0,
            minimum_stock INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    """)

    # 4. Purchases Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            purchase_date TEXT NOT NULL,
            total_amount INTEGER NOT NULL,
            reference_number TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    """)

    # 5. Purchase Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchase_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            purchase_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price INTEGER NOT NULL,
            line_total INTEGER NOT NULL,
            FOREIGN KEY (purchase_id) REFERENCES purchases (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    # 6. Sales Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date TEXT NOT NULL,
            total_amount INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 7. Sale Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price INTEGER NOT NULL,
            line_total INTEGER NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """)

    # 8. Stock Movements Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            movement_type TEXT NOT NULL,
            quantity_change INTEGER NOT NULL,
            previous_stock INTEGER NOT NULL,
            resulting_stock INTEGER NOT NULL,
            purchase_id INTEGER,
            sale_id INTEGER,
            reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products (id),
            FOREIGN KEY (purchase_id) REFERENCES purchases (id),
            FOREIGN KEY (sale_id) REFERENCES sales (id)
        )
    """)

    # Indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_sku ON products (sku);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_products_category ON products (category_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_purchases_date ON purchases (purchase_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales (sale_date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movements_product ON stock_movements (product_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_movements_created ON stock_movements (created_at);")

    conn.commit()
    if close_when_done:
        conn.close()

if __name__ == "__main__":
    initialize_database()
    print("Database schema initialized successfully.")