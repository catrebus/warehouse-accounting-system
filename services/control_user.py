from sqlalchemy import select

from db.db_session import get_db_session
from db.models import UserAccount, Role, Employee


def get_user_by_login(login:str):
    """Получение информации об учетной записи по логину"""
    with get_db_session() as session:
        stmt = select(UserAccount.login, Role.name, Employee.last_name, Employee.first_name, UserAccount.is_active).\
            join(Employee, Employee.id == UserAccount.employee_id).\
            join(Role, Role.id == UserAccount.role_id).where(UserAccount.login==login)

        user = session.execute(stmt).one_or_none()

        if user:
            return {"login":user[0], "role":user[1], "lastName":user[2], "firstName":user[3], "isActive":user[4]}

        return False

def update_user(login:str, newRole:str, newIsActive:bool):
    with get_db_session() as session:
        stmt = select(UserAccount).where(UserAccount.login==login)
        user = session.scalar(stmt)

        stmt = select(Role.id).where(Role.name==newRole)
        newRole = session.scalar(stmt)

        user.role_id = newRole
        user.is_active = int(newIsActive)

        return True




