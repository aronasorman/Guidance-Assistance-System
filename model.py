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
    address = Column(String, nullable=False)
    telno = Column(String(20))
    celno = Column(String(20))
    email = Column(String(40))
    birthdate = Column(Date, nullable=False)
    position = Column(String(15), default='Counselor')
    religion = Colum(String(20), nullable=False)
    height = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    overall_health = Column(String(1))
    eyesight = Column(String(1), nullable=False)
    hearing = Column(String(1), nullable=False)
    lungs = Column(String(1), nullable=False)
    handicaps = Column(Text)

    sections = relationship('Section', order_by='Section.name', backref='user')

class Section(Base):
    __tablename__ = 'section_assignments'

    year = Column(Integer, primary_key=True)
    name = Column(String(1), primary_key=True)
    counselor_id = Column(Integer, ForeignKey('Counselor.id'))

    counselor = relationship('Counselor', backref=backref('sections'))