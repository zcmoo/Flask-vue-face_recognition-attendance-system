from app import db
from sqlalchemy import Column, Integer, Time, Enum, Date, String

class AttendanceRecord_KQ(db.Model):
    __tablename__ = 'attendance_records'
    __table_args__ = {'extend_existing': True}
    record_id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(20), nullable=False)
    employee_name = Column(String(50), nullable=False)
    attendance_date = Column(Date, nullable=False)
    attendance_time = Column(Time)
    departure_time = Column(Time)  
    attendance_status = Column(Enum('on_time', 'late', 'absent', 'leave', 'early_departure'), nullable=False)

class LeaveApplication_KQ(db.Model):
    __tablename__ = 'leave_application'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, nullable=False)
    employee_name = Column(String, nullable=False)
    department = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    leave_type = Column(Enum('病假', '年假', '事假', '产假', '其他', name='leave_type_enum'), default='事假', nullable=False)
    leave_days = Column(Integer, nullable=False)
    leave_reason = Column(String, nullable=True)
    status = Column(Enum('待审批', '已通过', '已拒绝', '已批准', name='leave_status_enum'), default='待审批', nullable=False)


