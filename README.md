# WebCam, YOLOv5, PyQt를 활용한 주차장 빈자리 탐지 프로그램
### 개요
YOLOv5를 이용해 주차장의 빈자리를 탐지하는 모델(best.pt)을 학습시켰고, PyQt 기반 주소록 저장 프로그램(mainAPP.py)에 해당 모델을 통합하여, 주차장 빈자리 탐지 기능이 포함된 주소록 프로그램(mainAPP_yolov5.py)을 구현하였습니다.
![image](https://github.com/user-attachments/assets/b1668a99-278e-4f7d-a59b-0ad062b26eef)
### 주요 기능
- 이름, 전화번호, 메모, 사진을 함께 저장할 수 있는 주소록 형태의 GUI
- 사용자가 입력한 정보와 함께, 웹캠을 통한 주차장 빈자리를 자동 탐지
- 객체(빈 주차 공간)가 탐지된 이미지는 image 폴더에 저장
- 이름, 전화번호, 메모, 이미지 파일 경로는 CSV 파일로 저장
