from dataclasses import dataclass

@dataclass
class Supplier:
    id: int = None
    name: str = ""
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    notes: str = ""
    is_active: int = 1
    created_at: str = ""
