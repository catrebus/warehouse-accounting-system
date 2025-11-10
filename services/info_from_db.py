from sqlalchemy import select

from db.db_session import get_db_session
from db.models import Employee, Warehouse, UserAccount, Role, Post


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

def get_warehouses(warehouses=None):
    with get_db_session() as session:
        stmt = select(Warehouse.id, Warehouse.name)
        if warehouses:
            stmt = stmt.where(Warehouse.id.in_(warehouses))
        warehouses = session.execute(stmt).all()

        return warehouses

