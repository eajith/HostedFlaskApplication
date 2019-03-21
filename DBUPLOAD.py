from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from modelsNew import Category, Base, Items, Users

import datetime
import psycopg2 


currentDT = datetime.datetime.now()

engine = create_engine('postgresql://catalog:catalog@localhost/catalogdb')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

session.query(Category).delete()
session.commit()
session.query(Items).delete()
session.commit()
session.query(Users).delete()
session.commit()

User1 = Users(name="Ajithkumar", email="eajithkumar128@gmail.com",picture='dd')
session.add(User1)
session.commit()

#Menu for UrbanBurger
category1 = Category(user_id=1,name = "Football")

session.add(category1)
session.commit()

Item1 = Items(user_id=1,title='ball',Description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
					upload_date=currentDT,category=category1)

session.add(Item1)
session.commit()

Item2 = Items(user_id=1,title='shoe',Description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
					upload_date=currentDT,category=category1)

session.add(Item2)
session.commit()

category2 = Category(user_id=1,name = "Hockey")

session.add(category2)
session.commit()

Item3 = Items(user_id=1,title='ball',Description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
					upload_date=currentDT,category=category2)

session.add(Item3)
session.commit()

Item4 = Items(user_id=1,title='shoe',Description="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.",
					upload_date=currentDT,category=category2)

session.add(Item4)
session.commit()
# Item1 = Items(title='ball',Description='something about the ball',
# 					upload_date=datetime.datetime.now(),category=category1)

# session.add(Item1)
# session.commit()


# Item2 = Items=2,title='Shoe',Description='something about the shoe',
# 					upload_date=datetime.datetime.now(),category=category2)

# session.add(Item2)
# session.commit()
