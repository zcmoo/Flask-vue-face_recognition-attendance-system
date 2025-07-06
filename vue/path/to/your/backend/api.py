from flask import Flask, jsonify, request
from models import SurgeryNotification_KQ, db

app = Flask(__name__)

@app.route('/api/employee/get_surgeries/<username>', methods=['GET'])
def get_surgeries(username):
    try:
        # 假设 responsible_doctor_id 是员工的唯一标识
        surgeries = SurgeryNotification_KQ.query.filter_by(responsible_doctor_id=username).all()
        surgery_list = []
        for surgery in surgeries:
            surgery_list.append({
                'notification_id': surgery.notification_id,
                'surgery_date': surgery.surgery_date.strftime('%Y-%m-%d'),
                'surgery_time': surgery.surgery_time.strftime('%H:%M:%S'),
                'department': surgery.department,
                'operating_room': surgery.operating_room,
                'patient_name': surgery.patient_name,
                'surgery_type': surgery.surgery_type,
                'responsible_doctor_id': surgery.responsible_doctor_id,
                'notes': surgery.notes
            })
        return jsonify(surgery_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)