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
from sqlalchemy import or_
from sqlalchemy.orm import subqueryload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from utils import to_date, iso_to_date, partition

urls = (
    '/', 'login'
    , '/create-account', 'accountcreation'
    , '/main', 'mainpage'
    , '/logout', 'logout'
    , '/conductcounseling', 'conductcounseling'
    , '/createnotation', 'createnotation'
    , '/assigncounselor', 'assigncounselor'
    , '/viewstudent', 'viewstudent'
    , '/studentprofile', 'studentprofile'
    , '/editweekly', 'editweekly'
    , '/deletefromweekly', 'deletefromweekly'
    , '/choosing', 'choosing'
    , '/assignstudent', 'assignstudent'
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

class editweekly:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            dates_this_week = dates_of_current_week()
            periods_of_counselor = DBSession().query(Period).outerjoin(Period.entries).\
                                   filter(Period.date.in_(dates_this_week)).\
                                   filter(or_(Period.entries.any(counselor_id = session.user.id), Period.entries == None)).\
                                   order_by(Period.num, Period.date)
            periods_partitioned = partition(periods_of_counselor, lambda p: p.num)
            return render.editweekly(periods_partitioned, period_labels)

class deletefromweekly:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            data = web.input()
            try:
                date = iso_to_date(data['date'])
                num = int(data['num'])
            except ValueError:
                return 'Naughty. Try entering a legal number, please.'

            db_session = DBSession()
            entry = db_session.query(ScheduleEntry).join(Period).\
                    filter(Period.num == num, Period.date == date).\
                    filter(ScheduleEntry.counselor_id == session.user.id).first()
            if entry:
                db_session.delete(entry)
                db_session.commit()
                web.seeother('/editweekly')
            else:
                return 'No permission to delete student, or no such date/period.'

class assignstudent:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            data = web.input()
            try:
                student_id = int(data['id'])
                date = iso_to_date(data['date'])
                num = int(data['num'])
                interview_type_id = int(data['interview_type'])
            except ValueError:
                return "Don't mess with my GET parameters!"

            db_session = DBSession()
            period = db_session.query(Period).filter_by(date = date, num = num).one()
            interview_type = db_session.query(InterviewType).filter_by(id = interview_type_id).one()
            counselor = db_session.query(Counselor).filter_by(id = session.user.id).one()
            student = db_session.query(Student).filter_by(id = student_id).one()

            # check if a counselor has already scheduled something for this date,
            # or if student is already scheduled for that date
            counselor_already_scheduled = db_session.query(ScheduleEntry).filter_by(period = period, counselor = counselor).first()
            student_already_scheduled_this_date = db_session.query(ScheduleEntry).filter_by(period = period, student = student).first()
            if counselor_already_scheduled or student_already_scheduled_this_date:
                web.seeother('/editweekly')
            else:
                sched = ScheduleEntry()
                sched.period = period
                sched.type = interview_type
                sched.counselor = counselor
                sched.student = student

                db_session.add(sched)
                db_session.commit()
                web.seeother('/editweekly')
            

class choosing:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            data = web.input()
            db_session = DBSession()
            try:
                date = iso_to_date(data['date'])
                num = int(data['num'])
            except ValueError:
                return 'stop tampering with my GET parameters!'

            period = db_session.query(Period).filter_by(date = date, num = num).one()
            counselor = db_session.query(Counselor).filter_by(id = session.user.id).one()
            handled_section_ids = db_session.query(Section.id).filter_by(counselor_id = counselor.id)
            students = db_session.query(Student).filter(Student.section_id.in_(handled_section_ids)).join(Student.section)
            interview_types = db_session.query(InterviewType)
            if 'letter' in data:
                students = students.filter(Student.last_name.like(data['letter'] + '%'))
            elif 'year' in data:
                students = students.filter(Section.year == int(data['year']))
            elif 'section' in data:
                students = students.filter(Section.year == int(data['section'][0]), Section.name == data['section'][1])

            return render.choosing(students, date.isoformat(), num, interview_types, str)

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

class createnotation:
    '''
    Generalized handler that handles the creation of both a routine interview
    and a followup interview
    '''
    routine_textbox_names = ['General Mental Ability', 'Academic History'
                             , 'Family Relationship'
                             , 'Personal/Emotional', 'Peer Relationship'
                             , 'Goals/Motivation', 'Recommendation']
    routine_form = form.Form(*[form.Textarea(name=name, rows=15,cols=75) for name in routine_textbox_names])

    followup_textbox_names = ['Comments', 'Planned Intervention']
    followup_form = lambda self, nature_of_problems: form.Form(form.Dropdown('Nature of problem', args=[(nature.id, nature.name) for nature in nature_of_problems],value=1)
                                                               ,*[form.Textarea(name=name, rows=15, cols=75) for name in self.followup_textbox_names])

    hidden_forms = lambda self, period, student, type: form.Form(*[form.Hidden(name='period_id', value=period.id)
                                                                   , form.Hidden(name='student_id', value=student.id)
                                                                   , form.Hidden(name='interview_type', value=type.id)])

    button_names = ['save as draft', 'submit']
    button_form = form.Form(*[form.Button(button_name) for button_name in button_names])

    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            data = web.input()
            try:
                num = int(data['num'])
                date = iso_to_date(data['date'])
                student_id = int(data['student'])
                type = int(data['type'])
            except ValueError:
                return 'Invalid GET Parameters!'
                
            db_session = DBSession()
            counselor = db_session.query(Counselor).filter_by(id = session.user.id).one()
            try:
                period = db_session.query(Period).filter_by(num = num, date = date).one()
                student = db_session.query(Student).filter_by(id = student_id).one()
                interview_type = db_session.query(InterviewType).filter_by(id = type).one()
            except NoResultsFound:
                return 'No such period, interview type, or student!'

            if interview_type.name == 'Followup Interview': # A followup interview
                natures_of_problem = db_session.query(NatureOfProblemType)
                main_form = self.followup_form(natures_of_problem)
            elif interview_type.name == 'Routine Interview': # routine interview
                main_form = self.routine_form
            else: # other interview, which we have no form for yet...
                main_form = None
        return render.create_notation(main_form, self.hidden_forms(period, student, interview_type), self.button_form)

    def POST(self):
        data = web.input()
        db_session = DBSession()

        period_id = int(data['period_id'])
        student_id = int(data['student_id'])
        interview_type_id = int(data['interview_type'])

        main_form = None
        interview_type = db_session.query(InterviewType).filter_by(id = interview_type_id).one()

        interview = Interview()
        interview.type = interview_type
        interview.counselor_id = session.user.id
        interview.period_id = period_id
        interview.student_id = student_id
        latest_interview_id = db_session.query(Interview.id).order_by(Interview.id).all()
        interview.id = 1 + latest_interview_id[-1] if latest_interview_id else 0
        
        if interview_type.name == 'Routine Interview':
            rform = self.routine_form
            routine = RoutineInterview()
            routine.general_mental_ability = data['General Mental Ability']
            routine.academic_history = data['Academic History']
            routine.family_relationship = data['Family Relationship']
            routine.personal_emotional = data['Personal/Emotional']
            routine.peer_relationship = data['Peer Relationship']
            routine.goals = data['Goals/Motivation']
            routine.recommendation = data['Recommendation']

            routine.id = interview.id
            db_session.add(routine)

        elif interview_type.name == 'Followup Interview':
            import pdb; pdb.set_trace()
            natures_of_problem = db_session.query(NatureOfProblemType)
            fform = self.followup_form(natures_of_problem)
            followup = FollowupInterview()
            followup.nature_of_problem_id = int(data['Nature of problem'])
            followup.comments = data['Comments']
            followup.planned_intervention = data['Planned Intervention']

            followup.id = interview.id
            db_session.add(followup)

        db_session.add(interview)
        db_session.commit()
    
class conductcounseling:
    '''
    Handler for the conduct counseling page
    '''
    def GET(self):
        if session.user is None:
            web.seeother('/')
        else:
            db_session = DBSession()
            dates_this_week = dates_of_current_week()
            periods_of_counselor = db_session.query(Period).outerjoin(Period.entries).\
                                   filter(Period.date.in_(dates_this_week)).\
                                   filter(or_(Period.entries.any(counselor_id = session.user.id), Period.entries == None)).\
                                   order_by(Period.num, Period.date)
            periods_partitioned = partition(periods_of_counselor, lambda p: p.num)

            counselor = db_session.query(Counselor).filter_by(id=session.user.id).one()
            return render.conductcounseling(counselor, periods_partitioned, period_labels)
        
if __name__ == '__main__':
    app.run()