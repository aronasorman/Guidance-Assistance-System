from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

DBNAME = 'counselor.db'

engine = create_engine('sqlite:///' + DBNAME, echo=True)
Session = sessionmaker(bind=engine)

logging.basicConfig(filename='sql_queries.log')
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

NUM_OF_PERIODS=18

COUNSELOR_NUM_WORK_DAYS=5

period_labels = ['1st period - Student 1', '        Student 2',
                 '2nd period - Student 1', '        Student 2',
                 '3rd period - Student 1', '        Student 2',
                 '4th period - Student 1', '        Student 2',
                 '5th period (1) - Student 1', '        Student 2',
                 '5th period (2) - Student 1', '        Student 2',
                 '6th period - Student 1', '                      Student 2',
                 '7th period - Student 1', '                      Student 2',
                 '8th period - Student 1', '                      Student 2']

period_span = 1000 # days

