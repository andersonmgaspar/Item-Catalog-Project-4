from models import *
from flask import (Flask, jsonify, request, url_for, render_template,
                   redirect, make_response, flash)
from flask import session as login_session

import os
import random
import string
import httplib2
import json
import requests
from datetime import datetime
from functools import wraps

from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import desc, asc

from flask_sqlalchemy import SQLAlchemy

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


app = Flask(__name__)
# Load the server configuration file
app.config.from_pyfile('app.cfg')
# create a secret key
app.secret_key = os.urandom(24)
# Load the Database connection
db = SQLAlchemy(app)
state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                for x in xrange(32))

g_client_secret_file = 'g_client_secret.json'

# Getting my client_id from the g_client_secret_file
client_id = json.loads(
    open(g_client_secret_file, 'r').read())['web']['client_id']


# Anotation to check if user is logged
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Authenticaltion - check if user is logged-in
        if 'username' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect(url_for('showCatalog'))
    return decorated_function


# Create a user with the session information
def create_user(login_session):
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    db.session.add(new_user)
    db.session.commit()
    user = (db.session.query(User).
            filter_by(email=login_session['email']).first())
    return user.id


# Retrieve a User object by it's ID
def get_user_info(user_id):
    user = db.session.query(User).filter_by(id=user_id).first()
    return user


# Retrieve a user id by an e-mail
def get_user_id(email):
    try:
        user = db.session.query(User).filter_by(email=email).first()
        return user.id
    except:
        print("NO USER FOUND!")
        return None


# DEPRECATED
# Create an anti-forgery state token and redirect to Login page
@app.route('/login')
def showLogin():
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# A method to process the Google OAUTH2 flow
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Anti-forgery system. Checks if the same code is being passed back
    # by the user
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Receive and collect the one-time code sent by the website after
    # login
    auth_code = request.data
    try:
        # Upgrade the authorization or one-time code into a credentials
        # object
        oauth_flow = flow_from_clientsecrets(g_client_secret_file, scope='')
        # Define as 'postmessage' that this is the one-time code being
        # sent to the server
        oauth_flow.redirect_uri = 'postmessage'
        # Initiate the exchange passing the one-time code, if it goes
        # well, it creates the object, if goes bad, raises the
        # following exception
        credentials = oauth_flow.step2_exchange(auth_code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print(response)
        return response
    # Check that the access token is valid
    # Store the access token inside a variable
    access_token = credentials.access_token
    # Checks if the token is valid by making an API call using the
    # access token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort mission bt
    # sending an error message.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if the access token is from the intended user. If not,
    # send error message
    google_id = credentials.id_token['sub']
    if result['user_id'] != google_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if the access token is valid for this app. If not,
    # send error message
    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_google_id = login_session.get('google_id')
    if stored_access_token is not None and google_id == stored_google_id:
        response = make_response(json.dumps('Current user is connected'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # If everything is fine until now, store the access token in the
    # session for later use
    login_session['provider'] = 'google'
    login_session['access_token'] = access_token
    login_session['google_id'] = google_id
    # Get User Info using the access token, but only the data allowed
    # by my token scope which is defined in the button setup
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # Checks if the user already exists in the database. If not creates
    # a new user into the database.
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    # Add the defintiely user_id to the login_session
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' "style = "width: 250px;'
    output += 'height: 250px;'
    output += 'border-radius: 150px;'
    output += '-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;">'
    flash("You are now logged in as %s." % login_session['username'])
    return output


# Disconnect Google Account.
def gdisconnect():
    """Disconnect the Google account of the current logged-in user."""

    # Only disconnect the connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Log out the currently connected user.
@app.route('/logout')
def logout():
    print("Logging out...")
    if 'username' in login_session:
        gdisconnect()
        del login_session['google_id']
        del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        flash("You have been successfully logged out!")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in!")
        return redirect(url_for('showCatalog'))


# Show the main page
@app.route('/')
@app.route('/catalog/')
def showCatalog():
    login_session['state'] = state
    categories = db.session.query(Category).order_by(asc(Category.name))
    items = db.session.query(Item).order_by(desc(Item.date)).limit(5)
    return render_template('catalog.html', categories=categories,
                           items=items, STATE=state)


# Save a new Category
@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def saveCategory():
    if request.method == 'POST':
        # NEED TO ADD USER
        newCategory = Category(name=request.form['name'],
                               user_id=login_session['user_id'])
        db.session.add(newCategory)
        db.session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newCategory.html')


# Show the itens list in a determined category
@app.route('/category/<int:category_id>/items')
def showCategory(category_id):
    category = db.session.query(Category).filter_by(id=category_id).one()
    items = db.session.query(Item).filter_by(category_id=category_id)
    return render_template(
        'category.html', category=category, items=items)


# Save a new item for a determined category
@app.route('/category/<int:category_id>/new', methods=['GET', 'POST'])
@login_required
def saveItem(category_id):
    if request.method == 'POST':
        # NEED TO ADD USER
        newItem = Item(name=request.form['name'], date=datetime.now(),
                       description=request.form['description'],
                       picture=request.form['picture'],
                       category_id=category_id,
                       user_id=login_session['user_id'])
        db.session.add(newItem)
        db.session.commit()
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template('newItem.html', category_id=category_id)


# Delete a category
@app.route('/category/<int:category_id>/delete')
@login_required
def deleteCategory(category_id):
    categoryToDelete = (db.session.query(Category)
                        .filter_by(id=category_id).one())
    db.session.delete(categoryToDelete)
    db.session.commit()
    return redirect(url_for('showCatalog'))


# Delete a item from a category
@app.route('/category/<int:category_id>/<int:item_id>/delete')
@login_required
def deleteItem(category_id, item_id):
    itemToDelete = db.session.query(Item).filter_by(id=item_id).one()
    db.session.delete(itemToDelete)
    db.session.commit()
    return redirect(url_for('showCategory', category_id=category_id))


# Edit a item from a category
@app.route('/category/<int:category_id>/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
    editedItem = db.session.query(Item).filter_by(id=item_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['picture']:
            editedItem.price = request.form['picture']
        editedItem.date = datetime.now()
        db.session.add(editedItem)
        db.session.commit()
        return redirect(url_for('showCategory', category_id=category_id))
    else:
        return render_template(
            'editItem.html', category_id=category_id, item=editedItem)

# JSON Endpoints


# Return a JSON of all categories in the catalog
@app.route('/category/JSON')
def categories_JSON():
    categories = db.session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


# Return a JSON of all categories in the catalog
@app.route('/category/<int:category_id>/JSON')
def itemsCategoryJSON(category_id):
    items = db.session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Items=[i.serialize for i in items])


# Return a JSON of all the items in the catalog
@app.route('/catalog/JSON')
def showCatalogJSON():
    items = db.session.query(Item).order_by(Item.id.desc())
    return jsonify(catalog=[i.serialize for i in items])


# Users JSON endpoint, for tests purposes
@app.route('/user/JSON')
def usersJSON():
    users = db.session.query(User).all()
    return jsonify(Users=[i.serialize for i in users])


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
