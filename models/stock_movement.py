from dataclasses import dataclass

@dataclass
class StockMovement:
    id: int = None
    product_id: int = 0
    movement_type: str = ""  # 'OPENING_STOCK', 'PURCHASE', 'SALE', 'ADJUSTMENT'
    quantity_change: int = 0  # Can be positive or negative
    previous_stock: int = 0
    resulting_stock: int = 0
    purchase_id: int = None
    sale_id: int = None
    reason: str = ""
    created_at: str = ""
    product_name: str = ""
    product_sku: str = ""
