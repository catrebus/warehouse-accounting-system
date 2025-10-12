import bcrypt

def hash_password(password: str) -> str:
    """Функция для шифровки пароля"""

    # Перевод пароля в байты
    password_bytes = password.encode('utf-8')

    # Генерация соли
    salt = bcrypt.gensalt()

    # Генерация хэша
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Возврат хэша в виде строки
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверка пароля на соответствие"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))