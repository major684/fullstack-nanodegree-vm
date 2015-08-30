# Populate Catalog Database
# Author: Lucas Velasquez
# Date: 8/30/2015

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bine = engine
DBSession = sessionmaker(bind = engine)

# Clear Records in tables
sessionD = DBSession()
delItems = sessionD.query(Items).delete()
delCat = sessionD.query(Categories).delete()
sessionD.commit()

# Create New Records to seed database
session = DBSession()
# Create a new category named Insturments
newCategory = Categories(category_name = 'Instruments')
session.add(newCategory)
# Commit changes to database
session.commit()
# Add items for the category Instruments
newItem = Items(item_name = 'Guitar', description = 'Amazing guitar with personal stickers attached',
				 category_id = newCategory.id)
session.add(newItem)
newItem = Items(item_name = 'Ukulele', description = 'Keep it island with this beautiful Ukulele',
				 category_id = newCategory.id)
session.add(newItem)
# Commit changes to database
session.commit()