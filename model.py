from sqlalchemy import Column, Integer, String, Text, Date, LargeBinary, create_engine, Float, Boolean, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

Base = declarative_base()


class Counselor(Base):
    __tablename__ = "counselors"

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    picture = Column(LargeBinary)
    nickname = Column(String(20))
    address = Column(Text, nullable=False)
    telno = Column(String(20))
    celno = Column(String(20))
    email = Column(String(40))
    birthdate = Column(Date, nullable=False)
    position_id = Column(Integer, ForeignKey('Position.id')) # add position field
    religion = Column(String(20))
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    overall_health = Column(String(1))
    eyesight = Column(String(1), nullable=False)
    hearing = Column(String(1), nullable=False)
    lungs = Column(String(1), nullable=False)
    handicaps = Column(Text)

    sections = relationship('Section', order_by='Section.name', backref='user')

class Position(Base):
    __tablename__ = 'position'

    id = Column(Integer, primary_key=True)
    position_name = Column(String(15), nullable=False)

class Section(Base):
    __tablename__ = 'sections'

    section_id = Column(String(2), primary_key=True)
    year = Column(Integer)
    name = Column(String(1))
    counselor_id = Column(Integer, ForeignKey('Counselor.id'))

    counselor = relationship('Counselor', backref=backref('sections'))

# association for student class to favorite subjects
student_favorite_subjects = Table('student_favorite_subjects', Base.metadata
                                  , Column('student_id', Integer, ForeignKey('Student.id'))
                                  , Column('subject_id', Integer, ForeignKey('Subject.id'))                                  )

student_dire_subjects = Table('student_dire_subjects', Base.metadata
                              , Column('student_id', Integer, ForeignKey('Student.id'))
                              , Column('subject_id', Integer, ForeignKey('Subject.id')))

student_tutored_subjects = Table('student_tutored_subjects', Base.metadata
                              , Column('student_id', Integer, ForeignKey('Student.id'))
                              , Column('subject_id', Integer, ForeignKey('Subject.id')))

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    picture = Column(LargeBinary)
    name = Column(String(40), nullable=False)
    year = Column(Integer, ForeignKey('Section.year'))
    section_name = Column(String(1), ForeignKey('Section.name'))
    nickname = Column(String(20))
    address = Column(Text, nullable=False)
    telno = Column(String(20))
    celno = Column(String(20))
    email = Column(String(40))
    birthdate = Column(Date, nullable=False)
    birthplace = Column(Text, nullable=False)
    overall_health = Column(String(1))
    eyesight = Column(String(1), nullable=False)
    hearing = Column(String(1), nullable=False)
    lungs = Column(String(1), nullable=False)
    handicaps = Column(Text)
    parent_status_id = Column(Integer, ForeignKey('ParentStatus.id'), nullable=False)
    single_parent_id = Column(Integer, ForeignKey('SingleParent.id'))
    sibling_comments = Column(Text)
    family_concerns = Column(Text)
    most_significant_person = Column(String(40))
    why_significant = Column(Text)
    favorite_subjects = relationship('Subject', secondary=student_favorite_subjects, backref='students')
    dire_subjects = relationship('Subject', secondary=student_dire_subjects, backref='students')
    tutored_subjects = relationship('Subject', secondary=student_tutored_subjects, backref='students')
    study_length_id = Column(Integer, ForeignKey('StudyLength.id'))
    study_partners = relationship('StudyPartners', backref='student')
    is_special_guidance_needed = Column(Boolean, nullable=False)
    special_guidance_elaboration = Column(Text)
    # ask if clubs or organizations is fixed
    work_experience = Column(Text)
    interests = Column(Text)
    
class StudyPartner(Base):
    __tablename__ = 'student_study_partners'

    id = Column(Integer, primary_key=True)
    name = Column(Integer(40), nullable=False)
    student_id = Column(Integer, ForeignKey('Student.id'))
    student = relationship('Student', backref=backref('study_partners'))
    
class ParentStatus(Base):
    __tablename__ = 'parent_status_lookup'

    id = Column(Integer, primary_key=True)
    status = Column(String(25), nullable=False)

class SingleParent(Base):
    __tablename__ = 'single_parent_lookup'

    id = Column(Integer, primary_key=True)
    status = Column(String(6), nullable=False)

class LivingWith(Base):
    __tablename__ = 'living_with_lookup'

    id = Column(Integer, primary_key=True)
    status = Column(String(12), nullable=False)

class StudyLength(Base):
    __tablename__ = 'study_length_lookup'

    id = Column(Integer, primary_key=True)
    length = Column(String(20), nullable=False)

class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)