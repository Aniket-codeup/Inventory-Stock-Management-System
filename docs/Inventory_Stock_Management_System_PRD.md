# Product Requirements Document (PRD)
## Inventory & Stock Management System

**Project Type:** B.Tech IT Final-Year Group Project  
**Project No.:** 12 — Python Final-Year Project Ideas  
**Primary Language:** Python  
**Database:** SQLite  
**Data Exchange:** CSV  
**Application Type:** Desktop Application  
**Document Version:** 1.0

---

# 1. Project Overview

## 1.1 Project Title

**Inventory & Stock Management System Using Python, OOP, SQLite, and CSV**

## 1.2 Introduction

The Inventory & Stock Management System is a desktop application designed to help small businesses manage their products, stock quantities, suppliers, purchases, and sales.

Many small businesses maintain inventory records manually in notebooks or spreadsheets. These methods can lead to incorrect stock calculations, misplaced records, difficulty tracking sales, and delays in identifying products that need replenishment.

This project aims to simplify inventory management by providing a centralized application that stores product information, tracks stock movements, calculates sales and purchase totals, and generates reports.

The application will use Python for its application logic, Object-Oriented Programming (OOP) for organizing the code, SQLite for persistent database storage, and CSV files for importing and exporting inventory data.

## 1.3 Problem Statement

Small businesses often face difficulties maintaining accurate inventory records.

Common problems include:

- Manually calculating available stock.
- Losing or duplicating product records.
- Difficulty tracking purchases and sales.
- Accidentally selling products that are out of stock.
- Not knowing when products need replenishment.
- Difficulty generating inventory reports.
- Lack of a simple system for backing up or transferring product records.

The proposed system addresses these problems through a simple, reliable, and easy-to-use inventory management application.

## 1.4 Proposed Solution

The application will provide a graphical interface through which an authorized user can:

1. Add and manage products.
2. Organize products into categories.
3. Manage supplier information.
4. Record purchases and increase stock.
5. Record sales and decrease stock.
6. View current stock levels.
7. Receive low-stock warnings.
8. Search and filter products.
9. Generate inventory and transaction reports.
10. Import and export records through CSV files.

All essential records will be stored locally in an SQLite database.

## 1.5 Project Objectives

The main objectives are:

- Develop a functional inventory management application using Python.
- Demonstrate practical implementation of OOP.
- Use SQLite for persistent storage and database operations.
- Use CSV for importing and exporting records.
- Automate stock calculations.
- Reduce errors caused by manual inventory management.
- Generate useful inventory and transaction reports.
- Develop a project that is straightforward to demonstrate during a practical examination or viva.

---

# 2. Project Scope

## 2.1 In Scope

The first version will include the following modules:

- Dashboard
- Product Management
- Category Management
- Supplier Management
- Purchase Management
- Sales Management
- Stock Management
- Low-Stock Alerts
- Search and Filtering
- Reports
- CSV Import and Export
- Basic Application Settings

## 2.2 Out of Scope

To keep the project manageable, the initial version will not include:

- Online shopping or customer-facing e-commerce.
- Online payment gateways.
- Cloud synchronization.
- Multiple branches.
- Barcode scanner integration.
- GST invoicing and tax-compliance functionality.
- AI-based demand forecasting.
- Mobile applications.
- Multi-user network synchronization.
- Integration with external accounting software.

These features may be considered future enhancements.

## 2.3 Target Users

The application is intended for:

- Small retail shops.
- Stationery stores.
- Grocery shops.
- Electronics shops.
- Small warehouses.
- College project demonstrations.

The first version will assume that a single business manages its inventory on one computer.

---

# 3. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Programming language | Python 3 | Application logic |
| User interface | Tkinter with ttk | Desktop graphical interface |
| Database | SQLite | Persistent data storage |
| Data import/export | Python CSV module | Import and export records |
| Date handling | Python datetime | Transaction dates and timestamps |
| Decimal calculations | Python Decimal | Reliable monetary calculations |
| Object-oriented design | Python classes and objects | Organize application components |
| Testing | Python unittest | Verify application behavior |

### Why this stack?

Python, Tkinter, and SQLite are sufficient to create a complete desktop application without requiring a web server or external database service.

The CSV module is part of Python's standard library, so the project does not need an additional package for CSV processing.

The proposed stack is suitable for a student project because it is relatively simple to install, develop, test, and demonstrate.

---

# 4. Core Functional Requirements

## 4.1 Dashboard

### Purpose

The dashboard will provide an overview of the business's inventory.

### Information displayed

- Total number of active products.
- Total units currently in stock.
- Number of products with low stock.
- Number of out-of-stock products.
- Total sales recorded.
- Total purchases recorded.
- Recent transactions.

### Dashboard behavior

When the application starts, it will load the dashboard.

The displayed information will be calculated from the database rather than stored as independent, manually maintained values.

### Example

| Metric | Example Value |
|---|---:|
| Active Products | 125 |
| Total Units in Stock | 2,450 |
| Low-Stock Products | 8 |
| Out-of-Stock Products | 3 |
| Today's Sales | ₹4,500 |
| Today's Purchases | ₹2,000 |

These values are illustrative and will change according to the database contents.

### Acceptance criteria

- The dashboard loads without errors.
- Counts reflect the current database records.
- Sales and purchase totals use clearly defined date ranges.
- The dashboard updates after successful stock transactions.

---

## 4.2 Product Management

### Purpose

Allow users to create, view, update, search, and deactivate product records.

### Product fields

| Field | Type | Required |
|---|---|---|
| Product ID | Integer | Automatically generated |
| SKU | Text | Yes |
| Product Name | Text | Yes |
| Category | Reference to category | Yes |
| Description | Text | No |
| Purchase Price | Decimal-compatible value | Yes |
| Selling Price | Decimal-compatible value | Yes |
| Current Stock | Integer | Managed by transactions |
| Minimum Stock Level | Integer | Yes |
| Supplier | Optional reference | No |
| Created Date | Date and time | Automatic |
| Updated Date | Date and time | Automatic |
| Active Status | Boolean | Automatic default |

**Important design decision:** Current stock should not be directly editable through the ordinary product-edit form.

Stock should change through purchase entries, sales entries, or explicitly authorized stock adjustments. This preserves a meaningful transaction history.

### Features

#### A. Add Product

The user enters:

- SKU.
- Product name.
- Category.
- Purchase price.
- Selling price.
- Minimum stock level.
- Optional description and supplier.

The system validates the information before saving.

#### B. View Products

The application displays a table containing:

- SKU.
- Product name.
- Category.
- Purchase price.
- Selling price.
- Available stock.
- Stock status.

#### C. Edit Product

Users can update product information such as its name, price, category, and description.

The system will preserve the existing stock quantity when editing ordinary product details.

#### D. Deactivate Product

Instead of permanently deleting a product with transaction history, the system will allow the user to deactivate it.

Deactivated products will not appear in the normal active-product selection lists but will remain available in historical reports.

#### E. Search Products

Users can search using:

- SKU.
- Product name.
- Category.

### Validation rules

- SKU must be unique.
- Product name cannot be empty.
- Prices cannot be negative.
- Minimum stock cannot be negative.
- Category must exist.
- Prices must be valid numeric values.
- Invalid input must produce a readable error message.

### Acceptance criteria

The user can create and update products, and changes persist after restarting the application.

Duplicate SKUs and invalid prices must be rejected.

---

## 4.3 Category Management

### Purpose

Organize products into meaningful groups.

### Example categories

- Electronics.
- Stationery.
- Groceries.
- Accessories.
- Household Items.

### Features

- Add category.
- View categories.
- Rename category.
- Deactivate unused categories.

### Rules

- Category names must not be empty.
- Duplicate category names should be prevented.
- A category referenced by existing products cannot be physically deleted without an appropriate reassignment or archival process.

### Acceptance criteria

Users can organize products into categories and filter inventory using those categories.

---

## 4.4 Supplier Management

### Purpose

Maintain supplier details for purchasing inventory.

### Supplier fields

| Field | Description |
|---|---|
| Supplier ID | Automatically generated identifier |
| Supplier Name | Required |
| Contact Person | Optional |
| Phone Number | Optional |
| Email | Optional |
| Address | Optional |
| Notes | Optional |
| Active Status | Indicates whether the supplier is active |

### Features

- Add supplier.
- View supplier list.
- Edit supplier information.
- Search suppliers.
- Deactivate suppliers.

### Validation

- Supplier name cannot be empty.
- Email must follow a basic valid format when provided.
- Phone numbers must be stored as text to preserve leading zeros and country codes.

### Acceptance criteria

The user can associate a supplier with purchase transactions and view the supplier's purchasing history.

---

## 4.5 Purchase Management

### Purpose

Record incoming stock when products are purchased from suppliers.

### Purchase workflow

1. Open the Purchase Management section.
2. Select a supplier.
3. Add one or more products.
4. Enter the quantity purchased.
5. Confirm the purchase price.
6. Review the purchase total.
7. Save the purchase.
8. Increase the relevant stock quantities.
9. Record the transaction in the database.

### Purchase fields

**Purchase header:**

- Purchase ID.
- Supplier ID.
- Purchase date.
- Total amount.
- Optional reference number.
- Notes.

**Purchase items:**

- Product ID.
- Quantity.
- Unit purchase price.
- Line total.

### Calculation

For each purchase item:

`Line Total = Quantity × Unit Purchase Price`

For the complete purchase:

`Purchase Total = Sum of All Line Totals`

### Example

A business purchases 20 notebooks at ₹30 each.

Purchase total:

`20 × ₹30 = ₹600`

If the previous stock was 15 notebooks, the new stock becomes:

`15 + 20 = 35 notebooks`

### Business rules

- Purchase quantity must be a positive integer.
- Unit purchase price cannot be negative.
- A purchase must contain at least one valid item.
- Product and supplier references must exist.
- Saving the purchase and increasing stock must occur in one database transaction.
- If the operation fails, the database must roll back the entire purchase.
- The system must prevent the same purchase from being applied twice.

### Acceptance criteria

A successfully recorded purchase increases the stock of the relevant products and appears in purchase history.

---

## 4.6 Sales Management

### Purpose

Record outgoing stock when products are sold.

### Sales workflow

1. Open Sales Management.
2. Select the product.
3. Enter the quantity sold.
4. Retrieve the current selling price.
5. Calculate the line total.
6. Add more products if necessary.
7. Review the final amount.
8. Confirm the sale.
9. Decrease stock.
10. Save the transaction and display a confirmation.

### Sales fields

**Sale header:**

- Sale ID.
- Sale date.
- Total amount.
- Optional notes.

**Sale items:**

- Product ID.
- Quantity.
- Unit selling price.
- Line total.

### Calculation

`Line Total = Quantity Sold × Unit Selling Price`

`Sale Total = Sum of All Line Totals`

### Example

A customer purchases 3 notebooks at ₹45 each.

`3 × ₹45 = ₹135`

If the previous stock was 35 notebooks, the remaining stock becomes:

`35 - 3 = 32 notebooks`

### Business rules

- Quantity must be a positive integer.
- Selling price cannot be negative.
- The requested quantity cannot exceed available stock.
- Inactive products cannot be used in new sales.
- A sale must contain at least one valid item.
- Saving the sale and decreasing stock must occur in one database transaction.
- Failed transactions must not change stock.
- A sale must not be recorded twice because of an accidental repeated submission.

### Acceptance criteria

A completed sale reduces stock accurately, appears in sales history, and updates the dashboard.

The system must reject attempts to sell more units than are available.

---

## 4.7 Stock Management

### Purpose

Provide an accurate view of current stock levels.

### Features

- View stock for all active products.
- Search by SKU or name.
- Filter by category.
- Sort by available quantity.
- Identify low-stock products.
- Identify out-of-stock products.
- View stock movement history.

### Stock calculation

The system should maintain a current stock quantity for efficient queries.

The intended relationship is:

`Current Stock = Opening Stock + Stock In - Stock Out + Adjustments`

For the first version:

- Purchases increase stock.
- Sales decrease stock.
- Authorized positive adjustments increase stock.
- Authorized negative adjustments decrease stock.

Every adjustment must have a reason and be recorded in the transaction history.

The opening stock should be established through a controlled opening-stock or initial-stock adjustment operation.

### Stock statuses

| Condition | Status |
|---|---|
| Available stock is greater than the minimum stock level | In Stock |
| Available stock is positive but at or below the minimum stock level | Low Stock |
| Available stock equals zero | Out of Stock |

An out-of-stock product should be classified separately even if its minimum stock threshold is zero.

### Stock movement history

Each stock movement should record:

- Movement ID.
- Product ID.
- Movement type.
- Quantity change.
- Previous stock quantity.
- Resulting stock quantity.
- Reference transaction, if applicable.
- Timestamp.
- Reason, where applicable.

### Acceptance criteria

Stock quantities remain consistent with recorded transactions.

The user can trace stock changes to the relevant purchase, sale, or adjustment.

---

## 4.8 Low-Stock Alerts

### Purpose

Help users identify products that require replenishment.

### Functionality

The application compares each product's current stock with its configured minimum stock level.

When the current quantity reaches or falls below the threshold, the product is displayed in the low-stock section.

### Example

Product: USB Cable

Current stock: 4

Minimum stock level: 10

Status: Low Stock

### Requirements

- Display a low-stock count on the dashboard.
- Highlight low-stock products in the inventory table.
- Display out-of-stock products separately.
- Update stock status after purchases, sales, and adjustments.
- Allow users to filter the inventory by stock status.

### Acceptance criteria

The alert status changes automatically when the stock quantity changes.

---

## 4.9 Search, Filtering, and Sorting

### Purpose

Make it easy to locate specific records.

### Product search

Users should be able to search by:

- Product name.
- SKU.
- Category.

### Transaction filters

Users should be able to filter sales and purchases by:

- Transaction ID.
- Date range.
- Product.
- Supplier, for purchases.

### Sorting

The product table should support sorting by:

- Product name.
- Available stock.
- Purchase price.
- Selling price.
- Category.

### Acceptance criteria

Searches should return matching records without modifying the underlying database.

Empty results should be handled gracefully.

---

## 4.10 Reports

### Purpose

Provide useful information about stock and business transactions.

### Required reports

#### A. Inventory Report

Displays:

- SKU.
- Product name.
- Category.
- Current stock.
- Purchase price.
- Selling price.
- Stock status.

#### B. Low-Stock Report

Displays products whose stock is at or below their minimum threshold.

#### C. Sales Report

Displays:

- Sale ID.
- Date.
- Products sold.
- Quantities.
- Selling prices.
- Total sales amount.

#### D. Purchase Report

Displays:

- Purchase ID.
- Date.
- Supplier.
- Products purchased.
- Quantities.
- Purchase prices.
- Total purchase amount.

#### E. Stock Movement Report

Displays the recorded stock increases, decreases, and adjustments.

### Report filters

Where appropriate, reports should support:

- Date range.
- Product.
- Category.
- Supplier.
- Stock status.

### Acceptance criteria

Reports must use database records as their source of truth and display totals consistent with the underlying transactions.

---

## 4.11 CSV Import and Export

This module is essential because CSV is one of the three required Python concepts.

### A. Export Products to CSV

Users can export product records to a CSV file.

Suggested columns:

`SKU, Product Name, Category, Purchase Price, Selling Price, Current Stock, Minimum Stock`

### B. Import Products from CSV

Users can select a CSV file containing product information.

The system should:

1. Read the file using Python's CSV module.
2. Check that the required columns exist.
3. Validate each row.
4. Identify duplicate SKUs.
5. Identify missing or invalid values.
6. Import valid rows.
7. Report skipped rows and errors.

### C. Export Sales to CSV

The system should export sales transaction information for reporting.

### D. Export Purchases to CSV

The system should export purchase transaction information.

### E. Error handling

The application must handle:

- Missing files.
- Incorrect file formats.
- Missing columns.
- Invalid quantities.
- Invalid prices.
- Duplicate SKUs.
- Empty files.
- Incorrectly formatted rows.

### Important stock-integrity rule

Importing a product file must not silently overwrite current stock quantities.

The import workflow should distinguish between:

- Creating new products.
- Updating product details.
- Performing an authorized stock adjustment.

Stock changes must be recorded in the stock movement history.

### Acceptance criteria

Users can export records to CSV and import valid product records without corrupting existing data.

The application must provide a summary of successful imports and rejected rows.

---

# 5. User Interface Requirements

## 5.1 Interface Design

The application should have a clean, simple desktop interface suitable for a small business.

The interface should prioritize readability, clear navigation, and easy data entry.

### Main layout

The application should use a sidebar and a main content area.

**Sidebar navigation:**

1. Dashboard
2. Products
3. Categories
4. Suppliers
5. Purchases
6. Sales
7. Stock
8. Reports
9. CSV Import/Export
10. Settings

The main area should display the selected page.

### Dashboard layout

The dashboard should contain:

- Summary cards.
- A recent-transactions table.
- A low-stock products table.
- Quick-action buttons for adding products, recording purchases, and recording sales.

### Products page

The products page should contain:

- Search field.
- Category filter.
- Add Product button.
- Product table.
- Edit and deactivate actions.
- CSV import/export actions.

### Sales and purchases pages

These pages should use a transaction form containing:

- Transaction date.
- Product selector.
- Quantity.
- Unit price.
- Line total.
- Item list.
- Grand total.
- Save and cancel buttons.

### Interface behavior

- Required fields should be clearly indicated.
- Errors should appear near the relevant form or in readable dialogs.
- Destructive operations should require confirmation.
- Successful actions should display a confirmation message.
- Tables should display an appropriate message when no records exist.
- Long operations should not freeze the interface.

For the initial project, Tkinter with ttk widgets is sufficient. A more elaborate UI framework is not required.

---

# 6. Python Concepts and Their Required Implementation

The project must demonstrate the exact three concepts listed for Inventory & Stock Management System in the supplied project-ideas PDF: OOP, SQLite, and CSV.

## 6.1 Object-Oriented Programming (OOP)

OOP must be used in the actual implementation rather than mentioned only in the project report.

### Proposed classes

| Class | Responsibility |
|---|---|
| Product | Represent product information and product-related behavior |
| Category | Represent product categories |
| Supplier | Represent supplier information |
| Purchase | Represent a purchase transaction |
| PurchaseItem | Represent an individual item within a purchase |
| Sale | Represent a sale transaction |
| SaleItem | Represent an individual item within a sale |
| InventoryService | Apply stock changes and enforce stock rules |
| ProductRepository | Perform product-related database operations |
| PurchaseRepository | Perform purchase-related database operations |
| SaleRepository | Perform sales-related database operations |
| CSVService | Import and export CSV files |
| ReportService | Generate inventory and transaction reports |

### Example

```python
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:
    sku: str
    name: str
    purchase_price: Decimal
    selling_price: Decimal
    current_stock: int
    minimum_stock: int

    @property
    def is_low_stock(self) -> bool:
        return (
            self.current_stock > 0
            and self.current_stock <= self.minimum_stock
        )

    @property
    def is_out_of_stock(self) -> bool:
        return self.current_stock == 0
```

This example demonstrates:

- Class definition.
- Object creation.
- Attributes.
- Methods and properties.
- Encapsulation of product-related behavior.

The production implementation must also validate input and protect stock changes through the inventory service.

## 6.2 SQLite Database

SQLite must be used as the primary persistent storage system.

### Required database operations

- `INSERT` to create records.
- `SELECT` to retrieve records.
- `UPDATE` to update permitted fields.
- `DELETE` only where deletion is safe and appropriate.
- SQL filtering and sorting.
- Primary and foreign keys.
- Transactions using `COMMIT` and `ROLLBACK`.

### Database requirements

- Enable foreign-key enforcement.
- Use parameterized SQL queries.
- Avoid constructing SQL queries by directly concatenating user input.
- Use transactions for purchases, sales, and stock adjustments.
- Preserve historical transaction records.
- Store monetary amounts in a consistent representation, such as integer paise or validated decimal strings.

## 6.3 CSV

CSV must be used for genuine data exchange.

### Required demonstrations

1. Export all active products.
2. Import products from a CSV file.
3. Export sales reports.
4. Export purchase reports.
5. Handle malformed rows and duplicate records.

The implementation should use Python's `csv` module, including `csv.reader`, `csv.DictReader`, or `csv.DictWriter` as appropriate.

The project must demonstrate actual reading and writing of CSV files.

---

# 7. Database Design

The application will use SQLite with the following tables.

## 7.1 Categories Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Category identifier |
| name | TEXT UNIQUE | Category name |
| is_active | INTEGER | Active status |
| created_at | TEXT | Creation timestamp |

## 7.2 Suppliers Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Supplier identifier |
| name | TEXT | Supplier name |
| contact_person | TEXT | Contact person |
| phone | TEXT | Phone number |
| email | TEXT | Email address |
| address | TEXT | Supplier address |
| notes | TEXT | Additional notes |
| is_active | INTEGER | Active status |
| created_at | TEXT | Creation timestamp |

## 7.3 Products Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Product identifier |
| sku | TEXT UNIQUE | Unique stock-keeping unit |
| name | TEXT | Product name |
| category_id | INTEGER | Category reference |
| description | TEXT | Product description |
| purchase_price | INTEGER or TEXT | Price in the chosen exact-money representation |
| selling_price | INTEGER or TEXT | Price in the chosen exact-money representation |
| current_stock | INTEGER | Current quantity |
| minimum_stock | INTEGER | Reorder threshold |
| is_active | INTEGER | Active status |
| created_at | TEXT | Creation timestamp |
| updated_at | TEXT | Last update timestamp |

For a simple and reliable implementation, storing money as integer paise is recommended. For example, ₹125.50 is stored as 12550 paise.

The application can convert paise into rupees when displaying values.

## 7.4 Purchases Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Purchase identifier |
| supplier_id | INTEGER | Supplier reference |
| purchase_date | TEXT | Purchase date and time |
| total_amount | INTEGER | Total in paise |
| reference_number | TEXT | Optional supplier reference |
| notes | TEXT | Additional notes |
| created_at | TEXT | Record creation timestamp |

## 7.5 Purchase Items Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Purchase item identifier |
| purchase_id | INTEGER | Purchase reference |
| product_id | INTEGER | Product reference |
| quantity | INTEGER | Purchased quantity |
| unit_price | INTEGER | Unit price in paise |
| line_total | INTEGER | Line total in paise |

## 7.6 Sales Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Sale identifier |
| sale_date | TEXT | Sale date and time |
| total_amount | INTEGER | Total in paise |
| notes | TEXT | Additional notes |
| created_at | TEXT | Record creation timestamp |

## 7.7 Sale Items Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Sale item identifier |
| sale_id | INTEGER | Sale reference |
| product_id | INTEGER | Product reference |
| quantity | INTEGER | Quantity sold |
| unit_price | INTEGER | Selling price in paise |
| line_total | INTEGER | Line total in paise |

## 7.8 Stock Movements Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY | Movement identifier |
| product_id | INTEGER | Product reference |
| movement_type | TEXT | Opening stock, purchase, sale, or adjustment |
| quantity_change | INTEGER | Positive or negative stock change |
| previous_stock | INTEGER | Stock before movement |
| resulting_stock | INTEGER | Stock after movement |
| purchase_id | INTEGER | Optional purchase reference |
| sale_id | INTEGER | Optional sale reference |
| reason | TEXT | Explanation for manual adjustments |
| created_at | TEXT | Movement timestamp |

### Database integrity rules

- Product SKU must be unique.
- Quantities must be non-negative in product records.
- Stock movements must have valid references.
- Purchase and sale items must reference valid products.
- Deactivating a product must not erase its transaction history.
- A failed transaction must not leave partially updated stock.
- Monetary totals must be calculated and validated by the application.
- Foreign-key enforcement must be enabled on each database connection.

---

# 8. Application Architecture

The project should use a simple layered architecture.

## 8.1 Presentation Layer

**Responsibility:** Display information and collect user input.

Components:

- Dashboard UI.
- Product forms.
- Supplier forms.
- Purchase forms.
- Sales forms.
- Report screens.
- CSV import/export dialogs.

Technology: Tkinter and ttk.

## 8.2 Business Logic Layer

**Responsibility:** Apply rules and calculate results.

Components:

- InventoryService.
- ProductService.
- PurchaseService.
- SalesService.
- ReportService.
- Validation functions.

Examples:

- Prevent negative stock.
- Calculate transaction totals.
- Check low-stock conditions.
- Validate imported records.
- Ensure stock changes are consistent.

## 8.3 Data Access Layer

**Responsibility:** Read and write database records.

Components:

- ProductRepository.
- CategoryRepository.
- SupplierRepository.
- PurchaseRepository.
- SaleRepository.
- StockMovementRepository.

Technology: Python's built-in SQLite support.

## 8.4 File Processing Layer

**Responsibility:** Handle external CSV files.

Component:

- CSVService.

Functions:

- Import products.
- Export products.
- Export sales.
- Export purchases.
- Validate CSV headers and rows.
- Produce import summaries.

### Request flow

`User Interface → Business Logic → Repository → SQLite`

For CSV import:

`CSV File → CSVService → Validation → Business Logic → Repository → SQLite`

For CSV export:

`SQLite → Repository → Report/Export Logic → CSV File`

This architecture keeps database operations separate from the interface and makes the project easier to test.

---

# 9. Non-Functional Requirements

## 9.1 Usability

- The interface should be understandable to a first-time user.
- Common operations should require minimal steps.
- Errors should explain what the user needs to correct.
- Stock status should be visually distinguishable.

## 9.2 Performance

For the initial project, the application should support at least 5,000 product records and a substantial transaction history on a typical student or office computer.

Product search, dashboard calculations, and ordinary database operations should remain responsive at this scale.

## 9.3 Reliability

- Database operations must use appropriate transactions.
- Failed purchases and sales must roll back.
- Invalid input must not corrupt records.
- Database errors must be handled gracefully.
- The application must not silently discard failed imports.

## 9.4 Security

- Use parameterized SQL queries.
- Validate user input.
- Restrict database writes to the appropriate application services.
- Avoid exposing database internals in error messages.
- Confirm potentially destructive actions.
- Store the database in a predictable, writable application-data directory.

Because the initial version is a single-user desktop application, a full authentication system is not required.

## 9.5 Maintainability

- Use meaningful class and function names.
- Separate UI code from business logic.
- Avoid duplicating stock calculation logic.
- Document important functions.
- Keep database schema creation and initialization separate from normal application workflows.

## 9.6 Portability

The application should run on a supported desktop operating system with a compatible Python installation.

Packaging it as a standalone executable can be considered after the application works correctly.

---

# 10. Error Handling and Edge Cases

The application must handle the following situations.

### Product Management

- Duplicate SKU.
- Empty product name.
- Invalid price.
- Negative minimum stock.
- Missing category.
- Editing an inactive product.

### Purchases

- Empty purchase.
- Invalid quantity.
- Missing supplier.
- Invalid price.
- Database failure while updating stock.
- Repeated submission of the same transaction.

### Sales

- Sale quantity greater than available stock.
- Sale of an inactive product.
- Invalid quantity.
- Empty sale.
- Database failure during stock reduction.

### CSV

- File does not exist.
- File is empty.
- Incorrect headers.
- Duplicate SKUs.
- Invalid quantities or prices.
- Incorrect encoding.
- Partially invalid files.
- File permission errors.

### Database

- Database cannot be opened.
- Required table is missing.
- Foreign-key constraint fails.
- Database transaction fails.
- Application closes during a transaction.

For every error, the system should display a meaningful message and preserve the integrity of existing data.

---

# 11. Testing Requirements

## 11.1 Unit Testing

Test individual functions and classes.

Examples:

- Product validation.
- Low-stock calculation.
- Purchase total calculation.
- Sale total calculation.
- CSV row validation.
- Stock adjustment validation.

## 11.2 Integration Testing

Test complete workflows involving multiple components.

Examples:

- Create a product and retrieve it from SQLite.
- Record a purchase and verify the stock increase.
- Record a sale and verify the stock decrease.
- Import a CSV file and verify inserted records.
- Export products and verify the generated CSV.
- Force a transaction failure and verify rollback.

## 11.3 User Interface Testing

Verify that:

- Forms accept valid data.
- Validation errors appear correctly.
- Tables display the correct information.
- Navigation works.
- Confirmation dialogs appear for destructive actions.
- The interface refreshes after successful operations.

## 11.4 Acceptance Testing

| Test ID | Test | Expected Result |
|---|---|---|
| TC-01 | Add a valid product | Product is saved |
| TC-02 | Add duplicate SKU | Duplicate is rejected |
| TC-03 | Record a purchase | Stock increases |
| TC-04 | Record a sale | Stock decreases |
| TC-05 | Sell more than available stock | Sale is rejected |
| TC-06 | Reach the minimum stock threshold | Low-stock alert appears |
| TC-07 | Export products | Valid CSV file is created |
| TC-08 | Import valid CSV | Products are imported |
| TC-09 | Import invalid CSV rows | Errors are reported |
| TC-10 | Restart application | Existing records remain |
| TC-11 | Force a failed stock transaction | Database changes are rolled back |
| TC-12 | Deactivate a product with history | Historical records remain available |

---

# 12. Development Plan

The project should be developed in manageable stages.

## Phase 1: Project Setup

Tasks:

- Install Python.
- Set up the project directory.
- Create the virtual environment if needed.
- Create the initial Tkinter window.
- Establish the database connection.
- Initialize the database schema.

Deliverable: Application opens and connects to SQLite.

## Phase 2: Core Product Management

Tasks:

- Create the Product class.
- Implement product validation.
- Build product forms.
- Implement product repositories.
- Add product listing, searching, editing, and deactivation.
- Implement category management.

Deliverable: Working product management module.

## Phase 3: Supplier Management

Tasks:

- Create the Supplier class.
- Design the supplier database table.
- Implement supplier operations.
- Build supplier forms.
- Add supplier search.

Deliverable: Working supplier module.

## Phase 4: Purchase Management

Tasks:

- Create purchase-related classes.
- Implement purchase forms.
- Calculate purchase totals.
- Update stock transactionally.
- Record stock movements.

Deliverable: Working purchase and stock-in module.

## Phase 5: Sales Management

Tasks:

- Create sale-related classes.
- Implement sales forms.
- Calculate totals.
- Validate available stock.
- Decrease stock transactionally.
- Record stock movements.

Deliverable: Working sales and stock-out module.

## Phase 6: Dashboard and Reports

Tasks:

- Calculate dashboard metrics.
- Display low-stock alerts.
- Implement sales and purchase reports.
- Implement stock movement history.
- Add report filters.

Deliverable: Working dashboard and reports.

## Phase 7: CSV Integration

Tasks:

- Implement product CSV export.
- Implement product CSV import.
- Validate imported records.
- Implement sales and purchase exports.
- Display import success and error summaries.

Deliverable: Complete CSV functionality.

## Phase 8: Testing and Finalization

Tasks:

- Run unit and integration tests.
- Test invalid inputs.
- Test transaction rollback.
- Verify database persistence.
- Improve error messages.
- Prepare screenshots.
- Prepare project documentation.
- Prepare the demonstration and viva explanation.

Deliverable: Tested application ready for submission.

---

# 13. Suggested Project Folder Structure

```text
inventory-management-system/
│
├── main.py
├── requirements.txt
├── README.md
│
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── schema.py
│
├── models/
│   ├── __init__.py
│   ├── product.py
│   ├── category.py
│   ├── supplier.py
│   ├── purchase.py
│   └── sale.py
│
├── repositories/
│   ├── __init__.py
│   ├── product_repository.py
│   ├── category_repository.py
│   ├── supplier_repository.py
│   ├── purchase_repository.py
│   └── sale_repository.py
│
├── services/
│   ├── __init__.py
│   ├── inventory_service.py
│   ├── product_service.py
│   ├── purchase_service.py
│   ├── sales_service.py
│   ├── report_service.py
│   └── csv_service.py
│
├── ui/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── products.py
│   ├── categories.py
│   ├── suppliers.py
│   ├── purchases.py
│   ├── sales.py
│   ├── stock.py
│   └── reports.py
│
├── exports/
│   └── .gitkeep
│
└── tests/
    ├── test_products.py
    ├── test_inventory.py
    ├── test_purchases.py
    ├── test_sales.py
    └── test_csv.py
```

The database file should be created in an appropriate writable application-data directory rather than relying on the current working directory.

The exports directory is intended for generated reports, not as the primary database.

---

# 14. Expected Project Deliverables

At completion, the project should include:

1. A working Python desktop application.
2. SQLite database initialization and persistence.
3. Product management.
4. Category and supplier management.
5. Purchase and sales processing.
6. Stock calculations and movement history.
7. Low-stock alerts.
8. Inventory and transaction reports.
9. CSV import/export.
10. Unit and integration tests.
11. Source code with a clear folder structure.
12. A README containing installation and usage instructions.
13. Project report and relevant screenshots.
14. A demonstration covering OOP, SQLite, and CSV.

---

# 15. Project Success Criteria

The project will be considered successful when:

- Users can create and manage products.
- Product information persists after the application closes.
- Purchases increase stock accurately.
- Sales decrease stock accurately.
- Negative stock is prevented.
- Stock movements can be traced.
- Low-stock alerts work correctly.
- CSV import and export function correctly.
- Invalid inputs are handled safely.
- Database transactions protect stock integrity.
- The application runs reliably during the final demonstration.
- All three required Python concepts are demonstrably implemented.

---

# 16. Future Enhancements

After completing the core project, the following features may be considered:

- Barcode scanning.
- PDF invoice generation.
- Supplier purchase-order generation.
- User login and role-based permissions.
- Multiple business locations.
- Cloud database synchronization.
- Web-based administration.
- Advanced sales analytics.
- Automatic stock replenishment suggestions.
- Graphical charts for sales and inventory trends.

These features are optional and must not delay completion of the core project.

---

# 17. Final Recommendation

The first version should prioritize correctness and simplicity over unnecessary complexity.

The recommended implementation order is:

1. Database setup.
2. Product and category management.
3. Supplier management.
4. Purchase processing.
5. Sales processing.
6. Stock tracking.
7. Dashboard and reports.
8. CSV import/export.
9. Testing and documentation.

The project should use OOP to structure its code, SQLite to store persistent records, and CSV to exchange data.

**Final project title: Inventory & Stock Management System Using Python, SQLite, and CSV.**
