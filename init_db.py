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

def init_sections():
    session = Session()
    sections = [ Section(year=year,name=name) for year in range(1,5) for name in "abcdefghijklmn"]
    session.add_all(sections)
    session.commit()

def init_parent_status():
    session = Session()
    session.add_all([
        ParentStatus("Living Together")
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
    init_parent_status()
    init_single_parent()
    init_living_with()
    init_study_length()
    init_subjects()

if __name__ == '__main__':
    db_init()