from datetime import date

from sqlalchemy import select

from db.db_session import get_db_session
from db.models import UserAccount, Role, Employee, Post, t_employee_warehouse, Warehouse


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

def get_employees():
    with get_db_session() as session:
        stmt = select(Employee.id, Employee.first_name, Employee.last_name, Employee.passport_series, Employee.passport_number,Employee.phone_number, Post.name, Employee.date_of_employment, Employee.is_active).join(Post, Post.id == Employee.post_id)
        employees = session.execute(stmt)
        res = []
        for id, firstName, lastName, series, number,phone, post, date, isActive in employees:
            res.append([id, firstName, lastName, series, number,phone, post, str(date.day) + '.' + str(date.month) + '.' + str(date.year), isActive])
        return res

def add_employee(firstName:str, lastName:str, passportSeries:str, passportNumber:str, phoneNumber:str, post:str, warehouses:list):
    with get_db_session() as session:

        stmt = select(Employee.passport_series, Employee.passport_number).where(Employee.passport_series==passportSeries).where(Employee.passport_number==passportNumber)
        serNumIndex = session.scalar(stmt)

        if serNumIndex:
            return {'success':False,'message':'Человек с такой серией и номером паспорта уже существует'}

        stmt = select(Post.id).where(Post.name == post)
        postId = session.execute(stmt).one_or_none()

        newEmployee = Employee(first_name=firstName, last_name=lastName, passport_series=passportSeries, passport_number=passportNumber, phone_number=phoneNumber, post_id=postId[0], date_of_employment=date.today(), is_active=1)

        warehouseObjects = session.query(Warehouse).filter(Warehouse.id.in_(warehouses)).all()

        newEmployee.warehouse.extend(warehouseObjects)

        session.add(newEmployee)

        return {'success':True, 'message':'Пользователь успешно добавлен'}

