import os
import tempfile
import unittest
from tests.test_base import BaseTestCase
from repositories.category_repository import CategoryRepository
from repositories.product_repository import ProductRepository
from services.product_service import ProductService
from services.csv_service import CSVService

class TestCSV(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.category_id = CategoryRepository.add("Electronics")
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        super().tearDown()
        if os.path.exists(self.temp_dir):
            for f in os.listdir(self.temp_dir):
                try:
                    os.remove(os.path.join(self.temp_dir, f))
                except Exception:
                    pass
            try:
                os.rmdir(self.temp_dir)
            except Exception:
                pass

    def test_export_products(self):
        """TC-07: Export products to CSV."""
        ProductService.create_product(
            sku="EXP-01",
            name="USB Hub",
            category_id=self.category_id,
            purchase_price_rupees=300.0,
            selling_price_rupees=600.0,
            minimum_stock=5,
            initial_stock=12
        )
        export_file = os.path.join(self.temp_dir, "products_export.csv")
        count = CSVService.export_products(export_file)
        self.assertEqual(count, 1)
        self.assertTrue(os.path.exists(export_file))

        with open(export_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("EXP-01", content)
            self.assertIn("USB Hub", content)
            self.assertIn("Electronics", content)

    def test_import_valid_csv(self):
        """TC-08: Import valid CSV creates products."""
        csv_file = os.path.join(self.temp_dir, "valid_import.csv")
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("SKU,Product Name,Category,Purchase Price,Selling Price,Current Stock,Minimum Stock\n")
            f.write("IMP-01,Wired Mouse,Electronics,150.00,300.00,20,5\n")
            f.write("IMP-02,Mechanical Pencil,Stationery,40.00,80.00,50,10\n")

        summary = CSVService.import_products(csv_file)
        self.assertEqual(summary["total"], 2)
        self.assertEqual(summary["imported"], 2)
        self.assertEqual(summary["skipped"], 0)

        # Verify created products
        p1 = ProductRepository.get_by_sku("IMP-01")
        self.assertIsNotNone(p1)
        self.assertEqual(p1.current_stock, 20)
        self.assertEqual(p1.purchase_price_rupees, 150.0)

        p2 = ProductRepository.get_by_sku("IMP-02")
        self.assertIsNotNone(p2)
        self.assertEqual(p2.current_stock, 50)

    def test_import_invalid_rows_and_duplicates(self):
        """TC-09: Invalid rows and duplicate SKUs are reported in summary without crash."""
        csv_file = os.path.join(self.temp_dir, "bad_import.csv")
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write("SKU,Product Name,Category,Purchase Price,Selling Price,Current Stock,Minimum Stock\n")
            f.write("VALID-01,Valid Item,Electronics,100,200,10,2\n")
            f.write(",No SKU Item,Electronics,100,200,10,2\n")  # Missing SKU
            f.write("VALID-01,Duplicate SKU,Electronics,100,200,10,2\n")  # Duplicate SKU in file
            f.write("BAD-PRC,Bad Price,Electronics,-50,200,10,2\n")  # Negative price

        summary = CSVService.import_products(csv_file)
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["imported"], 1)
        self.assertEqual(summary["skipped"], 3)
        self.assertEqual(len(summary["errors"]), 3)

if __name__ == "__main__":
    unittest.main()
