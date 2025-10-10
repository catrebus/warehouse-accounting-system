from contextlib import contextmanager

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, declarative_base

from config_private import DATABASE_URL

"""Точка доступа к бд"""

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

@contextmanager
def get_db_session():
    """Контекстный менеджер для безопасной работы с БД"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except exc.SQLAlchemyError as e:
        session.rollback()
        print(f"Ошибка при работе с БД: {e}")
        raise
    finally:
        session.close()