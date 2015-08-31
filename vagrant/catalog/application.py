# Application 3 Catalog
# Application.py
# Author: Lucas Velasquez
# Date: 8/25/2015

# Import Flask
from flask import Flask, render_template, url_for, request, redirect
app = Flask(__name__)
# Import DB
from sqlalchemy import create_engine, and_
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
# Item View Route
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def viewItem(category_name, item_name):
    categories = session.query(Categories).all()
    items = session.query(Items).join(Categories, Items.category_id == Categories.id) \
    							.filter(Categories.category_name == category_name, Items.item_name == item_name) \
    							.values(Items.item_name, Items.description, Categories.category_name)

    
    return render_template('items.html', categories = categories, items = items, \
    					    categoryName = category_name)
# Item New Route
@app.route('/catalog/<string:category_name>/new', methods=['GET', 'POST'])
def newItem(category_name):
	if request.method == 'POST':
		getCategoryid = session.query(Categories).filter(Categories.category_name == request.form['category_name']).first()
		newItem = Items(item_name = request.form['item_name'], description = request.form['description'], \
						category_id = getCategoryid.id)
		try:
			session.add(newItem)
			session.commit()
			return redirect(url_for('homePage'))
		except:
			return "Error Saving Record to Database"

	else:
		categories = session.query(Categories).all()
    	return render_template('new_item.html', categories = categories, categoryName = category_name)
# Item Edit Route
@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_name):
	if request.method == 'POST':
		newCategoryid = session.query(Categories).filter(Categories.category_name == request.form['category_name']).one()
		oldCategoryid = session.query(Categories).filter(Categories.category_name == category_name).first()
		getRecord = session.query(Items).filter(Items.item_name == item_name, Items.category_id == oldCategoryid.id).one()
		getRecord.item_name = request.form['item_name']
		getRecord.description = request.form['description']
		getRecord.category_id = newCategoryid.id
		try:
			session.add(getRecord)
			session.commit()
			return redirect(url_for('homePage'))
		except:
			return "Error Saving Record to Database"
	else:
		categories = session.query(Categories).all()
    	items = session.query(Items).join(Categories, Items.category_id == Categories.id) \
    							.filter(Categories.category_name == category_name, Items.item_name == item_name) \
    							.values(Items.item_name, Items.description, Categories.category_name, Items.category_id)
    	itemDescription = session.query(Items).filter(Items.item_name == item_name).first()
    	return render_template('edit_item.html', categories = categories, item_name = item_name, \
    					    	categoryName = category_name, item_description = itemDescription.description)
# Item Delete Route
@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
	if request.method == 'POST':
		oldCategoryid = session.query(Categories).filter(Categories.category_name == category_name).first()
		getRecord = session.query(Items).filter(Items.item_name == item_name, Items.category_id == oldCategoryid.id).one()
		try:
			session.delete(getRecord)
			session.commit()
			return redirect(url_for('homePage'))
		except:
			return "Error Saving Record to Database"
	else:
		categories = session.query(Categories).all()
    	
    	return render_template('delete_item.html', categories = categories, item_name = item_name, \
    							categoryName = category_name)
if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
