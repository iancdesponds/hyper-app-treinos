# models.py
from sqlalchemy import (
    Column, Float, Integer, String, DateTime, Date, Time, ForeignKey, CheckConstraint, UniqueConstraint, SmallInteger
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Condition(Base):
    __tablename__ = 'condition'

    id = Column(Integer, primary_key=True, autoincrement=True)
    diabetes = Column(SmallInteger)
    hyper_tension = Column(SmallInteger)
    cardiovascular_disease = Column(SmallInteger)
    obesity = Column(SmallInteger)
    asthma = Column(SmallInteger)
    arthritis = Column(SmallInteger)
    osteoporosis = Column(SmallInteger)
    chronic_back_pain = Column(SmallInteger)
    damaged_left_upper_body = Column(SmallInteger)
    damaged_right_upper_body = Column(SmallInteger)
    damaged_left_lower_body = Column(SmallInteger)
    damaged_right_lower_body = Column(SmallInteger)
    damaged_body_core = Column(SmallInteger)
    recent_surgery = Column(SmallInteger)
    pregnancy = Column(SmallInteger)


class Exercise(Base):
    __tablename__ = 'exercise'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(90), unique=True)


class Password(Base):
    __tablename__ = 'password'

    id = Column(Integer, primary_key=True, autoincrement=True)
    password256 = Column(String(256), nullable=False)


class PersonalInfo(Base):
    __tablename__ = 'personal_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Integer, nullable=False)
    bio_gender = Column(String(1), nullable=False)
    training_since = Column(DateTime, nullable=False)


class TrainingAvailability(Base):
    __tablename__ = 'training_availability'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sunday = Column(SmallInteger, nullable=False)
    monday = Column(SmallInteger, nullable=False)
    tuesday = Column(SmallInteger, nullable=False)
    wednesday = Column(SmallInteger, nullable=False)
    thursday = Column(SmallInteger, nullable=False)
    friday = Column(SmallInteger, nullable=False)
    saturday = Column(SmallInteger, nullable=False)


class Train(Base):
    __tablename__ = 'train'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey('user.id'))
    name = Column(String(90))
    date = Column(Date)
    expected_duration = Column(Integer)
    start_time = Column(Time)
    end_time = Column(Time)
    feedback = Column(Integer)

    __table_args__ = (
        CheckConstraint('feedback BETWEEN 1 AND 10', name='chk_feedback_range'),
    )

    user = relationship("User", back_populates="trains")
    series = relationship("Series", back_populates="train")


class Series(Base):
    __tablename__ = 'series'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_train = Column(Integer, ForeignKey('train.id'))
    id_exercise = Column(Integer, ForeignKey('exercise.id'))
    weight = Column(Float)
    repetitions = Column(Integer)
    rest_time = Column(Integer)

    train = relationship("Train", back_populates="series")
    exercise = relationship("Exercise")


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    username = Column(String(60), nullable=False)
    cpf = Column(String(45), nullable=False, unique=True)
    birth_date = Column(DateTime, nullable=False)
    email = Column(String(45), nullable=False)
    phone_number = Column(String(15), nullable=False)
    id_infos = Column(Integer, ForeignKey('personal_info.id', ondelete='SET NULL', onupdate='CASCADE'))
    id_dates = Column(Integer, ForeignKey('training_availability.id', ondelete='SET NULL', onupdate='CASCADE'))
    id_conditions = Column(Integer, ForeignKey('condition.id'))
    id_password = Column(Integer, ForeignKey('password.id'))

    trains = relationship("Train", back_populates="user")
    personal_info = relationship("PersonalInfo")
    availability = relationship("TrainingAvailability")
    condition = relationship("Condition")
    password = relationship("Password")

    __table_args__ = (
        UniqueConstraint('id_infos'),
        UniqueConstraint('id_dates'),
        UniqueConstraint('id_conditions'),
        UniqueConstraint('id_password'),
        UniqueConstraint('id'),
    )


class TrainExerciseView(Base):
    __tablename__ = 'Train_Exercise'
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True)
    train_id = Column(Integer, primary_key=True)
    train_name = Column(String(90))
    series_id = Column(Integer, primary_key=True)
    exercise_id = Column(Integer, primary_key=True)
    exercise_name = Column(String(90))
    exercise_weight = Column(Float)
    exercise_repetitions = Column(Integer)
    exercise_rest = Column(Integer)
    expected_duration = Column(Integer)
    training_start = Column(Time)
    training_end = Column(Time)
    training_feedback = Column(Integer)
