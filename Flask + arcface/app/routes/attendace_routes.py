from flask import Blueprint,Response, request, jsonify
from app.models_kq.user import Employee_KQ
from app.recognition.add_mask import FaceMasker, BLUE_IMAGE_PATH  
import cv2
import os
import random
import numpy as np
import time
from app import extract_embeddings
from app import db 
import threading
from PIL import Image, ImageDraw, ImageFont
from app.models_kq.attendance import AttendanceRecord_KQ
from datetime import datetime

attendace_routes = Blueprint('attendace', __name__)
detected_name = ""
start_time = None
capture_folder_name = None
capture_num_images = 10
capture_count = 0
capture_in_progress = False
capture_lock = threading.Lock()
capture_completed = False 
dataset_path = r"./app/recognition/dataset"

def cv2ImgAddText(img, label, left, top, textColor=(0,0,255)):
    current_dir = os.path.dirname(__file__)
    font_path = os.path.join(current_dir, 'model_data', 'simhei.ttf')
    img = Image.fromarray(np.uint8(img))
    font = ImageFont.truetype(font=font_path, size=30)
    draw = ImageDraw.Draw(img)
    label = label.encode('utf-8')
    draw.text((left, top), str(label,'UTF-8'), fill=textColor, font=font)
    return np.asarray(img)

def adjust_brightness(image, factor):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * factor, 0, 255)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def change_color_gamut(image, gamma=1.0):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255
                    for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def transform_image(image):
    image = adjust_brightness(image, random.uniform(0.6, 1.4))
    image = change_color_gamut(image, random.uniform(0.7, 1.3))
    return image

def is_valid_folder_name(folder_name):
    return folder_name.isdigit()

def record_attendance(employee_id):
    try:
        employee = db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == employee_id).first()
        now = datetime.now()
        attendance_date = now.date()
        attendance_time = now.time()
        is_late = now.time() > datetime.strptime("09:00:00", "%H:%M:%S").time()
        attendance_status = 'late' if is_late else 'on_time'
        existing_record = db.session.query(AttendanceRecord_KQ).filter(
            AttendanceRecord_KQ.employee_id == employee_id,
            AttendanceRecord_KQ.attendance_date == attendance_date
        ).first()
        if existing_record:
            print(f"员工 {employee_id} 当天已经签到，无需重复签到", flush=True)
            return
        attendance_record = AttendanceRecord_KQ(
            employee_id=employee_id,
            employee_name=employee.employee_name,
            attendance_date=attendance_date,
            attendance_time=attendance_time,
            attendance_status=attendance_status
        )
        db.session.add(attendance_record)
        db.session.commit()
    except Exception as e:
        print(f"插入考勤记录时出错: {e}", flush=True)

def record_departure(employee_id):
    try:
        now = datetime.now()
        departure_time = now.time()
        is_early_departure = now.time() < datetime.strptime("18:00:00", "%H:%M:%S").time()
        attendance_status = 'early_departure' if is_early_departure else 'on_time'
        existing_record = db.session.query(AttendanceRecord_KQ).filter(
            AttendanceRecord_KQ.employee_id == employee_id,
            AttendanceRecord_KQ.attendance_date == now.date()
        ).first()
        if existing_record:
            existing_record.departure_time = departure_time
            existing_record.attendance_status = attendance_status
            db.session.commit()
            print(f"员工 {employee_id} 签退成功，签退时间为 {departure_time}", flush=True)
        else:
            employee = db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == employee_id).first()
            attendance_record = AttendanceRecord_KQ(
                employee_id=employee_id,
                employee_name=employee.employee_name,
                attendance_date=now.date(),
                attendance_status='absent'
            )
            db.session.add(attendance_record)
            db.session.commit()
            print(f"员工 {employee_id} 没有当天的签到记录，已插入缺勤记录", flush=True)
    except Exception as e:
        print(f"插入签退记录时出错: {e}", flush=True)

def generate_video_frames_with_capture():
    global capture_folder_name, capture_num_images, capture_count, capture_in_progress, capture_lock, capture_completed, dataset_path
    target_folder = None
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    fps = 0.0
    current_angle = 0 
    angle_names = ['平视', '抬头', '低头', '左转', '右转']
    angle_arrows = [
        None,  
        ((320, 380), (320, 100)),  
        ((320, 100), (320, 380)),  
        ((540, 240), (100, 240)),  
        ((100, 240), (540, 240))  
    ]
    if not cap.isOpened():
        raise ValueError("无法打开摄像头，请检查摄像头连接及权限设置")
    while True:
        ret, frame = cap.read()
        t1 = time.time()
        if not ret:
            break
        original_frame = frame.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = extract_embeddings.draw_face_frame(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame = cv2ImgAddText(frame, f"采集指导: {angle_names[current_angle]}", 0, 80)
        frame = cv2ImgAddText(frame, f"进度: {capture_count+ 1}/90", 0, 120)
        if current_angle in [1, 2, 3, 4] and angle_arrows[current_angle]:
            start_point, end_point = angle_arrows[current_angle]
            cv2.arrowedLine(frame, start_point, end_point, (0, 255, 0), 3, tipLength=0.3)
        with capture_lock:
            if capture_in_progress:
                if capture_folder_name:
                    if not os.path.exists(dataset_path):
                        os.makedirs(dataset_path)
                    target_folder = os.path.join(dataset_path, capture_folder_name)
                    target_folder_name = str(capture_folder_name)
                    if not os.path.exists(target_folder):
                        os.makedirs(target_folder)
                if capture_count < capture_num_images:
                    frame1 = transform_image(original_frame)
                    file_name = os.path.join(target_folder, f"{capture_count:03d}.png")
                    cv2.imwrite(file_name, frame1)
                    image_path = file_name
                    name = target_folder_name
                    extract_embeddings.encode_face_dataset(image_path, name)
                    capture_count += 1
                    if capture_count % 18 == 0:
                        current_angle = (current_angle + 1) % len(angle_names)
                    fps = (fps + (1. / (time.time() - t1))) / 2
                    capture_folder_name = None 
                    if capture_count >= capture_num_images:
                        fps = 0.0
                        capture_in_progress = False
                        capture_count = 0
                        capture_completed = True
                        image_files = sorted([f for f in os.listdir(target_folder) if f.endswith('.png')])
                        # 只留下最后一张照片
                        if len(image_files) > 1:
                            for file_to_remove in image_files[:-1]:
                                os.remove(os.path.join(target_folder, file_to_remove))
                        print("已采集完毕。")
        if fps>0:
            frame = cv2.putText(frame, "fps= %.2f" % (fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()
    cv2.destroyAllWindows()

# 万不得已，就用这个识别戴口罩的人脸
# def generate_video_frames_with_capture():
#     global capture_folder_name, capture_num_images, capture_count, capture_in_progress, capture_lock, capture_completed, dataset_path
#     target_folder = None
#     cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#     if not cap.isOpened():
#         raise ValueError("无法打开摄像头，请检查摄像头连接及权限设置")
#     while True:
#         ret, frame = cap.read()
#         t1 = time.time()
#         if not ret:
#             break
#         original_frame = frame.copy()
#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         frame = extract_embeddings.draw_face_frame(frame)
#         frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
#         with capture_lock:
#             if capture_in_progress:
#                 if capture_folder_name:
#                     if not os.path.exists(dataset_path):
#                         os.makedirs(dataset_path)
#                     target_folder = os.path.join(dataset_path, capture_folder_name)
#                     target_folder_name = str(capture_folder_name)
#                     if not os.path.exists(target_folder):
#                         os.makedirs(target_folder)
#                 if capture_count < capture_num_images:
#                     frame1 = transform_image(original_frame)
#                     file_name = os.path.join(target_folder, f"{capture_count:03d}.png")
#                     cv2.imwrite(file_name, frame1)
#                     FaceMasker(file_name, BLUE_IMAGE_PATH, False, 'hog').mask()
#                     file_name1 = os.path.join(target_folder, f"{capture_count:03d}-with-mask.png")
#                     image_path = file_name
#                     image_path1 = file_name1
#                     name = target_folder_name
#                     extract_embeddings.encode_face_dataset(image_path, name)
#                     extract_embeddings.encode_face_dataset(image_path1, name)
#                     capture_count += 1
#                     capture_folder_name = None 
#                     if capture_count >= capture_num_images:
#                         capture_in_progress = False
#                         capture_count = 0
#                         capture_completed = True
#                         image_files = sorted([f for f in os.listdir(target_folder) if f.endswith('.png')])
#                         if len(image_files) > 2:
#                             for file_to_remove in image_files[:-2]:
#                                 os.remove(os.path.join(target_folder, file_to_remove))
#                         print("已采集完毕。")
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#     cap.release()
#     cv2.destroyAllWindows()

def generate_frames():
    global detected_name, start_time
    detected_name = None
    fps = 0.0
    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not capture.isOpened():
        raise ValueError("未能正确打开摄像头")
    save_count = 0  # 用于计数保存的照片数量
    save_path = "app/recognition/saved_frames"  # 保存照片的路径
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    while True:
        success, frame = capture.read()
        t1 = time.time()
        if not success:
            break
        try:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result_dict = extract_embeddings.detect_image(frame)
            frame = result_dict["image"]
            name = result_dict["name"]
            if name != "unknown":
                detected_name = name
                if start_time is None:
                    start_time = time.time()
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            fps = (fps + (1. / (time.time() - t1))) / 2
            # frame = cv2.putText(frame, "fps= %.2f" % (fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            if save_count < 5:
                file_name = os.path.join(save_path, f"frame_{save_count:03d}.jpg")
                cv2.imwrite(file_name, frame)
                save_count += 1
                print(f"已保存照片: {file_name}")
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        except Exception as e:
            print(f"人脸识别过程出现错误: {e}")
            capture.release()
            cv2.destroyAllWindows()
            continue
    capture.release()
    cv2.destroyAllWindows()

@attendace_routes.route('/video')
def video():
    return Response(generate_video_frames_with_capture(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@attendace_routes.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@attendace_routes.route('/start_capture', methods=['POST'])
def start_capture():
    global capture_folder_name, capture_num_images, capture_in_progress, capture_lock, capture_count, capture_completed, dataset_path
    try:
        data = request.get_json()
        folder_name = data.get('folder_name', '')
        target_folder = os.path.join(dataset_path, folder_name)
        with capture_lock:
            if capture_in_progress:
                return jsonify({"success": False, "message": "图像采集正在进行中，请稍后重试。"}), 200
            if not is_valid_folder_name(folder_name):
                return jsonify({"success": False, "message": "工号格式不正确，请输入仅包含数字的工号。"}), 200
            if os.path.exists(target_folder):
                return jsonify({"success": False, "message": "该工号已存在，请更换工号后重新尝试。"}), 200
            if not db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == folder_name).first():
                return jsonify({"success": False, "message": "不存在该员工，请添加后重新尝试"}), 200
            capture_folder_name = folder_name
            capture_num_images = 10
            capture_in_progress = True
            capture_count = 0
            capture_completed = False
        return jsonify({"success": True, "message": "采集中，请稍后"}), 200
    except Exception as e:
        print(f"start_capture 出现错误: {str(e)}")
        return jsonify({"success": False, "message": "服务器内部错误，请稍后重试。"}), 500

@attendace_routes.route('/check_capture_status', methods=['GET'])
def check_capture_status():
    global capture_completed
    with capture_lock:
        if capture_completed:
            capture_completed = False 
            return jsonify({"success": True, "message": "采集已完成。"}), 200
        else:
            return jsonify({"success": False, "message": "采集正在进行中。"}), 202

@attendace_routes.route('/check_integration', methods=['POST'])
def check_integration():
    global start_time, detected_name
    try:
        if start_time is None:
            return jsonify({"success": False, "message": "未识别到，请识别到后重试"}), 400
        if detected_name and detected_name != "unknown":
            start_time = None
            record_attendance(detected_name)
            employee = db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == detected_name).first()
            return jsonify({"success": True, "message": str(employee.employee_name) + "签到成功"}), 200
        return jsonify({"success": False, "message": "未识别到，请识别到后重试"}), 202
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@attendace_routes.route('/check_departure', methods=['POST'])
def check_departure():
    global start_time, detected_name
    try:
        if start_time is None:
            return jsonify({"success": False, "message": "未识别到，请识别到后重试"}), 400
        if detected_name and detected_name != "unknown":
            start_time = None
            record_departure(detected_name)
            employee = db.session.query(Employee_KQ).filter(Employee_KQ.employee_id == detected_name).first()
            return jsonify({"success": True, "message": str(employee.employee_name) + "签退成功"}), 200
        return jsonify({"success": False, "message": "未识别到，请识别到后重试"}), 202
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500