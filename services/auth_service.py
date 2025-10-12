from sqlalchemy import select

from db.db_session import get_db_session
from db.models import InviteCode, UserAccount, Employee
from utils.password_utils import hash_password


def register_user(inviteCode: str, login: str, password: str) -> dict:
    with get_db_session() as session:
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
        new_user = UserAccount(login=login,
                               password=hashedPassword,
                               employee_id=inviteCodeObj.employee_id,
                               role_id=inviteCodeObj.role_id)
        session.add(new_user)

        # Деактивация пригласительного кода
        inviteCodeObj.is_active = 0

        return {'success': True, 'message': 'Регистрация прошла успешно'}
