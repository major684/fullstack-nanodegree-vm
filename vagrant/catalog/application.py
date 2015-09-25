# Application 3 Catalog
# Application.py
# Author: Lucas Velasquez
# Date: 8/25/2015

# Import Flask
from flask import Flask, render_template, url_for, request, redirect, jsonify, flash
app = Flask(__name__)
# Import OAuth
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests
from flask import make_response

CLIENT_ID = json.loads(
	open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"
# Import DB
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Categories, Items
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Facebook login
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = request.data
	print "access token received %s " % access_token

	app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
		'web']['app_id']
	app_secret = json.loads(
		open('fb_client_secrets.json', 'r').read())['web']['app_secret']
	url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
		app_id, app_secret, access_token)
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]

	# Use token to get user info from API
	userinfo_url = "https://graph.facebook.com/v2.4/me"
	# strip expire tag from access token
	token = result.split("&")[0]


	url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	# print "url sent for API access:%s"% url
	# print "API JSON result: %s" % result
	data = json.loads(result)
	login_session['provider'] = 'facebook'
	login_session['username'] = data["name"]
	login_session['email'] = data["email"]
	login_session['facebook_id'] = data["id"]

	# The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
	stored_token = token.split("=")[1]
	login_session['access_token'] = stored_token

	# Get user picture
	url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	data = json.loads(result)

	login_session['picture'] = data["data"]["url"]
	login_session['provider'] = 'facebook'
	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']

	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

	flash("Now logged in as %s" % login_session['username'])
	return output


@app.route('/fbdisconnect')
def fbdisconnect():
	facebook_id = login_session['facebook_id']
	# The access token must me included to successfully logout
	access_token = login_session['access_token']
	url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
	h = httplib2.Http()
	result = h.request(url, 'DELETE')[1]
	return "you have been logged out"

# Gconnect
# Create anti-forgery state token
@app.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(
			json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid.
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
		   % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
			json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'),
								 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['provider'] = 'google'
	login_session['credentials'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	print "done!"
	return output
# Logout
@app.route('/gdisconnect')
def gdisconnect():
		# Only disconnect a connected user.
	credentials = login_session.get('credentials')
	if credentials is None:
		response = make_response(
			json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	access_token = login_session.get('credentials')
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	if result['status'] == '200':
		# Reset the user's sesson.
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']

		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		flash('response')
		return redirect(url_for('homePage'))
	else:
		# For whatever reason, the given token was invalid.
		response = make_response(
			json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response
# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
	if 'provider' in login_session:
		if login_session['provider'] == 'google':
			gdisconnect()
			del login_session['credentials']
		if login_session['provider'] == 'facebook':
			fbdisconnect()
			del login_session['facebook_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['provider']
		flash("You have successfully been logged out.")
		return redirect(url_for('homePage'))
	else:
		flash("You were not logged in")
		return redirect(url_for('homePage'))

# Login View Route
@app.route('/login')
def showLogin():
	# Create anti-forgery token key
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)
# Home View Route
@app.route('/')
@app.route('/home')
def homePage():
	# Get all categories for side cateogry menu
	categories = session.query(Categories).all()
	# Grab a collection of items
	items = session.query(Items).join(Categories, Items.category_id == Categories.id) \
									.order_by(Items.date_added.desc()).limit(5) \
									.values(Items.item_name, Categories.category_name)
	# Check to see if user logged in or not and return appropriate page
	if 'username' not in login_session:
		return render_template('public_home.html', categories = categories, items = items)
	else:
		return render_template('home.html', categories = categories, items = items)
# Categories Route
@app.route('/catalog/<string:category_name>/items/')
def categoryItems(category_name):
	# Get all categories for side cateogry menu
	categories = session.query(Categories).all()
	# Grab a Collection of items
	items = session.query(Items).join(Categories, Items.category_id == Categories.id) \
								.filter(Categories.category_name == category_name) \
								.values(Items.item_name, Categories.category_name)
	# Get a count of items in a category
	count = session.query(Items).join(Categories, Items.category_id == Categories.id) \
								.filter(Categories.category_name == category_name) \
								.count()
	if 'username' not in login_session:
		return render_template('public_categories.html', categories = categories, items = items, itemCount = count, \
							categoryName = category_name)
	else:
		return render_template('categories.html', categories = categories, items = items, itemCount = count, \
							categoryName = category_name)
# Item View Route
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def viewItem(category_name, item_name):
	# Get all categories for side cateogry menu
	categories = session.query(Categories).all()
	# Grab a Collection of items
	items = session.query(Items).join(Categories, Items.category_id == Categories.id) \
								.filter(Categories.category_name == category_name, \
										Items.item_name == item_name) \
								.values(Items.item_name, Items.description, Categories.category_name)

	if 'username' not in login_session:
		return render_template('public_items.html', categories = categories, items = items, \
							categoryName = category_name)
	else:
		return render_template('items.html', categories = categories, items = items, \
							categoryName = category_name)
# Item New Route
@app.route('/catalog/<string:category_name>/new', methods=['GET', 'POST'])
def newItem(category_name):
	# Check to see if authenticated
	if 'username' not in login_session:
		return redirect('login')
	# Do if form method is a post
	if request.method == 'POST':
		getCategoryid = session.query(Categories).filter(Categories.category_name == \
										request.form['category_name']).first()
		newItem = Items(item_name = request.form['item_name'], description = \
										request.form['description'], category_id = getCategoryid.id)
		# Try/except for error handling
		try:
			session.add(newItem)
			session.commit()
			return redirect(url_for('homePage'))
		except:
			return "Error Saving Record to Database"
	else:
		# Get all categories for side cateogry menu for get method
		categories = session.query(Categories).all()
		return render_template('new_item.html', categories = categories, categoryName = category_name)
# Item Edit Route
@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
def editItem(category_name, item_name):
	# Check to see if authenticated
	if 'username' not in login_session:
		return redirect('login')
	# Do if form method is a post
	if request.method == 'POST':
		newCategoryid = session.query(Categories).filter(Categories.category_name == \
										request.form['category_name']).one()
		oldCategoryid = session.query(Categories).filter(Categories.category_name == \
										category_name).first()
		getRecord = session.query(Items).filter(Items.item_name == item_name, \
										Items.category_id == oldCategoryid.id).one()
		getRecord.item_name = request.form['item_name']
		getRecord.description = request.form['description']
		getRecord.category_id = newCategoryid.id
		# Try/except for error handling
		try:
			session.add(getRecord)
			session.commit()
			return redirect(url_for('homePage'))
		except:
			return "Error Saving Record to Database"
	else:
		# Get all categories for side cateogry menu for get method
		categories = session.query(Categories).all()
		# Grab a Collection of items
		items = session.query(Items).join(Categories, Items.category_id == Categories.id) \
								.filter(Categories.category_name == category_name, \
										Items.item_name == item_name) \
								.values(Items.item_name, Items.description, Categories.category_name, \
										Items.category_id)
		itemDescription = session.query(Items).filter(Items.item_name == item_name).first()
		return render_template('edit_item.html', categories = categories, item_name = item_name, \
								categoryName = category_name, item_description = itemDescription.description)
# Item Delete Route
@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
	# Check to see if authenticated
	if 'username' not in login_session:
		return redirect('login')
	# Do if form method is a post
	if request.method == 'POST':
		# Original cateogry id
		oldCategoryid = session.query(Categories).filter(Categories.category_name == category_name) \
									 .first()
		getRecord = session.query(Items).filter(Items.item_name == item_name, Items.category_id == \
								   oldCategoryid.id).one()
		# Try/except for error handling
		try:
			session.delete(getRecord)
			session.commit()
			return redirect(url_for('homePage'))
		except:
			return "Error Saving Record to Database"
	else:
		# Get all categories for side cateogry menu
		categories = session.query(Categories).all()
		
		return render_template('delete_item.html', categories = categories, item_name = item_name, \
								categoryName = category_name)

# Making an API Endpoing (GET)
# Get Items in a category
@app.route('/catalog/<string:category_name>/items/JSON')
def categoryItemsJSON(category_name):
	# Grab a Collection of items
	items = session.query(Items).join(Categories, Items.category_id == Categories.id) \
								.filter(Categories.category_name == category_name) \
								.all()
	return jsonify(CategoryItems=[i.serialize for i in items])

# Get all categories
@app.route('/catalog/allCategories/JSON')
def allCategories():
	# Grab a Collection of items
	categories = session.query(Categories).all()
	return jsonify(Categories=[i.serialize for i in categories])

# Main App Defenition
if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)
