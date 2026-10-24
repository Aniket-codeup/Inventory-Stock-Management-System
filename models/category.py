from dataclasses import dataclass

@dataclass
class Category:
    id: int = None
    name: str = ""
    is_active: int = 1
    created_at: str = ""
    product_count: int = 0