import time
import cv2
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))  
from app import extract_embeddings
def execute():
    fps = 0.0
    capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    ref, frame = capture.read()
    if not ref:
        raise ValueError("未能正确读取摄像头")
    while True:
        t1 = time.time()
        # 读取某一帧
        ref, frame = capture.read()
        if not ref:
            break
        # 格式转变，BGRtoRGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # 进行检测，获取返回的包含图像和姓名的字典
        result_dict = extract_embeddings.detect_image(frame)
        # 取出处理后的图像
        frame = result_dict["image"]
        # 取出识别出的人名
        detected_name = result_dict["name"]
        # RGBtoBGR满足opencv显示格式
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        fps = (fps + (1. / (time.time() - t1))) / 2
        frame = cv2.putText(frame, "fps= %.2f" % (fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("video", frame)
        c = cv2.waitKey(1) & 0xff
        if c == 113:
            capture.release()
            break
    capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    execute()