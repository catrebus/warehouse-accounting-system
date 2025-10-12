import datetime

from sqlalchemy import CHAR, Date, ForeignKeyConstraint, Index, Integer, String
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db_session import Base


class Post(Base):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    salary: Mapped[int] = mapped_column(Integer, nullable=False)

    employee: Mapped[list['Employee']] = relationship('Employee', back_populates='post')


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = (
        Index('name_UNIQUE', 'name', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)

    invite_code: Mapped[list['InviteCode']] = relationship('InviteCode', back_populates='role')
    user_account: Mapped[list['UserAccount']] = relationship('UserAccount', back_populates='role')


class Employee(Base):
    __tablename__ = 'employee'
    __table_args__ = (
        ForeignKeyConstraint(['post_id'], ['post.id'], name='post_id_employee'),
        Index('post_id_employee_idx', 'post_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    passport_series: Mapped[str] = mapped_column(CHAR(4), nullable=False)
    passport_number: Mapped[str] = mapped_column(CHAR(6), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(11), nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date_of_employment: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    post: Mapped['Post'] = relationship('Post', back_populates='employee')
    invite_code: Mapped[list['InviteCode']] = relationship('InviteCode', back_populates='employee')
    user_account: Mapped[list['UserAccount']] = relationship('UserAccount', back_populates='employee')


class InviteCode(Base):
    __tablename__ = 'invite_code'
    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['employee.id'], name='employee_id_invite_code'),
        ForeignKeyConstraint(['role_id'], ['role.id'], name='role_id_invite_code'),
        Index('code_UNIQUE', 'code', unique=True),
        Index('employee_id_UNIQUE', 'employee_id', unique=True),
        Index('employee_id_invite_code_idx', 'employee_id'),
        Index('role_id_invite_code_idx', 'role_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(45), nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[int] = mapped_column(TINYINT, nullable=False)

    employee: Mapped['Employee'] = relationship('Employee', back_populates='invite_code')
    role: Mapped['Role'] = relationship('Role', back_populates='invite_code')


class UserAccount(Base):
    __tablename__ = 'user_account'
    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['employee.id'], name='employee_id_user_account'),
        ForeignKeyConstraint(['role_id'], ['role.id'], name='role_id_user_account'),
        Index('employee_id_user_account_idx', 'employee_id'),
        Index('login_UNIQUE', 'login', unique=True),
        Index('role_id_user_account_idx', 'role_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)

    employee: Mapped['Employee'] = relationship('Employee', back_populates='user_account')
    role: Mapped['Role'] = relationship('Role', back_populates='user_account')
