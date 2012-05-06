#!/usr/bin/env python

'''
fills the database with initial values, mostly for the lookup tables.
'''

from model import *
from config import *

def init_dummy_user():
    session = Session()
    session.add(User(password='iamdummy'))
    session.commit()

def init_guardian_types():
    session = Session()
    session.add_all([
        GuardianType(type='Mother')
        , GuardianType(type='Father')
        , GuardianType(type='Guardian')
        ])

def init_sections():
    session = Session()
    sections = [ Section(year=year,name=name) for year in range(1,5) for name in "abcdefghijklmno".upper()]
    session.add_all(sections)
    session.commit()

def init_position():
    session = Session()
    session.add_all([
        Position(title='Counselor')
        , Position(title='Head Counselor')
        , Position(title='Secretary')
        , Position(title='Administrator')
        ])
    session.commit()

def init_allowed_pages():
    session = Session()
    counselor = session.query(Position).filter_by(title='Counselor').one()
    head_counselor = session.query(Position).filter_by(title='Head Counselor').one()
    secretary = session.query(Position).filter_by(title='Secretary').one()
    session.add_all([
        AllowedPages(position=counselor, allowed_url='/changepass', url_title='Change Password')
        , AllowedPages(position=counselor, allowed_url='/viewaccount', url_title='View own account')
        , AllowedPages(position=counselor, allowed_url='/editweekly', url_title='Edit Weekly Plan')
        , AllowedPages(position=counselor, allowed_url='/viewstudent', url_title='View Student Profile')
        , AllowedPages(position=counselor, allowed_url='/conductcounseling', url_title='Conduct Counseling')
        ])
    session.add_all([
        AllowedPages(position=head_counselor, allowed_url='/changepass', url_title='Change Password')
        , AllowedPages(position=head_counselor, allowed_url='/viewcounselor', url_title='View Counselor Accounts')
        , AllowedPages(position=head_counselor, allowed_url='/editweekly', url_title='Edit Weekly Plan')
        , AllowedPages(position=head_counselor, allowed_url='/conductcounseling', url_title='Conduct Counseling')
        , AllowedPages(position=head_counselor, allowed_url='/viewstudent', url_title='View Student Profile')
        , AllowedPages(position=head_counselor, allowed_url='/assigncounselor', url_title='Assign counselors')
        ])
    session.add_all([
        AllowedPages(position=secretary, allowed_url='/changepass', url_title='Change Password')
        , AllowedPages(position=secretary, allowed_url='/uploadtesting', url_title='Upload Testing data')
        , AllowedPages(position=secretary, allowed_url='/uploadregistrar', url_title='Upload Registrar data')
        ])
    session.commit()

def init_nature_of_problem_types():
    session = Session()
    session.add_all([NatureOfProblemType(name='Family')
                 , NatureOfProblemType(name='Friends')
                 , NatureOfProblemType(name='Academics')
                 , NatureOfProblemType(name='Others')])
    session.commit()

def init_interview_types():
    session = Session()
    session.add_all([
        InterviewType(name='Followup Interview')
        , InterviewType(name='Routine Interview')
        , InterviewType(name='Other')
        ])
    session.commit()

def init_parent_status():
    session = Session()
    session.add_all([
        ParentStatus("Together")
        , ParentStatus('Separated')
        , ParentStatus('Remarried')
        , ParentStatus('Deceased - Mother')
        , ParentStatus('Deceased - Father')
        , ParentStatus('Deceased - Both')
        ])
    session.commit()

def init_single_parent():
    session = Session()
    session.add_all([
        SingleParent('Mother')
        , SingleParent('Father')
        , SingleParent('None')
        ])
    session.commit()

def init_living_with():
    session = Session()
    session.add_all([
        LivingWith('Both Parents')
        , LivingWith('Mother')
        , LivingWith('Father')
        , LivingWith('Guardian')
        ])
    session.commit()

def init_study_length():
    session = Session()
    session.add_all([
        StudyLength('less than 1 hour')
        , StudyLength('1-3 hours')
        , StudyLength('4-5 hours')
        , StudyLength('more than 5 hours')
        ])
    session.commit()

def init_subjects():
    session = Session()
    session.add_all([
        Subject('Filipino')
        , Subject('English')
        , Subject('Science')
        , Subject('Social Science')
        , Subject('Theology')
        , Subject('Chemistry')
        , Subject('Biology')
        , Subject('Physics')
        , Subject('Algebra')
        , Subject('History')
        , Subject('Computer Science')
        , Subject('Home Economics')
        , Subject('Physical Education')
        , Subject('Philosophy')
        , Subject('Geometry')
        , Subject('Calculus')
        , Subject('Journalism')
        ])
    session.commit()

def db_init():
    Base.metadata.create_all(engine)
    init_sections()
    init_position()
    init_allowed_pages()
    init_guardian_types()
    init_interview_types()
    init_nature_of_problem_types()
    init_parent_status()
    init_single_parent()
    init_living_with()
    init_study_length()
    init_subjects()

if __name__ == '__main__':
    db_init()