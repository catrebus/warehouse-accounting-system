from datetime import datetime

from sqlalchemy import select, func, or_
from sqlalchemy.orm import aliased

from db.db_session import get_db_session
from db.models import Transfer, Employee, Warehouse, TransferLine, Product, Inventory, UserAccount
from utils.app_state import AppState


def get_transfers_data(warehouses=None):
    with get_db_session() as session:
        try:

            fromWarehouse = aliased(Warehouse)
            toWarehouse = aliased(Warehouse)

            stmt = select(Transfer.id, fromWarehouse.name, toWarehouse.name, func.concat(Employee.last_name, ' ' , Employee.first_name), Transfer.date)\
            .join(toWarehouse, toWarehouse.id == Transfer.to_warehouse_id) \
            .join(fromWarehouse, fromWarehouse.id == Transfer.from_warehouse_id) \
            .join(Employee, Employee.id == Transfer.employee_id)\
            .order_by(Transfer.id.desc())
            if warehouses:
                stmt = stmt.where(or_(Transfer.from_warehouse_id.in_(warehouses), Transfer.to_warehouse_id.in_(warehouses)))
            transfers = session.execute(stmt).all()
            return {
                'success': True,
                'data': transfers
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

def get_warehouses_data():
    with get_db_session() as session:
        try:
            stmt = select(Warehouse.id, Warehouse.name, Warehouse.address, Warehouse.floor_space)
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

def get_transfer_details(transferId):
    with get_db_session() as session:
        try:
            stmt = select(Product.name, TransferLine.quantity)\
            .join(Product, Product.id == TransferLine.product_id).where(TransferLine.transfer_id == transferId)
            transferDetails = session.execute(stmt).all()

            return {
                'success': True,
                'data': transferDetails
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

def add_new_transfer(fromWarehouseId, toWarehouseId, productsList):
    with get_db_session() as session:
        try:
            transfer = Transfer(from_warehouse_id=fromWarehouseId,
                                to_warehouse_id=toWarehouseId,
                                employee_id=(select(UserAccount.employee_id).where(
                                    UserAccount.login == AppState.currentUser.login)).scalar_subquery(),
                                date=datetime.now())
            session.add(transfer)

            for productId, quantity in productsList:
                stmt = select(Inventory).where(
                    Inventory.product_id == productId,
                    Inventory.warehouse_id == fromWarehouseId)
                fromWarehouseInvenory = session.execute(stmt).scalar_one_or_none()
                if fromWarehouseInvenory.quantity - quantity < 0:
                    return {
                        'success': False,
                        'data': 'Вы пытаетесь взять со склада больше товара, чем фактически имеется'
                    }
                fromWarehouseInvenory.quantity -= quantity

                stmt = select(Inventory).where(
                    Inventory.product_id == productId,
                    Inventory.warehouse_id == toWarehouseId)
                toWarehouseInventory = session.execute(stmt).scalar_one_or_none()
                if toWarehouseInventory.quantity + quantity > 2000000000:
                    return {
                        'success': False,
                        'data': 'Получившееся значение количества товара после изменения на конечном складе слишком большое'
                    }
                toWarehouseInventory.quantity += quantity

                transferLine = TransferLine(transfer_id=transfer.id,
                                            product_id=productId,
                                            quantity=quantity)
                session.add(transferLine)
            return {
                'success': True,
                'data': 'Транспортировка успешно оформлена'
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

def add_new_warehouse(warehouseName, warehouseAddress, warehouseArea):
    with get_db_session() as session:
        try:
            stmt = select(Warehouse).where(
                or_(
                    Warehouse.name == warehouseName,
                    Warehouse.address == warehouseAddress
                )
            )
            isExists = session.execute(stmt).scalar_one_or_none()
            if isExists:
                return {
                    'success': False,
                    'data': 'Склад с таким названием или адресом уже существует'
                }
            newWarehouse = Warehouse(name=warehouseName,
                                     address=warehouseAddress,
                                     floor_space=warehouseArea)
            session.add(newWarehouse)
            return {
                'success': True,
                'data': 'Новый склад успешно добавлен'
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }