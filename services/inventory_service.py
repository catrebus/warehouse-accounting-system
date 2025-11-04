from datetime import datetime

from sqlalchemy import select, update

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

def add_count(productName,warehouse, quantity):
    with get_db_session() as session:
        try:
            stmt = select(Inventory.quantity).where(
                Inventory.product_id == (select(Product.id).where(Product.name == productName).scalar_subquery()),
                Inventory.warehouse_id == (select(Warehouse.id).where(Warehouse.name == warehouse)).scalar_subquery())
            currentQuantity = session.execute(stmt).scalar()
            if currentQuantity + quantity > 2000000000:
                return {'success': False, 'message': 'Получившееся значение после изменения слишком большое'}

            stmt = update(Inventory).where(
                Inventory.product_id==(select(Product.id).where(Product.name==productName).scalar_subquery()),
                Inventory.warehouse_id==(select(Warehouse.id).where(Warehouse.name==warehouse)).scalar_subquery())\
                .values(quantity=quantity+Inventory.quantity).values(updated_at=datetime.now())
            session.execute(stmt)
        except Exception as e:
            return {'success': False, 'message':e}
        return {'success': True, 'message':'Количество товара успешно обновлено'}

def substract_count(productName,warehouse, quantity):
    with get_db_session() as session:
        try:
            stmt = select(Inventory.quantity).where(
                Inventory.product_id == (select(Product.id).where(Product.name == productName).scalar_subquery()),
                Inventory.warehouse_id == (select(Warehouse.id).where(Warehouse.name == warehouse)).scalar_subquery())
            currentQuantity = session.execute(stmt).scalar()

            if currentQuantity < quantity:
                return {'success': False, 'message': 'Вы пытаетесь вычесть слишком большое число'}

            stmt = update(Inventory).where(
                Inventory.product_id == (select(Product.id).where(Product.name == productName).scalar_subquery()),
                Inventory.warehouse_id == (select(Warehouse.id).where(Warehouse.name == warehouse)).scalar_subquery()) \
                .values(quantity=Inventory.quantity - quantity).values(updated_at=datetime.now())

            session.execute(stmt)
        except Exception as e:
            return {'success': False, 'message':e}
        return {'success': True, 'message':'Количество товара успешно обновлено'}


