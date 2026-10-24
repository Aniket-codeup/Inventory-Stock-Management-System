# Inventory & Stock Management System

An enterprise-grade desktop inventory and stock management system built with **Python 3**, **Object-Oriented Programming (OOP)**, **SQLite (with ACID transactions & foreign key integrity)**, **CSV data interchange**, and **Tkinter (custom modern ttk UI)**.

---

## 🌟 Key Project Highlights

- **Standard Library Only**: Requires zero external packages (`pip install` not required for core application).
- **Core Python Concepts Demonstrated**:
  1. **Object-Oriented Programming (OOP)**: Models, repositories, services, encapsulation, properties, dataclasses.
  2. **SQLite Database**: 8 relational tables, `PRAGMA foreign_keys = ON;`, indexed queries, atomic commit/rollback transactions.
  3. **CSV Interchange**: Product import with row-by-row validation, duplicate SKU detection, and multi-ledger exports.
- **Accurate Monetary Calculations**: Stores currency as **integer paise** (e.g., ₹125.50 = 12,550 paise) to prevent floating-point rounding errors.
- **Stock Integrity Guarantee**: Stock can **never** be edited arbitrarily via product details. It is exclusively adjusted through Purchases (stock-in), Sales (stock-out), or explicit authorized adjustments, with 100% traceable stock movement history.
- **Negative Stock Prevention**: Sales attempts exceeding available stock are rejected transactionally.

---

## 🏗️ Architecture & Three Core Python Concepts

### 1. Object-Oriented Programming (OOP)
- **Data Models (`models/`)**: `Product`, `Category`, `Supplier`, `Purchase`, `PurchaseItem`, `Sale`, `SaleItem`, `StockMovement`.
  - Properties: `is_low_stock`, `is_out_of_stock`, `stock_status`, `purchase_price_rupees`, `selling_price_rupees`.
  - Encapsulation of domain logic and currency conversion helpers.
- **Repositories (`repositories/`)**: Data access layer executing parameterized SQL queries.
  - `ProductRepository`, `CategoryRepository`, `SupplierRepository`, `PurchaseRepository`, `SaleRepository`, `StockMovementRepository`.
- **Services (`services/`)**: Business logic layer enforcing validation, business rules, and atomic transactions.
  - `InventoryService`, `ProductService`, `SupplierService`, `PurchaseService`, `SalesService`, `ReportService`, `CSVService`, `SampleDataService`.

### 2. SQLite Database
- Database file: `inventory.db`
- Connection handling in `database/connection.py` ensures:
  - `PRAGMA foreign_keys = ON;` on every connection.
  - `sqlite3.Row` dictionary mapping.
  - Atomic transaction blocks with `conn.commit()` and `conn.rollback()`.
- Relational schema with 8 tables in `database/schema.py`:
  - `categories` (Departments)
  - `suppliers` (Vendor records)
  - `products` (Inventory items with integer paise pricing)
  - `purchases` & `purchase_items` (Inward stock orders)
  - `sales` & `sale_items` (Outward customer orders)
  - `stock_movements` (Immutable audit log for all stock changes)

### 3. CSV Module Interchange
- Implemented using Python standard library `csv.reader`, `csv.writer`, `csv.DictReader`, and `csv.DictWriter`.
- **Import Validation**:
  - Validates required headers (`SKU`, `Product Name`, `Category`, `Purchase Price`, `Selling Price`).
  - Catches duplicate SKUs in CSV file and active database.
  - Rejects negative prices or malformed quantities.
  - Auto-creates new categories on the fly.
  - Generates comprehensive import result reports (total rows, imported, skipped, error messages).
- **Export**: Exports Products catalog, Sales ledger, Purchase register, and Stock Movements audit trail to CSV.

---

## 📂 Project Directory Structure

```text
inventory-management-system/
│
├── main.py                     # Desktop application entry point (Tkinter GUI)
├── requirements.txt            # Python dependencies (Standard library)
├── README.md                   # Complete documentation and viva guide
├── inventory.db                # SQLite database file
│
├── database/
│   ├── __init__.py
│   ├── connection.py           # Database connection & foreign key pragma
│   └── schema.py               # Table schema definitions & indexes
│
├── models/
│   ├── __init__.py
│   ├── category.py             # Category dataclass model
│   ├── supplier.py             # Supplier dataclass model
│   ├── product.py              # Product model with stock status properties
│   ├── purchase.py             # Purchase and PurchaseItem models
│   ├── sale.py                 # Sale and SaleItem models
│   └── stock_movement.py       # StockMovement audit model
│
├── repositories/
│   ├── __init__.py
│   ├── category_repository.py  # Category SQL queries
│   ├── supplier_repository.py  # Supplier SQL queries
│   ├── product_repository.py   # Product SQL queries & stock updates
│   ├── purchase_repository.py  # Purchase SQL queries
│   ├── sale_repository.py      # Sales SQL queries
│   └── stock_movement_repository.py # Stock movement queries
│
├── services/
│   ├── __init__.py
│   ├── inventory_service.py    # Stock adjustments & summary metrics
│   ├── product_service.py      # Product validation & opening stock
│   ├── supplier_service.py     # Supplier operations & email validation
│   ├── purchase_service.py     # Transactional purchases & stock increments
│   ├── sales_service.py        # Stock availability checks & decrements
│   ├── report_service.py       # Dashboard metrics & reporting
│   ├── csv_service.py          # CSV import/export processing
│   └── sample_data_service.py  # Demo data seeder & database reset
│
├── ui/
│   ├── __init__.py
│   ├── styles.py               # Modern UI theme, color tokens, and ttk styles
│   ├── dashboard.py            # Executive KPI dashboard & alerts
│   ├── products.py             # Product catalog, filters, add/edit dialogs
│   ├── categories.py           # Category management & product counters
│   ├── suppliers.py            # Vendor directory & modal dialogs
│   ├── purchases.py            # Inward stock order builder & audit
│   ├── sales.py                # Point of sale cart & stock decrement
│   ├── stock.py                # Stock level monitor & manual adjustment modal
│   ├── reports.py              # Valuation, replenishment, & transaction reports
│   ├── csv_view.py             # CSV import preview & quick export tools
│   └── settings_view.py        # Database diagnostics & viva seeder
│
├── exports/
│   └── products_import_template.csv  # Ready-to-use sample CSV template
│
└── tests/
    ├── __init__.py
    ├── test_base.py            # Test fixture using isolated temporary SQLite DB
    ├── test_products.py        # Product unit & integration tests
    ├── test_inventory.py       # Stock adjustments & negative stock tests
    ├── test_purchases.py       # Purchase order & stock increment tests
    ├── test_sales.py           # Stock decrement & over-selling prevention tests
    └── test_csv.py             # CSV import, export, and malformed row tests
```

---

## 🚀 How to Run the Application

### 1. Requirements
- Python 3.10+ (Python 3.10, 3.11, 3.12, 3.13 supported)
- Windows, macOS, or Linux

### 2. Launch the Application
Open a terminal in the project directory and run:
```bash
python main.py
```

### 3. Load Demonstration Data (Instant Viva Setup)
1. On the left sidebar, click **⚙️ Settings & Demo Data**.
2. Click **✨ Load Sample Demonstration Data**.
3. The system will instantly populate categories (Electronics, Stationery, Groceries, etc.), suppliers, inventory items with varying stock levels (in stock, low stock, out of stock), purchase orders, and sales receipts.
4. Navigate back to **📊 Dashboard** to view live cards, charts, and tables!

---

## 🧪 Running the Test Suite

The test suite contains 21 unit and integration tests that verify database transactions, validation errors, and stock calculations in isolated in-memory/temporary SQLite databases without touching production data.

Run all tests:
```bash
python -m unittest discover tests
```

Expected output:
```text
.....................
----------------------------------------------------------------------
Ran 21 tests in 3.065s

OK
```

---

## 📋 Comprehensive Viva Demonstration Guide

When presenting this project during a practical examination or viva, follow these steps to showcase all requirements:

| Step | Section | Action to Demonstrate |
|---|---|---|
| **1** | **Executive Dashboard** | Show KPI summary cards (Active products, Stock units, Low-stock alerts, Today's sales, Cost valuation). Point out the low-stock alert warnings and recent stock movement feed. |
| **2** | **Product Management** | Open **Products**, click **➕ Add Product**, enter a new product with initial stock. Show how duplicate SKUs and negative prices are blocked. Click **✏️ Edit** on an existing product and demonstrate that ordinary details can be edited while current stock remains preserved. |
| **3** | **Purchase Order (Stock-In)** | Open **Purchases**, pick a supplier, select a product, enter 10 units at ₹100, and click **Save Purchase**. Show that product stock increases by 10 and a stock movement entry is created. |
| **4** | **Point of Sale (Stock-Out)** | Open **Sales**, pick a product. Attempt to sell **more units than are available in stock**. Show that the system immediately rejects the sale. Then sell a valid quantity and observe that stock decreases accurately. |
| **5** | **Stock Adjustment & Audit** | Open **Stock Control**, select an item, click **⚖️ Stock Adjustment**, select "Damaged / Expired (-)", enter an audit reason, and apply. Switch to **Movement History & Audit Trail** tab to trace the movement with exact timestamps and reason. |
| **6** | **CSV Import & Export** | Open **CSV Import / Export**, click **Export Products CSV** to save a file. Then click **Browse CSV File...**, select `exports/products_import_template.csv`, and click **Process Import** to demonstrate the preview table and import summary dialog. |
| **7** | **Reports** | Open **Business Reports**, switch between Valuation, Replenishment, Sales, and Purchases tabs, apply date filters, and click **Export to CSV**. |
| **8** | **Automated Tests** | Run `python -m unittest discover tests` in the terminal to demonstrate that all 21 automated unit and integration tests pass with 100% success. |

---

## 📜 License
Developed for Academic Final-Year Project Demonstration.
