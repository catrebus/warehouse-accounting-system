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

def add_new_product_to_warehouse(productName,warehouse):
    with get_db_session() as session:
        try:
            stmt = select(Inventory).where(
                Inventory.product_id == (select(Product.id).where(Product.name == productName).scalar_subquery()),
                Inventory.warehouse_id == (select(Warehouse.id).where(Warehouse.name == warehouse)).scalar_subquery())
            isAlreadeExists = session.execute(stmt).scalar()
            if isAlreadeExists:
                return {'success': False, 'message':'Этот товар уже есть на складе'}

            warehouseId = session.scalar(select(Warehouse.id).where(Warehouse.name == warehouse))
            productId = session.scalar(select(Product.id).where(Product.name == productName))

            newInventory = Inventory(product_id=productId, warehouse_id=warehouseId, quantity=0, updated_at=datetime.now())

            session.add(newInventory)
            return {'success':True, 'message':'Новый товар успешно добавлен'}

        except Exception as e:
            return {'success': False, 'message':e}

def del_product_from_warehouse(productName,warehouse):
    with get_db_session() as session:
        try:
            stmt = select(Inventory).where(
                Inventory.product_id == (select(Product.id).where(Product.name == productName).scalar_subquery()),
                Inventory.warehouse_id == (select(Warehouse.id).where(Warehouse.name == warehouse)).scalar_subquery())
            inventoryItem = session.execute(stmt).scalar()
            if inventoryItem:
                session.delete(inventoryItem)
                return {'success': True, 'message':'Товар успешно удален'}
            return {'success': False, 'message': 'Этого товара нет складе'}

        except Exception as e:
            return {'success': False, 'message':e}

def get_all_products():
    with get_db_session() as session:
        try:
            stmt = select(Product.name)
            products = session.scalars(stmt).all()
            return {'success':True, 'data':products}

        except Exception as e:
            return {'success': False, 'message':e}

def get_all_product_and_ids():
    with get_db_session() as session:
        stmt = select(Product.id, Product.name)
        products = session.execute(stmt).all()
        return {'success': True, 'data': products}

def add_product(productName):
    with get_db_session() as session:
        try:
            stmt = select(Product.name).where(Product.name == productName)
            isAlreadeExists = session.execute(stmt).scalar()
            if isAlreadeExists:
               return {'success': False, 'message': 'Товар с таким именем уже существует'}

            newProduct = Product(name=productName)
            session.add(newProduct)

            return {'success': True, 'message': 'Новый товар успешно добавлен'}
        except Exception as e:
            return {'success': False, 'message':e}

def del_product(productId):
    with get_db_session() as session:
        try:
            stmt = select(Product).where(Product.id == productId)
            productObj = session.execute(stmt).scalar()
            if not productObj:
                return {'success':False, 'message': 'Товара с таким Id не существует'}

            stmt = select(Inventory.product_id).where(Inventory.product_id == productId)
            isUsed = session.execute(stmt).scalar()
            if isUsed:
                return {'success': False, 'message': 'Невозможно удалить товар, который используется на складах'}

            session.delete(productObj)

            return {'success':True, 'message': 'Товар успешно удален'}
        except Exception as e:
            return {'success': False, 'message':e}


print(del_product(6))