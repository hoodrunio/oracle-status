from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

#TODO: when deploying, replace engine with postgresql
#sqlite is only for local testing
engine = create_engine('sqlite:///kujira.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


def initialize():
    """
    Create database and tables
    """
    Base.metadata.create_all(engine)

class Missing(Base):
    __tablename__ = 'missing'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    count = Column(Integer)

class User(Base):
    __tablename__ = 'validators'

    id = Column(Integer, primary_key=True)
    discordname = Column(String)
    telegramname = Column(String)
    address = Column(String)
    moniker = Column(String)
    missing = relationship(Missing)

    def __repr__(self):
        return f'User {self.moniker}'

    def add_missing(self, count):
        pass