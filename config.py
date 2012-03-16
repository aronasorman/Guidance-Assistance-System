from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

DBNAME = 'counselor.db'

engine = create_engine('sqlite:///' + DBNAME, echo=True)
Session = sessionmaker(bind=engine)

logging.basicConfig(filename='sql_queries.log')
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

NUM_OF_PERIODS=9

COUNSELOR_NUM_WORK_DAYS=5

period_labels = ['1st period', '2nd period', '3rd period', '4th period',
                 '5th period (1)', '5th period (2)', '6th period', '7th period', '8th period']

period_span = 3000 # days

