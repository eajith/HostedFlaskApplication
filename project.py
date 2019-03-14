from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)


from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from modelsNew import Base, Category, Items, User
from sqlalchemy import desc


from flask import session as login_session
import random, string	


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

import datetime


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ItemCatalog"


engine = create_engine('sqlite:///itemcategoryDB.db',
						connect_args={'check_same_thread':False})
Base.metadata.bind = engine


DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route("/login")
def loginRoute():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('loginPage.html',STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    print("came")
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
        return response

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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])

    if not user_id:
    	user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print('User name is: ')
    print(login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('homePage'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route("/")
@app.route("/catalog")
def homePage():
	category = session.query(Category).all()
	items = session.query(Items).order_by(desc(Items.upload_date)).all()
	if 'username' not in login_session:
		login_session['user_id']=None
	return render_template('homePage.html',category=category,
					items=items,loginId=login_session['user_id'])


@app.route("/catalog/<int:category_id>/items")
def catalogItems(category_id):
	categoryItems = session.query(Items).filter_by(
							category_id=category_id).all()
	category = session.query(Category).filter_by(
							id=category_id
						).one()
	allCategory= session.query(Category).all()
	if 'username' not in login_session:
		login_session['user_id']=None
	return render_template('catalogItem.html',
								Category_name=category,
								category=allCategory,
								categoryItems=categoryItems,
								loginId=login_session['user_id'])


@app.route("/catalog/new",methods=['GET','POST'])
def addCategory():
	if 'username' not in login_session:
		return redirect(url_for("loginRoute"))
	if request.method == 'POST':
		newCategory = Category(name=request.form['name'],
						user_id=login_session['user_id']
									)
		session.add(newCategory)
		session.commit()
		return redirect(url_for('homePage'))
	else:
		if 'username' not in login_session:
			login_session['user_id']=None
		return render_template('newCategory.html',
						loginId=login_session['user_id'])


@app.route("/catalog/<int:category_id>/edit/",methods=['GET','POST'])
def editCategory(category_id):
	if 'username' not in login_session:
		return redirect(url_for("loginRoute"))
	editedCategory = session.query(Category).filter_by(id=category_id).one()
	if login_session['user_id'] != editedCategory.user_id:
		return "YOU DON'T HAVE PERMISSION TO DELTE THE ITEM"
	if request.method == 'POST':
	    if request.form['name']:
	    	editedCategory.name = request.form['name']
	    session.add(editedCategory)
	    session.commit()
	    return redirect(url_for('homePage'))
	else:
		if 'username' not in login_session:
			login_session['user_id']=None
		return render_template('editCategory.html',
									category=editedCategory,
									loginId=login_session['user_id'])


@app.route("/catalog/<int:category_id>/delete/",methods=['GET','POST'])
def deleteCategory(category_id):
	if 'username' not in login_session:
		return redirect(url_for("loginRoute"))
	deleteCategory = session.query(Category).filter_by(id=category_id).one()
	deleteItems = session.query(Items).filter_by(category_id=category_id).all()
	if login_session['user_id'] != deleteCategory.user_id:
		return "YOU DON'T HAVE PERMISSION TO DELTE THE ITEM"
	if request.method == 'POST':
		session.delete(deleteCategory)
		for item in deleteItems:
			session.delete(item)
			session.commit()
		session.commit()
		return redirect(url_for('homePage'))
	else:
		if 'username' not in login_session:
			login_session['user_id']=None
		return render_template('deleteCategory.html',
									category=deleteCategory,
									loginId=login_session['user_id'])


@app.route("/catalog/<int:category_id>/<int:item>/")
def itemDetails(category_id,item):
	itemDetail = session.query(Items).filter_by(id=item).one()
	loggedIn = None
	if login_session['user_id'] == itemDetail.user_id:
	   loggedIn = 'Yes'
	if 'username' not in login_session:
			login_session['user_id']=None
	return render_template('itemDetail.html',itemDetail=itemDetail,
								loggedIn = loggedIn,
								loginId=login_session['user_id'])


@app.route("/catalog/add/items",methods=['GET','POST'])
def addItem():
	if 'username' not in login_session:
		return redirect(url_for("loginRoute"))
	if request.method == 'POST':
		category = session.query(Category).filter_by(id=request.form['category_id']).one()
		print(category)
		newItem = Items(title=request.form['name'],
							Description=request.form['description'],
							upload_date=datetime.datetime.now(),
							category=category,
							user_id=login_session['user_id'])
		print(newItem)
		session.add(newItem)
		session.commit()
		return redirect(url_for('homePage'))
	else:
		category = session.query(Category).all()
		if 'username' not in login_session:
			login_session['user_id']=None
		return render_template('newItem.html',
									category=category,
									loginId=login_session['user_id'])


@app.route("/catalog/<int:category_id>/<int:item_id>/edit",methods=['GET','POST'])
def editItem(category_id,item_id):
	if 'username' not in login_session:
		return redirect(url_for("loginRoute"))
	editedItem = session.query(Items).filter_by(id=item_id).one()
	if login_session['user_id'] != editedItem.user_id:
		return "YOU DON'T HAVE PERMISSION TO DELTE THE ITEM"
	if request.method == 'POST':
	   if request.form['name']:
	   		editedItem.title=request.form['name']
	   if request.form['Description']:
	   		editedItem.Description = request.form['Description']
	   session.add(editedItem)
	   session.commit()
	   return redirect(url_for('itemDetails',category_id=category_id,item=editedItem.id))
	else:
		category = session.query(Category).all()
		itemDetail = session.query(Items).filter_by(id=item_id).one()
		if 'username' not in login_session:
			login_session['user_id']=None
		return render_template('editItem.html',item=itemDetail,
								category=category,
								loginId=login_session['user_id'])


@app.route("/catalog/<int:category_id>/<int:item_id>/delete",methods=['GET','POST'])
def deleteItem(category_id,item_id):
	if 'username' not in login_session:
		return redirect(url_for("loginRoute"))
	category = session.query(Category).filter_by(id=category_id).one()
	itemToDelete = session.query(Items).filter_by(id=item_id).one()
	if login_session['user_id'] != itemToDelete.user_id:
		return "YOU DON'T HAVE PERMISSION TO DELTE THE ITEM"
	if request.method == 'POST':
	   session.delete(itemToDelete)
	   session.commit()
	   return redirect(url_for('catalogItems',category_id=category.id))
	else:
		itemDetail = session.query(Items).filter_by(id=item_id).one()
		if 'username' not in login_session:
			login_session['user_id']=None
		return render_template('deleteItem.html',item=itemDetail,
										loginId=login_session['user_id'])


if __name__ == '__main__':
	app.debug = True
	app.secret_key = 'some secret key'
	app.run(host='0.0.0.0',port=5000)
