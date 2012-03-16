#!bin/python

from csv import DictReader
from datetime import date
import sys

from model import *
from config import *

def unicode_dict_reader(unicode_csv_data, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = DictReader(unicode_csv_data, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield {row_name : unicode(cell, 'utf-8', 'ignore') for row_name, cell in row.iteritems()}

def parse_date(datestr):
    date_split = datestr.split('/') 
    month, day, year = [int(x) for x in date_split]
    year += 1900 if year > 50 else 2000 # we assume that all people born by this time are born within the previous or current century
    return date(year, month, day)

def import_csv(fname):
    reader = unicode_dict_reader(open(fname, 'rU'))
    db_session = Session()
    for fields in reader:
        grade_school = db_session.query(GradeSchool).filter_by(name = fields['GS NAME']).first()
        if grade_school is None:
            gs = GradeSchool(name=fields['GS NAME'])
            db_session.add(gs)
            db_session.commit()
            grade_school = db_session.query(GradeSchool).filter_by(name = fields['GS NAME']).first()
        parent_status = db_session.query(ParentStatus).filter_by(status = fields['PARENTS ARE']).one()
        living_with_id = db_session.query(LivingWith).filter_by(status = fields['STUD_LIVI_WITH']).one().id
        
        s = Student()
        s.id = int(fields['STUDNO'].replace('-',''))
        s.first_name = fields['FNAME']
        s.last_name = fields['LNAME']
        s.middle_name = fields['MNAME']
        class_no = fields['CLNO']
        year_int = int(class_no[0])
        section_raw = class_no[1]
        s.section = db_session.query(Section).filter_by(year = year_int, name = section_raw).one()
        date_raw = fields['DATEOFBIRTH']
        s.birthdate = parse_date(date_raw)
        s.birthplace = fields['PLACEOFBIRTH']
        s.address = fields['ADDRESS1']
        s.telno = fields['TEL1']
        s.grade_schools.append(grade_school)
        s.parent_status = parent_status
        s.living_with_id = living_with_id
        s.is_special_guidance_needed = False

        s.eyesight = 'E'
        s.overall_health = 'E'
        s.hearing = 'E'
        s.lungs = 'E'

        db_session.add(s)
    db_session.commit()

if __name__ == '__main__':
    fname = sys.argv[1]
    import_csv(fname)