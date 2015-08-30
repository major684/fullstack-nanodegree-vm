# Create database
# Author: Lucas Velasquez

import sys
import datetime
# Import for mapper code
from sqlalchemy import \
 Column, ForeignKey, Integer, String, DateTime
# Used for config and class code
from sqlalchemy.ext.declarative import \
declarative_base
# Used to create FK relationship
from sqlalchemy.orm import relationship
# Used for create engine
from sqlalchemy import create_engine
# Lets sqlalchemy know we are using special classes
Base = declarative_base()

#Classes
class Categories(Base):
	__tablename__ = 'categories'
	id = Column(
		Integer, primary_key = True)
	category_name = Column(
		String(200), nullable = False)
	date_added = Column(
		DateTime, default = datetime.datetime.now)

class Items(Base):
	__tablename__ = 'items'
	id = Column(
		Integer, primary_key = True)
	item_name = Column(
		String(150), nullable = False)
	description = Column(
		String(250), nullable = False)
	category_id = Column(
		Integer, ForeignKey(Categories.id))
	date_added = Column(
		DateTime, default = datetime.datetime.now)


# Insert at end of file
engine = create_engine(
    'sqlite:///catalog.db')

Base.metadata.create_all(engine)
