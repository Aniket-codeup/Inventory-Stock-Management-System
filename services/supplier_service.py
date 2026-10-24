import re
from models.supplier import Supplier
from repositories.supplier_repository import SupplierRepository

class SupplierService:
    @staticmethod
    def _validate_email(email: str) -> bool:
        if not email:
            return True
        pattern = r"^[^@]+@[^@]+\.[^@]+$"
        return bool(re.match(pattern, email.strip()))

    @staticmethod
    def create_supplier(
        name: str,
        contact_person: str = "",
        phone: str = "",
        email: str = "",
        address: str = "",
        notes: str = ""
    ) -> int:
        name = str(name).strip()
        if not name:
            raise ValueError("Supplier Name is required.")

        email = str(email).strip()
        if email and not SupplierService._validate_email(email):
            raise ValueError("Invalid email format.")

        supplier = Supplier(
            name=name,
            contact_person=contact_person.strip(),
            phone=phone.strip(),
            email=email,
            address=address.strip(),
            notes=notes.strip()
        )
        return SupplierRepository.add(supplier)

    @staticmethod
    def update_supplier(
        supplier_id: int,
        name: str,
        contact_person: str = "",
        phone: str = "",
        email: str = "",
        address: str = "",
        notes: str = ""
    ):
        name = str(name).strip()
        if not name:
            raise ValueError("Supplier Name is required.")

        email = str(email).strip()
        if email and not SupplierService._validate_email(email):
            raise ValueError("Invalid email format.")

        supplier = SupplierRepository.get_by_id(supplier_id)
        if not supplier:
            raise ValueError(f"Supplier with ID {supplier_id} not found.")

        supplier.name = name
        supplier.contact_person = contact_person.strip()
        supplier.phone = phone.strip()
        supplier.email = email
        supplier.address = address.strip()
        supplier.notes = notes.strip()

        SupplierRepository.update(supplier)

    @staticmethod
    def deactivate_supplier(supplier_id: int):
        supplier = SupplierRepository.get_by_id(supplier_id)
        if not supplier:
            raise ValueError(f"Supplier with ID {supplier_id} not found.")
        SupplierRepository.deactivate(supplier_id)

    @staticmethod
    def list_suppliers(query: str = None):
        if query and query.strip():
            return SupplierRepository.search(query.strip())
        return SupplierRepository.get_all()

    @staticmethod
    def get_supplier(supplier_id: int):
        return SupplierRepository.get_by_id(supplier_id)
