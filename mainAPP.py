from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QDialog, QLineEdit, QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QImage
import sys
import cv2
import os
import csv

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
        # 웹캠 화면을 QLabel에 표시
        def update_frame():
            if self.timer_active:
                ret, frame = self.cap.read()
                if ret:
                    self.current_frame = frame
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                    pixmap = QPixmap.fromImage(qt_image)
                    self.cam_label.setPixmap(pixmap.scaled(self.cam_label.width(), self.cam_label.height()))

        # 타이머를 사용하여 주기적으로 화면 업데이트
        self.timer = self.startTimer(30)  # 30ms마다 업데이트
        self.timerEvent = lambda event: update_frame()

    def capture_picture(self):
        # 웹캠 화면 멈추기
        self.timer_active = False
        if self.current_frame is not None:
            # 사진 저장
            picture_name = "cam_save.jpg"  # 기본 파일 이름
            file_name = os.path.join(self.image_save_path, picture_name)
            cv2.imwrite(file_name, self.current_frame)
            print(f"사진이 저장되었습니다: {file_name}")

            # 저장된 파일 경로를 picture_put(QLineEdit)에 표시
            self.picture_name_input.setText(file_name)

    def save_data(self):
        # 입력된 데이터를 CSV 파일에 저장
        name = self.name_input.text()
        phone = self.phone_input.text()
        memo = self.memo_input.text()
        image_file = self.picture_name_input.text()  # picture_put에서 파일 경로 가져오기

        if name and phone and os.path.exists(image_file):  # 이름, 전화번호, 사진이 있는지 확인
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

    def closeEvent(self, event):
        # 종료 시 웹캠 해제
        self.cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    parking_app = ParkingApp()
    parking_app.show()
    sys.exit(app.exec())