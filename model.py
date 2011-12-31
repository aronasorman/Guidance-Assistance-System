from sqlalchemy import Column, Integer, String, Text, Date, LargeBinary, create_engine, Float
from sqlalchemy.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

Base = declarative_base()

engine = create_engine('sqlite://test.db', echo=True)

session = sessionmaker(bind=engine)

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
    position = Column(String(15), default='Counselor')
    religion = Colum(String(20))
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    overall_health = Column(String(1))
    eyesight = Column(String(1), nullable=False)
    hearing = Column(String(1), nullable=False)
    lungs = Column(String(1), nullable=False)
    handicaps = Column(Text)

    sections = relationship('Section', order_by='Section.name', backref='user')

class Section(Base):
    __tablename__ = 'sections'

    year = Column(Integer, primary_key=True)
    name = Column(String(1), primary_key=True)
    counselor_id = Column(Integer, ForeignKey('Counselor.id'))

    counselor = relationship('Counselor', backref=backref('sections'))

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
    parent_status = Column(Integer, ForeignKey('ParentStatus.id'))

class ParentStatus(Base):
    __tablename__ = 'parent_status'

    id = Column(Integer, primary_key=True)
    status = Column(String(25), nullable=False)