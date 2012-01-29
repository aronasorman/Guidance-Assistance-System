#!/usr/bin/python

'''
Logic for handling user login and homepage
'''

import web
from web import form
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from misc_models import *
from model import *

urls = (
    '/', 'login'
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
    def GET(self):
        f = loginform()
        return f.render()
    def POST(self):
        f = loginform()
        if f.validates():
            password_hash = sha256(f['password'])
            userlist = [ row.User for row in db_session.query(User, User.password).all() if row.password == password_hash]
            if len(userlist) > 0:
                user = userlist[0]
                session.user = user
                raise web.redirect('/index')
            else:
                return f.render()
        else:
            f.render()

if __name__ == '__main__':
    app.run()