from sqlalchemy import Column, Integer, String, Text, Date, LargeBinary, create_engine, Float, Boolean, Table, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    password = Column(String(64), nullable=False)
    position_id = Column(Integer, ForeignKey('positions.id'), nullable=False)

    position = relationship('Position')

class Counselor(Base):
    __tablename__ = "counselors"

    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    picture = Column(LargeBinary)
    nickname = Column(String(20))
    address = Column(Text, nullable=False)
    telno = Column(String(20))
    celno = Column(String(20))
    email = Column(String(40))
    user = relationship('User')
    
class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    title = Column(String(15), nullable=False)

class Section(Base):
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    name = Column(String(1))
    counselor_id = Column(Integer, ForeignKey('counselors.id'))

    counselor = relationship('Counselor', backref=backref('sections'))

class Period(Base):
    __tablename__ = 'periods'

    id = Column(Integer, primary_key=True)
    num = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)

class ScheduleEntry(Base):
    __tablename__ = 'schedule_entries'

    period_id = Column(Integer, ForeignKey('periods.id'), primary_key=True) # So we're supposed to generate new periods every week...
    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    counselor_id = Column(Integer, ForeignKey('counselors.id'))
    type_id = Column(Integer, ForeignKey('interview_types.id'))

    type = relationship('InterviewType')
    period = relationship('Period', backref=backref('entries'))
    counselor = relationship('Counselor', backref=backref('schedule_entries'))
    student = relationship('Student', backref=backref('schedule_entries'))

class InterviewType(Base):
    __tablename__ = 'interview_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)

class Interview(Base):
    __tablename__ = 'interviews'

    id = Column(Integer, primary_key=True)
    period_id = Column(Integer, ForeignKey('periods.id'))
    student_id = Column(Integer, ForeignKey('students.id'))
    counselor_id = Column(Integer, ForeignKey('counselors.id'))
    type_id = Column(Integer, ForeignKey('interview_types.id'))

    type = relationship('InterviewType')
    period = relationship('Period', backref=backref('interviews'))
    counselor = relationship('Counselor', backref=backref('interviews'))
    student = relationship('Student', backref=backref('interviews'))

class FollowupInterview(Base):
    __tablename__ = 'followup_interviews'

    id = Column(Integer, ForeignKey('interviews.id'), primary_key=True)
    nature_of_problem_id = Column(Integer, ForeignKey('nature_of_problem_types.id'))
    comments = Column(Text)
    planned_intervention = Column(Text)

    interview = relationship('Interview')
    nature_of_problem = relationship('NatureOfProblemType')

class OtherInterview(Base):
    __tablename__ = 'other_interviews'

    id = Column(Integer, ForeignKey('interviews.id'), primary_key=True)
    content = Column(Text)

class NatureOfProblemType(Base):
    __tablename__ = 'nature_of_problem_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)

class RoutineInterview(Base):
    __tablename__ = 'routine_interviews'

    id = Column(Integer, ForeignKey('interviews.id'), primary_key=True)
    general_mental_ability = Column(Text)
    academic_history = Column(Text)
    family_relationship = Column(Text)
    personal_emotional = Column(Text)
    peer_relationship = Column(Text)
    goals = Column(Text)
    recommendation = Column(Text)

    interview = relationship('Interview')

# association for student class to favorite subjects
student_favorite_subjects = Table('favorite_subjects', Base.metadata
                                  , Column('student_id', Integer, ForeignKey('students.id'))
                                  , Column('subject_id', Integer, ForeignKey('subjects.id'))                                  )

student_dire_subjects = Table('dire_subjects', Base.metadata
                              , Column('student_id', Integer, ForeignKey('students.id'))
                              , Column('subject_id', Integer, ForeignKey('subjects.id')))

student_tutored_subjects = Table('tutored_subjects', Base.metadata
                              , Column('student_id', Integer, ForeignKey('students.id'))
                              , Column('subject_id', Integer, ForeignKey('subjects.id')))

grade_school_alumni = Table('grade_school_alumni', Base.metadata
                              , Column('student_id', Integer, ForeignKey('students.id'))
                              , Column('grade_school_id', Integer, ForeignKey('grade_schools.id')))

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    picture = Column(LargeBinary)
    first_name = Column(String(40), nullable=False)
    last_name = Column(String(40), nullable=False)
    middle_name = Column(String(40), nullable=False)
    section_id = Column(Integer, ForeignKey('sections.id'))
    section = relationship('Section', backref=backref('students'))
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
    parent_status_id = Column(Integer, ForeignKey('parent_status_lookup.id'), nullable=False)
    parent_status = relationship('ParentStatus')
    single_parent_id = Column(Integer, ForeignKey('single_parent_lookup.id'))
    living_with_id = Column(Integer, ForeignKey('living_with_lookup.id'))
    sibling_comments = Column(Text)
    family_concerns = Column(Text)
    most_significant_person = Column(String(40))
    why_significant = Column(Text)
    favorite_subjects = relationship('Subject', secondary=student_favorite_subjects, backref='students_who_like_this_subject')
    dire_subjects = relationship('Subject', secondary=student_dire_subjects, backref='students_who_hate_this_subject')
    tutored_subjects = relationship('Subject', secondary=student_tutored_subjects, backref='students_who_are_being_tutored_in_this_subject')
    study_length_id = Column(Integer, ForeignKey('study_length_lookup.id'))
    is_special_guidance_needed = Column(Boolean, nullable=False)
    special_guidance_elaboration = Column(Text)
    # ask if clubs or organizations is fixed
    work_experience = Column(Text)
    interests = Column(Text)
    grade_schools = relationship('GradeSchool', secondary=grade_school_alumni,backref='students')
    siblings = relationship('Sibling', backref='student')

class Sibling(Base):
    __tablename__ = 'siblings'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    age = Column(Integer)
    school_or_work = Column(String(50))
    student_id = Column(Integer, ForeignKey('students.id'))

class Guardian(Base):
    __tablename__ = 'guardians'

    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)
    age = Column(Integer)
    occupation = Column(String(50))
    work_address = Column(String(70))
    telno = Column(String(20))
    celno = Column(String(20))
    email = Column(String(40))
    religion = Column(String(50))
    student_id = Column(Integer, ForeignKey('students.id'))

class GradeSchool(Base):
    __tablename__ = 'grade_schools'

    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    
class StudyPartner(Base):
    __tablename__ = 'student_study_partners'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    student_id = Column(Integer, ForeignKey('students.id'))
    student = relationship('Student', backref=backref('study_partners', order_by=id))
    
class ParentStatus(Base):
    __tablename__ = 'parent_status_lookup'

    id = Column(Integer, primary_key=True)
    status = Column(String(25), nullable=False)

    def __init__(self, status):
        self.status = status

class SingleParent(Base):
    __tablename__ = 'single_parent_lookup'

    id = Column(Integer, primary_key=True)
    status = Column(String(6), nullable=False)

    def __init__(self, status):
        self.status = status
        
class LivingWith(Base):
    __tablename__ = 'living_with_lookup'

    id = Column(Integer, primary_key=True)
    status = Column(String(12), nullable=False)

    def __init__(self, status):
        self.status = status
        
class StudyLength(Base):
    __tablename__ = 'study_length_lookup'

    id = Column(Integer, primary_key=True)
    length = Column(String(20), nullable=False)

    def __init__(self, length):
        self.length = length
        
class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)

    def __init__(self, name):
        self.name = name
