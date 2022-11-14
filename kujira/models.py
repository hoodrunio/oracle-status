from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import UniqueConstraint
from datetime import datetime

#TODO: when deploying, replace engine with postgresql
#sqlite is only for local testing

ENGINE='postgresql://kujirabottestuser:32319ae795b57d2e61b105dfd6f@localhost:5432/kujiratestdb'  # test

ENGINE='postgresql://kujirabotuser:32319ae795b57d2e61b105dfd6f@localhost:5432/kujiradb' # main

engine = create_engine(ENGINE)
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


class Notify(Base):
    __tablename__ = 'notifylist'
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey("validators.id"))
    discord_name = Column(String)


class User(Base):
    __tablename__ = 'validators'
    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, index=True)
    moniker = Column(String)
    missing = relationship("Missing")
    last_alarm_count = Column(Integer)
    last_alarm_date = Column(DateTime)
    alarm_threshold = Column(Integer)
    notify = relationship("Notify")

    def __repr__(self):
        return f'User {self.moniker}'

    def alarm_message(self):
        return f"Moniker :{self.moniker}\nAddress :{self.address}\nAlarm date:{self.missing[-1].date}\nAlarm Value:{self.missing[-1].value}\nNotification List{self.notify_list()}"
    
    def notify_list(self):
        msg = "\n"
        for user in self.notify:
            msg += " * " + user.discord_name + "\n"
        return msg

    def delete_notify(self, user_to_notify):
        for user in self.notify:
            if user.discord_name == user_to_notify:
                session.delete(user)
                session.commit()
                return True
        return False
    
    def add_notify(self, user_to_notify):
        found = False
        for user in self.notify:
            if user.discord_name == user_to_notify:
                found = True
                return False
        if not found:
            n = Notify(userid=self.id, discord_name=user_to_notify)
            session.add(n)
            session.commit()
        return True


    def check_alarm_status(self):
        session.refresh(self)
        last = None
        if len(self.missing) > 0:
            last = self.missing[-1]
            if self.last_alarm_date is not None:
                if last.value - self.last_alarm_count >= self.alarm_threshold:
                    self.last_alarm_date = last.date
                    self.last_alarm_count = last.value
                    session.commit()
                    return True
                else:
                    return False
            else:
                self.last_alarm_date = last.date
                self.last_alarm_count = last.value
                session.commit()
                return False
        else:
            return False
                    
    def add_missing(self, value):
        if len(self.missing) > 0:
            last_missing = self.missing[-1].value
            if value !=last_missing:
                # warning, if the count reset and then increase to the same value,
                # we can't catch that alarm
                newrecord = Missing(value=value, userid=self.id)
                session.add(newrecord)
                session.commit()
        else:
            newrecord = Missing(value=value, userid=self.id)
            session.add(newrecord)
            session.commit()

