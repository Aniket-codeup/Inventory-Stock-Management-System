from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

@dataclass
class Product:
    id: int = None
    sku: str = ""
    name: str = ""
    category_id: int = 0
    description: str = ""
    purchase_price: int = 0  # Stored in integer paise (₹1.00 = 100 paise)
    selling_price: int = 0   # Stored in integer paise
    current_stock: int = 0
    minimum_stock: int = 0
    is_active: int = 1
    created_at: str = ""
    updated_at: str = ""
    category_name: str = ""  # Enriched display field

    @property
    def is_low_stock(self) -> bool:
        """True if stock is positive but at or below the minimum stock threshold."""
        return self.current_stock > 0 and self.current_stock <= self.minimum_stock

    @property
    def is_out_of_stock(self) -> bool:
        """True if current stock is zero or negative."""
        return self.current_stock <= 0

    @property
    def stock_status(self) -> str:
        """Return standardized stock status."""
        if self.current_stock <= 0:
            return "Out of Stock"
        elif self.current_stock <= self.minimum_stock:
            return "Low Stock"
        return "In Stock"

    @property
    def purchase_price_rupees(self) -> float:
        """Convert paise to rupees for display."""
        return round(self.purchase_price / 100.0, 2)

    @property
    def selling_price_rupees(self) -> float:
        """Convert paise to rupees for display."""
        return round(self.selling_price / 100.0, 2)

    @staticmethod
    def rupees_to_paise(rupees: float | int | str) -> int:
        """Accurately convert rupee decimal value to integer paise using Decimal."""
        if rupees is None or str(rupees).strip() == "":
            return 0
        dec_val = Decimal(str(rupees).strip()).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return int(dec_val * 100)

    @staticmethod
    def paise_to_rupees_str(paise: int) -> str:
        """Format paise as currency string e.g. '₹125.50'."""
        if paise is None:
            paise = 0
        return f"₹{paise / 100.0:,.2f}"