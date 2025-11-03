from sqlalchemy import select

from db.db_session import get_db_session
from db.models import Product, Inventory, Warehouse


def get_inventory(warehouseIds:list = None):
    """Получение записей о хранящихся товарах"""
    with get_db_session() as session:
        stmt = select(Product.name, Warehouse.name, Inventory.quantity, Inventory.updated_at)\
            .join(Product, Product.id == Inventory.product_id)\
            .join(Warehouse, Warehouse.id == Inventory.warehouse_id)
        #Фильтр складов, если указан
        if warehouseIds:
            stmt = stmt.where(Inventory.warehouse_id.in_(warehouseIds))

        inventory = session.execute(stmt).all()
        return inventory

