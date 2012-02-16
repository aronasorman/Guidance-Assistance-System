#!bin/python

'''
Module that creates periods in the database.

Run this at least once every week, ideally at the start of the week, around Sunday?
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Period, Base
from datetime import date, time, datetime, timedelta
import os.path
import os

DBNAME = 'counselor.db'

DBPATH = os.getcwd()

engine = create_engine('sqlite:////' + os.path.join(DBPATH,DBNAME), echo=True)

Session = sessionmaker(bind=engine)

PERIOD_LENGTH = 15 # minutes

START_TIME_HOUR = 7
START_TIME_MINUTE = 30

END_TIME_HOUR = 17 # military time, bitches!
END_TIME_MINUTE = 30

def dates_of_current_week():
    today = date.today()
    day_of_week = today.weekday()
    dates = [today - timedelta(day_of_week - x) for x in range(7)]
    return dates

def generate_timeslots():
    timeslots = []
    today = date.today() # dummy date data used for turning time to datetime
    start_timeslot = datetime.combine(today, time(START_TIME_HOUR, START_TIME_MINUTE)) # we coerce to datetime so that we can use timedelta arithmetic
    end_timeslot = datetime.combine(today, time(END_TIME_HOUR, END_TIME_MINUTE))
    current_timeslot = start_timeslot
    while current_timeslot <= end_timeslot:
        timeslots.append(current_timeslot.time()) # we bring back the datetime to time here
        current_timeslot = current_timeslot + timedelta(minutes=PERIOD_LENGTH)
    return timeslots

def generate_periods():
    return [datetime.combine(date,time) for date in dates_of_current_week() for time in generate_timeslots()]

def create_periods():
    periods = generate_periods()
    period_entities = [Period(datetime=period) for period in periods]
    session = Session()
    session.add_all(period_entities)
    session.commit()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    create_periods()