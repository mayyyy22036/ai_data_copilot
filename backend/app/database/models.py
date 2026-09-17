from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.session import Base


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(Integer, primary_key=True)
    store_type = Column(String(1))
    assortment = Column(String(1))
    competition_distance = Column(Float, nullable=True)
    competition_open_since_month = Column(Integer, nullable=True)
    competition_open_since_year = Column(Integer, nullable=True)
    promo2 = Column(Boolean, default=False)
    promo2_since_week = Column(Integer, nullable=True)
    promo2_since_year = Column(Integer, nullable=True)
    promo_interval = Column(String(50), nullable=True)

    sales = relationship("Sales", back_populates="store")


class Sales(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_id = Column(Integer, ForeignKey("stores.store_id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    day_of_week = Column(Integer)
    sales = Column(Float, nullable=False)
    customers = Column(Integer)
    open = Column(Boolean)
    promo = Column(Boolean)
    state_holiday = Column(String(1))
    school_holiday = Column(Boolean)

    store = relationship("Store", back_populates="sales")