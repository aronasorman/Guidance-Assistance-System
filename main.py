#!/usr/bin/python

'''
Logic for handling user login and homepage
'''

import web
from web import form
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from hashlib import sha256
import os

from misc_models import *
from model import *
from utils import to_date

urls = (
    '/', 'login'
    , '/create-account', 'accountcreation'
    , '/main', 'mainpage'
    )

DBNAME = 'counselor.db'
DBPATH = os.getcwd()

engine = create_engine('sqlite:////' + os.path.join(DBPATH,DBNAME), echo=True)
Session = sessionmaker(bind=engine)

app =  web.application(urls, globals())
render = web.template.render('templates/')
initializer = {
    'user' : None
    }
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer = initializer)

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
            password_hash = sha256(data['password']).hexdigest()
            db_session = Session()
            import pdb; pdb.set_trace()
            user = db_session.query(User).filter(User.id==name).filter(User.password==password_hash).first()
            if user:
                session.user = user
                raise web.seeother('/mainpage')
            else:
                return render.login('Username or password is incorrect.')
            
class accountcreation:
    '''
    Handler for account creation
    '''
    def GET(self):
        return render.createaccount()

    def POST(self):
        
        db_session = Session()
        data = web.input()
        user = User()
        user.id = int(data['ID Number'])
        user.password = sha256(data['Password']).hexdigest()
        db_session.add(user)
        db_session.commit()

        db_session = Session()
        counselor = Counselor()
        counselor.id = user.id
        name = ' '.join([data['firstname'], data['middleinitial'], data['lastname']])
        counselor.name = name
        counselor.nickname = data['Nickname']
        counselor.address = data['City Address']
        counselor.telno = data['telephone']
        counselor.celno = data['cellphone']
        counselor.email = data['email']
        counselor.is_head_counselor = False
        db_session.add(counselor)
        db_session.commit()

        return "success!"
        
class index:
    '''
    Class that handles the homepage once a person has logged in.
    '''
    def GET(self):
        pass

if __name__ == '__main__':
    app.run()