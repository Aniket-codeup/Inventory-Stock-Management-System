from dataclasses import dataclass, field
from typing import List

@dataclass
class PurchaseItem:
    id: int = None
    purchase_id: int = None
    product_id: int = 0
    quantity: int = 0
    unit_price: int = 0  # In integer paise
    line_total: int = 0  # In integer paise
    product_name: str = ""
    product_sku: str = ""

    @property
    def unit_price_rupees(self) -> float:
        return round(self.unit_price / 100.0, 2)

    @property
    def line_total_rupees(self) -> float:
        return round(self.line_total / 100.0, 2)

@dataclass
class Purchase:
    id: int = None
    supplier_id: int = 0
    purchase_date: str = ""
    total_amount: int = 0  # In integer paise
    reference_number: str = ""
    notes: str = ""
    created_at: str = ""
    supplier_name: str = ""
    items: List[PurchaseItem] = field(default_factory=list)

    @property
    def total_amount_rupees(self) -> float:
        return round(self.total_amount / 100.0, 2)
