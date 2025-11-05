from ctypes.wintypes import HDESK

from sqlalchemy import select, func

from db.db_session import get_db_session
from db.models import Supplier, Shipment, Employee, Warehouse


def get_shipments_data():
    with get_db_session() as session:
        try:
            stmt = select(Shipment.id, Supplier.name, func.concat(Employee.last_name, ' ' , Employee.first_name), Warehouse.name, Shipment.date)\
                .join(Supplier, Supplier.id == Shipment.supplier_id)\
                .join(Employee, Employee.id == Shipment.employee_id)\
                .join(Warehouse, Warehouse.id == Shipment.warehouse_id)\
                .order_by(Shipment.date.desc())
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

