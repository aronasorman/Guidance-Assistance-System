#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import User, Counselor, Student, Base
from hashlib import sha256
import os.path
import os

DBNAME = 'counselor.db'

DBPATH = os.getcwd()

engine = create_engine('sqlite:////' + os.path.join(DBPATH,DBNAME), echo=True)

Session = sessionmaker(bind=engine)


def test_counselor():
    session = Session()
    user = User()
    user.id = 90275
    user.name = 'Aron Fyodor M. Asor'
    user.password = sha256(user.name + 'asakapa').hexdigest()
    user.is_counselor = True
    session.add(user)

    counselor = Counselor()
    counselor.id = user.id
    counselor.nickname = 'Aron'
    counselor.address = 'somewhere'
    counselor.telno = '091xnice'
    counselor.celno = '046bogus'
    counselor.email = 'aronasorman@gmail.com'
    counselor.is_head_counselor = False
    session.add(counselor)
    session.commit()

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    test_counselor()