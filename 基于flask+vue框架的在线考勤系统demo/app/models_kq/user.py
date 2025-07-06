from app import db
from sqlalchemy import Column, Integer, String, Date, Text, Time


class Employee_KQ(db.Model):
    __tablename__ = 'employees'
    __table_args__ = {'extend_existing': True}
    employee_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_name = db.Column(db.String(50), nullable=False)
    job_title = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))

class Administrator_KQ(db.Model):
    __tablename__ = 'administrators'
    __table_args__ = {'extend_existing': True}
    admin_id = db.Column(db.String(20), primary_key=True)
    admin_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))

class SurgeryNotification_KQ(db.Model):
    __tablename__ = 'surgery_notification'
    __table_args__ = {'extend_existing': True}
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    surgery_date = Column(Date, nullable=False)  
    surgery_time = Column(Time, nullable=False)  
    department = Column(String(50), nullable=False)
    operating_room = Column(String(50), nullable=False)
    patient_name = Column(String(50), nullable=False)
    surgery_type = Column(String(50), nullable=False)
    responsible_doctor_id = Column(Integer, nullable=False)
    notes = Column(Text)
