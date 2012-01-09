#!/usr/bin/env python

'''
fills the database with initial values, mostly for the lookup tables.
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import ParentStatus, SingleParent, LivingWith, StudyLength

engine = create_engine('sqlite:///test.db', echo=True)

session = sessionmaker(bind=engine)
