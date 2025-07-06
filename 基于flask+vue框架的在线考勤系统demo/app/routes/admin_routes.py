from flask import Blueprint, request, jsonify
from app.models_kq.user import Employee_KQ, SurgeryNotification_KQ
from app.models_kq.attendance import AttendanceRecord_KQ, LeaveApplication_KQ
from app import db
from sqlalchemy import String
import datetime
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/add_employee_kq', methods=['POST'])
def add_employee_kq():
    try:
        new_employee_data = request.get_json()
        new_employee = Employee_KQ(
            employee_name=new_employee_data.get('employee_name'),
            job_title=new_employee_data.get('job_title'),
            password=new_employee_data.get('password'),
            department=new_employee_data.get('department'),
            phone_number=new_employee_data.get('phone_number'),
            email=new_employee_data.get('email')
        )
        db.session.add(new_employee)
        db.session.commit()
        return jsonify({'message': '员工信息添加成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '添加员工信息失败：{}'.format(str(e))}), 500

@admin_bp.route('/get_employees_kq', methods=['GET'])
def get_employees_kq():
    search = request.args.get('search', '')
    department = request.args.get('department', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    query = Employee_KQ.query
    if search:
        query = query.filter(
            (Employee_KQ.employee_name.contains(search)) |
            (Employee_KQ.employee_id.cast(String).contains(search))
        )
    if department:
        query = query.filter(Employee_KQ.department == department)
    paginated_employees = query.paginate(page=page, per_page=page_size, error_out=False)
    employee_list = []
    for employee in paginated_employees.items:
        employee_list.append({
            'employee_id': employee.employee_id,
            'employee_name': employee.employee_name,
            'department': employee.department,
            'job_title': employee.job_title,
            'phone_number': employee.phone_number,
            'email': employee.email,
            'password': employee.password
        })
    return jsonify({
        'items': employee_list,
        'total': paginated_employees.total
    })

@admin_bp.route('/edit_employee_kq/<int:employee_id>', methods=['PUT'])
def edit_employee_kq(employee_id):
    employee = Employee_KQ.query.get(employee_id)
    if not employee:
        return jsonify({'message': '员工信息不存在'}), 404
    data = request.get_json()
    employee.employee_name = data.get('employee_name', employee.employee_name)
    employee.department = data.get('department', employee.department)
    employee.job_title = data.get('job_title', employee.job_title)
    employee.phone_number = data.get('phone_number', employee.phone_number)
    employee.email = data.get('email', employee.email)
    employee.password = data.get('password', employee.password)
    try:
        db.session.commit()
        return jsonify({'message': '员工信息编辑成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'编辑员工信息失败: {str(e)}'}), 500

@admin_bp.route('/delete_employee_kq/<int:employee_id>', methods=['DELETE'])
def delete_employee_kq(employee_id):
    employee = Employee_KQ.query.get(employee_id)
    if not employee:
        return jsonify({'message': '员工信息不存在'}), 404
    try:
        db.session.delete(employee)
        db.session.commit()
        return jsonify({'message': '员工信息删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'删除员工信息失败: {str(e)}'}), 500

@admin_bp.route('/get_attendance_records_kq', methods=['GET'])
def get_attendance_records():
    search = request.args.get('search', '')
    status = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    query = AttendanceRecord_KQ.query
    if search:
        query = query.filter(
            (AttendanceRecord_KQ.employee_name.contains(search)) |
            (AttendanceRecord_KQ.employee_id.contains(search))
        )
    if status:
        query = query.filter(AttendanceRecord_KQ.attendance_status == status)
    paginated_records = query.paginate(page=page, per_page=page_size, error_out=False)
    records = []
    for record in paginated_records.items:
        record_data = {
            'attendance_date': record.attendance_date.strftime('%Y-%m-%d'),
            'employee_id': record.employee_id,
            'employee_name': record.employee_name,
            'attendance_time': record.attendance_time.strftime('%H:%M:%S') if record.attendance_time else '',
            'departure_time': record.departure_time.strftime('%H:%M:%S') if record.departure_time else '',
            'attendance_status': record.attendance_status
        }
        records.append(record_data)
    return jsonify({
        'items': records,
        'total': paginated_records.total
    })

@admin_bp.route('/surgery_notifications_kq', methods=['GET'])
def get_surgery_notifications():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    date_filter = request.args.get('date')
    department_filter = request.args.get('department')
    query = SurgeryNotification_KQ.query
    if date_filter:
        date = datetime.datetime.strptime(date_filter, '%Y-%m-%d')
        query = query.filter(SurgeryNotification_KQ.surgery_date >= date,
                             SurgeryNotification_KQ.surgery_date < date.replace(day=date.day + 1))
    if department_filter:
        query = query.filter(SurgeryNotification_KQ.department == department_filter)
    notifications = query.paginate(page=page, per_page=page_size, error_out=False)
    items = []
    for notification in notifications.items:
        item = {
            'notification_id': notification.notification_id,
            'surgery_date': notification.surgery_date.strftime('%Y-%m-%d %H:%M:%S'),
            'surgery_time': notification.surgery_time.strftime('%Y-%m-%d %H:%M:%S'),
            'department': notification.department,
            'operating_room': notification.operating_room,
            'patient_name': notification.patient_name,
            'surgery_type': notification.surgery_type,
            'responsible_doctor_id': notification.responsible_doctor_id,
            'notes': notification.notes
        }
        items.append(item)
    return jsonify({
        'items': items,
        'total': notifications.total
    })

@admin_bp.route('/surgery_notifications_kq', methods=['POST'])
def add_surgery_notification():
    data = request.get_json()
    try:
        surgery_time_str = data['surgery_time'].split('T')[1].split('.')[0]
        surgery_date = datetime.datetime.strptime(data['surgery_date'], '%Y-%m-%d').date()  
        surgery_time = datetime.datetime.strptime(surgery_time_str,'%H:%M:%S').time()  
        notification = SurgeryNotification_KQ(
            surgery_date=surgery_date,
            surgery_time=surgery_time,
            department=data['department'],
            operating_room=data['operating_room'],
            patient_name=data['patient_name'],
            surgery_type=data['surgery_type'],
            responsible_doctor_id=data['responsible_doctor_id'],
            notes=data['notes']
        )
        db.session.add(notification)
        db.session.commit()
        return jsonify({'message': '发布成功'}), 201
    except ValueError as e:
        db.session.rollback()
        return jsonify({'message': f'日期或时间格式错误: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'发布失败: {str(e)}'}), 500

@admin_bp.route('/surgery_notifications_kq/<int:notification_id>', methods=['PUT'])
def edit_surgery_notification(notification_id):
    data = request.get_json()
    notification = SurgeryNotification_KQ.query.get(notification_id)
    if not notification:
        return jsonify({'message': '未找到该手术通知'}), 404
    surgery_time_str = data['surgery_time'].split('T')[1].split('.')[0]
    surgery_date = datetime.datetime.strptime(data['surgery_date'], '%Y-%m-%d').date()
    surgery_time = datetime.datetime.strptime(surgery_time_str,'%H:%M:%S').time()  
    notification.surgery_date = surgery_date
    notification.surgery_time = surgery_time
    notification.department = data['department']
    notification.operating_room = data['operating_room']
    notification.patient_name = data['patient_name']
    notification.surgery_type = data['surgery_type']
    notification.responsible_doctor_id = data['responsible_doctor_id']
    notification.notes = data['notes']
    db.session.commit()
    return jsonify({'message': '修改成功'})

@admin_bp.route('/surgery_notifications_kq/<int:notification_id>', methods=['DELETE'])
def delete_surgery_notification(notification_id):
    notification = SurgeryNotification_KQ.query.get(notification_id)
    if not notification:
        return jsonify({'message': '未找到该手术通知'}), 404
    db.session.delete(notification)
    db.session.commit()
    return jsonify({'message': '删除成功'})

@admin_bp.route('/leave-applications', methods=['GET'])
def get_leave_applications():
    page = request.args.get('page', default=1, type=int)
    size = request.args.get('size', default=10, type=int)
    search = request.args.get('search', '')
    department = request.args.get('department', '')
    status = request.args.get('status', '')
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    query = LeaveApplication_KQ.query
    if search:
        query = query.filter(
            (LeaveApplication_KQ.employee_name.contains(search)) |
            (LeaveApplication_KQ.id.cast(String).contains(search))
        )
    if department:
        query = query.filter(LeaveApplication_KQ.department == department)
    if status:
        query = query.filter(LeaveApplication_KQ.status == status)
    if start_date and end_date:
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        query = query.filter(LeaveApplication_KQ.start_date >= start, LeaveApplication_KQ.end_date <= end)
    applications = query.paginate(page=page, per_page=size)
    result = [
        {
            "id": app.id,
            "name": app.employee_name,
            "department": app.department,
            "leaveType": app.leave_type,
            "startDate": str(app.start_date),
            "endDate": str(app.end_date),
            "days": app.leave_days,
            "reason": app.leave_reason,
            "status": app.status
        }
        for app in applications.items
    ]
    response = jsonify(result)
    response.headers['total-count'] = applications.total
    return response

@admin_bp.route('/leave-applications/<int:application_id>/approve', methods=['POST'])
def approve_leave_application(application_id):
    application = LeaveApplication_KQ.query.get(application_id)
    if not application:
        return jsonify({"message": "未找到该请假申请"}), 404
    application.status = '已通过' 
    db.session.commit()
    return jsonify({"message": "批准成功"})

@admin_bp.route('/leave-applications/<int:application_id>/reject', methods=['POST'])
def reject_leave_application(application_id):
    application = LeaveApplication_KQ.query.get(application_id)
    if not application:
        return jsonify({"message": "未找到该请假申请"}), 404
    application.status = '已拒绝'
    db.session.commit()
    return jsonify({"message": "拒绝成功"})

@admin_bp.route('/get_dashboard_data', methods=['get'])
def get_dashboard_data():
    try:
        employee_total = db.session.query(func.count(Employee_KQ.employee_id)).scalar()
        today = datetime.date.today()
        today_attendance_count = db.session.query(func.count(AttendanceRecord_KQ.record_id)).filter(
            AttendanceRecord_KQ.attendance_date == today).scalar()
        pending_leave_applications_count = db.session.query(func.count(LeaveApplication_KQ.id)).filter(
            LeaveApplication_KQ.status == '待审批').scalar()
        today_surgery_notifications_count = db.session.query(func.count(SurgeryNotification_KQ.notification_id)).filter(
            SurgeryNotification_KQ.surgery_date == today).scalar()
        recent_attendance_records = db.session.query(AttendanceRecord_KQ).order_by(
            AttendanceRecord_KQ.attendance_date.desc()).limit(10).all()
        attendance_records = []
        for record in recent_attendance_records:
            attendance_records.append({
            'attendance_date': record.attendance_date.strftime('%Y-%m-%d'),
            'employee_id': record.employee_id,
            'employee_name': record.employee_name,
            'attendance_time': record.attendance_time.strftime('%H:%M:%S') if record.attendance_time else '',
            'departure_time': record.departure_time.strftime('%H:%M:%S') if record.departure_time else '',
            'attendance_status': record.attendance_status
            })
        response_data = {
            'employeeTotal': employee_total,
            'todayAttendanceCount': today_attendance_count,
            'pendingLeaveApplicationsCount': pending_leave_applications_count,
            'todaySurgeryNotificationsCount': today_surgery_notifications_count,
            'attendanceRecords': attendance_records
        }
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
