import unittest
from tests.test_base import BaseTestCase
from models.supplier import Supplier
from repositories.category_repository import CategoryRepository
from repositories.supplier_repository import SupplierRepository
from repositories.product_repository import ProductRepository
from services.product_service import ProductService
from services.purchase_service import PurchaseService

class TestPurchases(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category_id = CategoryRepository.add("Electronics")
        self.supplier_id = SupplierRepository.add(Supplier(name="Tech Distro Ltd.", phone="1234567890"))
        self.prod_id = ProductService.create_product(
            sku="CABLE-01",
            name="HDMI Cable 2m",
            category_id=self.category_id,
            purchase_price_rupees=100.0,
            selling_price_rupees=200.0,
            minimum_stock=5,
            initial_stock=10
        )

    def test_record_purchase_increases_stock(self):
        """TC-03: Record a purchase and verify stock increase."""
        purchase_id = PurchaseService.record_purchase(
            supplier_id=self.supplier_id,
            items=[{"product_id": self.prod_id, "quantity": 15, "unit_price": 10000}],
            reference_number="PO-1001",
            notes="Initial shipment"
        )
        self.assertIsNotNone(purchase_id)

        # Stock should be 10 (initial) + 15 = 25
        product = ProductRepository.get_by_id(self.prod_id)
        self.assertEqual(product.current_stock, 25)

        # Retrieve detailed purchase
        purchase = PurchaseService.get_purchase(purchase_id)
        self.assertEqual(purchase.supplier_name, "Tech Distro Ltd.")
        self.assertEqual(purchase.total_amount_rupees, 1500.0)  # 15 * 100.0
        self.assertEqual(len(purchase.items), 1)
        self.assertEqual(purchase.items[0].quantity, 15)

    def test_empty_purchase_rejected(self):
        """Purchase without items must fail."""
        with self.assertRaises(ValueError):
            PurchaseService.record_purchase(
                supplier_id=self.supplier_id,
                items=[]
            )

    def test_invalid_supplier_rejected(self):
        """Non-existent supplier must fail."""
        with self.assertRaises(ValueError):
            PurchaseService.record_purchase(
                supplier_id=99999,
                items=[{"product_id": self.prod_id, "quantity": 5, "unit_price": 10000}]
            )

if __name__ == "__main__":
    unittest.main()
