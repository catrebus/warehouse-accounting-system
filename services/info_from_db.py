from datetime import date

from sqlalchemy import select

from db.db_session import get_db_session
from db.models import Shipment, Supplier, Employee, Warehouse, UserAccount, Role, Post


def get_upcoming_shipments():
    with get_db_session() as session:
        stmt = select(Supplier.name, Employee.last_name,Employee.first_name, Warehouse.name, Shipment.date).\
            join(Supplier, Supplier.id == Shipment.supplier_id).\
            join(Employee, Employee.id == Shipment.employee_id).\
            join(Warehouse, Warehouse.id == Shipment.warehouse_id).\
            where(Shipment.date > date.today()).order_by(Shipment.date)
        shipments = session.execute(stmt).all()

        upcomingShipments = []
        for shipment in shipments:
            shipment = list(shipment)
            shipment[1] = shipment[1] + ' ' + shipment.pop(2)
            upcomingShipments.append(shipment)
    return upcomingShipments

def get_users():
    with get_db_session() as session:
        stmt = select(UserAccount.login, Role.name, Employee.last_name, Employee.first_name, UserAccount.is_active).\
            join(Employee, Employee.id == UserAccount.employee_id).\
            join(Role, Role.id == UserAccount.role_id).order_by(UserAccount.id)
        users = session.execute(stmt).all()

        usersList = []

        for user in users:
            user = list(user)
            usersList.append(user)
    return usersList

def get_roles():
    with get_db_session() as session:
        stmt = select(Role.name)
        roles = session.scalars(stmt).all()

        return roles

def get_posts():
    with get_db_session() as session:
        stmt = select(Post.name)
        posts = session.scalars(stmt).all()

        return posts

def get_warehouses():
    with get_db_session() as session:
        stmt = select(Warehouse.id, Warehouse.name)
        warehouses = session.execute(stmt).all()

        return warehouses

