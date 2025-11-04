from sqlalchemy import select

from db.db_session import get_db_session
from db.models import Supplier


def get_suppliers():
    with get_db_session() as session:
        try:
            stmt = select(Supplier.id, Supplier.name)
            suppliers = session.execute(stmt).all()
            return {
                'success': True,
                'data': suppliers
            }
        except Exception as e:
            return {
                'success': False,
                'data': str(e)
            }

