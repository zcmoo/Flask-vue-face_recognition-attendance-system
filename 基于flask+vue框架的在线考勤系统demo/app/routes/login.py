from flask import Blueprint, request, jsonify
from app.models_kq.user import Employee_KQ, Administrator_KQ
from app import db

login_routes = Blueprint('login', __name__)

@login_routes.route('/login', methods=["POST"])
def login():
    name = request.form.get("username")
    pwd = request.form.get("password")
    user_type = request.form.get("user_type")
    if user_type == "employee":
        user = db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == name).first()
    else:
        user = db.session.query(Administrator_KQ).filter(Administrator_KQ.admin_id == name).first()
    if user:
        if user.password == pwd:
            if user_type == "employee":
                return jsonify({
                    'message': '登录成功', 
                    'user_type': 'employee',
                    'user_name': user.employee_name,
                    'user_department' : user.department,
                }), 200
            else:
                return jsonify({
                    'message': '登录成功', 
                    'user_type': 'admin',
                }), 200
        else:
            return jsonify({'message': '密码错误，登录失败'}), 401
    else:
        return jsonify({'message': '用户名不存在，登录失败'}), 401