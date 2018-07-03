import datetime
from flask_sqlalchemy import SQLAlchemy
from .app import app


db = SQLAlchemy(app)


class Log(db.Model):
    __tablename__ = "taigabuddy_log"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True),
                          nullable=False,
                          default=datetime.datetime.utcnow)
    logentry = db.Column(db.String)


class SprintPoints(db.Model):
    __tablename__ = "taigabuddy_sprintdata"

    id = db.Column(db.Integer, primary_key=True)
    sprintid = db.Column(db.Integer)
    opened = db.Column(db.DateTime)
    who = db.Column(db.String, nullable=False)
    sprintname = db.Column(db.String, nullable=False)
    start_points = db.Column(db.Float, default=0.0)
    current_points = db.Column(db.Float, default=0.0)

    def __str__(self):
        return "<SprintPoints(%d, %s, %s, %s, %s)>" % (
            self.sprintid, self.opened, self.who,
            self.start_points, self.current_points)


print("model.py: app.config = ", dir(app.config))
db.create_all()
