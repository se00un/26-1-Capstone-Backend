from sqlalchemy import Column, String, BigInteger, Numeric, Date
from app.db.database import Base

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    base_currency = Column(String(10), default='KRW')
    target_currency = Column(String(10))
    rate = Column(Numeric, nullable=False)
    fetched_date = Column(Date, index=True)
