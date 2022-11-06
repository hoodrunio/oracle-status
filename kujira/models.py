from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import UniqueConstraint

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
    date = Column(DateTime, server_default=func.now())
    value = Column(Integer)
    userid = Column(Integer, ForeignKey("validators.id"))


class User(Base):
    __tablename__ = 'validators'

    id = Column(Integer, primary_key=True)
    discordname = Column(String)
    address = Column(String, unique=True, index=True)
    moniker = Column(String)
    missing = relationship("Missing")
    last_alarm_count = Column(Integer)
    alarm_threshold = Column(Integer)

    def __repr__(self):
        return f'User {self.moniker}'

    def check_alarm_status(self, new_value):
        if self.last_alarm_count == None:
            self.last_alarm_count = new_value
        else:
            if (new_value - self.last_alarm_count) > self.alarm_threshold:
                #Notify via discord
                #after successful notification, set last alarm count to new value
                self.last_alarm_count = new_value

    def add_missing(self, value):
        last_missing = self.missing[-1].value
        if value !=last_missing:
            #warning, if the count reset and then increase to the same value,
            #we can't catch that alarm
            newrecord = Missing(value=value, userid=self.id)
            session.add(newrecord)
            session.commit()
            self.check_alarm_status(value)
