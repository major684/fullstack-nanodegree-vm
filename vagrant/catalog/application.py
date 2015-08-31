# Application 3 Catalog
# Application.py
# Author: Lucas Velasquez
# Date: 8/25/2015

# Import Flask
from flask import Flask, render_template, url_for, request
app = Flask(__name__)
# Import DB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
# Home View Route
@app.route('/')
@app.route('/home')
def homePage():
    categories = session.query(Categories).all()
    items = session.query(Items).join(Categories, Items.category_id == Categories.id) \
    							.order_by(Items.date_added.desc()).limit(5) \
    							.values(Items.item_name, Categories.category_name)
    
    return render_template('home.html', categories = categories, items = items)
# Categories Route
@app.route('/catalog/<string:category_name>/items/')
def categoryItems(category_name):
    categories = session.query(Categories).all()
    items = session.query(Items).join(Categories, Items.category_id == Categories.id) \
    							.filter(Categories.category_name == category_name) \
    							.values(Items.item_name, Categories.category_name)
    count = session.query(Items).join(Categories, Items.category_id == Categories.id) \
    							.filter(Categories.category_name == category_name) \
    							.count()
    
    return render_template('categories.html', categories = categories, items = items, itemCount = count, \
    					    categoryName = category_name)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
