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
from sqlalchemy.orm import subqueryload
from utils import to_date, iso_to_date

urls = (
    '/', 'login'
    , '/create-account', 'accountcreation'
    , '/main', 'mainpage'
    , '/logout', 'logout'
    , '/conductcounseling', 'conductcounseling'
    , '/create_routine', 'create_routine'
    , '/assigncounselor', 'assigncounselor'
    , '/viewstudent', 'viewstudent'
    , '/studentprofile', 'studentprofile'
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

class assigncounselor:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            db_session = DBSession()
            counselors = db_session.query(Counselor).order_by(Counselor.id).all()
            sections = db_session.query(Section).filter_by(counselor_id=None).order_by(Section.id).all()
            return render.assigncounselor(counselors, sections, str)

    def POST(self):
        data = web.input(selected_drop=[]) # we put a default value so that web.py puts the multivalued select fields into a list, and not simply give the last item
        id = int(data['counselor_chosen'])
        db_session = DBSession()
        counselor = db_session.query(Counselor).filter_by(id = id).one()
        all_sections = db_session.query(Section)
        chosen_sections = [section for section in all_sections if str(section.year) + section.name in data['selected_drop']]
        counselor.sections = chosen_sections
        db_session.add(counselor)
        db_session.commit()
        return 'success!'

class viewstudent:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            db_session = DBSession()
            data = web.input()
            counselor = db_session.query(Counselor).filter_by(id = session.user.id).one()
            handled_section_ids = db_session.query(Section.id).filter_by(counselor_id = counselor.id)
            students = db_session.query(Student).filter(Student.section_id.in_(handled_section_ids)).join(Student.section)
            if 'letter' in data:
                students = students.filter(Student.last_name.like(data['letter'] + '%'))
            elif 'year' in data:
                students = students.filter(Section.year == int(data['year']))
            elif 'section' in data:
                students = students.filter(Section.year == int(data['section'][0]), Section.name == data['section'][1])
            return render.viewstudent(students.all(), str)

class studentprofile:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            data = web.input()
            id = int(data['id'])
            student = DBSession().query(Student).filter_by(id = id).one()
            return render.studentprofile(student)

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

class create_routine:

    def GET(self):
        return render.create_routine()

    def POST(self):
        data = web.input()
        db_session = DBSession()
        
        id = int(data['id'])
        date = iso_to_date(data['date'])
        num = int(data['num'])
        student = db_session.query(Student).filter_by(id=id).first()
        period = db_session.query(Period).filter_by(date=date, num=num).first()
        counselor = db_session.query(Counselor).filter_by(id=session.user.id).first()
        type = db_session.query(InterviewType).filter_by(name='Routine Interview').first()

        interview = Interview()
        interview.type = type
        interview.counselor = counselor
        interview.period = period
        interview.student = student

        routine = RoutineInterview()
        routine.general_mental_ability = data['gen_ability']
        routine.academic_history = data['academic_history']
        routine.family_relationship = data['family']
        routine.personal_emotional = data['personal']
        routine.peer_relationship = data['peer']
        routine.goals = data['goals']
        routine.recommendation = data['recommendation']

        db_session.add(interview)
        db_session.commit()
        db_session.add(routine)
        routine.id = interview.id
        db_session.commit()
        return 'Success!'
        
    
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