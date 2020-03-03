import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
import os
import cv2
import numpy as np

# UI 파일 로드
form_class = uic.loadUiType("main(eng).ui")[0]

# 윈도우 클래스 정의
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 로컬 이미지
        self.origin = None
        self.seed = None
        self.segmentation = None
        self.paintedCanvas = None

        # 로컬 마우스 포인트
        self.oldPoint = None

        # 자동 저장 활성화 여부
        self.autoSave = False

        # 수정여부
        self.isModified = False

        # 경로 변수 저장
        self.imagePath = None  # 이미지 경로
        self.maskPath = None  # 마스크 경로

        # 컬러 맵 정의
        self.colorMap = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 255), (100, 50, 0),
                         (100, 100, 100), (20, 0, 100), (255, 0, 100), (255, 100, 0), (255, 100, 100), (255, 255, 255)]
        # 현재 사용 중인 컬러
        self.colorNow = 0

        # 이미지 번호 변수
        self.currentNum = 0  # 현재 작업 중인 번호
        self.lastNum = 0  # 이전 작업 번호
        self.nextNum = 1  # 다음 작업 번호
        self.imgCount = 0  # 이미지 갯수

        # 이미지 경로 지정 버튼 이벤트 지정
        self.button_imgPath.clicked.connect(self.loadImagePath)

        # 마스크 경로 지정 버튼 이벤트 지정
        self.button_maskPath.clicked.connect(self.loadMaskPath)

        # 이전 이미지로 바로가기 버튼 이벤트 지정
        self.button_last.clicked.connect(self.clickButtonLast)

        # 다음 이미지로 바로가기 버튼 이벤트 지정
        self.button_next.clicked.connect(self.clickButtonNext)

        # 다이얼 이벤트 지정
        self.dial_img.valueChanged.connect(self.dialMoved)

        # 붓 굵기 콤보박스 초기화
        self.initBrush()

        # 자동 시작 활성화 체크박스 이벤트 지정
        self.checkBox_autoSave.stateChanged.connect(self.clickCheckBoxAutoSave)

        # 저장하기 이벤트 등록
        self.button_save.clicked.connect(self.clickButtonSave)

        # 다시그리기 버튼 이벤트 등록
        self.button_repaint.clicked.connect(self.clickButtonRepaint)

        # 캔버스 마우스 이벤트 등록
        self.label_canvasImg.mousePressEvent = self.canvasMousePressed
        self.label_canvasImg.mouseMoveEvent = self.canvasMouseMove
        self.label_canvasImg.mouseReleaseEvent = self.canvasMouseRelease
        self.label_canvasImg.wheelEvent = self.canvasWheel

        # 이미지 박스 초기화
        self.loadAllImage()

    # 키보드 이벤트 정의
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S:
            self.clickButtonSave()
        elif event.key() == Qt.Key_R:
            self.clickButtonRepaint()
        elif event.key() == Qt.Key_Right or event.key() == Qt.Key_Space:
            self.clickButtonNext()
        elif event.key() == Qt.Key_Left:
            self.clickButtonLast()
        elif event.key() == Qt.Key_1:
            self.clickColor1()
        elif event.key() == Qt.Key_2:
            self.clickColor2()
        elif event.key() == Qt.Key_3:
            self.clickColor3()
        elif event.key() == Qt.Key_4:
            self.clickColor4()
        elif event.key() == Qt.Key_5:
            self.clickColor5()
        elif event.key() == Qt.Key_6:
            self.clickColor6()
        elif event.key() == Qt.Key_7:
            self.clickColor7()
        elif event.key() == Qt.Key_8:
            self.clickColor8()
        elif event.key() == Qt.Key_9:
            self.clickColor9()
        elif event.key() == Qt.Key_0:
            self.clickColor10()
        elif event.key() == Qt.Key_Minus:
            self.clickColor11()
        elif event.key() == Qt.Key_Plus:
            self.clickColor12()
        else:
            pass

    # 다시그리기 버튼 이벤트
    def clickButtonRepaint(self):
        self.loadAllImage()

    # 오토세이브 체크박스 클릭 이벤트
    def clickCheckBoxAutoSave(self):
        if self.checkBox_autoSave.isChecked():
            self.autoSave = True
        else:
            self.autoSave = False

    # 저장하기 버튼 이벤트
    def clickButtonSave(self):
        if self.isModified:
            try:
                img = cv2.cvtColor(self.segmentation, cv2.COLOR_RGB2BGR)
                path = self.maskPath + '/' + self.lineEdit_img.text()
                if self.imwrite(path, img):
                    print(path, 'Success to save')
                else:
                    print(path, 'Failed to save')
                self.updateMaskList()
            except AssertionError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("There is no image to save")
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Image is not modified")
            msg.setWindowTitle("Warning")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    # 캔버스 마우스 클릭 이벤트
    def canvasMousePressed(self, event):
        try:
            thickness = int(self.comboBox_lineThick.currentText())
            height = self.label_canvasImg.size().height()
            width = self.label_canvasImg.size().width()
            x = int(event.x() * self.paintedCanvas.shape[1] / width)
            y = int(event.y() * self.paintedCanvas.shape[0] / height)
            self.oldPoint = (x, y)
            cv2.line(self.paintedCanvas, self.oldPoint, self.oldPoint, self.colorMap[self.colorNow], thickness)
            cv2.line(self.seed, self.oldPoint, self.oldPoint, self.colorNow + 1, thickness)
            self.updateCurrentImage()
        except AttributeError:
            pass

    # 캔버스 마우스 동작 이벤트
    def canvasMouseMove(self, event):
        try:
            thickness = int(self.comboBox_lineThick.currentText())
            height = self.label_canvasImg.size().height()
            width = self.label_canvasImg.size().width()
            x = int(event.x() * self.paintedCanvas.shape[1] / width)
            y = int(event.y() * self.paintedCanvas.shape[0] / height)
            cv2.line(self.paintedCanvas, self.oldPoint, (x, y), self.colorMap[self.colorNow], thickness)
            cv2.line(self.seed, self.oldPoint, (x, y), self.colorNow + 1, thickness)
            self.oldPoint = (x, y)
            self.updateCurrentImage()
        except AttributeError:
            pass

    # 캔버스 마우스 뗄 때 이벤트
    def canvasMouseRelease(self, event):
        try:
            thickness = int(self.comboBox_lineThick.currentText())
            height = self.label_canvasImg.size().height()
            width = self.label_canvasImg.size().width()
            x = int(event.x() * self.paintedCanvas.shape[1] / width)
            y = int(event.y() * self.paintedCanvas.shape[0] / height)
            cv2.line(self.paintedCanvas, self.oldPoint, (x, y), self.colorMap[self.colorNow], thickness)
            cv2.line(self.seed, self.oldPoint, (x, y), self.colorNow + 1, thickness)
            self.oldPoint = None
            self.updateCurrentImage()
            self.updateSegmentationImage()
        except AttributeError:
            pass

    # 캔버스 마우스 휠 이벤트
    def canvasWheel(self, event):
        index = self.comboBox_lineThick.currentIndex()
        maxIndex = self.comboBox_lineThick.count()
        if event.angleDelta().y() > 0:
            self.comboBox_lineThick.setCurrentIndex(index + 1 if index < maxIndex - 1 else maxIndex - 1)
        else:
            self.comboBox_lineThick.setCurrentIndex(index - 1 if index > 0 else 0)

    # 붓 설정 초기화
    def initBrush(self):
        # 붓 굵기 정의
        self.comboBox_lineThick.addItems(['1', '2', '5', '10', '20', '40', '80', '160', '250', '400'])
        # 팔레트 색상 정의
        self.button_color1.setStyleSheet("background-color:rgb({},{},{})".
                                         format(self.colorMap[0][0], self.colorMap[0][1], self.colorMap[0][2]))
        self.button_color2.setStyleSheet("background-color:rgb({},{},{})".
                                         format(self.colorMap[1][0], self.colorMap[1][1], self.colorMap[1][2]))
        self.button_color3.setStyleSheet("background-color:rgb({},{},{})".
                                         format(self.colorMap[2][0], self.colorMap[2][1], self.colorMap[2][2]))
        self.button_color4.setStyleSheet("background-color:rgb({},{},{})".
                                         format(self.colorMap[3][0], self.colorMap[3][1], self.colorMap[3][2]))
        self.button_color5.setStyleSheet("background-color:rgb({},{},{})".
                                         format(self.colorMap[4][0], self.colorMap[4][1], self.colorMap[4][2]))
        self.button_color6.setStyleSheet("background-color:rgb({},{},{})".
                                         format(self.colorMap[5][0], self.colorMap[5][1], self.colorMap[5][2]))
        self.button_color7.setStyleSheet("background-color:rgb({},{},{})".
                                         format(self.colorMap[6][0], self.colorMap[6][1], self.colorMap[6][2]))
        self.button_color8.setStyleSheet("background-color:rgb({},{},{})".
                                         format(self.colorMap[7][0], self.colorMap[7][1], self.colorMap[7][2]))
        self.button_color9.setStyleSheet("background-color:rgb({},{},{})".
                                         format(self.colorMap[8][0], self.colorMap[8][1], self.colorMap[8][2]))
        self.button_color10.setStyleSheet("background-color:rgb({},{},{})".
                                          format(self.colorMap[9][0], self.colorMap[9][1], self.colorMap[9][2]))
        self.button_color11.setStyleSheet("background-color:rgb({},{},{})".
                                          format(self.colorMap[10][0], self.colorMap[10][1], self.colorMap[10][2]))
        self.button_color12.setStyleSheet("background-color:rgb({},{},{})".
                                          format(self.colorMap[11][0], self.colorMap[11][1], self.colorMap[11][2]))
        # 팔레트 클릭 시 해당 색상으로 전환
        self.button_color1.clicked.connect(self.clickColor1)
        self.button_color2.clicked.connect(self.clickColor2)
        self.button_color3.clicked.connect(self.clickColor3)
        self.button_color4.clicked.connect(self.clickColor4)
        self.button_color5.clicked.connect(self.clickColor5)
        self.button_color6.clicked.connect(self.clickColor6)
        self.button_color7.clicked.connect(self.clickColor7)
        self.button_color8.clicked.connect(self.clickColor8)
        self.button_color9.clicked.connect(self.clickColor9)
        self.button_color10.clicked.connect(self.clickColor10)
        self.button_color11.clicked.connect(self.clickColor11)
        self.button_color12.clicked.connect(self.clickColor12)
        # 디폴트 색상 1번
        self.clickColor1()

    # 컬러 버튼 클릭 시 발생하는 이벤트 1~12번 색상
    def clickColor1(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[0][0], self.colorMap[0][1], self.colorMap[0][2]))
        self.colorNow = 0

    def clickColor2(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[1][0], self.colorMap[1][1], self.colorMap[1][2]))
        self.colorNow = 1

    def clickColor3(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[2][0], self.colorMap[2][1], self.colorMap[2][2]))
        self.colorNow = 2

    def clickColor4(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[3][0], self.colorMap[3][1], self.colorMap[3][2]))
        self.colorNow = 3

    def clickColor5(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[4][0], self.colorMap[4][1], self.colorMap[4][2]))
        self.colorNow = 4

    def clickColor6(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[5][0], self.colorMap[5][1], self.colorMap[5][2]))
        self.colorNow = 5

    def clickColor7(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[6][0], self.colorMap[6][1], self.colorMap[6][2]))
        self.colorNow = 6

    def clickColor8(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[7][0], self.colorMap[7][1], self.colorMap[7][2]))
        self.colorNow = 7

    def clickColor9(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[8][0], self.colorMap[8][1], self.colorMap[8][2]))
        self.colorNow = 8

    def clickColor10(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[9][0], self.colorMap[9][1], self.colorMap[9][2]))
        self.colorNow = 9

    def clickColor11(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[10][0], self.colorMap[10][1], self.colorMap[10][2]))
        self.colorNow = 10

    def clickColor12(self):
        self.button_colorNow.setStyleSheet("background-color:rgb({},{},{})"
                                           .format(self.colorMap[11][0], self.colorMap[11][1], self.colorMap[11][2]))
        self.colorNow = 11

    # 다이얼 동기화 함수
    def updateDial(self):
        self.dial_img.setValue(self.currentNum)

    # 다이얼 이벤트 함수
    def dialMoved(self):
        if self.imgCount is 0:
            return
        value = self.dial_img.value()
        self.currentNum = value
        if value is self.imgCount - 1:
            self.nextNum = self.imgCount - 1
        else:
            self.nextNum = value + 1
        if value is 0:
            self.lastNum = 0
        else:
            self.lastNum = value - 1
        self.loadAllImage()

    # 다이얼 초기화 함수
    def initDial(self):
        self.dial_img.setMinimum(0)
        self.dial_img.setMaximum(self.imgCount - 1)

    # 이미지 경로 지정 버튼 함수
    def loadImagePath(self):
        # 파일 다이얼로그로부터 경로 추출
        self.imagePath = QFileDialog.getExistingDirectory()
        if self.imagePath.__len__() is 0:
            return
        img_list = []
        for file in os.listdir(self.imagePath):
            img_list.append(os.path.basename(file))
        # 이미지 파일 리스트에 추가
        self.listWidget_img.clear()
        self.listWidget_img.addItems(img_list)
        # 이미지 갯수 저장
        self.imgCount = self.listWidget_img.count()
        # 다이얼 초기화
        self.initDial()

        # 마스크 파일 리스트 갱신
        if self.maskPath is not None:
            self.updateMaskList()

    # 마스크 경로 지정 버튼 함수
    def loadMaskPath(self):
        self.maskPath = QFileDialog.getExistingDirectory()
        if self.maskPath.__len__() is 0:
            return
        # 마스크 파일 리스트 갱신
        if self.maskPath is not None:
            self.updateMaskList()

    # 마스크 파일 리스트 업데이트
    def updateMaskList(self):
        if self.imagePath is None:
            # 이미지 경로 설정이 안되있는 경우 오류 메시지
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("이미지 경로를 지정해주세요")
            msg.setWindowTitle("경고")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            # 이미지 파일리스트와 이름이 같은 게 존재할 경우 추가
            self.listWidget_mask.clear()
            for i in range(self.listWidget_img.count()):
                img = self.listWidget_img.item(i).text()
                mask = self.maskPath + '/' + img
                if os.path.exists(mask):
                    self.listWidget_mask.addItem(img)
        # 모든 이미지 출력
        self.loadAllImage()
        # LCD 업데이트
        self.updateLCD()

    # LCD 숫자 변경 및 프로그레스바 업데이트
    def updateLCD(self):
        # 작업량이 변경될 때마다 LCD 숫자를 변경
        done = self.listWidget_mask.count()
        do = self.imgCount - done
        self.lcdNumber_done.display(done)
        self.lcdNumber_do.display(do)
        # 프로그레스바 업데이트
        try:
            self.progressBar_work.setValue(int(done * 100 / self.imgCount))
        except ZeroDivisionError:
            self.progressBar_work.setValue(0)

    # 모든 이미지를 출력하는 함수
    def loadAllImage(self):
        # 현재 이미지 칸에 이미지 출력
        self.loadCurrentImage()
        # 다음 이미지 칸에 이미지 출력
        self.loadNextImage()
        # 이전 이미지 칸에 이미지 출력
        self.loadLastImage()
        # 세그멘테이션 이미지 출력
        self.loadSegImage()
        # 혼합 이미지 출력
        self.loadMixImage()
        self.isModified = False

    # 이전 이미지로 바로가기 버튼 이벤트
    def clickButtonLast(self):
        if self.nextNum > 1:
            self.nextNum -= 1
        if self.currentNum > 0:
            self.currentNum -= 1
        if self.lastNum > 0:
            self.lastNum -= 1
        if self.isModified is True and self.autoSave is True:
            self.clickButtonSave()
        self.updateDial()
        self.loadAllImage()

    # 다음 이미지로 바로가기 버튼 이벤트
    def clickButtonNext(self):
        if self.nextNum < self.imgCount - 1:
            self.nextNum += 1
        if self.currentNum < self.imgCount - 1:
            self.currentNum += 1
        if self.lastNum < self.imgCount - 1:
            self.lastNum += 1
        if self.isModified is True and self.autoSave is True:
            self.clickButtonSave()
        self.updateDial()
        self.loadAllImage()

    # 이미지 리스트로부터 현재 이미지 불러오기
    def loadCurrentImage(self):
        if self.listWidget_img.count() is 0:
            return
        try:
            img_name = self.listWidget_img.item(self.currentNum).text()
            path = self.imagePath + '/' + img_name
            if os.path.exists(path):
                self.origin = self.imread(path)
                self.origin = cv2.cvtColor(self.origin, cv2.COLOR_BGR2RGB)
                self.segmentation = np.zeros_like(self.origin)
                self.seed = np.zeros(self.origin.shape[0:2], dtype='int32')
                self.paintedCanvas = np.copy(self.origin)
                self.updateCurrentImage()
                self.updateCurrentImagePanel(img_name)
            else:
                pix_map = QPixmap('no_image.jpg')
                pix_map = pix_map.scaled(self.label_canvasImg.size(), Qt.IgnoreAspectRatio)
                self.label_canvasImg.setPixmap(pix_map)
        except AttributeError:
            pass

    # 현재 이미지 갱신
    def updateCurrentImage(self):
        size = self.paintedCanvas.shape
        qim = QImage(self.paintedCanvas, size[1], size[0], QImage.Format_RGB888)
        pix_map = QPixmap.fromImage(qim)
        pix_map = pix_map.scaled(self.label_canvasImg.size(), Qt.IgnoreAspectRatio)
        self.label_canvasImg.setPixmap(pix_map)

    # 세그멘테이션 이미지 갱신
    def updateSegmentationImage(self):
        seedCopy = np.copy(self.seed)
        markers = cv2.watershed(self.origin, seedCopy)
        for i in range(self.colorMap.__len__()):
            self.segmentation[markers == i + 1] = self.colorMap[i]
        size = self.segmentation.shape
        qim = QImage(self.segmentation, size[1], size[0], QImage.Format_RGB888)
        pix_map = QPixmap.fromImage(qim)
        pix_map = pix_map.scaled(self.label_segImg.size(), Qt.IgnoreAspectRatio)
        self.label_segImg.setPixmap(pix_map)
        self.updateMixImage()
        self.isModified = True

    # 이전 이미지 불러오기
    def loadLastImage(self):
        if self.listWidget_img.count() is 0:
            return
        try:
            img_name = self.listWidget_img.item(self.lastNum).text()
            path = self.imagePath + '/' + img_name
            if os.path.exists(path):
                pix_map = QPixmap(path)
                pix_map = pix_map.scaled(self.label_lastImg.size(), Qt.IgnoreAspectRatio)
                self.label_lastImg.setPixmap(pix_map)
            else:
                pix_map = QPixmap('no_image.jpg')
                pix_map = pix_map.scaled(self.label_lastImg.size(), Qt.IgnoreAspectRatio)
                self.label_lastImg.setPixmap(pix_map)
        except AttributeError:
            pass

    # 다음 이미지 불러오기
    def loadNextImage(self):
        if self.listWidget_img.count() is 0:
            return
        try:
            img_name = self.listWidget_img.item(self.nextNum).text()
            path = self.imagePath + '/' + img_name
            if os.path.exists(path):
                pix_map = QPixmap(path)
                pix_map = pix_map.scaled(self.label_nextImg.size(), Qt.IgnoreAspectRatio)
                self.label_nextImg.setPixmap(pix_map)
            else:
                pix_map = QPixmap('no_image.jpg')
                pix_map = pix_map.scaled(self.label_nextImg.size(), Qt.IgnoreAspectRatio)
                self.label_nextImg.setPixmap(pix_map)
        except AttributeError:
            pass

    # 세그멘테이션 이미지 불러오기
    def loadSegImage(self):
        if self.listWidget_mask.count() is 0:
            return
        try:
            img_name = self.listWidget_img.item(self.currentNum).text()
            path = self.maskPath + '/' + img_name
            if os.path.exists(path):
                pix_map = QPixmap(path)
                pix_map = pix_map.scaled(self.label_segImg.size(), Qt.IgnoreAspectRatio)
                self.label_segImg.setPixmap(pix_map)
                self.updateCurrentMaskPanel(img_name)
            else:
                pix_map = QPixmap('no_image.jpg')
                pix_map = pix_map.scaled(self.label_segImg.size(), Qt.IgnoreAspectRatio)
                self.label_segImg.setPixmap(pix_map)
                self.updateCurrentMaskPanel()
        except AttributeError:
            pass

    # 한글 경로 처리 (읽기) - OpenCV가 한글 경로 처리를 못해서 따로 처리
    def imread(self, filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
        try:
            n = np.fromfile(filename, dtype)
            img = cv2.imdecode(n, flags)
            return img
        except Exception as e:
            print(e)
            return None

    # 한글 경로 처리 (쓰기) - OpenCV가 한글 경로 처리를 못해서 따로 처리
    def imwrite(self, filename, img, params=None):
        try:
            ext = os.path.splitext(filename)[1]
            result, n = cv2.imencode(ext, img, params)

            if result:
                with open(filename, mode='w+b') as f:
                    n.tofile(f)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False

    # 혼합 이미지 불러오기
    def loadMixImage(self):
        if self.listWidget_mask.count() is 0:
            return
        try:
            img_name = self.listWidget_img.item(self.currentNum).text()
        except AttributeError:
            return
        img_path = self.imagePath + '/' + img_name
        mask_path = self.maskPath + '/' + img_name

        if os.path.exists(mask_path) and os.path.exists(img_path):
            img = self.imread(img_path)
            mask = self.imread(mask_path)
            mix = cv2.addWeighted(img, 0.5, mask, 0.5, 0)
            cvt_mix = cv2.cvtColor(mix, cv2.COLOR_BGR2RGB)
            h, w, c = cvt_mix.shape
            qImg = QImage(cvt_mix.data, w, h, w * c, QImage.Format_RGB888)
            pix_map = QPixmap.fromImage(qImg)
            pix_map = pix_map.scaled(self.label_mixImg.size(), Qt.IgnoreAspectRatio)
            self.label_mixImg.setPixmap(pix_map)
        else:
            # 마스크 이미지가 없는 경우에 대한 예외처리
            pix_map = QPixmap('no_image.jpg')
            pix_map = pix_map.scaled(self.label_mixImg.size(), Qt.IgnoreAspectRatio)
            self.label_mixImg.setPixmap(pix_map)

    # 혼합 이미지 갱신
    def updateMixImage(self):
        mix = cv2.addWeighted(self.origin, 0.5, self.segmentation, 0.5, 0)
        size = self.segmentation.shape
        qim = QImage(mix, size[1], size[0], QImage.Format_RGB888)
        pix_map = QPixmap.fromImage(qim)
        pix_map = pix_map.scaled(self.label_mixImg.size(), Qt.IgnoreAspectRatio)
        self.label_mixImg.setPixmap(pix_map)

    # 현재 이미지 명 업데이트
    def updateCurrentImagePanel(self, name=""):
        self.lineEdit_img.setText(name)

    # 현재 마스크 명 없데이트
    def updateCurrentMaskPanel(self, name=""):
        self.lineEdit_mask.setText(name)


def main():
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()


if __name__ == '__main__':
    main()
