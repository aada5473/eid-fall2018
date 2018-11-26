from PyQt5 import QtCore, QtGui, QtWidgets
import Adafruit_DHT
import sys
import csv
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import dates
import threading



templist=[]
humlist=[]
timestamplist=[]
temp_high =-40.0;
temp_low = 125.0;
hum_high = 0.0;
hum_low = 100.0;
temp_unit = 'C' 
count = 0

def Get_Param():
    """
    This function gets sensor data 
    """
    #Select sensor module and pin
    sensor_module = Adafruit_DHT.DHT22
    sensor_pin = 4
    data=[]
    temp_type_str = "C"
    global temp, temp_low, temp_high, temp_avg, hum, hum_low, hum_high, hum_avg, timenow_temp_low, timenow_temp_high, timenow_hum_low, timenow_hum_high, unit, ui, count;
    t_int = threading.Timer(5,Get_Param).start()

    #Read sensor data and format
    hum, temp = Adafruit_DHT.read_retry(sensor_module, sensor_pin)
    temp_avg = temp;
    hum_avg = hum;
    temp_low = temp;
    hum_low = hum;
    temp_high = temp;
    hum_high = hum;
    temp_str_csv = "{:.2f}".format(temp)
    temp_avg_str_csv = "{:.2f}".format(temp_avg)
    temp_low_str_csv = "{:.2f}".format(temp_low)
    temp_high_str_csv = "{:.2f}".format(temp_high)
    
    #Get current time
    timenow = datetime.now().strftime('%H:%M:%S')
    ui.curhtime.setText(timenow)
    ui.curttime.setText(timenow)
    timenow_temp_low = timenow;
    timenow_hum_low = timenow;
    timenow_temp_high = timenow;
    timenow_hum_high = timenow;
    
    humlist.append(hum)
    templist.append(temp)
    timestamplist.append(timenow)

    count = count + 1
    if(count>1): 
        timenow_temp_high, timenow_hum_high, temp_high, hum_high = high_comp()
        temp_avg, hum_avg = avg_comp()
        timenow_temp_low, timenow_hum_low, temp_low, hum_low = low_comp()
        
    
    if(temp_unit=='F' and temp!=None):
        temp= (temp*1.8) + 32
        temp_str = "{:.2f}".format(temp)
        temp_avg= (temp_avg*1.8) + 32
        temp_avg_str = "{:.2f}".format(temp_avg)
        temp_low= (temp_low*1.8) + 32
        temp_low_str = "{:.2f}".format(temp_low)
        temp_high= (temp_high*1.8) + 32
        temp_high_str = "{:.2f}".format(temp_high)
        temp_type_str = "F"
        
    if(temp==None):
        ui.curtemp.setText("N/A")
    else:
        temp_str = "{:.2f}".format(temp)
        temp_avg_str = "{:.2f}".format(temp_avg)
        temp_low_str = "{:.2f}".format(temp_low)
        temp_high_str = "{:.2f}".format(temp_high)
        ui.lowtemp.setText(temp_low_str)
        ui.curtemp.setText(temp_str)
        ui.avgt.setText(temp_avg_str)
        ui.hightemp.setText(temp_high_str)
   
    if(hum==None):
        ui.curh.setText("N/A")
    else:
        hum_str = "{:.2f}".format(hum)
        hum_avg_str = "{:.2f}".format(hum_avg)
        hum_low_str = "{:.2f}".format(hum_low)
        hum_high_str = "{:.2f}".format(hum_high)
        ui.curh.setText(hum_str)
        ui.avgh.setText(hum_avg_str)
        ui.lowh.setText(hum_low_str)
        ui.highh.setText(hum_high_str)
    
    ui.timelowtemp.setText(timenow_temp_low)
    ui.timethigh.setText(timenow_temp_high)
    ui.lowtime.setText(timenow_hum_low)
    ui.timehumhigh.setText(timenow_hum_high)

    data.append(timenow)
    data.append(temp_str)
    data.append(temp_low_str)
    data.append(timenow_temp_high)
    data.append(temp_avg_str)
    data.append(hum_str)
    data.append(hum_avg_str)
    data.append(timenow_temp_low)
    data.append(temp_high_str)
    data.append(timenow_hum_low)
    data.append(hum_low_str)
    data.append(timenow_hum_high)
    data.append(hum_high_str)

    with open('temp_hum_data.csv', 'w') as csvfile: #write data to CSV file
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(data)

def fahranheit_comp():
    """change units from degC to F"""
    global temp_unit
    temp_unit = 'F'
    Get_Param()

def celsius_comp():
    """change units from F to degC"""
    global temp_unit
    temp_unit = 'C'
    Get_Param()

def avg_comp():
    """function to calculate averages of temp and rh"""
    temp_total = 0.0; hum_total = 0.0;
    for i in range(0,len(timestamplist)):
        temp_total += templist[i]
        hum_total += humlist[i]
    temp_avg = temp_total/len(timestamplist)
    hum_avg = hum_total/len(timestamplist)
    return temp_avg, hum_avg

def low_comp():
    """function to calculate minimum values of temp and rh"""
    global temp_low, hum_low, timenow_temp_low, timenow_hum_low
    for i in range(0,len(timestamplist)):
        if(templist[i]<temp_low):
            temp_low = templist[i];
            timestamp_temp_low = timestamplist[i];
        if(humlist[i]<hum_low):
            hum_low = humlist[i];
            timenow_hum_low = timestamplist[i];
    return timenow_temp_low, timenow_hum_low, temp_low, hum_low

def high_comp():
    """function to calculate maximum values of temp and rh"""
    global temp_high, hum_high, timenow_temp_high, timenow_hum_high
    for i in range(0,len(timestamplist)):
        if(templist[i]>temp_high):
            temp_high = templist[i];
            timenow_temp_high = timestamplist[i];
        if(humlist[i]>hum_high):
            hum_high = humlist[i];
            timenow_hum_high = timestamplist[i];
    return timenow_temp_high, timenow_hum_high, temp_high, hum_high

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(771, 642)
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
        self.radioButton_2.setCheckable(True)
        self.radioButton_2.setChecked(False)
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


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    Get_Param()
    ui.radioButton_2.clicked.connect(lambda:fahranheit_comp())
    ui.radioButton.clicked.connect(lambda:celsius_comp())
    sys.exit(app.exec_())
