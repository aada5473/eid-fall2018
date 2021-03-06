from PyQt5 import QtCore, QtGui, QtWidgets
import Adafruit_DHT
import sys
import csv
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import dates
import threading
import boto3
import ast
from websocket import create_connection
import paho.mqtt.client as mqtt
import aiocoap
from aiocoap import *
import asyncio
import time

#Global declarations
templist = []
temphighlist = []
templowlist = []
tempavglist = []
humlist = []
humhighlist = []
humlowlist = []
humavglist = []
timestamplist = []
websockets_timelist = []
mqtt_time_init=[]
mqtt_timelist = []
coap_timelist = []
mqtt_time_end = []
data_list = []
mythread = []
fmtr = dates.DateFormatter("%H:%M:%S")
temp_unit = 'C'
temp = 0
temp_avg = 0
temp_low = 0
temp_high = 0
flag = 0
application = mqtt.Client()
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='RPi3-FIFO.fifo')

def multiprotocol():
    """
    Function to do multiprotocol test
    """
    global data_list, websockets_timelist, mqtt_time_init, mqtt_timelist, coap_timelist, mqtt_time_end
    
    ipaddress = "127.0.0.1"
    upload = 'upload_mqtt'
    download = 'download_mqtt'
    
    mywebsocket = create_connection("ws://" + ipaddress + ":8888/ws")
    for i in range(0,len(data_list)):
        start_web = time.time()
        mywebsocket.send(str(data_list[i]))
        result =  mywebsocket.recv()
        end_web = time.time()
        websockets_timelist.append(end_web - start_web)
        
    event_thread = threading.Event()
    mqtt_thread = threading.Thread(target=mqtt_server)
    mythread.append(mqtt_thread)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    time.sleep(1)
    for i in range(0,len(data_list)):
        print(i)
        mqtt_time_init.append(time.time())
        application.publish(upload, str(data_list[i]))
        application.subscribe(download)
        time.sleep(1)
     
    for i in range(0,len(mqtt_time_end)):
        mqtt_timelist.append(float(mqtt_time_end[i])-float(mqtt_time_init[i+(len(mqtt_time_init)-len(mqtt_time_end))]))
        
    for i in range(0,len(data_list)):
        start_coap = time.time()
        coap_client(i)
        end_coap = time.time()
        coap_timelist.append(end_coap - start_coap)
    
def time_plot():
    """
    Function to plot time comparisons
    """
    websocket_plot()
    mqtt_plot()
    coap_plot()
    fig2 = plt.figure()
    fig2.suptitle("Round trip time comparison for Websockets,mqtt and coap")
    plt.plot(websockets_timelist)
    plt.plot(mqtt_timelist)
    plt.plot(coap_timelist)
    plt.legend(['websockets','mqtt','coap'],loc='upper right')
    ax=plt.gca()
    plt.xlabel('Number of messages')
    plt.ylabel('Time taken for round trip')
    plt.show()
    total_ws = sum(websockets_timelist)
    total_mqtt= sum(mqtt_timelist)
    total_coap = sum(coap_timelist)
    print('Total time for websockets')
    print(total_ws)
    print('Total time for mqtt')
    print(total_mqtt)
    print('Total time for coap')
    print(total_coap)

def websocket_plot():
    """
    Function to plot websocket time comparisons
    """
    fig2 = plt.figure()
    fig2.suptitle("Round trip time comparison for Websockets")
    plt.plot(websockets_timelist)
    plt.legend(['websockets'],loc='upper right')
    ax=plt.gca()
    plt.xlabel('Number of messages')
    plt.ylabel('Time taken for round trip')
    plt.show()

def mqtt_plot():
    """
    Function to plot mqtt time comparisons
    """
    fig2 = plt.figure()
    fig2.suptitle("Round trip time comparison for mqtt")
    plt.plot(mqtt_timelist)
    plt.legend(['mqtt'],loc='upper right')
    ax=plt.gca()
    plt.xlabel('Number of messages')
    plt.ylabel('Time taken for round trip')
    plt.show()

def coap_plot():
    """
    Function to plot coap time comparisons
    """
    fig2 = plt.figure()
    fig2.suptitle("Round trip time comparison for coap")
    plt.plot(coap_timelist)
    plt.legend(['coap'],loc='upper right')
    ax=plt.gca()
    plt.xlabel('Number of messages')
    plt.ylabel('Time taken for round trip')
    plt.show()
    
def mqtt_server():
    """
    Function for mqtt client
    """
    application.on_connect = on_connect
    application.on_message = on_message
    application.connect("iot.eclipse.org",1883,60)
    application.loop_forever()

def on_connect(application, userdata, flags, rc):
    print('mqtt connect')

def on_message(application, userdata, msg):
    global mqtt_time_end
    mqtt_time_end.append(time.time())

def coap_client(i):
    """
    Function for coap client
    """
    global data_list
    coap_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(coap_loop)
    coap_loop = asyncio.get_event_loop()
    coap_loop.run_until_complete(coap_sndrcv(str(data_list[i])))
    return 0
    
async def coap_sndrcv(data):
        context = await aiocoap.Context.create_client_context()
        request = aiocoap.Message(code=PUT, payload=bytes(data, 'utf-8'))
        request.opt.uri_host = "127.0.0.1"
        request.opt.uri_path = ("other", "block")
        response = await context.request(request).response

def plot():
    """
    Function to plot temp and humidity values
    """
    global flag,queue
    global templist, temphighlist, templowlist, tempavglist, humlist, humhighlist, humlowlist, humavglist, timestamplist
    
    fig = plt.figure()
    fig.suptitle('Obtained Temperature and Humidity values' + str(flag))
    plt.subplot(2,1,1)
    plt.plot(timestamplist,templist)
    plt.plot(timestamplist,temphighlist)
    plt.plot(timestamplist,templowlist)
    plt.plot(timestamplist,tempavglist)
    plt.legend(['Current','Maximum','Minimum','Average'],loc='upper left')
    ax=plt.gca()
    ax.xaxis.set_major_formatter(fmtr)
    plt.xlabel('Timestamp  in hh:mm:ss')
    plt.ylabel('Temp in C')
    
    plt.subplot(2,1,2)
    plt.plot(timestamplist,humlist)
    plt.plot(timestamplist,humhighlist)
    plt.plot(timestamplist,humlowlist)
    plt.plot(timestamplist,humavglist)
    plt.legend(['Current','Maximum','Minimum','Average'],loc='upper left')
    ax=plt.gca()
    ax.xaxis.set_major_formatter(fmtr)
    plt.xlabel('Timestamp in hh:mm:ss')
    plt.ylabel('Humidity in %')
    
    plt.show()

def getval():
    """
    Function to get 30 data items from sqs
    """
    global flag,queue
    global templist, temphighlist, templowlist, tempavglist, humlist, humhighlist, humlowlist, humavglist, timestamplist
    global temp_unit,temp, temp_low, temp_high, temp_avg, hum, hum_low, hum_high, hum_avg, timenow_temp_low, timestamp_temp_high, timestamp_hum_low, timestamp_hum_high;

    for i in range(3):
        response = queue.receive_messages(QueueUrl='https://sqs.us-west-2.amazonaws.com/518741721169/RPi3-FIFO.fifo',MaxNumberOfMessages=10)
        for msg in response:
            flag = flag + 1
            m = ast.literal_eval(msg.body)
            humlist.append(float(m['hum_str']))
            humhighlist.append(float(m['hum_high_str']))
            humlowlist.append(float(m['hum_low_str']))
            humavglist.append(float(m['hum_avg_str']))
            timestamplist.append(datetime.strptime(m['timenow'],'%H:%M:%S'))
            templist.append(float(m['temp_str']))
            temphighlist.append(float(m['temp_high_str']))
            templowlist.append(float(m['temp_low_str']))
            tempavglist.append(float(m['temp_avg_str']))
            data_list.append((m['temp_str'],m['temp_high_str'],m['temp_low_str'],m['temp_avg_str'],m['hum_str'],m['hum_high_str'],m['hum_low_str'],m['hum_avg_str'],m['timenow']))
            msg.delete()

    
    if flag == 0:
        print('Queue Error')


    ui.curh.setText(m['hum_str'])
    ui.avgh.setText(m['hum_avg_str'])
    ui.lowh.setText(m['hum_low_str'])
    ui.highh.setText(m['hum_high_str'])
    
    temp = float(m['temp_str'])
    temp_avg = float(m['temp_avg_str'])
    temp_low = float(m['temp_low_str'])
    temp_high = float(m['temp_high_str'])
    
    update()
    
    ui.timelowtemp.setText(m['timenow_temp_low'])
    ui.timethigh.setText(m['timenow_temp_high'])
    ui.lowtime.setText(m['timenow_hum_low'])
    ui.timehumhigh.setText(m['timenow_hum_high'])
    ui.curhtime.setText(m['timenow'])
    ui.curttime.setText(m['timenow'])
    
    plot()
    flag = 0

def fahranheit_comp():
    """
    Function for changing into fahranheit
    """
    global temp, temp_low, temp_high, temp_avg, hum, hum_low, hum_high, hum_avg, timenow_temp_low, timenow_temp_high, timenow_hum_low, timenow_hum_high, temp_unit, ui, count;
    temp_unit = 'F'
    temp2= (temp*1.8) + 32
    temp_str = "{:.2f}".format(temp2)
    temp_avg2= (temp_avg*1.8) + 32
    temp_avg_str = "{:.2f}".format(temp_avg2)
    temp_low2= (temp_low*1.8) + 32
    temp_low_str = "{:.2f}".format(temp_low2)
    temp_high2= (temp_high*1.8) + 32
    temp_high_str = "{:.2f}".format(temp_high2)
    ui.lowtemp.setText(temp_low_str)
    ui.curtemp.setText(temp_str)
    ui.avgt.setText(temp_avg_str)
    ui.hightemp.setText(temp_high_str)

def celsius_comp():
    """
    Function for changing into celsius
    """
    global temp, temp_low, temp_high, temp_avg, hum, hum_low, hum_high, hum_avg, timenow_temp_low, timenow_temp_high, timenow_hum_low, timenow_hum_high, temp_unit, ui, count;
    temp_unit = 'C'
    temp_str = "{:.2f}".format(temp)
    temp_avg_str = "{:.2f}".format(temp_avg)
    temp_low_str = "{:.2f}".format(temp_low)
    temp_high_str = "{:.2f}".format(temp_high)
    ui.lowtemp.setText(temp_low_str)
    ui.curtemp.setText(temp_str)
    ui.avgt.setText(temp_avg_str)
    ui.hightemp.setText(temp_high_str)

def update():
    
    """function to update temperature, humidity depending on radio button selected"""
    
    global temp, temp_low, temp_high, temp_avg, hum, hum_low, hum_high, hum_avg, timenow_temp_low, timenow_temp_high, timenow_hum_low, timenow_hum_high, temp_unit, ui, count;

    if(temp_unit=='F'):
        temp2= (temp*1.8) + 32
        temp_str = "{:.2f}".format(temp2)
        temp_avg2= (temp_avg*1.8) + 32
        temp_avg_str = "{:.2f}".format(temp_avg2)
        temp_low2= (temp_low*1.8) + 32
        temp_low_str = "{:.2f}".format(temp_low2)
        temp_high2= (temp_high*1.8) + 32
        temp_high_str = "{:.2f}".format(temp_high2)
        ui.lowtemp.setText(temp_low_str)
        ui.curtemp.setText(temp_str)
        ui.avgt.setText(temp_avg_str)
        ui.hightemp.setText(temp_high_str)
    else:    
        temp_str = "{:.2f}".format(temp)
        temp_avg_str = "{:.2f}".format(temp_avg)
        temp_low_str = "{:.2f}".format(temp_low)
        temp_high_str = "{:.2f}".format(temp_high)
        ui.lowtemp.setText(temp_low_str)
        ui.curtemp.setText(temp_str)
        ui.avgt.setText(temp_avg_str)
        ui.hightemp.setText(temp_high_str)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(771, 724)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(230, -40, 361, 131))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(540, 160, 121, 21))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(110, 150, 91, 41))
        self.label_3.setObjectName("label_3")
        self.radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton.setGeometry(QtCore.QRect(120, 90, 118, 26))
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.radioButton_2 = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton_2.setGeometry(QtCore.QRect(20, 90, 118, 26))
        self.radioButton_2.setObjectName("radioButton_2")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(340, 400, 91, 41))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(340, 310, 91, 41))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(330, 230, 91, 41))
        self.label_6.setObjectName("label_6")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(330, 190, 91, 41))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(320, 260, 91, 41))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setGeometry(QtCore.QRect(20, 50, 141, 41))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setGeometry(QtCore.QRect(330, 430, 91, 41))
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(320, 340, 91, 41))
        self.label_11.setObjectName("label_11")
        self.avgh = QtWidgets.QLabel(self.centralwidget)
        self.avgh.setGeometry(QtCore.QRect(120, 190, 91, 41))
        self.avgh.setObjectName("avgh")
        self.curh = QtWidgets.QLabel(self.centralwidget)
        self.curh.setGeometry(QtCore.QRect(120, 230, 91, 41))
        self.curh.setObjectName("curh")
        self.curhtime = QtWidgets.QLabel(self.centralwidget)
        self.curhtime.setGeometry(QtCore.QRect(120, 260, 91, 41))
        self.curhtime.setObjectName("curhtime")
        self.lowh = QtWidgets.QLabel(self.centralwidget)
        self.lowh.setGeometry(QtCore.QRect(120, 320, 91, 41))
        self.lowh.setObjectName("lowh")
        self.timehumhigh = QtWidgets.QLabel(self.centralwidget)
        self.timehumhigh.setGeometry(QtCore.QRect(130, 430, 91, 41))
        self.timehumhigh.setObjectName("timehumhigh")
        self.highh = QtWidgets.QLabel(self.centralwidget)
        self.highh.setGeometry(QtCore.QRect(130, 400, 91, 41))
        self.highh.setObjectName("highh")
        self.lowtime = QtWidgets.QLabel(self.centralwidget)
        self.lowtime.setGeometry(QtCore.QRect(120, 350, 91, 41))
        self.lowtime.setObjectName("lowtime")
        self.avgt = QtWidgets.QLabel(self.centralwidget)
        self.avgt.setGeometry(QtCore.QRect(570, 190, 91, 41))
        self.avgt.setObjectName("avgt")
        self.curtemp = QtWidgets.QLabel(self.centralwidget)
        self.curtemp.setGeometry(QtCore.QRect(570, 230, 91, 41))
        self.curtemp.setObjectName("curtemp")
        self.curttime = QtWidgets.QLabel(self.centralwidget)
        self.curttime.setGeometry(QtCore.QRect(570, 260, 91, 41))
        self.curttime.setObjectName("curttime")
        self.lowtemp = QtWidgets.QLabel(self.centralwidget)
        self.lowtemp.setGeometry(QtCore.QRect(580, 310, 91, 41))
        self.lowtemp.setObjectName("lowtemp")
        self.timelowtemp = QtWidgets.QLabel(self.centralwidget)
        self.timelowtemp.setGeometry(QtCore.QRect(580, 340, 91, 41))
        self.timelowtemp.setObjectName("timelowtemp")
        self.hightemp = QtWidgets.QLabel(self.centralwidget)
        self.hightemp.setGeometry(QtCore.QRect(570, 400, 91, 41))
        self.hightemp.setObjectName("hightemp")
        self.timethigh = QtWidgets.QLabel(self.centralwidget)
        self.timethigh.setGeometry(QtCore.QRect(570, 430, 91, 41))
        self.timethigh.setObjectName("timethigh")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(320, 510, 101, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(240, 560, 281, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(320, 610, 101, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 771, 27))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Temperature and Humidity Application"))
        self.label_2.setText(_translate("MainWindow", "Temperature"))
        self.label_3.setText(_translate("MainWindow", "Humidity"))
        self.radioButton.setText(_translate("MainWindow", "Celsius"))
        self.radioButton_2.setText(_translate("MainWindow", "Faranheit"))
        self.label_4.setText(_translate("MainWindow", "Highest"))
        self.label_5.setText(_translate("MainWindow", "Lowest"))
        self.label_6.setText(_translate("MainWindow", "Current"))
        self.label_7.setText(_translate("MainWindow", "Average"))
        self.label_8.setText(_translate("MainWindow", "Timestamp"))
        self.label_9.setText(_translate("MainWindow", "Temperature unit"))
        self.label_10.setText(_translate("MainWindow", "Timestamp"))
        self.label_11.setText(_translate("MainWindow", "Timestamp"))
        self.avgh.setText(_translate("MainWindow", "Val"))
        self.curh.setText(_translate("MainWindow", "Val"))
        self.curhtime.setText(_translate("MainWindow", "Val"))
        self.lowh.setText(_translate("MainWindow", "Val"))
        self.timehumhigh.setText(_translate("MainWindow", "Val"))
        self.highh.setText(_translate("MainWindow", "Val"))
        self.lowtime.setText(_translate("MainWindow", "Val"))
        self.avgt.setText(_translate("MainWindow", "Val"))
        self.curtemp.setText(_translate("MainWindow", "Val"))
        self.curttime.setText(_translate("MainWindow", "Val"))
        self.lowtemp.setText(_translate("MainWindow", "Val"))
        self.timelowtemp.setText(_translate("MainWindow", "Val"))
        self.hightemp.setText(_translate("MainWindow", "Val"))
        self.timethigh.setText(_translate("MainWindow", "Val"))
        self.pushButton.setText(_translate("MainWindow", "Get values"))
        self.pushButton_2.setText(_translate("MainWindow", "Execute Multi-Protocol Test"))
        self.pushButton_3.setText(_translate("MainWindow", "Plot"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    ui.radioButton_2.clicked.connect(lambda:fahranheit_comp())
    ui.radioButton.clicked.connect(lambda:celsius_comp())
    ui.pushButton.clicked.connect(lambda:getval())
    ui.pushButton_2.clicked.connect(lambda:multiprotocol())
    ui.pushButton_3.clicked.connect(lambda:time_plot())
    sys.exit(app.exec_())
