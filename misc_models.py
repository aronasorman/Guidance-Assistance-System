from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

'''
Entities not specific to the application at hand, i.e.
users and privileges
'''

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    login = Column(Integer, primary_key=True)
    password = Column(String(50), nullable=False)

class UserPrivileges(Base):
    __tablename__ = 'user_privileges'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    privilege_id = Column(Integer, ForeignKey('available_privileges.id'), primary_key=True)

class Privilege(Base):
    __tablename__ = 'available_privileges'

    id = Column(Integer, primary_key=True)
    privilege_name = Column(String(20), nullable=False)
    

