import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


Base = declarative_base()
# metadata = MetaData()
engine = create_engine('sqlite:////tmp/test.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                      # autoflush=False,
                                      bind=engine))


class Log(Base):
    __tablename__ = "taigabuddy_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True),
                       nullable=False,
                       default=datetime.datetime.utcnow)
    logentry = Column(String)


class SprintPoints(Base):
    __tablename__ = "taigabuddy_sprintdata"

    id = Column(Integer, primary_key=True)
    sprintid = Column(Integer)
    opened = Column(DateTime)
    who = Column(String, nullable=False)
    start_points = Column(Float, default=0.0)
    current_points = Column(Float, default=0.0)

    def __str__(self):
        return "<SprintPoints(%d, %s, %s, %s, %s)>" % (
            self.sprintid, self.opened, self.who,
            self.start_points, self.current_points)


def db_init(engine=engine):
    Base.metadata.create_all(bind=engine)
    print("-- db_init()")
