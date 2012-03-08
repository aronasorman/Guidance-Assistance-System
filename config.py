from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DBNAME = 'counselor.db'

engine = create_engine('sqlite:///' + DBNAME, echo=True)
Session = sessionmaker(bind=engine)

NUM_OF_PERIODS=9
