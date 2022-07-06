from concurrent.futures import thread
from PyQt5 import QtCore, QtGui, QtWidgets

import ui.Ui_111
import sys
import os
import psutil

class Scan_thread(QtCore.QThread):
    my_signal = QtCore.pyqtSignal(list)

    def __init__(self, disk_name, threshold):
        super().__init__()
        self.disk_name = disk_name
        self.threshold = threshold
    
    def run(self):
        d = {}
        for root, dirs, files in os.walk(self.disk_name + '\\'):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                except:
                    continue
                #print(file_path, file_size, threshold, disk_name, type(file_size), type(threshold))
                if file_size < self.threshold:
                    continue
                d[file_path] = file_size

        sort_list = sorted(d.items(), key=lambda x: x[1], reverse=True)
        self.my_signal.emit(sort_list)

class Logic(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = ui.Ui_111.Ui_MainWindow()
        self.ui.setupUi(self)

    #my logic

        disk_list = []
        for i in psutil.disk_partitions():
            disk_list.append(i[0][:-1])
        self.ui.comboBox_disk_name.addItems(disk_list)

        self.ui.lineEdit_threshold.setText('1')
        self.ui.lineEdit_threshold.setValidator(QtGui.QIntValidator(1, 1023))
        unit_list = ['GB', 'MB', 'KB']
        self.ui.comboBox_unit.addItems(unit_list)

        self.ui.pushButton.clicked.connect(self.start_scan)

        self.ui.treeView.setAlternatingRowColors(True)
    
    def start_scan(self):
        threshold = int(self.ui.lineEdit_threshold.text())
        if threshold < 1 or threshold > 1023:
            QtWidgets.QMessageBox.warning(self, '无效值', '门限值范围: 1 - 1023', QtWidgets.QMessageBox.Ok) 
            return
        
        self.ui.pushButton.setEnabled(False)
        self.start_loading()
        
        disk_name = self.ui.comboBox_disk_name.currentText()
        unit = self.ui.comboBox_unit.currentText()
        if unit == 'GB':
            threshold *= 1024 * 1024 * 1024
        elif unit == 'MB':
            threshold *= 1024 * 1024
        elif unit == 'KB':
            threshold *= 1024

        self.scan_thread = Scan_thread(disk_name, threshold)
        self.scan_thread.my_signal.connect(self.show_result)
        self.scan_thread.start()

    def show_result(self, sort_list):
        model = QtGui.QStandardItemModel()
        model.setHorizontalHeaderLabels(['文件路径', '文件大小'])  
        for l in sort_list:
            path = QtGui.QStandardItem(l[0])
            size = QtGui.QStandardItem(str(l[1]))
            model.appendRow([path, size])

        self.stop_loading()

        self.ui.pushButton.setEnabled(True)
        self.ui.treeView.setModel(model)



    def start_loading(self):
        self.gif = QtGui.QMovie('image/等待.gif')
        self.ui.label_3.setScaledContents(True)
        self.ui.label_3.setMovie(self.gif)
        self.gif.start()
    
    def stop_loading(self):
        self.gif.stop()
        self.ui.label_3.clear()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    logic = Logic()
    logic.show()

    sys.exit(app.exec_())