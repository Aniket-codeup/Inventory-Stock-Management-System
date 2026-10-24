import unittest
from tests.test_base import BaseTestCase
from models.product import Product
from repositories.category_repository import CategoryRepository
from repositories.product_repository import ProductRepository
from services.product_service import ProductService

class TestProducts(BaseTestCase):
    def setUp(self):
        super().setUp()
        # Seed a test category
        self.category_id = CategoryRepository.add("Electronics")

    def test_product_model_properties(self):
        """Test Product model stock status calculation and currency conversion."""
        p = Product(
            sku="SKU-1",
            name="Mouse",
            category_id=self.category_id,
            purchase_price=15050,  # ₹150.50
            selling_price=29900,   # ₹299.00
            current_stock=5,
            minimum_stock=10
        )
        self.assertTrue(p.is_low_stock)
        self.assertFalse(p.is_out_of_stock)
        self.assertEqual(p.stock_status, "Low Stock")
        self.assertEqual(p.purchase_price_rupees, 150.50)
        self.assertEqual(p.selling_price_rupees, 299.00)

        # Test out of stock
        p.current_stock = 0
        self.assertTrue(p.is_out_of_stock)
        self.assertFalse(p.is_low_stock)
        self.assertEqual(p.stock_status, "Out of Stock")

        # Test in stock
        p.current_stock = 25
        self.assertFalse(p.is_low_stock)
        self.assertFalse(p.is_out_of_stock)
        self.assertEqual(p.stock_status, "In Stock")

    def test_add_valid_product(self):
        """TC-01: Add a valid product and verify persistence."""
        pid = ProductService.create_product(
            sku="PROD-001",
            name="Wireless Keyboard",
            category_id=self.category_id,
            purchase_price_rupees=500.0,
            selling_price_rupees=999.0,
            minimum_stock=10,
            description="2.4GHz USB keyboard",
            initial_stock=20
        )
        self.assertIsNotNone(pid)
        product = ProductRepository.get_by_id(pid)
        self.assertEqual(product.sku, "PROD-001")
        self.assertEqual(product.name, "Wireless Keyboard")
        self.assertEqual(product.current_stock, 20)
        self.assertEqual(product.purchase_price, 50000)

    def test_duplicate_sku_rejected(self):
        """TC-02: Adding duplicate SKU should raise ValueError."""
        ProductService.create_product(
            sku="UNIQUE-1",
            name="Item One",
            category_id=self.category_id,
            purchase_price_rupees=100.0,
            selling_price_rupees=150.0,
            minimum_stock=5
        )
        with self.assertRaises(ValueError) as ctx:
            ProductService.create_product(
                sku="UNIQUE-1",
                name="Item Two",
                category_id=self.category_id,
                purchase_price_rupees=120.0,
                selling_price_rupees=160.0,
                minimum_stock=5
            )
        self.assertIn("already exists", str(ctx.exception))

    def test_invalid_prices_rejected(self):
        """Negative prices should raise ValueError."""
        with self.assertRaises(ValueError):
            ProductService.create_product(
                sku="BAD-PRICE",
                name="Bad Price Item",
                category_id=self.category_id,
                purchase_price_rupees=-50.0,
                selling_price_rupees=100.0,
                minimum_stock=5
            )

    def test_edit_preserves_stock(self):
        """Section 4.2 C: Editing ordinary details must preserve current stock."""
        pid = ProductService.create_product(
            sku="KEY-01",
            name="Old Keyboard",
            category_id=self.category_id,
            purchase_price_rupees=400.0,
            selling_price_rupees=800.0,
            minimum_stock=5,
            initial_stock=15
        )
        # Edit details
        ProductService.update_product(
            product_id=pid,
            sku="KEY-01",
            name="New Keyboard Deluxe",
            category_id=self.category_id,
            purchase_price_rupees=450.0,
            selling_price_rupees=850.0,
            minimum_stock=8,
            description="Upgraded switch model"
        )
        updated = ProductRepository.get_by_id(pid)
        self.assertEqual(updated.name, "New Keyboard Deluxe")
        self.assertEqual(updated.current_stock, 15)  # Stock untouched!

    def test_deactivate_product(self):
        """TC-12: Deactivating product marks it inactive."""
        pid = ProductService.create_product(
            sku="TO-DEACT",
            name="Deactivate Item",
            category_id=self.category_id,
            purchase_price_rupees=50.0,
            selling_price_rupees=100.0,
            minimum_stock=2
        )
        ProductService.deactivate_product(pid)
        active_list = ProductRepository.get_all()
        self.assertFalse(any(p.id == pid for p in active_list))

if __name__ == "__main__":
    unittest.main()
