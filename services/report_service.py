from datetime import datetime
from database.connection import get_db_connection
from models.product import Product
from repositories.product_repository import ProductRepository
from repositories.purchase_repository import PurchaseRepository
from repositories.sale_repository import SaleRepository
from repositories.stock_movement_repository import StockMovementRepository
from services.inventory_service import InventoryService

class ReportService:
    @staticmethod
    def get_dashboard_metrics() -> dict:
        """Fetch all dashboard metrics and KPIs in a single comprehensive call."""
        stock_summary = InventoryService.get_stock_summary()

        conn = get_db_connection()
        cursor = conn.cursor()

        # Total sales all time
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) AS total_sales, COUNT(*) AS sales_count FROM sales")
        sales_row = cursor.fetchone()
        total_sales_paise = sales_row["total_sales"]
        sales_count = sales_row["sales_count"]

        # Total purchases all time
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) AS total_purchases, COUNT(*) AS purchase_count FROM purchases")
        purch_row = cursor.fetchone()
        total_purchases_paise = purch_row["total_purchases"]
        purchase_count = purch_row["purchase_count"]

        # Today's dates
        today_str = datetime.now().strftime("%Y-%m-%d")

        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) AS today_sales FROM sales WHERE sale_date LIKE ?", (f"{today_str}%",))
        today_sales_paise = cursor.fetchone()["today_sales"]

        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) AS today_purchases FROM purchases WHERE purchase_date LIKE ?", (f"{today_str}%",))
        today_purchases_paise = cursor.fetchone()["today_purchases"]

        conn.close()

        # Recent stock movements / transactions
        recent_movements = StockMovementRepository.get_recent(limit=8)

        # Low stock products list
        low_stock_products = ProductRepository.get_low_stock()
        out_of_stock_products = ProductRepository.get_out_of_stock()

        return {
            "total_products": stock_summary["total_products"],
            "total_units": stock_summary["total_units"],
            "low_stock_count": stock_summary["low_stock_count"],
            "out_of_stock_count": stock_summary["out_of_stock_count"],
            "total_valuation_rupees": stock_summary["total_valuation_rupees"],
            "total_sales_paise": total_sales_paise,
            "total_sales_rupees": round(total_sales_paise / 100.0, 2),
            "sales_count": sales_count,
            "total_purchases_paise": total_purchases_paise,
            "total_purchases_rupees": round(total_purchases_paise / 100.0, 2),
            "purchase_count": purchase_count,
            "today_sales_rupees": round(today_sales_paise / 100.0, 2),
            "today_purchases_rupees": round(today_purchases_paise / 100.0, 2),
            "recent_movements": recent_movements,
            "low_stock_products": low_stock_products,
            "out_of_stock_products": out_of_stock_products
        }

    @staticmethod
    def get_inventory_report(category_id: int = None, status_filter: str = None):
        """Retrieve inventory report data."""
        products = ProductRepository.search(category_id=category_id, stock_status=status_filter)
        report_data = []
        for p in products:
            cost_val = round((p.current_stock * p.purchase_price) / 100.0, 2)
            retail_val = round((p.current_stock * p.selling_price) / 100.0, 2)
            report_data.append({
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "category": p.category_name,
                "current_stock": p.current_stock,
                "minimum_stock": p.minimum_stock,
                "purchase_price": p.purchase_price_rupees,
                "selling_price": p.selling_price_rupees,
                "cost_valuation": cost_val,
                "retail_valuation": retail_val,
                "status": p.stock_status
            })
        return report_data

    @staticmethod
    def get_low_stock_report():
        """Retrieve all items that need replenishment (low stock + out of stock)."""
        products = ProductRepository.get_all()
        low_and_out = [p for p in products if p.is_low_stock or p.is_out_of_stock]
        report_data = []
        for p in low_and_out:
            reorder_needed = max(0, p.minimum_stock - p.current_stock + 10)  # Suggested reorder qty
            report_data.append({
                "sku": p.sku,
                "name": p.name,
                "category": p.category_name,
                "current_stock": p.current_stock,
                "minimum_stock": p.minimum_stock,
                "suggested_reorder": reorder_needed,
                "status": p.stock_status,
                "purchase_price": p.purchase_price_rupees
            })
        return report_data

    @staticmethod
    def get_sales_report(start_date: str = None, end_date: str = None):
        """Retrieve sales transactions report."""
        sales = SaleRepository.get_all(start_date=start_date, end_date=end_date)
        report_data = []
        for s in sales:
            detailed_sale = SaleRepository.get_by_id(s.id)
            items_str = ", ".join([f"{item.product_name} (x{item.quantity})" for item in detailed_sale.items])
            report_data.append({
                "sale_id": s.id,
                "sale_date": s.sale_date,
                "items_count": len(detailed_sale.items),
                "items_summary": items_str,
                "total_amount": s.total_amount_rupees,
                "notes": s.notes or ""
            })
        return report_data

    @staticmethod
    def get_purchases_report(start_date: str = None, end_date: str = None, supplier_id: int = None):
        """Retrieve purchases report."""
        purchases = PurchaseRepository.get_all(supplier_id=supplier_id, start_date=start_date, end_date=end_date)
        report_data = []
        for p in purchases:
            detailed = PurchaseRepository.get_by_id(p.id)
            items_str = ", ".join([f"{item.product_name} (x{item.quantity})" for item in detailed.items])
            report_data.append({
                "purchase_id": p.id,
                "purchase_date": p.purchase_date,
                "supplier": p.supplier_name,
                "reference_number": p.reference_number or "",
                "items_count": len(detailed.items),
                "items_summary": items_str,
                "total_amount": p.total_amount_rupees,
                "notes": p.notes or ""
            })
        return report_data

    @staticmethod
    def get_stock_movement_report(start_date: str = None, end_date: str = None, product_id: int = None, movement_type: str = None):
        """Retrieve detailed stock movements log."""
        movements = StockMovementRepository.get_all(
            product_id=product_id, 
            movement_type=movement_type, 
            start_date=start_date, 
            end_date=end_date, 
            limit=500
        )
        report_data = []
        for m in movements:
            ref = ""
            if m.purchase_id:
                ref = f"Purchase #{m.purchase_id}"
            elif m.sale_id:
                ref = f"Sale #{m.sale_id}"
            elif m.reason:
                ref = m.reason
            report_data.append({
                "movement_id": m.id,
                "created_at": m.created_at,
                "sku": m.product_sku,
                "product_name": m.product_name,
                "movement_type": m.movement_type,
                "quantity_change": m.quantity_change,
                "previous_stock": m.previous_stock,
                "resulting_stock": m.resulting_stock,
                "reference": ref
            })
        return report_data
