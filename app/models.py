from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, String
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ---------- senha separada ----------
class Password(Base):
    __tablename__ = "password"
    id           = Column(Integer, primary_key=True, autoincrement=True)
    password256  = Column(String(256), nullable=False)

    user = relationship("User", back_populates="password_obj", uselist=False)

# ---------- tabelas auxiliares ----------
class Condition(Base):
    __tablename__ = "condition"

    id = Column(Integer, primary_key=True, autoincrement=True)
    diabetes                 = Column(Boolean)
    hyper_tension            = Column(Boolean)
    cardiovascular_disease   = Column(Boolean)
    obesity                  = Column(Boolean)
    asthma                   = Column(Boolean)
    arthritis                = Column(Boolean)
    osteoporosis             = Column(Boolean)
    chronic_back_pain        = Column(Boolean)
    damaged_left_upper_body  = Column(Boolean)
    damaged_right_upper_body = Column(Boolean)
    damaged_left_lower_body  = Column(Boolean)
    damaged_right_lower_body = Column(Boolean)
    damaged_body_core        = Column(Boolean)
    recent_surgery           = Column(Boolean)
    pregnancy                = Column(Boolean)

    user = relationship("User", back_populates="condition", uselist=False)

class PersonalInfo(Base):
    __tablename__ = "personal_info"

    id             = Column(Integer, primary_key=True, autoincrement=True)
    weight_kg      = Column(Integer, nullable=False)
    height_cm      = Column(Integer, nullable=False)
    bio_gender     = Column(String(1), nullable=False)          # M / F / O
    training_since = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="personal_info", uselist=False)

class TrainingAvailability(Base):
    __tablename__ = "training_availability"

    id        = Column(Integer, primary_key=True, autoincrement=True)
    sunday    = Column(Boolean, nullable=False)
    monday    = Column(Boolean, nullable=False)
    tuesday   = Column(Boolean, nullable=False)
    wednesday = Column(Boolean, nullable=False)
    thursday  = Column(Boolean, nullable=False)
    friday    = Column(Boolean, nullable=False)
    saturday  = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="training_availability", uselist=False)

# ---------- usuário ----------
class User(Base):
    __tablename__ = "user"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    first_name   = Column(String(45), nullable=False)
    last_name    = Column(String(45), nullable=False)
    cpf          = Column(String(45), unique=True, nullable=False)
    birth_date   = Column(DateTime, nullable=False)
    email        = Column(String(45), nullable=False)
    phone_number = Column(String(15), nullable=False)

    # FKs
    id_infos      = Column(Integer, ForeignKey("personal_info.id"))
    id_dates      = Column(Integer, ForeignKey("training_availability.id"))
    id_conditions = Column(Integer, ForeignKey("condition.id"))
    id_password   = Column(Integer, ForeignKey("password.id"))

    personal_info         = relationship("PersonalInfo", back_populates="user", cascade="all, delete")
    training_availability = relationship("TrainingAvailability", back_populates="user", cascade="all, delete")
    condition             = relationship("Condition", back_populates="user", cascade="all, delete")
    password_obj          = relationship("Password", back_populates="user", cascade="all, delete")