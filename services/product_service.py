from database.connection import get_db_connection
from models.product import Product
from repositories.product_repository import ProductRepository
from repositories.category_repository import CategoryRepository

class ProductService:
    @staticmethod
    def create_product(
        sku: str,
        name: str,
        category_id: int,
        purchase_price_rupees: float | int | str,
        selling_price_rupees: float | int | str,
        minimum_stock: int,
        description: str = "",
        initial_stock: int = 0
    ) -> int:
        """Validate and create a new product with optional initial opening stock."""
        sku = str(sku).strip()
        if not sku:
            raise ValueError("Product SKU is required.")

        name = str(name).strip()
        if not name:
            raise ValueError("Product Name is required.")

        if not category_id or int(category_id) <= 0:
            raise ValueError("A valid category must be selected.")

        category = CategoryRepository.get_by_id(int(category_id))
        if not category or not category.is_active:
            raise ValueError("Selected category does not exist or is inactive.")

        existing = ProductRepository.get_by_sku(sku)
        if existing and existing.is_active:
            raise ValueError(f"A product with SKU '{sku}' already exists.")

        try:
            purchase_price_paise = Product.rupees_to_paise(purchase_price_rupees)
            selling_price_paise = Product.rupees_to_paise(selling_price_rupees)
        except Exception:
            raise ValueError("Prices must be valid positive numbers.")

        if purchase_price_paise < 0:
            raise ValueError("Purchase price cannot be negative.")
        if selling_price_paise < 0:
            raise ValueError("Selling price cannot be negative.")

        try:
            min_stock = int(minimum_stock)
            if min_stock < 0:
                raise ValueError("Minimum stock cannot be negative.")
        except Exception:
            raise ValueError("Minimum stock must be a non-negative integer.")

        try:
            init_stock = int(initial_stock)
            if init_stock < 0:
                raise ValueError("Initial stock cannot be negative.")
        except Exception:
            raise ValueError("Initial stock must be a non-negative integer.")

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # If existing product was deactivated with this SKU, re-activate and update
            if existing and not existing.is_active:
                cursor.execute("""
                    UPDATE products 
                    SET name = ?, category_id = ?, description = ?, 
                        purchase_price = ?, selling_price = ?, current_stock = ?, 
                        minimum_stock = ?, is_active = 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    name, int(category_id), description.strip(),
                    purchase_price_paise, selling_price_paise, init_stock,
                    min_stock, existing.id
                ))
                product_id = existing.id
            else:
                cursor.execute("""
                    INSERT INTO products (
                        sku, name, category_id, description, 
                        purchase_price, selling_price, current_stock, minimum_stock
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sku, name, int(category_id), description.strip(),
                    purchase_price_paise, selling_price_paise, init_stock, min_stock
                ))
                product_id = cursor.lastrowid

            # If initial stock is specified, record an opening stock movement
            if init_stock > 0:
                cursor.execute("""
                    INSERT INTO stock_movements (
                        product_id, movement_type, quantity_change, 
                        previous_stock, resulting_stock, reason
                    )
                    VALUES (?, 'OPENING_STOCK', ?, 0, ?, 'Initial opening stock')
                """, (product_id, init_stock, init_stock))

            conn.commit()
            return product_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @staticmethod
    def update_product(
        product_id: int,
        sku: str,
        name: str,
        category_id: int,
        purchase_price_rupees: float | int | str,
        selling_price_rupees: float | int | str,
        minimum_stock: int,
        description: str = ""
    ):
        """Update product details while strictly preserving current stock."""
        sku = str(sku).strip()
        if not sku:
            raise ValueError("Product SKU is required.")

        name = str(name).strip()
        if not name:
            raise ValueError("Product Name is required.")

        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found.")

        # Check unique SKU if SKU was changed
        if sku.lower() != product.sku.lower():
            existing = ProductRepository.get_by_sku(sku)
            if existing and existing.id != product_id and existing.is_active:
                raise ValueError(f"A product with SKU '{sku}' already exists.")

        category = CategoryRepository.get_by_id(int(category_id))
        if not category or not category.is_active:
            raise ValueError("Selected category does not exist or is inactive.")

        try:
            purchase_price_paise = Product.rupees_to_paise(purchase_price_rupees)
            selling_price_paise = Product.rupees_to_paise(selling_price_rupees)
        except Exception:
            raise ValueError("Prices must be valid numeric values.")

        if purchase_price_paise < 0:
            raise ValueError("Purchase price cannot be negative.")
        if selling_price_paise < 0:
            raise ValueError("Selling price cannot be negative.")

        min_stock = int(minimum_stock)
        if min_stock < 0:
            raise ValueError("Minimum stock cannot be negative.")

        product.sku = sku
        product.name = name
        product.category_id = int(category_id)
        product.purchase_price = purchase_price_paise
        product.selling_price = selling_price_paise
        product.minimum_stock = min_stock
        product.description = description.strip()

        # Update product without touching current_stock
        ProductRepository.update(product)

    @staticmethod
    def deactivate_product(product_id: int):
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found.")
        ProductRepository.deactivate(product_id)

    @staticmethod
    def get_product(product_id: int):
        return ProductRepository.get_by_id(product_id)

    @staticmethod
    def list_products(query: str = None, category_id: int = None, stock_status: str = None):
        return ProductRepository.search(query=query, category_id=category_id, stock_status=stock_status)
