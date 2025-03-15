from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, Date, Integer, Boolean
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Record(Base):
    __tablename__ = 'Record'
    id = Column(String(32), primary_key=True)
    name = Column(String(32))
    temperature = Column(Float)
    date = Column(Date)


class Prize(Base):
    __tablename__ = 'Prize'
    id = Column(Integer, primary_key=True, autoincrement=True)
    lottery_round = Column(Integer)
    round_level = Column(Integer)
    desc = Column(String(128))
    prize_count = Column(Integer)
    sponsor = Column(String(32))
    is_global = Column(Boolean)


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean)
    single_prize_id = Column(Integer)
    global_prize_id = Column(Integer)
    external_prize_id = Column(Integer)


sqlite_url = 'sqlite:///bmw.db?check_same_thread=False'

engine = create_engine(sqlite_url)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

session = Session()


