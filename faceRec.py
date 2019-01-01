import sys
from PyQt5.QtWidgets import (QWidget, QMessageBox, QLabel, QDialog, QGridLayout,QVBoxLayout,QHBoxLayout,QInputDialog,
    QApplication, QPushButton, QDesktopWidget, QLineEdit, QTabWidget,QTextEdit,QLineEdit)
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPalette, QBrush
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtCore
import pymysql
import uuid
import ctypes
from PIL import Image,ImageDraw,ImageFont

import numpy as np
import os
import cv2
import time
import datetime

import requests
from json import JSONDecoder
import datetime
import json

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
key ="atJbXy90W7ChxK1P0vOLcz4Qq6Q5PkDs"
secret ="GLWNjjnVyUTiWUysugalf-kjRdcfiTZU"

# 换成自己创建的人脸集合
faceset_token = '80017334f525d986445aeb794a459472'
#时间模块、
d1 = time.localtime(time.time())

year = d1.tm_year
month = d1.tm_mon
day = d1.tm_mday

#规定九点后迟到
d2 = datetime.datetime(year,month,day,9).timetuple()

#获取当前时间
def isNotLate():
	lon = time.mktime(d2)
	nowTime = time.time()
	if (nowTime - lon) > 0:
		return 0
	else:
		return 1



def putTextCN(img, string, position, color):
	#1 cv2转PIL
	cv2_im = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # cv2和PIL中颜色的hex码的储存顺序不同
	pil_im = Image.fromarray(cv2_im)
	# PIL图片上打印中文
	#2 括号中为需要打印的canvas，这里就是在图片上直接打印
	draw = ImageDraw.Draw(pil_im) 
	# 第一个参数为字体文件路径，第二个为字体大
	font = ImageFont.truetype("simhei.ttf", 20, encoding="utf-8")
	# 第一个参数为打印的坐标，第二个为打印的文本，第三个为字体颜色，第四个为字体
	draw.text(position,  string, color, font=font) 
	#3 PIL图片转cv2
	cv2_text_im = cv2.cvtColor(np.array(pil_im), cv2.COLOR_RGB2BGR)
	return cv2_text_im

def getConnection():
    db = pymysql.connect("localhost","root","root","faceset")
    return db


#  界面类，继承基类 QWidget-空白界面

class addStuInfo(QWidget):
     
    def __init__(self):
        super().__init__()
         
        self.initUI()
              
    def initUI(self):
        #标题
        self.label = QLabel(self)
        self.label.setText("<h2>请按照规定录入你的相关信息</h2>")
        self.label.setFixedWidth(300)
        self.label.setFixedHeight(30)
        self.label.move(170,40)
        self.label.show()
        #button
        self.submit = QPushButton('提交',self)
        #初始化标签
        self.info = ["学号","姓名","性别","年龄"]
        #用于存放对应的edit地址
        self.editObjects = {}
        #遍历生成标签界面
        for i in range(0,4):
            self.label = QLabel(self) 
            self.label.setText("<h3>"+self.info[i]+"</h3>")
            self.label.setFixedWidth(40)   # 固定大小
            self.label.setFixedHeight(30)
            self.label.move(150,90+50*i)
            self.label.show()

            self.qLineEdit = QLineEdit(self) 
            self.qLineEdit.setFixedWidth(200)   # 固定大小
            self.qLineEdit.setFixedHeight(25)
            self.qLineEdit.move(190,95+50*i)
            self.qLineEdit.show()

            self.editObjects.update({self.info[i]:self.qLineEdit})

        # print(self.editObjects)
        self.submit.clicked.connect(self.submitInfo)
        self.submit.move(310,300)

    #获取值
    def getEditValue(self):
        self.card_number = self.editObjects['学号'].text()
        self.name = self.editObjects['姓名'].text()
        self.sex = self.editObjects['性别'].text()
        self.age = self.editObjects['年龄'].text()

    #刷新
    def reflash(self):
        for self.inf in self.info:
            self.editObjects[self.inf].setText("")

    #提交
    def submitInfo(self):
        self.getEditValue()
        self.sql_insert = "insert into student_info(card_number,name,sex,age) values(%s,%s,%s,%s)"
        self.db = getConnection()
        self.cursor = self.db.cursor()
        try:
            self.cursor.execute(self.sql_insert,(self.card_number,self.name,self.sex,int(self.age)))
            self.db.commit()
            ctypes.windll.user32.MessageBoxA(0,u"提交成功".encode('gb2312'),u' 信息'.encode('gb2312'),0)
            self.reflash()
        except Exception as e:
            ctypes.windll.user32.MessageBoxA(0,u"提交失败".encode('gb2312'),u' 信息'.encode('gb2312'),0)
            print(e)
        finally:
            self.db.close()
        

 

class FaceDetect(QWidget):
    # 构造函数 
    def __init__(self):
        # 调用父类的构造函数，完成widget初始化
        super().__init__()
         
        self.initUI()
    # 自定义的界面布局，并且实现信号和槽的处理（人机交互）         
    def initUI(self):
        # 显示标签--显示我们采集的图片
        self.label = QLabel(self)  
        self.label.setFixedWidth(640)   # 固定大小
        self.label.setFixedHeight(480)  
        self.label.move(0,0)  # 位置
        # 初始背景
        self.pixMap = QPixmap("background.png").scaled(self.label.width(),self.label.height()) 
        self.label.setPixmap(self.pixMap)
        #  显示lable
        self.label.show()
        # 三个按钮 -打开摄像头/关闭摄像头/拍照--需要进行布局
        self.startButton = QPushButton('start', self)
        self.startButton.move(530, 25)
        self.stopButton = QPushButton('stop', self)
        self.stopButton.move(530, 75)
        self.capPictureButton = QPushButton('capPicture', self)
        self.capPictureButton.move(530, 125)
        # 设置按钮的信号和槽函数           self.start类内成员函数
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.capPictureButton.clicked.connect(self.cap)
        # 摄像头
        self.cap = None
        self.timer = QTimer()   # 定时器
        #   闹钟--timeout信号（闹铃）
        self.timer.timeout.connect(self.detectface)
        
        

    def start(self,event):
        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        #  启动定时器
        self.timer.start()
        #  间隔33毫秒--每次闹铃--调用  detectface进行人脸检测
        self.timer.setInterval(33)

    def stop(self):
        # 关闭摄像头
        self.cap.release()
        #  关闭定时器
        self.timer.stop()

    def showPONInputDialog(self):
        opN,okPressed = QInputDialog.getText(self,"录入学号","请输入你的学号:",QLineEdit.Normal, "")
        if okPressed and opN.strip():
            print('PON:' + opN)
            carNumber = opN
            return carNumber
        else:
            QMessageBox.critical(self,"错误","请输入学号,点击OK进入系统!")
            


    def cap(self,event):
        # 拍照，保存
        ret, img = self.cap.read()
        if ret != None:
        	#s随机生成32位字符串
            self.pic =  uuid.uuid4()
            #图片保存路径
            self.picName = "E:\\pythonWorkplace\\project\\pic\\"+str(self.pic)+".jpg"
            ctypes.windll.user32.MessageBoxA(0,u"保存图片	成功".encode('gb2312'),u' 信息'.encode('gb2312'),0)
            #写入img
            cv2.imwrite(self.picName, img)
            self.carNumber = self.showPONInputDialog()
            #得到face_token
            try:
            	#捕捉异常 否则则会发生face_token 无法获取的情况。则导致接下发生空指针异常。
                self.face_token = self.request_detect(self.picName)
            except Exception as e:
                ctypes.windll.user32.MessageBoxA(0,u"未识别到人脸，请重新拍照".encode('gb2312'),u' 信息'.encode('gb2312'),0)
                return
            
            
            print(self.face_token)
            #数据库
            #更新表 添入picPath and face——token
            self.sql_update = "update student_info set pic_path = %s ,face_token = %s where card_number = %s"
            self.db = getConnection()
            self.cursor = self.db.cursor()#游标
            try:
            	self.cursor.execute(self.sql_update,(self.picName,self.face_token,self.carNumber))
            	self.db.commit()
            except Exception as e:
            	print("sqlException")
            	self.db.rollback()
            finally:
            	self.db.close()
            
           #print(stuInfo)
            self.cap.release()
            #  关闭定时器
            self.timer.stop()

          #  Obj = "E:\\pythonWorkplace\\project\\pic"
           # os.startfile(str(Obj)
    # 使用opencv进行人脸检测  
    def  request_detect(self,picName):
        self.filepath = picName
        self.files = {"image_file": open(self.filepath, "rb")}
        self.data_detect = {"api_key": key, "api_secret": secret, "return_landmark": "1"}
        self.response = requests.post("https://api-cn.faceplusplus.com/facepp/v3/detect", data=self.data_detect, files=self.files)
        self.req_con = self.response.content.decode('utf-8')
        self.req_dict = JSONDecoder().decode(self.req_con)
        self.face_token = self.req_dict['faces'][0]['face_token']
        self.data_addface = {"api_key": key, "api_secret": secret, "faceset_token": faceset_token,"face_tokens":self.face_token}
        requests.post("https://api-cn.faceplusplus.com/facepp/v3/faceset/addface", data=self.data_addface)      
        #print(self.face_token)
        return self.face_token
    def detectface(self):
        
        if (self.cap.isOpened()):
            # get a frame
            ret, img = self.cap.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
                self.face = cv2.resize(img[y:y+h, x:x+w],(224, 224), interpolation=cv2.INTER_CUBIC)
            height, width, bytesPerComponent = img.shape
            bytesPerLine = bytesPerComponent * width
            # 变换彩色空间顺序
            cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
            # 转为QImage对象是，在label中显示图像
            self.image = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(self.image).scaled(self.label.width(),self.label.height()))




class FaceRec(QWidget):
     
    def __init__(self):
        super().__init__()
         
        self.initUI()
              
    def initUI(self):
        # 显示标签--显示我们采集的图片
        self.label = QLabel(self)  
        self.label.setFixedWidth(640)   # 固定大小
        self.label.setFixedHeight(480)  
        self.label.move(0,0)  # 位置
        # 初始背景
        self.pixMap = QPixmap("background2.png").scaled(self.label.width(),self.label.height()) 
        self.label.setPixmap(self.pixMap)
        #  显示lable
        self.label.show()
        # 三个按钮 -打开摄像头/关闭摄像头/拍照--需要进行布局
        self.startButton = QPushButton('start', self)
        self.startButton.move(530, 25)
        self.stopButton = QPushButton('stop', self)
        self.stopButton.move(530, 75)
        self.searchButton = QPushButton('search', self)
        self.searchButton.move(530, 125)
        # 设置按钮的信号和槽函数           self.start类内成员函数
        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.searchButton.clicked.connect(self.cap)
        # 摄像头
        self.cap = None
        self.timer = QTimer()   # 定时器
        #   闹钟--timeout信号（闹铃）
        self.timer.timeout.connect(self.detectface)

    def cap(self,event):
        # 拍照，保存
        ret, img = self.cap.read()
        if ret != None:
            self.pic =  uuid.uuid4()
            self.picName = "E:\\pythonWorkplace\\project\\picSearch\\"+str(self.pic)+".jpg"
            #ctypes.windll.user32.MessageBoxA(0,u"保存图片成功".encode('gb2312'),u' 信息'.encode('gb2312'),0)
            cv2.imwrite(self.picName, img)
            self.face_token = self.search()
            print(self.face_token)
            self.realName = self.getFaceTokens(self.face_token)
            self.isNotLate = isNotLate()
            #更新数据库的状态
            self.updateStatus()
            if self.isNotLate == 1:
            	self.status = "未迟到"
            else:
            	self.status = "迟到"
            if self.realName != "":
                self.stu_info = "此人名字是："+self.realName+",状态:"+self.status
                img = putTextCN(img,self.stu_info,(80,100),(0,0,255))
                cv2.imshow("res",img)
            self.cap.release()
             #  关闭定时器
            self.timer.stop()
    def updateStatus(self):
    	self.sql_updateStatus = "update student_info set status = %s,late_count = late_count +1 where name = %s"
    	self.db = getConnection()
    	self.cursor = self.db.cursor()
    	try:
    	    self.cursor.execute(self.sql_updateStatus,(self.isNotLate,self.realName))
    	    self.db.commit()
    	except Exception as e:
    	    raise
    	finally:
    	    self.db.close()
    def getFaceTokens(self,face_token):
    	self.sql_select = "select name from student_info where face_token = %s"
    	self.db = getConnection()
    	self.cursor = self.db.cursor()
    	self.realName = ""
    	try:
    		self.cursor.execute(self.sql_select,(face_token))
    		self.results = self.cursor.fetchall()
    		if len(self.results) == 0:
    			ctypes.windll.user32.MessageBoxA(0,u"查询不到此人".encode('gb2312'),u' 信息'.encode('gb2312'),0)
    		else:
    			self.realName = self.results[0][0]
    			print(self.realName)
    	except Exception as e:
    		raise
    	finally:
    		self.db.close()
    	return self.realName
    

    def search(self):
            self.filePath = self.picName
            self.files = {"image_file": open(self.filePath, "rb")}
            self.data_search = {"api_key": key, "api_secret": secret, "faceset_token": faceset_token}
            self.response = requests.post("https://api-cn.faceplusplus.com/facepp/v3/search", data=self.data_search, files=self.files)
            self.req_con = self.response.content.decode('utf-8')
            self.req_dict = JSONDecoder().decode(self.req_con)
            self.face_token = self.req_dict['results'][0]['face_token']
            return self.face_token

    def start(self,event):
        # 打开摄像头
        self.cap = cv2.VideoCapture(0)
        #  启动定时器
        self.timer.start()
        #  间隔33毫秒--每次闹铃--调用  detectface进行人脸检测
        self.timer.setInterval(33)
    def stop(self):
        # 关闭摄像头
        self.cap.release()
        #  关闭定时器
        self.timer.stop()

    def detectface(self):
    
        if (self.cap.isOpened()):
            # get a frame
            ret, img = self.cap.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = img[y:y+h, x:x+w]
                self.face = cv2.resize(img[y:y+h, x:x+w],(224, 224), interpolation=cv2.INTER_CUBIC)
            height, width, bytesPerComponent = img.shape
            bytesPerLine = bytesPerComponent * width
            # 变换彩色空间顺序
            cv2.cvtColor(img, cv2.COLOR_BGR2RGB, img)
            # 转为QImage对象是，在label中显示图像
            self.image = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(self.image).scaled(self.label.width(),self.label.height()))

    

class Database(QWidget):

    def __init__(self):
        super().__init__()
         
        self.initUI()
              
    def initUI(self):
    	self.selcetQline = QLineEdit(self)
    	self.selcetQline.setFixedWidth(150)
    	self.selcetQline.setFixedHeight(30)
    	self.selcetQline.move(160,10)
    	self.selcetQline.show()
    	self.submitButton = QPushButton('提交', self)
    	self.submitButton.move(350, 15)
    	self.submitButton.clicked.connect(self.getData)

    def getData(self):
        self.db = getConnection()
        self.cursor = self.db.cursor()
        self.sql_select = "select *from student_info where card_number = %s"   
        self.cursor.execute(self.sql_select,self.selcetQline.text())
        self.results = self.cursor.fetchall()
        self.sql_columnNames = "select COLUMN_NAME from information_schema.COLUMNS where table_name = 'student_info'"
        self.cursor.execute(self.sql_columnNames)  
        self.columnNames = self.cursor.fetchall()
        i = 1
        #存放内容
        self.nameDic={}
        print(len(self.results))
        #初始化key值为1 j++ 
        self.j = 1
        if len(self.results)== 0:
            ctypes.windll.user32.MessageBoxA(0,u"请输入正确的学号".encode('gb2312'),u' 信息'.encode('gb2312'),0)
            return
        for k in range(0,len(self.results)):
           # print(k)
            self.info=[]
            for s in range(0,len(self.results[k])):
                self.info.append(self.results[k][s])
            self.nameDic.update({self.j:self.info})
            self.j = self.j +1
        print(self.nameDic)
        
        for columnName in self.columnNames:
           
            self.label = QLabel(self) 
            self.label.setFixedWidth(80)   # 固定大小
            self.label.setFixedHeight(30)

            self.qLineEdit = QLineEdit(self) 
            self.qLineEdit.setFixedWidth(500)   # 固定大小
            self.qLineEdit.setFixedHeight(30)

            self.label.setText(str(columnName[0]))
    
            print(columnName[0])
            print(self.nameDic[1][i-1])
            self.qLineEdit.setText(str(self.nameDic[1][i-1]))
            self.label.move(10,30+30*i)
            self.label.show()
            self.qLineEdit.move(130,30+30*i)
            self.qLineEdit.show()
        
            i = i +1;

            

class TabWidget(QTabWidget):

    def __init__(self, parent=None):
        super(TabWidget, self).__init__(parent)
        # 标题名称
        self.setWindowTitle('Face Recognition')
        #  图标                   缺图片
        self.setWindowIcon(QIcon('add.png'))
        #  大小
        self.resize(640, 480)
        #  居中
        self.center()
        # 创建一个界面类对象
        
        self.addStuInfo = addStuInfo()
        self.addTab(self.addStuInfo, QIcon('add.png'), "信息录入")

        self.FaceDetect = FaceDetect()  #人脸检测类 opencv
        # 添加到tabwidget
        self.addTab(self.FaceDetect, QIcon('detect.png'), "人脸检测")


        self.FaceRec = FaceRec()
        self.addTab(self.FaceRec, QIcon('search.png'), "人脸识别")

        self.Database = Database()
        self.addTab(self.Database, QIcon('database.png'), "数据库")
   
        palette=QPalette()     
        icon=QPixmap('background.png').scaled(1024,768)
        palette.setBrush(self.backgroundRole(), QBrush(icon)) #添加背景图片
        self.setPalette(palette)


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
         
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)
 
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore() 

#  main函数
if __name__ == '__main__':
    # 创建应用程序 
    app = QApplication(sys.argv)
    #  标签页
    t = TabWidget()
    t.show()
    #ex = Example()
    # 进入事件循环
    sys.exit(app.exec_())