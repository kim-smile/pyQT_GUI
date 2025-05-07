from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QImage
import sys
import cv2
import os
import csv
import shutil
from yolov5.detect import run  # YOLOv5 detect.py의 run 함수 호출

class ParkingApp(QDialog):
    def __init__(self):
        super().__init__()
        # parking.ui 로드
        uic.loadUi("res/parking.ui", self)

        # 위젯 연결
        self.name_input = self.findChild(QLineEdit, "name_put")
        self.phone_input = self.findChild(QLineEdit, "phone_put")
        self.memo_input = self.findChild(QLineEdit, "memo_put")
        self.picture_name_input = self.findChild(QLineEdit, "picture_put")  # picture_put 필드
        self.save_button = self.findChild(QPushButton, "save")
        self.picture_button = self.findChild(QPushButton, "picture")
        self.cam_label = self.findChild(QLabel, "cam")

        # 버튼 클릭 이벤트 연결
        self.save_button.clicked.connect(self.save_data)
        self.picture_button.clicked.connect(self.capture_picture)

        # 사진 저장 경로 설정
        self.image_save_path = "image"
        if not os.path.exists(self.image_save_path):
            os.makedirs(self.image_save_path)

        # 웹캠 초기화
        self.cap = cv2.VideoCapture(0)
        self.current_frame = None
        self.timer_active = True
        self.start_webcam()

    def start_webcam(self):
        # 웹캠 화면을 QLabel에 표시하며 YOLOv5 객체 탐지 수행
        def update_frame():
            if self.timer_active:
                ret, frame = self.cap.read()
                if ret:
                    # YOLOv5 객체 탐지 수행
                    detected_frame = self.detect_objects(frame)

                    # OpenCV 이미지를 QPixmap으로 변환하여 QLabel에 표시
                    rgb_image = cv2.cvtColor(detected_frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(qt_image)
                    self.cam_label.setPixmap(pixmap.scaled(self.cam_label.width(), self.cam_label.height()))

        # 타이머를 사용하여 주기적으로 화면 업데이트
        self.timer = self.startTimer(30)  # 30ms마다 업데이트
        self.timerEvent = lambda event: update_frame()
        
    def detect_objects(self, frame):
        # YOLOv5 객체 탐지 수행
        temp_image_path = "temp_frame.jpg"  # 임시 파일 경로
        cv2.imwrite(temp_image_path, frame)  # 현재 프레임을 임시 파일로 저장

        # YOLOv5 실행
        output_dir = "runs/detect"
        run(weights="d:/2025_robot/pyqtgui001_yolov5/best.pt", source=temp_image_path, project=output_dir, name="exp", exist_ok=True)

        # YOLOv5 결과를 반환 (탐지된 프레임을 화면에 표시)
        detected_image_path = os.path.join(output_dir, "exp", os.path.basename(temp_image_path))
        if os.path.exists(detected_image_path):
            detected_frame = cv2.imread(detected_image_path)  # 탐지된 결과 이미지를 읽음
            self.current_frame = detected_frame  # 탐지된 프레임을 저장

            # 탐지 결과 파일 삭제
            if os.path.exists(detected_image_path):
                os.remove(detected_image_path)

            # 임시 파일 삭제
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

            return detected_frame
        
        else:
            print("객체 탐지 결과 이미지를 찾을 수 없습니다.")

            # 임시 파일 삭제
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)

            return frame  # 탐지 실패 시 원본 프레임 반환

        # YOLOv5 작업 디렉터리 정리 (필요한 경우)
        exp_dir = os.path.join(output_dir, "exp")
        if os.path.exists(exp_dir):
            shutil.rmtree(exp_dir)  # 탐지 결과 디렉터리 삭제

    def capture_picture(self):
        # 탐지 중인 화면을 저장
        if self.current_frame is not None:
            # 현재 탐지된 프레임 저장
            picture_name = "cam_save.jpg"  # 기본 파일 이름
            file_name = os.path.join(self.image_save_path, picture_name)
            cv2.imwrite(file_name, self.current_frame)  # 탐지된 프레임 저장
            print(f"사진이 저장되었습니다: {file_name}")

            # 저장된 파일 경로를 picture_put(QLineEdit)에 표시
            self.picture_name_input.setText(file_name)
        else:
            print("현재 프레임이 None입니다. 웹캠이 제대로 작동하는지 확인하세요.")

    def save_data(self):
        # 입력된 데이터를 CSV 파일에 저장
        name = self.name_input.text()
        phone = self.phone_input.text()
        memo = self.memo_input.text()
        image_file = self.picture_name_input.text()  # picture_put에서 파일 경로 가져오기

        if name.strip() and phone.strip() and os.path.exists(image_file):  # 이름, 전화번호, 사진이 있는지 확인
            file_exists = os.path.isfile("parking_data.csv")
            try:
                with open("parking_data.csv", "a", newline="", encoding="utf-8-sig") as file:
                    writer = csv.writer(file)
                    if not file_exists:
                        writer.writerow(["이름", "전화번호", "메모", "사진"])
                    writer.writerow([name, phone, memo, image_file])
                print(f"저장된 데이터: 이름={name}, 전화번호={phone}, 메모={memo}, 사진={image_file}")
            except Exception as e:
                print(f"데이터 저장 중 오류 발생: {e}")
        else:
            print("이름, 전화번호, 사진은 필수 입력 항목입니다.")
            return

        # 프로그램 종료
        QApplication.quit()

    def closeEvent(self, event):
        # 종료 시 웹캠 해제
        self.cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    parking_app = ParkingApp()
    parking_app.show()
    sys.exit(app.exec())