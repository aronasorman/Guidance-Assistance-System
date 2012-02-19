#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from model import User, Counselor, Student, Base, ParentStatus, ScheduleEntry, Section, Period
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
    user.password = sha256(str(user.id) + 'asakapa').hexdigest()
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

def scheduled_student():
    # note: we input the attribute values in the class constructor due to a bug in
    # sqlalchemy missing the attribute values
    session = Session()
    student = Student(
        id=91635
    , section=session.query(Section).filter(Section.year==1).filter(Section.name=='b').first()
    , name='April Ann E. Canlas'
    , nickname='The Chosen One'
    , address='Binondo,  Manila'
    , telno='xxx'
    , celno='xxxx'
    , parent_status=session.query(ParentStatus).filter(ParentStatus.status=='Separated').one()
    , email='aprilcanlas@ateneoinnovation.org'
    , birthdate=date(1992,  4,  15)
    , birthplace='China'
    , overall_health='E'
    , eyesight='E'
    , hearing='E'
    , lungs='E'
    , handicaps='cars'

    , is_special_guidance_needed=False)

    sched = ScheduleEntry(
    period=session.query(Period).first()
    , counselor=session.query(Counselor).filter(Counselor.id==90275).first()
    , student=student
        )

    session.add(student)
    session.add(sched)
    session.commit()
    

if __name__ == '__main__':
    Base.metadata.create_all(engine)
