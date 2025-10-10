from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from .db_session import Base

# Таблица role
class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(45), unique=True, nullable=False)

    users = relationship('User', back_populates='role')

# Таблица user_account
class UserAccount(Base):
    __tablename__ = 'user_account'

    id = Column(Integer, primary_key=True, nullable=False)
    login = Column(String(20), unique=True, nullable=False)
    password = Column(String(45), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'))

    role = relationship('Role', back_populates='users')

# Таблица employee
class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    passport_series = Column(String(length=4), nullable=False)
    passport_number = Column(String(length=6), nullable=False)
    phone_number = Column(String(length=11), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    date_of_employment = Column(Date, nullable=False)

    post = relationship('Post', back_populates='employee')

# Таблица post
class Post(Base):
    __tablename__ = 'post'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(45), nullable=False)
    salary = Column(Integer, nullable=False)

    employee = relationship('Employee', back_populates='post')