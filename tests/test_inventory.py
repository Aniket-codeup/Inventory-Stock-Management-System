import unittest
from tests.test_base import BaseTestCase
from repositories.category_repository import CategoryRepository
from repositories.product_repository import ProductRepository
from services.product_service import ProductService
from services.inventory_service import InventoryService

class TestInventory(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category_id = CategoryRepository.add("Stationery")
        self.product_id = ProductService.create_product(
            sku="BOOK-01",
            name="Notebook 100p",
            category_id=self.category_id,
            purchase_price_rupees=30.0,
            selling_price_rupees=50.0,
            minimum_stock=10,
            initial_stock=15
        )

    def test_stock_adjustment_increase(self):
        """Positive stock adjustment increases stock and records movement."""
        result = InventoryService.adjust_stock(
            product_id=self.product_id,
            quantity_change=5,
            movement_type="ADJUSTMENT",
            reason="Found extra stock during audit"
        )
        self.assertEqual(result["previous_stock"], 15)
        self.assertEqual(result["resulting_stock"], 20)

        p = ProductRepository.get_by_id(self.product_id)
        self.assertEqual(p.current_stock, 20)

        movements = InventoryService.get_movements(product_id=self.product_id)
        # Should have initial opening stock movement + adjustment movement
        self.assertGreaterEqual(len(movements), 2)
        latest = movements[0]
        self.assertEqual(latest.quantity_change, 5)
        self.assertEqual(latest.reason, "Found extra stock during audit")

    def test_stock_adjustment_decrease(self):
        """Negative stock adjustment decreases stock and records movement."""
        result = InventoryService.adjust_stock(
            product_id=self.product_id,
            quantity_change=-3,
            movement_type="ADJUSTMENT",
            reason="Water damaged items disposed"
        )
        self.assertEqual(result["previous_stock"], 15)
        self.assertEqual(result["resulting_stock"], 12)

    def test_negative_stock_prevented(self):
        """Attempting adjustment that results in negative stock must be rejected."""
        with self.assertRaises(ValueError) as ctx:
            InventoryService.adjust_stock(
                product_id=self.product_id,
                quantity_change=-20,  # Only 15 available!
                movement_type="ADJUSTMENT",
                reason="Deducting too much"
            )
        self.assertIn("negative stock", str(ctx.exception))

    def test_adjustment_without_reason_rejected(self):
        """Adjustment without reason must be rejected."""
        with self.assertRaises(ValueError):
            InventoryService.adjust_stock(
                product_id=self.product_id,
                quantity_change=2,
                movement_type="ADJUSTMENT",
                reason=""
            )

    def test_stock_summary(self):
        """Verify dashboard stock summary counts and valuation."""
        summary = InventoryService.get_stock_summary()
        self.assertEqual(summary["total_products"], 1)
        self.assertEqual(summary["total_units"], 15)
        self.assertEqual(summary["total_valuation_rupees"], 450.0)  # 15 * 30.0

if __name__ == "__main__":
    unittest.main()
