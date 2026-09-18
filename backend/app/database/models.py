"""
Modèles SQLAlchemy — schéma Rossmann.

Deux tables, qui reflètent exactement la structure documentation Kaggle :
- `stores`  : dimension (un magasin = une ligne, ne change pas dans le temps)
- `sales`   : faits (une ligne par magasin par jour — c'est la grosse table)

Pourquoi deux tables et pas une seule table "à plat" comme les CSV originaux ?
Parce que StoreType, Assortment, CompetitionDistance sont des attributs du
MAGASIN, pas de la vente du jour. Les répéter sur chaque ligne de vente
(comme dans le CSV brut) est une redondance qu'une vraie base relationnelle
évite via une jointure. C'est exactement le genre de normalisation qu'on
veut pouvoir expliquer en entretien.
"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class Store(Base):
    __tablename__ = "stores"

    store_id = Column(Integer, primary_key=True)  # correspond à "Store" dans store.csv
    store_type = Column(String(1))                 # a/b/c/d
    assortment = Column(String(1))                  # a=basic, b=extra, c=extended
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


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="conversation", order_by="Message.id")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # "user" ou "assistant"
    content = Column(Text, nullable=False)
    tool_used = Column(String(50), nullable=True)  # rag/sql/python/direct_answer, None pour role="user"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship("Conversation", back_populates="messages")