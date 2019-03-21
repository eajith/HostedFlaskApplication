import os
import sys
import psycopg2
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(2500))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)

    @property
    def serialize(self):
        return{
            'name' : self.name,
            'id'   : self.id
        }


class Items(Base):
    __tablename__ = 'items'


    title =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    Description = Column(String(25000))
    upload_date = Column(DateTime,nullable=False)
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category,backref='items')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(Users)

    @property
    def serialize(self):
        return{
            'id' : self.id,
            'title' : self.title,
            'Description' : self.Description,
            'upload_date' : self.upload_date,
        }


engine = create_engine('postgresql://catalog:catalog@localhost/catalogdb')


Base.metadata.create_all(engine)
