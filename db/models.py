import datetime

from sqlalchemy import CHAR, Column, Date, DateTime, ForeignKeyConstraint, Index, Integer, String, Table
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.db_session import Base


class Post(Base):
    __tablename__ = 'post'
    __table_args__ = (
        Index('name_UNIQUE', 'name', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    salary: Mapped[int] = mapped_column(Integer, nullable=False)

    employee: Mapped[list['Employee']] = relationship('Employee', back_populates='post')


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        Index('name_UNIQUE', 'name', unique=True),
        Index('sku_UNIQUE', 'sku', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    sku: Mapped[str] = mapped_column(String(20), nullable=False)

    inventory: Mapped[list['Inventory']] = relationship('Inventory', back_populates='product')
    shipment_line: Mapped[list['ShipmentLine']] = relationship('ShipmentLine', back_populates='product')
    transfer_line: Mapped[list['TransferLine']] = relationship('TransferLine', back_populates='product')


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = (
        Index('name_UNIQUE', 'name', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    user_account: Mapped[list['UserAccount']] = relationship('UserAccount', back_populates='role')


class Supplier(Base):
    __tablename__ = 'supplier'
    __table_args__ = (
        Index('email_UNIQUE', 'email', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(45), nullable=False)
    email: Mapped[str] = mapped_column(String(45), nullable=False)

    shipment: Mapped[list['Shipment']] = relationship('Shipment', back_populates='supplier')


class Warehouse(Base):
    __tablename__ = 'warehouse'
    __table_args__ = (
        Index('address_UNIQUE', 'address', unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    floor_space: Mapped[str] = mapped_column(String(45), nullable=False)

    employee: Mapped[list['Employee']] = relationship('Employee', secondary='employee_warehouse', back_populates='warehouse')
    inventory: Mapped[list['Inventory']] = relationship('Inventory', back_populates='warehouse')
    shipment: Mapped[list['Shipment']] = relationship('Shipment', back_populates='warehouse')
    transfer: Mapped[list['Transfer']] = relationship('Transfer', foreign_keys='[Transfer.from_warehouse_id]', back_populates='from_warehouse')
    transfer_: Mapped[list['Transfer']] = relationship('Transfer', foreign_keys='[Transfer.to_warehouse_id]', back_populates='to_warehouse')


class Employee(Base):
    __tablename__ = 'employee'
    __table_args__ = (
        ForeignKeyConstraint(['post_id'], ['post.id'], name='post_id_employee'),
        Index('post_id_employee_idx', 'post_id'),
        Index('unique_passport', 'passport_series', 'passport_number', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    passport_series: Mapped[str] = mapped_column(CHAR(4), nullable=False)
    passport_number: Mapped[str] = mapped_column(CHAR(6), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date_of_employment: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    post: Mapped['Post'] = relationship('Post', back_populates='employee')
    warehouse: Mapped[list['Warehouse']] = relationship('Warehouse', secondary='employee_warehouse', back_populates='employee')
    invite_code: Mapped[list['InviteCode']] = relationship('InviteCode', back_populates='employee')
    shipment: Mapped[list['Shipment']] = relationship('Shipment', back_populates='employee')
    transfer: Mapped[list['Transfer']] = relationship('Transfer', back_populates='employee')
    user_account: Mapped[list['UserAccount']] = relationship('UserAccount', back_populates='employee')


class Inventory(Base):
    __tablename__ = 'inventory'
    __table_args__ = (
        ForeignKeyConstraint(['product_id'], ['product.id'], name='product_id_inventory'),
        ForeignKeyConstraint(['warehouse_id'], ['warehouse.id'], name='warehouse_id_inventory'),
        Index('product_id_inventory_idx', 'product_id'),
        Index('warehouse_id_inventory_idx', 'warehouse_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    product: Mapped['Product'] = relationship('Product', back_populates='inventory')
    warehouse: Mapped['Warehouse'] = relationship('Warehouse', back_populates='inventory')


t_employee_warehouse = Table(
    'employee_warehouse', Base.metadata,
    Column('employee_id', Integer, primary_key=True),
    Column('warehouse_id', Integer, primary_key=True),
    ForeignKeyConstraint(['employee_id'], ['employee.id'], name='employee_id_employee_warehouse'),
    ForeignKeyConstraint(['warehouse_id'], ['warehouse.id'], name='warehouse_id_employee_warehouse'),
    Index('warehouse_id_employee_warehouse_idx', 'warehouse_id')
)


class InviteCode(Base):
    __tablename__ = 'invite_code'
    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['employee.id'], name='employee_id_invite_code'),
        ForeignKeyConstraint(['role_id'], ['invite_code.id'], name='role_id_invite_code'),
        Index('code_UNIQUE', 'code', unique=True),
        Index('employee_id_UNIQUE', 'employee_id', unique=True),
        Index('role_id_invite_code_idx', 'role_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[int] = mapped_column(TINYINT, nullable=False)

    employee: Mapped['Employee'] = relationship('Employee', back_populates='invite_code')
    role: Mapped['InviteCode'] = relationship('InviteCode', remote_side=[id], back_populates='role_reverse')
    role_reverse: Mapped[list['InviteCode']] = relationship('InviteCode', remote_side=[role_id], back_populates='role')


class Shipment(Base):
    __tablename__ = 'shipment'
    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['employee.id'], name='employee_id_shipment'),
        ForeignKeyConstraint(['supplier_id'], ['supplier.id'], name='supplier_id_shipment'),
        ForeignKeyConstraint(['warehouse_id'], ['warehouse.id'], name='warehouse_id_shipment'),
        Index('employee_id_shipment_idx', 'employee_id'),
        Index('supplier_id_shipment_idx', 'supplier_id'),
        Index('warehouse_id_shipment_idx', 'warehouse_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    supplier_id: Mapped[int] = mapped_column(Integer, nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    warehouse_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    employee: Mapped['Employee'] = relationship('Employee', back_populates='shipment')
    supplier: Mapped['Supplier'] = relationship('Supplier', back_populates='shipment')
    warehouse: Mapped['Warehouse'] = relationship('Warehouse', back_populates='shipment')
    shipment_line: Mapped[list['ShipmentLine']] = relationship('ShipmentLine', back_populates='shipment')


class Transfer(Base):
    __tablename__ = 'transfer'
    __table_args__ = (
        ForeignKeyConstraint(['employee_id'], ['employee.id'], name='employee_id_transfer_line'),
        ForeignKeyConstraint(['from_warehouse_id'], ['warehouse.id'], name='from_warehouse_id_transfer_line'),
        ForeignKeyConstraint(['to_warehouse_id'], ['warehouse.id'], name='to_warehouse_id_transfer_line'),
        Index('employee_id_idx', 'employee_id'),
        Index('from_warehouse_id_transfer_line_idx', 'from_warehouse_id'),
        Index('to_warehouse_id_transfer_line_idx', 'to_warehouse_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    from_warehouse_id: Mapped[int] = mapped_column(Integer, nullable=False)
    to_warehouse_id: Mapped[int] = mapped_column(Integer, nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    employee: Mapped['Employee'] = relationship('Employee', back_populates='transfer')
    from_warehouse: Mapped['Warehouse'] = relationship('Warehouse', foreign_keys=[from_warehouse_id], back_populates='transfer')
    to_warehouse: Mapped['Warehouse'] = relationship('Warehouse', foreign_keys=[to_warehouse_id], back_populates='transfer_')
    transfer_line: Mapped[list['TransferLine']] = relationship('TransferLine', back_populates='transfer')


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
    login: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    employee_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role_id: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[int] = mapped_column(TINYINT, nullable=False)

    employee: Mapped['Employee'] = relationship('Employee', back_populates='user_account')
    role: Mapped['Role'] = relationship('Role', back_populates='user_account')


class ShipmentLine(Base):
    __tablename__ = 'shipment_line'
    __table_args__ = (
        ForeignKeyConstraint(['product_id'], ['product.id'], name='product_id_shipment_line'),
        ForeignKeyConstraint(['shipment_id'], ['shipment.id'], name='shipment_id_shipment_line'),
        Index('product_id_shipment_line_idx', 'product_id'),
        Index('shipment_id_shipment_line_idx', 'shipment_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    shipment_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    product: Mapped['Product'] = relationship('Product', back_populates='shipment_line')
    shipment: Mapped['Shipment'] = relationship('Shipment', back_populates='shipment_line')


class TransferLine(Base):
    __tablename__ = 'transfer_line'
    __table_args__ = (
        ForeignKeyConstraint(['product_id'], ['product.id'], name='product_id_transfer_line'),
        ForeignKeyConstraint(['transfer_id'], ['transfer.id'], name='transfer_id_transfer_line'),
        Index('product_id_transfer_line_idx', 'product_id'),
        Index('transfer_id_transfer_line_idx', 'transfer_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transfer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[str] = mapped_column(String(45), nullable=False)

    product: Mapped['Product'] = relationship('Product', back_populates='transfer_line')
    transfer: Mapped['Transfer'] = relationship('Transfer', back_populates='transfer_line')
