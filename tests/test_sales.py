import unittest
from tests.test_base import BaseTestCase
from repositories.category_repository import CategoryRepository
from repositories.product_repository import ProductRepository
from services.product_service import ProductService
from services.sales_service import SalesService

class TestSales(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category_id = CategoryRepository.add("Stationery")
        self.prod_id = ProductService.create_product(
            sku="PEN-01",
            name="Marker Pen",
            category_id=self.category_id,
            purchase_price_rupees=20.0,
            selling_price_rupees=40.0,
            minimum_stock=5,
            initial_stock=10
        )

    def test_record_sale_decreases_stock(self):
        """TC-04: Record a sale and verify stock reduction."""
        sale_id = SalesService.record_sale(
            items=[{"product_id": self.prod_id, "quantity": 4, "unit_price": 4000}],
            notes="Walk-in customer"
        )
        self.assertIsNotNone(sale_id)

        # Stock should be 10 - 4 = 6
        p = ProductRepository.get_by_id(self.prod_id)
        self.assertEqual(p.current_stock, 6)

        # Detailed sale
        sale = SalesService.get_sale(sale_id)
        self.assertEqual(sale.total_amount_rupees, 160.0)  # 4 * 40.0
        self.assertEqual(len(sale.items), 1)
        self.assertEqual(sale.items[0].quantity, 4)

    def test_sell_more_than_available_rejected(self):
        """TC-05: Attempting to sell more than available stock must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            SalesService.record_sale(
                items=[{"product_id": self.prod_id, "quantity": 25, "unit_price": 4000}]
            )
        self.assertIn("Insufficient stock", str(ctx.exception))

        # Ensure stock was not changed
        p = ProductRepository.get_by_id(self.prod_id)
        self.assertEqual(p.current_stock, 10)

    def test_sell_inactive_product_rejected(self):
        """Cannot sell inactive product."""
        ProductService.deactivate_product(self.prod_id)
        with self.assertRaises(ValueError) as ctx:
            SalesService.record_sale(
                items=[{"product_id": self.prod_id, "quantity": 1, "unit_price": 4000}]
            )
        self.assertIn("inactive", str(ctx.exception))

    def test_multi_item_sale_atomic_rollback(self):
        """TC-11: If any item in a sale fails, none of the items must be deducted."""
        prod2_id = ProductService.create_product(
            sku="PEN-02",
            name="Whiteboard Marker",
            category_id=self.category_id,
            purchase_price_rupees=25.0,
            selling_price_rupees=50.0,
            minimum_stock=5,
            initial_stock=2  # Only 2 available!
        )
        # Attempt sale: first item is valid (qty 3 out of 10), second item invalid (qty 5 out of 2)
        with self.assertRaises(ValueError):
            SalesService.record_sale(
                items=[
                    {"product_id": self.prod_id, "quantity": 3, "unit_price": 4000},
                    {"product_id": prod2_id, "quantity": 5, "unit_price": 5000}
                ]
            )

        # Neither stock should have changed
        p1 = ProductRepository.get_by_id(self.prod_id)
        p2 = ProductRepository.get_by_id(prod2_id)
        self.assertEqual(p1.current_stock, 10)
        self.assertEqual(p2.current_stock, 2)

if __name__ == "__main__":
    unittest.main()
