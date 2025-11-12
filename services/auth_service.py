from sqlalchemy import select

from db.db_session import get_db_session
from db.models import InviteCode, UserAccount, t_employee_warehouse
from utils.app_state import AppState, User
from utils.password_utils import hash_password, verify_password


def register_user(inviteCode: str, login: str, password: str) -> dict:
    """Внесение нового пользователя в бд"""
    with get_db_session() as session:
        try:
            # Сверка пригласительного кода
            stmt = select(InviteCode).where(InviteCode.code == inviteCode, InviteCode.is_active == 1)
            inviteCodeObj = session.scalar(stmt)

            # Пригласительного кода не существует или он уже активирован
            if not inviteCodeObj:
                return {'success': False, 'message': 'Некорректный код приглашения'}

            # Проверка на уникальность введенного логина
            stmt = select(UserAccount).where(UserAccount.login == login)
            loginExists = session.scalar(stmt)

            # Такой логин уже существует
            if loginExists:
                return {'success' : False, 'message': 'Введенный логин уже существует'}

            # Хеширование пароля
            hashedPassword = hash_password(password)

            # Добавление нового пользователя
            newUser = UserAccount(login=login,
                                   password=hashedPassword,
                                   employee_id=inviteCodeObj.employee_id,
                                   role_id=inviteCodeObj.role_id,
                                  is_active=1)
            session.add(newUser)

            # Деактивация пригласительного кода
            inviteCodeObj.is_active = 0

            stmt = select(t_employee_warehouse.c.warehouse_id).where(t_employee_warehouse.c.employee_id == inviteCodeObj.employee_id)
            warehouseIds = session.execute(stmt).scalars().all()

            AppState.currentUser = User(login=newUser.login,role=newUser.role_id, warehouses=warehouseIds)
            return {'success': True, 'message': 'Регистрация прошла успешно'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

def authorize_user(login: str, password: str) -> dict:
    """Авторизация пользователя"""
    with get_db_session() as session:
        try:
            #Получение пользователя по логину
            stmt = select(UserAccount).where(UserAccount.login == login)
            userObj = session.scalar(stmt)

            # Проверка на существование пользователя
            if userObj:

                if verify_password(password, userObj.password):
                    if not userObj.is_active:
                        return {'success': False, 'message': 'Учетная запись деактивирована'}
                    stmt = select(t_employee_warehouse.c.warehouse_id).where(t_employee_warehouse.c.employee_id == userObj.employee_id)
                    warehouseIds = session.execute(stmt).scalars().all()

                    AppState.currentUser = User(login=userObj.login, role=userObj.role_id, warehouses=warehouseIds)
                    return {'success': True, 'message': 'Авторизация прошла успешно'}

            return {'success': False, 'message': 'Неверный логин или пароль'}
        except Exception as e:
            return {'success': False, 'message': str(e)}