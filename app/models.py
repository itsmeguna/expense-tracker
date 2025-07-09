from sqlalchemy import Column, Integer, String, Float, DateTime,text,ForeignKey
from sqlalchemy.orm import relationship

from datetime import datetime
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    Note = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    timestamp =  Column(TIMESTAMP(timezone=True), server_default= (text('now()')), nullable=False)  #define the created_at column as a timestamp with timezone and default to current time
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # this links to the users table

    user = relationship("User", back_populates="expenses")  # change this for each model accordingly


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    note = Column(String, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # this links to the users table
    user = relationship("User", back_populates="incomes")  # this gives access to the full user object


class Saving(Base):
    __tablename__ = "savings"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    note = Column(String, nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # this links to the users table
    user = relationship("User", back_populates="savings")  # this gives access to the full user object


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    # Relationships
    expenses = relationship("Expense", back_populates="user")
    incomes = relationship("Income", back_populates="user")
    savings = relationship("Saving", back_populates="user")
