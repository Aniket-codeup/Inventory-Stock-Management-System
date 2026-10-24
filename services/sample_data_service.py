from database.connection import get_db_connection
from database.schema import initialize_database
from models.category import Category
from models.supplier import Supplier
from repositories.category_repository import CategoryRepository
from repositories.supplier_repository import SupplierRepository
from services.product_service import ProductService
from services.purchase_service import PurchaseService
from services.sales_service import SalesService
from services.inventory_service import InventoryService

class SampleDataService:
    @staticmethod
    def seed_data() -> dict:
        """Seed realistic sample data into the database for demonstration and testing."""
        # Ensure schema is intact
        initialize_database()

        # 1. Categories
        categories_to_seed = ["Electronics", "Stationery", "Groceries", "Beverages", "Household"]
        cat_ids = {}
        for cname in categories_to_seed:
            existing = CategoryRepository.get_by_name(cname)
            if not existing:
                cat_ids[cname] = CategoryRepository.add(cname)
            else:
                cat_ids[cname] = existing.id

        # 2. Suppliers
        suppliers_to_seed = [
            Supplier(
                name="Apex Electronics Ltd.",
                contact_person="Rajesh Sharma",
                phone="+91 98765 43210",
                email="rajesh@apexelectronics.in",
                address="Plot 12, Industrial Area, Pune",
                notes="Primary vendor for cables and accessories"
            ),
            Supplier(
                name="Standard Stationery Mart",
                contact_person="Priya Desai",
                phone="+91 98220 11223",
                email="priya@standardstationery.com",
                address="45 MG Road, Mumbai",
                notes="Notebooks, pens, and paper supplies"
            ),
            Supplier(
                name="Sunrise Wholesale Groceries",
                contact_person="Amitabh Verma",
                phone="+91 99112 33445",
                email="sales@sunrisegroceries.in",
                address="Sector 18, Vashi, Navi Mumbai",
                notes="Dry fruits, tea, coffee, and pantry essentials"
            )
        ]

        sup_ids = []
        for sup in suppliers_to_seed:
            existing_sups = SupplierRepository.search(sup.name)
            if not existing_sups:
                sup_ids.append(SupplierRepository.add(sup))
            else:
                sup_ids.append(existing_sups[0].id)

        # 3. Products
        products_to_seed = [
            # In Stock
            ("ELEC-USB-C", "Braided USB-C Cable (1m)", "Electronics", 120.00, 249.00, 10, 45, "Durable fast charging cable"),
            ("ELEC-EAR-01", "Wired In-Ear Headphones", "Electronics", 250.00, 499.00, 8, 25, "Deep bass earphone with mic"),
            ("STAT-NOTE-A4", "A4 Spiral Notebook (200 pgs)", "Stationery", 60.00, 120.00, 15, 60, "Single ruled premium paper"),
            ("STAT-PEN-BL", "Gel Pen Box (Blue - 10 pcs)", "Stationery", 90.00, 150.00, 10, 30, "Waterproof quick-dry ink"),
            ("GROC-TEA-250", "Premium Assam Tea (250g)", "Beverages", 140.00, 220.00, 10, 35, "Rich aromaCTC tea"),
            ("GROC-COF-100", "Instant Coffee Granules (100g)", "Beverages", 180.00, 290.00, 8, 20, "100% pure roasted coffee"),
            ("HOUSE-DET-1L", "Eco Liquid Detergent (1L)", "Household", 150.00, 240.00, 10, 40, "Safe for top & front load"),

            # Low Stock items (to trigger alerts!)
            ("ELEC-ADP-20W", "20W USB-C Power Adapter", "Electronics", 350.00, 699.00, 10, 4, "Fast power delivery adapter"),
            ("STAT-CALC-8D", "Desk Calculator 8-Digit", "Stationery", 180.00, 320.00, 5, 2, "Solar and battery powered"),
            ("GROC-ALM-500", "California Almonds (500g)", "Groceries", 380.00, 550.00, 6, 3, "Premium whole almonds"),

            # Out of Stock items
            ("ELEC-PW-10K", "10000mAh Power Bank", "Electronics", 650.00, 1199.00, 5, 0, "Dual output slim power bank"),
            ("STAT-STAP-STD", "Heavy Duty Desktop Stapler", "Stationery", 110.00, 199.00, 5, 0, "All metal body with 1000 staples")
        ]

        seeded_product_ids = []
        for sku, name, cat_name, p_price, s_price, min_stk, init_stk, desc in products_to_seed:
            cat_id = cat_ids.get(cat_name, 1)
            try:
                pid = ProductService.create_product(
                    sku=sku,
                    name=name,
                    category_id=cat_id,
                    purchase_price_rupees=p_price,
                    selling_price_rupees=s_price,
                    minimum_stock=min_stk,
                    description=desc,
                    initial_stock=init_stk
                )
                seeded_product_ids.append(pid)
            except ValueError:
                # If product already exists, skip
                pass

        # 4. Purchases
        if sup_ids and len(seeded_product_ids) >= 4:
            try:
                PurchaseService.record_purchase(
                    supplier_id=sup_ids[0],
                    items=[
                        {"product_id": seeded_product_ids[0], "quantity": 10, "unit_price": 12000},
                        {"product_id": seeded_product_ids[1], "quantity": 5, "unit_price": 25000}
                    ],
                    reference_number="PO-2026-001",
                    notes="Monthly restock order"
                )
            except Exception:
                pass

        # 5. Sales
        if len(seeded_product_ids) >= 3:
            try:
                SalesService.record_sale(
                    items=[
                        {"product_id": seeded_product_ids[0], "quantity": 3, "unit_price": 24900},
                        {"product_id": seeded_product_ids[2], "quantity": 2, "unit_price": 12000}
                    ],
                    notes="Walk-in retail customer sale"
                )
            except Exception:
                pass

        return {"status": "success", "message": "Sample data seeded successfully."}

    @staticmethod
    def reset_database():
        """Clear all records from database tables for a clean slate."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stock_movements;")
        cursor.execute("DELETE FROM sale_items;")
        cursor.execute("DELETE FROM sales;")
        cursor.execute("DELETE FROM purchase_items;")
        cursor.execute("DELETE FROM purchases;")
        cursor.execute("DELETE FROM products;")
        cursor.execute("DELETE FROM suppliers;")
        cursor.execute("DELETE FROM categories;")
        try:
            cursor.execute("DELETE FROM sqlite_sequence;")
        except Exception:
            pass
        conn.commit()
        conn.execute("VACUUM;")
        conn.close()
