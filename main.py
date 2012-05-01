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
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from utils import to_date, iso_to_date, partition

urls = (
    '/', 'login'
    , '/create-account', 'accountcreation'
    , '/main', 'mainpage'
    , '/logout', 'logout'
    , '/search', 'search'
    , '/conductcounseling', 'conductcounseling'
    , '/createnotation', 'createnotation'
    , '/assigncounselor', 'assigncounselor'
    , '/viewstudent', 'viewstudent'
    , '/studentprofile', 'studentprofile'
    , '/editweekly', 'editweekly'
    , '/deletefromweekly', 'deletefromweekly'
    , '/choosing', 'choosing'
    , '/assignstudent', 'assignstudent'
    , '/viewnotations', 'viewnotations'
    , '/viewnotation', 'viewnotation'
    , '/upload' , 'upload'
    , '/informationaboutfamily/([0-9]+)', 'informationaboutfamily'
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
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            db_session = DBSession()
            counselors = db_session.query(Counselor).order_by(Counselor.id).all()
            sections = db_session.query(Section).filter_by(counselor_id=None).order_by(Section.id).all()
            return render.assigncounselor(session.user, counselors, sections, str)

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
        return render.message(session.user, 'Section assignments updated!')

class editweekly:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            dates_this_week = dates_of_current_week()
            periods_of_counselor = DBSession().query(Period).outerjoin(Period.entries).\
                                   filter(Period.date.in_(dates_this_week)).\
                                   filter(or_(Period.entries.any(counselor_id = session.user.id), Period.entries == None)).\
                                   order_by(Period.num, Period.date)
            periods_partitioned = partition(periods_of_counselor, lambda p: p.num)
            return render.editweekly(session.user, periods_partitioned, period_labels)

class deletefromweekly:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            data = web.input()
            try:
                date = iso_to_date(data['date'])
                num = int(data['num'])
            except ValueError:
                return render.message(session.user, 'Naughty. Try entering a legal number, please.')

            db_session = DBSession()
            entry = db_session.query(ScheduleEntry).join(Period).\
                    filter(Period.num == num, Period.date == date).\
                    filter(ScheduleEntry.counselor_id == session.user.id).first()
            if entry:
                db_session.delete(entry)
                db_session.commit()
                web.seeother('/editweekly')
            else:
                return render.message(session.user, 'No permission to delete student, or no such date/period.')

class assignstudent:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            data = web.input()
            try:
                student_id = int(data['id'])
                date = iso_to_date(data['date'])
                num = int(data['num'])
                interview_type_id = int(data['interview_type'])
            except ValueError:
                return render.message(session.user, 'Don\'t mess with my GET parameters!')

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
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            data = web.input()
            db_session = DBSession()
            try:
                date = iso_to_date(data['date'])
                num = int(data['num'])
            except ValueError:
                return render.message(session.user, 'stop tampering with my GET parameters!')

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

            students = students.order_by(Student.section_id, Student.last_name)
            return render.choosing(session.user, students, date.isoformat(), num, interview_types, str)

class viewstudent:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
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
            students = students.order_by(Student.section_id, Student.last_name)
            return render.viewstudent(session.user,students.all(), str)

class studentprofile:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            data = web.input()
            id = int(data['id'])
            db_session = DBSession()
            student = db_session.query(Student).filter_by(id = id).one()
            interview_types = db_session.query(InterviewType)
            return render.studentprofile(session.user, student, interview_types)

class informationaboutfamily:
    def GET(self, student_id):
        if session.user == None:
            web.seeother('/')
        else:
            student_id = int(student_id)
            db_session = DBSession()
            student = db_session.query(Student).filter(Student.id == student_id).one()
            return render.informationaboutfamily(session.user, student)

class login:
    '''
    Class that handles logging in.
    '''
    
    def GET(self):
        if session.user:
            web.seeother('/main')
        else:
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
            user = db_session.query(User).options(joinedload(User.position)).filter(User.id==name).filter(User.password==password_hash).first()
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
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            user = session.user
            db_session = DBSession()
            counselor = db_session.query(Counselor).filter(Counselor.id==user.id).first()
            dates_this_week = dates_of_current_week()
            periods_of_counselor = DBSession().query(Period).outerjoin(Period.entries).\
                                   filter(Period.date.in_(dates_this_week)).\
                                   filter(or_(Period.entries.any(counselor_id = session.user.id), Period.entries == None)).\
                                   order_by(Period.num, Period.date)
            periods_partitioned = partition(periods_of_counselor, lambda p: p.num)
            return render.mainpage(user, periods_partitioned, period_labels)
        elif session.user.position.title in ['Secretary']:
            raise web.seeother('/upload')

class upload:
    def GET(self):
        if session.user is None:
            web.seeother('/') # they haven't logged in yet
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            raise web.seeother('/')
        elif session.user.position.title in ['Secretary']:
            return render.upload_file()

    def POST(self):
        data = web.input()
        try:
            file = data['file']
        except KeyError:
            return render.message(session.user,'Something is missing!')
        return render.message(session.user,'File uploaded!')

class accountcreation:
    '''
    Handler for account creation
    '''
    def GET(self):
        db_session = DBSession()
        positions = db_session.query(Position)
        return render.createaccount(positions)

    def POST(self):
        
        db_session = DBSession()
        data = web.input()
        user = User()
        user.id = int(data['ID Number'])
        name = ' '.join([data['firstname'], data['middleinitial'], data['lastname']])
        position_id = int(data['position'])
        user.name = name
        user.password = sha256(str(user.id) + data['Password']).hexdigest()
        user.position = db_session.query(Position).filter_by(id = position_id).one()
        db_session.add(user)
        db_session.commit()

        if user.position in ['Counselor', 'Head Counselor']:
            db_session = DBSession()
            counselor = Counselor()
            counselor.id = user.id
            counselor.nickname = data['Nickname']
            counselor.address = data['City Address']
            counselor.telno = data['telephone']
            counselor.celno = data['cellphone']
            counselor.email = data['email']
            db_session.add(counselor)
            db_session.commit()

        return render.message(user, ' '.join(['user', name, 'created!']))

class createnotation:
    '''
    Generalized handler that handles the creation of both a routine interview
    and a followup interview
    '''
    routine_textbox_names = ['General Mental Ability', 'Academic History'
                             , 'Family Relationship'
                             , 'Personal/Emotional', 'Peer Relationship'
                             , 'Goals/Motivation', 'Recommendation']
    routine_form = form.Form(*[form.Textarea(name,form.notnull, rows=15,cols=75) for name in routine_textbox_names])

    followup_textbox_names = ['Comments', 'Planned Intervention']
    followup_form = lambda self, nature_of_problems: form.Form(form.Dropdown('Nature of problem', args=[(nature.id, nature.name) for nature in nature_of_problems],value=1)
                                                               ,*[form.Textarea(name,form.notnull, rows=15, cols=75) for name in self.followup_textbox_names])

    other_textbox_names = ['Content']
    other_form = form.Form(*[form.Textarea(name=name, rows=15,cols=75) for name in other_textbox_names])

    hidden_forms = lambda self, period, student, type: form.Form(*[form.Hidden(name='period_id', value=period.id)
                                                                   , form.Hidden(name='student_id', value=student.id)
                                                                   , form.Hidden(name='interview_type', value=type.id)])

    button_names = ['save as draft', 'submit']
    button_form = form.Form(*[form.Button(button_name,form.notnull) for button_name in button_names])

    def GET(self):
        if session.user is None:
            web.seeother('/')
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            data = web.input()
            try:
                num = int(data['num'])
                date = iso_to_date(data['date'])
                student_id = int(data['student'])
                type = int(data['type'])
            except ValueError:
                return render.message(session.user, 'Invalid GET Parameters!')
                
            db_session = DBSession()
            counselor = db_session.query(Counselor).filter_by(id = session.user.id).one()
            try:
                period = db_session.query(Period).filter_by(num = num, date = date).one()
                student = db_session.query(Student).filter_by(id = student_id).one()
                interview_type = db_session.query(InterviewType).filter_by(id = type).one()
            except NoResultsFound:
                return render.message(session.user, 'No such period, interview type, or student!')

            if interview_type.name == 'Followup Interview': # A followup interview
                natures_of_problem = db_session.query(NatureOfProblemType)
                main_form = self.followup_form(natures_of_problem)
            elif interview_type.name == 'Routine Interview': # routine interview
                main_form = self.routine_form
            else: # other interview, which we have no form for yet...
                main_form = self.other_form
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
        latest_interview_id = db_session.query(Interview).order_by(Interview.id).all()
        interview.id = 1 + latest_interview_id[-1].id if latest_interview_id else 0

        date = iso_to_date(data['date'])
        student_id = int(data['student'])
        student = db_session.query(Student).filter_by(id = student_id).one()
        
        if interview_type.name == 'Routine Interview':
            rform = self.routine_form
            num = int(data['num'])
            period = db_session.query(Period).filter(Period.num == num, Period.date == date).one()
            if not rform.validates():
                return render.create_notation(rform,self.hidden_forms(period, student, interview_type), self.button_form)
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
            natures_of_problem = db_session.query(NatureOfProblemType)
            fform = self.followup_form(natures_of_problem)
            num = int(data['num'])
            period = db_session.query(Period).filter_by(num = num, date = date).one()
            if not fform.validates():
                return render.create_notation(fform,self.hidden_forms(period, student, interview_type), self.button_form)
            followup = FollowupInterview()
            followup.nature_of_problem_id = int(data['Nature of problem'])
            followup.comments = data['Comments']
            followup.planned_intervention = data['Planned Intervention']

            followup.id = interview.id
            db_session.add(followup)
        elif interview_type.name == 'Other':
            other = OtherInterview()
            other.content = data['Content']
            period = db_session.query(Period).filter_by(num = num, date = date).one()
            num = int(data['num'])

            other.id = interview.id
            db_session.add(other)

        db_session.add(interview)
        db_session.commit()

        return render.message(session.user, 'Interview conducted!')

class viewnotations:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            db_session = DBSession()
            data = web.input()
            try:
                student_id = int(data['student'])
                type_id = int(data['type'])
                student = db_session.query(Student).filter(Student.id == student_id).one()
                interview_type = db_session.query(InterviewType).filter_by(id = type_id).one()
            except ValueError:
                return render.message(session.user, 'Invalid GET parameters!')
            except MultipleResultsFound:
                return render.message(session.user, 'No such student or interview type!')

            counselor = db_session.query(Counselor).filter_by(id = session.user.id).one()
            interviews = db_session.query(Interview).\
                         filter(Interview.student_id == student.id, Interview.type_id == interview_type.id)
            return render.counselor_notations(session.user, counselor,student,interviews,interview_type)
    
class conductcounseling:
    '''
    Handler for the conduct counseling page
    '''
    def GET(self):
        if session.user is None:
            web.seeother('/')
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            db_session = DBSession()
            dates_this_week = dates_of_current_week()
            periods_of_counselor = db_session.query(Period).outerjoin(Period.entries).\
                                   filter(Period.date.in_(dates_this_week)).\
                                   filter(or_(Period.entries.any(counselor_id = session.user.id), Period.entries == None)).\
                                   order_by(Period.num, Period.date)
            periods_partitioned = partition(periods_of_counselor, lambda p: p.num)

            counselor = db_session.query(Counselor).filter_by(id=session.user.id).one()
            return render.conductcounseling(session.user, counselor, periods_partitioned, period_labels)

class viewnotation:
    def GET(self):
        if session.user is None:
            web.seeother('/')
        elif session.user.position.title in ['Counselor', 'Head Counselor']:
            data = web.input()
            db_session = DBSession()
            try:
                interview_id = int(data['id'])
            except ValueError:
                return render.message(session.user, 'Invalid GET parameter!')
                
            interview = db_session.query(Interview).filter(Interview.id == interview_id).one()
            interview_type = interview.type
            student = interview.student
            if student.section.counselor_id == session.user.id:
                if interview_type.name == 'Followup Interview':
                    interview, auxiliary = db_session.query(Interview, FollowupInterview).\
                                          join(FollowupInterview, Interview.id == FollowupInterview.id).\
                                          join(NatureOfProblemType, FollowupInterview.nature_of_problem_id == NatureOfProblemType.id).\
                                          filter(Interview.id == interview_id).\
                                          one()
                elif interview_type.name =='Routine Interview':
                    interview, auxiliary = db_session.query(Interview, RoutineInterview).\
                                         join(RoutineInterview, Interview.id == RoutineInterview.id).\
                                         filter(Interview.id == interview_id).\
                                         one()
                elif interview_type.name == 'Other':
                    interview, auxiliary = db_session.query(Interview, OtherInterview).\
                                         join(OtherInterview, Interview.id == OtherInterview.id).\
                                         filter(Interview.id == interview_id).\
                                         one()
                return render.viewnotation(session.user, interview,auxiliary,str)
            else:
                return render.message(session.user, 'No permission to see student!')

class search:
    '''
    Search for a student
    '''
    def GET(self):
        data = web.input()
        query = data['query']
        db_session = DBSession()
        complete_query = '%' + query + '%'
        counselor = db_session.query(Counselor).filter_by(id = session.user.id).one()
        handled_section_ids = db_session.query(Section.id).filter_by(counselor_id = counselor.id)
        students = db_session.query(Student).filter(Student.section_id.in_(handled_section_ids)).join(Student.section)
        students = students.filter(Student.last_name.like(complete_query))
        return render.viewstudent(session.user, students, str)
       
if __name__ == '__main__':
    app.run()