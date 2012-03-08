#!bin/python

'''
Module that creates periods in the database.

Run this at least once every week, ideally at the start of the week, around Sunday?
'''

from model import *
from datetime import date, time, datetime, timedelta
from config import *

def dates_of_current_week():
    today = date.today()
    day_of_week = today.weekday()
    dates = [today - timedelta(day_of_week - x) for x in range(COUNSELOR_NUM_WORK_DAYS)]
    return dates

def generate_periods():
    return [Period(num=num,date=date) for date in dates_of_current_week() for num in range(NUM_OF_PERIODS)]

def create_periods():
    periods = generate_periods()
    period_entities = generate_periods()
    session = Session()
    session.add_all(period_entities)
    session.commit()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    create_periods()