from __future__ import annotations

__version__='0.1.1'
__author__=['Ioannis Tsakmakis']
__date_created__='2025-01-27'
__last_updated__='2025-02-04'

# from engine import Base
from database.engine import Base
from sqlalchemy import ForeignKey, Numeric, String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import  Mapped, mapped_column
from databases_companion.enum_variables import AccountType

# Users
class Users(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    aws_user_name: Mapped[str] = mapped_column(String(500), nullable=False)
    email: Mapped[str] = mapped_column(String(500), nullable=False)
    account_type: Mapped[AccountType] = mapped_column(SQLAlchemyEnum(AccountType), nullable=False)
    subscription_expires_in: Mapped[float] = mapped_column(nullable=False)

# Parameters Mapping
class Variables(Base):
    __tablename__ = 'variables'

    variables_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    abbrev: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    long_name: Mapped[str] = mapped_column(String(100), nullable=False)
    standar_name: Mapped[str] = mapped_column(String(100), nullable=False)
    units: Mapped[str] = mapped_column(String(100), nullable=False)

class InfluxMapping(Base):
    __tablename__ = 'influx_mapping'

    influx_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    measurement: Mapped[str] = mapped_column(ForeignKey('variables.abbrev', ondelete='CASCADE'), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(10,6), nullable= False)
    longitude: Mapped[float] = mapped_column(Numeric(10,6), nullable=False)



