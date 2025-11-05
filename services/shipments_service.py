from ctypes.wintypes import HDESK
from datetime import datetime
from typing import List

from sqlalchemy import select, func, update, or_

from db.db_session import get_db_session
from db.models import Supplier, Shipment, Employee, Warehouse, ShipmentLine, Product, Inventory, UserAccount
from utils.app_state import AppState


def get_shipments_data(warehouses=None):
    with get_db_session() as session:
        try:
            stmt = select(Shipment.id, Supplier.name, func.concat(Employee.last_name, ' ' , Employee.first_name), Warehouse.name, Shipment.date)\
                .join(Supplier, Supplier.id == Shipment.supplier_id)\
                .join(Employee, Employee.id == Shipment.employee_id)\
                .join(Warehouse, Warehouse.id == Shipment.warehouse_id)\
                .order_by(Shipment.date.desc())
            if warehouses:
                stmt = stmt.where(Shipment.warehouse_id.in_(warehouses))
            shipments = session.execute(stmt).all()
            return {
                'success': True,
                'data': shipments
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }


def get_suppliers_name():
    with get_db_session() as session:
        try:
            stmt = select(Supplier.id, Supplier.name)
            suppliers = session.execute(stmt).all()
            return {
                'success': True,
                'data': suppliers
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

def get_suppliers_data():
    with get_db_session() as session:
        try:
            stmt = select(Supplier.name, Supplier.phone_number, Supplier.email)
            suppliers = session.execute(stmt).all()
            return {
                'success': True,
                'data': suppliers
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

def get_shipment_details(shipmentId):
    with get_db_session() as session:
        try:
            stmt = select(Product.name, ShipmentLine.quantity).join(Product, Product.id == ShipmentLine.product_id).where(ShipmentLine.shipment_id == shipmentId)
            shipmentDetails = session.execute(stmt).all()
            return {
                'success': True,
                'data': shipmentDetails
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

def get_users_warehouses():
    with get_db_session() as session:
        try:
            stmt = select(Warehouse.id, Warehouse.name).where(Warehouse.id.in_(AppState.currentUser.warehouses))
            warehouses = session.execute(stmt).all()
            return {
                'success': True,
                'data': warehouses
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

def get_available_products(warehouseId):
    with get_db_session() as session:
        try:
            stmt = select(Product.id, Product.name)\
                .join(Inventory, Inventory.product_id == Product.id)\
                .where(Inventory.warehouse_id == warehouseId)\
                .group_by(Product.id, Product.name)
            products = session.execute(stmt).all()
            return {
                'success': True,
                'data': products
            }

        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

def add_new_shipment(supplierId:int, warehouseId:int, productsList:List):
    with get_db_session() as session:
        try:
            # Проверки
            for productId, quantity in productsList:
                stmt = select(Inventory.quantity).where(Inventory.product_id == productId, Inventory.warehouse_id == warehouseId)
                currentQuantity = session.scalar(stmt)
                if currentQuantity + quantity > 2000000000:
                    return {
                        'success': False,
                        'data': 'Получившееся значение количества после добавления слишком большое'
                    }


            # Создание записи о поставке
            shipment = Shipment(supplier_id=supplierId,
                                employee_id=(select(UserAccount.employee_id).where(UserAccount.login == AppState.currentUser.login)).scalar_subquery(),
                                warehouse_id=warehouseId,
                                date=datetime.now())

            session.add(shipment)

            for productId, quantity in productsList:
                stmt = update(Inventory).where(Inventory.product_id == productId, Inventory.warehouse_id == warehouseId).values(quantity=Inventory.quantity + quantity).values(updated_at=datetime.now())
                session.execute(stmt)
                shipmentLine = ShipmentLine(shipment_id= shipment.id,product_id=productId,quantity=quantity)
                session.add(shipmentLine)
            return {
                'success': True,
                'data': 'Поставка успешно создана'
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

def add_new_supplier(supplierName, supplierPhone, supplierEmail):
    with get_db_session() as session:
        try:
            stmt = select(Supplier).where(
                or_(
                    Supplier.name == supplierName,
                    Supplier.email == supplierEmail,
                    Supplier.phone_number == supplierPhone
                )
            )
            isUnique = session.scalar(stmt)
            if isUnique:
                return {
                    'success': False,
                    'data': 'Вы ввели уже существующее значение'
                }

            supplier = Supplier(name=supplierName, phone_number=supplierPhone,email=supplierEmail)
            session.add(supplier)
            return {
                'success': True,
                'data': 'Поставщик успешно добавлен'
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }
