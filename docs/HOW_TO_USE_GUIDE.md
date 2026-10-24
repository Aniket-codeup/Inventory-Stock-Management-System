# User Manual & Operating Guide: Inventory & Stock Management System

A practical, step-by-step handbook on how to operate your Inventory & Stock Management System — covering daily inventory operations, recording purchases (stock-in), processing sales (stock-out), performing stock adjustments, managing low-stock warnings, and importing/exporting CSV data.

---

## Table of Contents
1. [Getting Started & First Launch](#1-getting-started--first-launch)
2. [Executive Dashboard: Overview & Quick Actions](#2-executive-dashboard-overview--quick-actions)
3. [Managing Products & Pricing](#3-managing-products--pricing)
4. [Organizing Categories & Departments](#4-organizing-categories--departments)
5. [Managing Suppliers & Vendors](#5-managing-suppliers--vendors)
6. [Purchases (Stock-In): Receiving New Inventory](#6-purchases-stock-in-receiving-new-inventory)
7. [Sales (Stock-Out): Point of Sale (POS) Checkout](#7-sales-stock-out-point-of-sale-pos-checkout)
8. [Stock Control, Audits & Adjustments](#8-stock-control-audits--adjustments)
9. [Generating Business Reports & Valuation](#9-generating-business-reports--valuation)
10. [CSV Data Interchange: Bulk Import & Export](#10-csv-data-interchange-bulk-import--export)
11. [System Settings & Demo Data Utilities](#11-system-settings--demo-data-utilities)

---

## 1. Getting Started & First Launch

### 1.1 Starting the Application
Open a terminal in the project directory (`d:\New folder (4)\inventory-management-system`) and run:
```bash
python main.py
```
The application will launch maximized/centered with a dark sidebar on the left and the main operational area on the right.

### 1.2 Quick Setup with Sample Data (Optional)
If you are testing the system for the first time or preparing for a live demonstration:
1. Click **⚙️ Settings & Demo Data** at the bottom of the left sidebar.
2. Click **✨ Load Sample Demonstration Data**.
3. Confirm the prompt. The database will immediately be populated with realistic electronics, stationery, groceries, suppliers, varied stock levels, purchase orders, and sales receipts.
4. Click **📊 Dashboard** in the sidebar to view live metrics!

---

## 2. Executive Dashboard: Overview & Quick Actions

The **Dashboard** is the first screen you see on startup. It gives you a real-time health check of your entire business.

### 2.1 Understanding Dashboard Metrics
- **Active Products:** Total count of active items currently in your catalog.
- **Total Stock Units:** Total count of physical units stored in your warehouse.
- **Low-Stock Alerts:** Products whose on-hand quantity has dropped to or below their configured minimum threshold.
- **Out of Stock:** Products with zero remaining units on the shelf.
- **Today's Sales (₹):** Total gross revenue generated from customer sales today.
- **Today's Purchases (₹):** Total expenditures on supplier deliveries recorded today.
- **Total All-Time Sales (₹):** Cumulative sales revenue across all time.
- **Inventory Valuation (₹):** Total asset value of your physical stock calculated at cost (`Current Stock × Purchase Price`).

### 2.2 Using Dashboard Quick Action Buttons
At the top of the dashboard, you have quick shortcut buttons:
- **➕ Add Product:** Directly opens the new product creation form.
- **📥 Record Purchase:** Jumps directly to the Purchase Order builder.
- **🛒 Record Sale:** Jumps directly to Point of Sale (POS) checkout.
- **⚖️ Stock Adjustment:** Opens the manual stock adjustment modal dialog.
- **🔄 Refresh Data:** Instantly re-queries the database for the newest totals.

### 2.3 Dashboard Alert Panels
- **⚠️ Low-Stock & Depleted Items (Left Panel):** Lists all items needing reordering with amber/red status badges. Click **View All** to jump to the full stock control table.
- **🕒 Recent Stock Movements (Right Panel):** Live audit stream showing the latest stock changes, movement types (`PURCHASE`, `SALE`, `ADJUSTMENT`), and resulting quantities. Click **Full Audit Log** to view all historical movements.

---

## 3. Managing Products & Pricing

Navigate to **📦 Products Catalog** in the sidebar.

### 3.1 Adding a New Product
1. Click **➕ Add Product** on the top toolbar.
2. Fill out the dialog form:
   - **SKU Code:** Unique Stock Keeping Unit (e.g. `ELEC-USB-01` or `STAT-PEN-BL`). *Required, must be unique.*
   - **Product Name:** Descriptive title (e.g. `Braided USB-C Cable 1m`). *Required.*
   - **Category:** Select from the dropdown (e.g. `Electronics`). *Required.*
   - **Purchase Price (₹):** What you pay the supplier per unit (e.g. `120.00`).
   - **Selling Price (₹):** What you charge customers per unit (e.g. `249.00`).
   - **Min Stock Alert Level:** Reorder threshold (e.g. `10`). When stock drops to or below this level, an alert is triggered.
   - **Initial Stock Quantity:** Opening inventory on hand (e.g. `25`). If greater than zero, an opening stock movement will automatically be logged.
   - **Description:** Optional notes or product specifications.
3. Click **Save Product**.

### 3.2 Searching & Filtering Products
- **Search Bar:** Type any part of a product's name, SKU, or description. Results filter dynamically as you type.
- **Category Filter:** Filter by specific department (e.g. `Electronics` or `Stationery`).
- **Status Filter:** Select `In Stock`, `Low Stock`, or `Out of Stock` to instantly isolate items needing attention.

### 3.3 Editing a Product
1. Select an item in the table and click **✏️ Edit Selected** (or simply double-click the row).
2. Modify the product's name, category, purchase price, selling price, minimum alert level, or description.
3. **Stock Protection Rule:** Notice that the current stock count is **read-only** here. You cannot arbitrarily tamper with stock quantities from the product edit window — this preserves complete transaction integrity.
4. Click **Save Product**.

### 3.4 Deactivating a Product (Soft Delete)
If you stop selling a product:
1. Select the product and click **🚫 Deactivate**.
2. Confirm the prompt.
3. The product is safely marked inactive: it will no longer appear in POS sales or active inventory lists, but **all past sales, purchases, and financial reports will permanently preserve its historical records**.

---

## 4. Organizing Categories & Departments

Navigate to **📁 Categories** in the sidebar.

### 4.1 Adding a Category
1. Locate the **New Category Name** input box on the top toolbar.
2. Type the category name (e.g., `Hardware` or `Packaging Materials`).
3. Click **➕ Add Category** (or press `Enter`).

### 4.2 Renaming a Category
1. Select the category row in the table.
2. Click **✏️ Rename Selected**.
3. Type the new name and click **OK**. All associated products automatically reflect the updated category name.

### 4.3 Safe Category Deactivation
1. Select the category and click **🚫 Deactivate Category**.
2. **Built-in Safety Check:** If any active products are currently assigned to this category, the system will block deactivation and inform you to reassign or deactivate the products first.

---

## 5. Managing Suppliers & Vendors

Navigate to **🏢 Suppliers** in the sidebar.

### 5.1 Adding a Vendor Profile
1. Click **➕ Add Supplier**.
2. Enter the supplier details:
   - **Supplier Company:** Name of company or distributor (e.g., `Apex Electronics Ltd.`). *Required.*
   - **Contact Person:** Name of representative (e.g., `Rajesh Sharma`).
   - **Phone Number:** Mobile or landline (e.g., `+91 98765 43210`).
   - **Email Address:** Vendor email (e.g., `rajesh@apexelectronics.in`). *Format is automatically verified.*
   - **Physical Address & Notes:** Delivery address, payment terms, or discount notes.
3. Click **Save Supplier**.

### 5.2 Editing or Deactivating Suppliers
- Select a supplier and click **✏️ Edit Selected** to update phone numbers or contacts.
- Click **🚫 Deactivate** to archive a vendor without losing past purchase orders.

---

## 6. Purchases (Stock-In): Receiving New Inventory

When you receive a shipment from a vendor, use **📥 Purchases** to increase stock quantities accurately and record expenditures.

### 6.1 Recording a Purchase Order Step-by-Step
1. Click the **📥 Record New Purchase** tab.
2. **Order Header:**
   - **Supplier:** Choose the vendor who delivered the goods.
   - **Date:** Auto-filled with current date and time (editable).
   - **Ref / Invoice #:** Enter the supplier's delivery challan or invoice number (e.g., `INV-2026-884`).
3. **Adding Items to the Purchase Order:**
   - **Select Product:** Choose the product from the dropdown.
   - **Cost Price (₹):** Auto-filled with the default product cost price. You can adjust it if this specific shipment had a discounted or increased unit cost.
   - **Quantity:** Enter how many units were received (e.g., `20`).
   - Click **➕ Add to Order** (or press `Enter`).
   - The item appears in the order table with its line total (`Quantity × Cost Price`).
4. **Repeat step 3** for all items included in the shipment.
5. **Review Grand Total:**
   - The summary card on the right calculates the total payable amount in real time.
   - Enter optional notes (e.g., `Paid via NEFT / Net 30 terms`).
6. Click **💾 Save Purchase & Update Stock**.

### 6.2 What Happens Behind the Scenes?
The system executes an **atomic database transaction**:
- It creates a master `purchases` record.
- It inserts each item into `purchase_items`.
- It increments the `current_stock` for every product received (`New Stock = Old Stock + Quantity`).
- It logs a `PURCHASE` movement in `stock_movements` for every item.

### 6.3 Viewing Purchase History & Receipts
1. Click the **📜 Purchase History & Audit** tab.
2. View past orders, filter by supplier, or double-click any row to open the **Purchase Order Details** modal showing all line items, unit costs, and total expenditure.

---

## 7. Sales (Stock-Out): Point of Sale (POS) Checkout

When customers buy goods, use **🛒 Sales** to process orders, enforce stock limits, and decrease on-hand inventory.

### 7.1 Processing a Customer Sale Step-by-Step
1. Click the **🛒 Record New Sale** tab.
2. **Sale Header:**
   - **Date & Time:** Defaults to now.
   - **Customer / Order Ref:** Enter customer name, invoice #, or leave as `Walk-in Customer`.
3. **Adding Products to Sale Cart:**
   - **Select Product:** Pick an item from the dropdown. Notice the green **Avail: X** indicator showing how many units are physically available in your warehouse right now!
   - **Selling Price (₹):** Defaults to product selling price (editable for custom customer discounts).
   - **Quantity:** Enter units being sold (e.g., `3`).
   - Click **➕ Add to Sale** (or press `Enter`).
4. **Repeat** to add all products the customer is purchasing.
5. **Review Grand Total:**
   - Check the total due displayed in large green font.
   - Enter optional notes.
6. Click **✅ Complete & Confirm Sale**.
7. A confirmation popup appears: stock is instantly deducted and a receipt number is generated.

### 7.2 Over-Selling Prevention (Stock Safety Guarantee)
Try entering a quantity **greater than the available stock** (for example, trying to sell 15 units when only 5 are in stock):
- The system will **reject** the entry immediately with an `Insufficient Stock` warning.
- It is mathematically impossible to sell into negative stock in this system.

### 7.3 Viewing Sales History & Receipts
1. Click the **📜 Sales History & Receipts** tab.
2. View all completed sales sorted by most recent first.
3. Double-click any sale row (or select it and click **🧾 View Selected Sale Receipt**) to open the itemized customer sales receipt dialog showing line items and totals.

---

## 8. Stock Control, Audits & Adjustments

Navigate to **⚖️ Stock Control & Audit** in the sidebar. This module is the operational core for warehouse managers.

### 8.1 Monitoring Warehouse Stock Levels
In the **📦 Current Stock Levels** tab:
- Every active product is displayed with its available stock and threshold.
- Color badges indicate item health:
  - 🟢 **In Stock:** Inventory is above the minimum threshold.
  - 🟡 **Low Stock:** Inventory is at or below the reorder point. Reorder soon!
  - 🔴 **Out of Stock:** Zero inventory. Replenishment required immediately.
- Use the **Search**, **Category**, and **Status** dropdowns to filter.

### 8.2 Performing an Authorized Stock Adjustment
Sometimes inventory changes outside of purchases and sales — such as water damage, expired goods, audit discrepancies, or customer returns.
1. Select the product in the table.
2. Click **⚖️ Stock Adjustment** (or double-click the row).
3. In the modal dialog:
   - **Product:** Verify the selected product.
   - **Action Type:**
     - `Add Stock (+)` — Found extra units during audit.
     - `Deduct Stock (-)` — Stock count correction.
     - `Damaged / Expired (-)` — Damaged units removed from shelves.
     - `Customer Return (+)` — Customer returned unopened product.
   - **Quantity:** Enter the number of units to adjust (e.g. `2`).
   - **Audit Reason:** *Mandatory.* Explain why this adjustment was made (e.g., `Damaged during warehouse transit by forklift`).
4. Click **Apply Adjustment**.
5. The stock level is updated and an immutable audit movement is logged with your reason!

### 8.3 Tracing Stock Movement Audit History
Click the **🔄 Movement History & Audit Trail** tab:
- Every stock change that has ever occurred is listed with:
  - Exact timestamp
  - Product SKU & Name
  - Movement Type (`PURCHASE`, `SALE`, `ADJUSTMENT`, `OPENING_STOCK`, `DAMAGE`, `RETURN`)
  - Quantity Change (`+10`, `-3`, etc.)
  - Previous Stock before the action
  - Resulting Stock after the action
  - Reference invoice # or authorized audit reason
- Use the **Movement Type** dropdown to filter exclusively by `PURCHASE`, `SALE`, or `ADJUSTMENT`.

---

## 9. Generating Business Reports & Valuation

Navigate to **📈 Business Reports** in the sidebar.

### 9.1 Report Types Available
1. **📊 Inventory Valuation:**
   - Displays all products, current stock, cost price, selling price, **Cost Valuation** (`Stock × Cost`), and **Retail Valuation** (`Stock × Retail`).
   - Filter by specific category.
2. **⚠️ Low-Stock & Replenishment:**
   - Isolates depleted and low-stock products.
   - Shows **Suggested Reorder Quantities** calculated automatically (`Minimum Level - Current Stock + 10 units`) to help you create purchase orders.
3. **📈 Sales Performance:**
   - Chronological breakdown of customer sales, items sold, revenues, and customer notes.
   - Filter by date range (e.g., `From: 2026-10-01` `To: 2026-10-24`).
4. **📥 Procurement & Purchases:**
   - Chronological vendor purchases, invoice numbers, quantities received, and expenditures.
   - Filter by date range.

### 9.2 Exporting Reports to CSV
Every report tab has an **📥 Export to CSV** button on the top right:
1. Click **Export to CSV**.
2. Choose where to save the file on your computer (e.g., `inventory_valuation_october.csv`).
3. Click **Save**. Open the CSV in Microsoft Excel, Google Sheets, or LibreOffice Calc for printing or accounting!

---

## 10. CSV Data Interchange: Bulk Import & Export

Navigate to **📄 CSV Import / Export** in the sidebar. This module is essential for bulk onboarding or migrating records from spreadsheets.

### 10.1 Bulk Importing Products from CSV
1. Open the **📥 Import Products from CSV** tab.
2. **Download Template:** Click **📄 Download Sample CSV Template** and save it.
3. Open the downloaded CSV in Excel and fill in your products:
   - Required columns: `SKU`, `Product Name`, `Category`, `Purchase Price`, `Selling Price`.
   - Optional columns: `Current Stock` (initial opening stock), `Minimum Stock`, `Description`.
   - *Tip:* New category names in your CSV will be created automatically!
4. **Select & Preview File:**
   - Click **📂 Browse CSV File...** and select your filled CSV.
   - The **CSV File Data Preview** table displays the first 12 rows so you can verify column headers and data formatting before importing.
5. **Execute Import:**
   - Click **🚀 Process Import**.
   - The validation engine checks each row.
   - A detailed **Import Execution Summary** dialog appears showing:
     - Total rows analyzed
     - Successfully imported count
     - Skipped rows count
     - Detailed error messages (e.g. duplicate SKUs in file, negative prices, or missing names).
   - Valid rows are saved; invalid rows are safely reported without crashing the application!

### 10.2 Bulk Data Exports
Open the **📤 Export Data to CSV** tab. You have four one-click export cards:
- **Export Products CSV:** Dumps entire active product catalog with pricing and stock levels.
- **Export Sales CSV:** Dumps all sales receipts and item summaries.
- **Export Purchases CSV:** Dumps all purchase orders, suppliers, and costs.
- **Export Movements CSV:** Dumps the complete stock movement audit log.

---

## 11. System Settings & Demo Data Utilities

Navigate to **⚙️ Settings & Demo Data** in the sidebar.

### 11.1 Live Database Diagnostics
- **File Location:** Displays the absolute path of your SQLite database (`inventory.db`).
- **File Size:** Displays real-time database storage size in kilobytes.
- **Table Row Counts:** Live record counts across all 8 tables (`Products`, `Categories`, `Suppliers`, `Purchases`, `Purchase Items`, `Sales`, `Sale Items`, `Stock Movements`).

### 11.2 Demonstration Utilities (For Presentations & Viva Exams)
- **✨ Load Sample Demonstration Data:**
  - Instantly populates realistic categories, vendors, inventory items (with in-stock, low-stock, and out-of-stock variations), purchase orders, and sales receipts.
  - Ideal for viva demonstrations or testing reports without typing 50 products manually.
- **🗑️ Purge All Records:**
  - Clears all tables for a clean slate. Requires explicit confirmation to prevent accidental data loss.

---

## Quick Reference: Daily Workflow Cheat Sheet

```text
Morning Review:
   Dashboard ──► Check "Low-Stock Alerts" & "Out of Stock" counts

Receiving Goods from Vendors:
   Purchases ──► "Record New Purchase" ──► Select Supplier & Items ──► Stock increases automatically (+)

Customer Retail Sales:
   Sales ──► "Record New Sale" ──► Select Items (Check Avail: X) ──► Stock decreases automatically (-)

Warehouse Audits / Discrepancies:
   Stock Control ──► Select Product ──► "Stock Adjustment" ──► Enter Mandatory Reason

Weekly/Monthly Management:
   Reports ──► Check "Inventory Valuation" & "Replenishment Recommendations" ──► Export to CSV
```
