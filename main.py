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

urls = (
    '/', 'login'
    , '/create-account', 'accountcreation'
    )

DBNAME = 'counselor.db'
DBPATH = os.getcwd()

engine = create_engine('sqlite:////' + os.path.join(DBPATH,DBNAME), echo=True)
Session = sessionmaker(bind=engine)
db_session = Session()

app =  web.application(urls, globals())
render = web.template.render('templates/')
initializer = {
    'user' : None
    }
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer = initializer)

loginform = form.Form(
    form.Textbox('username')
    , form.Password('password')
    , form.Button('login')
)

class login:
    '''
    Class that handles logging in.
    '''
    
    def GET(self):
        f = loginform()
        return render.login(f)
    def POST(self):
        f = loginform()
        if f.validates():
            data = web.input()
            password_hash = sha256(data['password'])
            userlist = [ row.User for row in db_session.query(User, User.password).all() if row.password == password_hash]
            if userlist:
                user = userlist[0]
                session.user = user
                raise web.redirect('/index')
            else:
                return render.login(f)
        else:
            render.login(f)

class accountcreation:
    '''
    Handler for account creation
    '''
    def GET(self):
        return render.createaccount()

class index:
    '''
    Class that handles the homepage once a person has logged in.
    '''
    def GET(self):
        pass

if __name__ == '__main__':
    app.run()