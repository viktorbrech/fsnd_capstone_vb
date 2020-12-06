from sqlalchemy import Column, String, Integer, create_engine, Enum, Date
from flask_sqlalchemy import SQLAlchemy
import json
import os
import enum
from datetime import date

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

class Gender(enum.Enum):
  female = 1
  male = 2
  other = 3


class Actor(db.Model):
    __tablename__ = "Actors"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    age = Column(Integer)
    gender = Column(Enum(Gender))

    """
    METHODS ADAPTED FROM COFFEE_SHOP PROJECT models.py FILE
    """

    '''
    format()
        representation of the model
    '''
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender.name
        }

    '''
    insert()
        inserts a new model into a database
        the model must have a unique name
        the model must have a unique id or null id
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
    '''
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.format())


class Movie(db.Model):
    __tablename__ = "Movies"
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    release_date = Column(Date)

    """
    METHODS ADAPTED FROM COFFEE_SHOP PROJECT models.py FILE
    """

    '''
    format()
        representation of the model
    '''
    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date.isoformat()
        }

    '''
    insert()
        inserts a new model into a database
        the model must have a unique title
        the model must have a unique id or null id
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a new model into a database
        the model must exist in the database
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a new model into a database
        the model must exist in the database
    '''
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.format())