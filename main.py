#!/usr/bin/python

'''
Logic for handling user login and homepage
'''

import web
from web import form
from hashlib import sha256

from config import *
from generate_period import dates_of_current_week
from model import *
from utils import to_date

urls = (
    '/', 'login'
    , '/create-account', 'accountcreation'
    , '/main', 'mainpage'
    , '/logout', 'logout'
    , '/conductcounseling', 'conductcounseling'
    )

app =  web.application(urls, globals())
render = web.template.render('templates/')

DBSession = Session

if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'user': None})
    web.config._session = session
else:
    session = web.config._session

class logout:
    def GET(self):
        session.kill()
        web.seeother('/')

class login:
    '''
    Class that handles logging in.
    '''
    
    def GET(self):
        return render.login(None)
    def POST(self):
        data = web.input()
        try:
            name = int(data['username'])
        except ValueError:
            return render.login("Please enter a number as the username.")
        else:
            password_hash = sha256(str(name) + data['password']).hexdigest()
            db_session = DBSession()
            user = db_session.query(User).filter(User.id==name).filter(User.password==password_hash).first()
            if user:
                session.user = user
                raise web.seeother('/main')
            else:
                return render.login('Username or password is incorrect.')

class mainpage:
    '''
    Class that handles the main menu,
    after the user has logged in successfully.
    '''
    def GET(self):
        if session.user is None:
            web.seeother('/') # they haven't logged in yet
        else:
            user = session.user
            db_session = DBSession()
            counselor = db_session.query(Counselor).filter(Counselor.id==user.id).first()
            return render.mainpage(user, counselor)
            
class accountcreation:
    '''
    Handler for account creation
    '''
    def GET(self):
        return render.createaccount()

    def POST(self):
        
        db_session = DBSession()
        data = web.input()
        user = User()
        user.id = int(data['ID Number'])
        name = ' '.join([data['firstname'], data['middleinitial'], data['lastname']])
        user.name = name
        user.password = sha256(str(user.id) + data['Password']).hexdigest()
        user.is_counselor = True
        db_session.add(user)
        db_session.commit()

        db_session = DBSession()
        counselor = Counselor()
        counselor.id = user.id
        counselor.nickname = data['Nickname']
        counselor.address = data['City Address']
        counselor.telno = data['telephone']
        counselor.celno = data['cellphone']
        counselor.email = data['email']
        counselor.is_head_counselor = False
        db_session.add(counselor)
        db_session.commit()

        return "success!"
        
class conductcounseling:
    '''
    Handler for the conduct counseling page
    '''
    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            db_session = DBSession()
            counselor = db_session.query(Counselor).filter_by(id=session.user.id).first()
            this_week = dates_of_current_week()
            recent_entries = [entry for entry in counselor.schedule_entries if entry.period.date in this_week]
            return render.conductcounseling(session.user, counselor, recent_entries)
        
if __name__ == '__main__':
    app.run()