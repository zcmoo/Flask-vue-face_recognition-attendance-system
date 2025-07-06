from flask import Blueprint, jsonify, request
from app import db
from app.models_kq.user import Employee_KQ, SurgeryNotification_KQ
from app.models_kq.attendance import AttendanceRecord_KQ, LeaveApplication_KQ
from datetime import datetime
from datetime import datetime, date 

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/get_employee/<int:employee_id>', methods=["GET"])
def get_employee_info(employee_id):
    employee = db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == employee_id).first()
    if employee:
        return jsonify({
            'employee_id': employee.employee_id,
            'employee_name': employee.employee_name,
            'job_title': employee.job_title,
            'department': employee.department,
            'phone_number': employee.phone_number,
            'email': employee.email
        }), 200
    else:
        return jsonify({'message': '员工信息不存在'}), 404

@employee_bp.route('/update_employee/<int:employee_id>', methods=["PUT"])
def update_employee_info(employee_id):
    data = request.get_json()
    employee = db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == employee_id).first()
    if employee:
        employee.employee_name = data.get('name', employee.employee_name)
        employee.phone_number = data.get('phone', employee.phone_number)
        employee.email = data.get('email', employee.email)
        db.session.commit()
        return jsonify({'message': '更新成功'}), 200
    else:
        return jsonify({'message': '员工信息不存在'}), 404

@employee_bp.route('/change_password', methods=["PUT"])
def change_password():
    data = request.get_json()
    employee = db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == data.get('employeeId')).first()
    if employee:
        if employee.password == data.get('oldPassword'):
            employee.password = data.get('newPassword')
            db.session.commit()
            return jsonify({'message': '密码修改成功'}), 200
        else:
            return jsonify({'message': '原密码错误'}), 401
    else:
        return jsonify({'message': '员工信息不存在'}), 404

@employee_bp.route('/get_surgeries/<int:employee_id>', methods=["GET"])
def get_surgeries(employee_id):
    page = request.args.get('page', default=1, type=int)  
    size = request.args.get('size', default=10, type=int) 
    start_date = request.args.get('start_date') 
    end_date = request.args.get('end_date')      
    query = db.session.query(SurgeryNotification_KQ).filter(
        SurgeryNotification_KQ.responsible_doctor_id == employee_id
    )
    if start_date and end_date:
        query = query.filter(
            SurgeryNotification_KQ.surgery_date >= start_date,
            SurgeryNotification_KQ.surgery_date <= end_date
        )
    surgeries = query.paginate(page=page, per_page=size)
    if surgeries.items:
        return jsonify({
            'data': [{
                'date': surgery.surgery_date.strftime('%Y-%m-%d'),
                'time': surgery.surgery_time.strftime('%H:%M:%S'),
                'patient_name': surgery.patient_name,
                'surgery_type': surgery.surgery_type,
                'room': surgery.operating_room,
                'remark': surgery.notes,
                'department': surgery.department
            } for surgery in surgeries.items],
            'total': surgeries.total 
        }), 200
    else:
        return jsonify({'message': '没有找到相关手术通知'}), 404

@employee_bp.route('/get_leave_records/<int:employee_id>', methods=["GET"])
def get_leave_records(employee_id):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    query = LeaveApplication_KQ.query.filter(LeaveApplication_KQ.employee_id == employee_id)
    paginated_records = query.paginate(page=page, per_page=page_size, error_out=False)
    data = []
    for record in paginated_records.items:
        data.append({
            'id': record.id,
            'start_date': record.start_date.strftime('%Y-%m-%d'),
            'end_date': record.end_date.strftime('%Y-%m-%d'),
            'leave_type': record.leave_type,
            'leave_days': record.leave_days,
            'leave_reason': record.leave_reason,
            'status': record.status
        })
    return jsonify({
        'success': True,
        'data': data,
        'total': paginated_records.total
    })

@employee_bp.route('/apply_leave/<int:employee_id>', methods=["POST"])
def apply_leave(employee_id):
    data = request.get_json()
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    leave_type = data.get('leave_type')
    leave_reason = data.get('leave_reason')
    employee_name = data.get('employee_name')
    department = data.get('department')
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    leave_days = (end - start).days + 1
    new_leave = LeaveApplication_KQ(
        employee_id=employee_id,
        employee_name=employee_name,
        department=department,
        start_date=start_date,
        end_date=end_date,
        leave_type=leave_type,
        leave_days=leave_days,
        leave_reason=leave_reason
    )
    try:
        db.session.add(new_leave)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '请假申请提交成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'请假申请提交失败: {str(e)}'
        })

@employee_bp.route('/edit_leave/<int:employee_id>/<int:leave_id>', methods=["POST"])
def edit_leave(employee_id, leave_id):
    data = request.get_json()
    leave = db.session.query(LeaveApplication_KQ).filter_by(id=leave_id, employee_id=employee_id).first()
    if not leave:
        return jsonify({
            'success': False,
            'message': '未找到该请假申请'
        })
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    leave_type = data.get('leave_type')
    leave_reason = data.get('leave_reason')
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    leave_days = (end - start).days + 1
    leave.start_date = start_date
    leave.end_date = end_date
    leave.leave_type = leave_type
    leave.leave_days = leave_days
    leave.leave_reason = leave_reason
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '请假申请修改成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'请假申请修改失败: {str(e)}'
        })

@employee_bp.route('/cancel_leave/<int:employee_id>/<int:leave_id>', methods=["POST"])
def cancel_leave(employee_id, leave_id):
    leave = db.session.query(LeaveApplication_KQ).filter_by(id=leave_id, employee_id=employee_id).first()
    if not leave:
        return jsonify({
            'success': False,
            'message': '未找到该请假申请'
        })
    try:
        db.session.delete(leave)
        db.session.commit()
        return jsonify({
            'success': True,
            'message': '请假申请取消成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'请假申请取消失败: {str(e)}'
        })

@employee_bp.route('/get_attendance_records/<int:employee_id>', methods=["GET"])
def get_attendance_records(employee_id):
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    status = request.args.get('status')
    query = AttendanceRecord_KQ.query.filter(AttendanceRecord_KQ.employee_id == employee_id)
    if start_date and end_date:
        query = query.filter(
            AttendanceRecord_KQ.attendance_date >= start_date,
            AttendanceRecord_KQ.attendance_date <= end_date
        )
    if status:
        query = query.filter(AttendanceRecord_KQ.attendance_status == status)
    paginated_records = query.paginate(page=page, per_page=page_size, error_out=False)
    data = []
    for record in paginated_records.items:
        data.append({
            'employee_id': record.employee_id,
            'employee_name': record.employee_name,
            'attendance_date': record.attendance_date.strftime('%Y-%m-%d'),
            'attendance_time': record.attendance_time.strftime('%H:%M:%S') if record.attendance_time else '',
            'departure_time': record.departure_time.strftime('%H:%M:%S') if record.departure_time else '',
            'attendance_status': record.attendance_status
        })
    return jsonify({
       'success': True,
        'data': data,
        'total': paginated_records.total
    })

@employee_bp.route('/get_dashboard_data/<int:employee_id>', methods=["GET"])
def get_dashboard_data(employee_id):
    try:
        today = date.today()  
        today_attendance = AttendanceRecord_KQ.query.filter(
            AttendanceRecord_KQ.employee_id == employee_id,
            AttendanceRecord_KQ.attendance_date == today
        ).first()
        attendance_status = today_attendance.attendance_status if today_attendance else '未打卡'
        pending_surgeries_count = SurgeryNotification_KQ.query.filter(
            SurgeryNotification_KQ.responsible_doctor_id == employee_id,
            SurgeryNotification_KQ.surgery_date == today
        ).count()
        leave_applications_count = LeaveApplication_KQ.query.filter(
            LeaveApplication_KQ.employee_id == employee_id,
            LeaveApplication_KQ.status == '待审批'
        ).count()
        this_month_start = date(today.year, today.month, 1)
        attendance_records_this_month = AttendanceRecord_KQ.query.filter(
            AttendanceRecord_KQ.employee_id == employee_id,
            AttendanceRecord_KQ.attendance_date >= this_month_start,
            AttendanceRecord_KQ.attendance_date <= today
        ).all()
        present_days = sum(1 for record in attendance_records_this_month if record.attendance_status == 'on_time')
        attendance_rate = (present_days / 30) * 100 if present_days else 0
        today_surgeries = SurgeryNotification_KQ.query.filter(
            SurgeryNotification_KQ.responsible_doctor_id == employee_id,
            SurgeryNotification_KQ.surgery_date == today
        ).all()
        surgeries_data = []
        for surgery in today_surgeries:
            surgeries_data.append({
                'date': surgery.surgery_date.strftime('%Y-%m-%d'),
                'time': surgery.surgery_time.strftime('%H:%M:%S'),
                'patient_name': surgery.patient_name,
                'surgery_type': surgery.surgery_type,
                'room': surgery.operating_room,
                'remark': surgery.notes,
                'department': surgery.department
            })
        recent_attendance = AttendanceRecord_KQ.query.filter(
            AttendanceRecord_KQ.employee_id == employee_id
        ).order_by(AttendanceRecord_KQ.attendance_date.desc()).limit(10).all()
        attendance_records = []
        for record in recent_attendance:
            attendance_records.append({
                'date': record.attendance_date.strftime('%Y-%m-%d'),
                'attendance_time': record.attendance_time.strftime('%H:%M:%S') if record.attendance_time else '',
                'departure_time': record.departure_time.strftime('%H:%M:%S') if record.departure_time else '',
                'status': record.attendance_status,
            })
        response_data = {
            'attendance_status': attendance_status,
            'pendingSurgeries': pending_surgeries_count,
            'leaveApplications': leave_applications_count,
            'attendanceRate': attendance_rate,
            'todaySurgeries': surgeries_data,
            'recentAttendance': attendance_records
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500