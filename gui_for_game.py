# Form implementation generated from reading ui file 'gui_for_game.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(363, 482)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.stackedWidget = QtWidgets.QStackedWidget(parent=self.centralwidget)
        self.stackedWidget.setEnabled(True)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page_0 = QtWidgets.QWidget()
        self.page_0.setObjectName("page_0")
        self.gridLayoutWidget = QtWidgets.QWidget(parent=self.page_0)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(0, 0, 341, 421))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.send_0 = QtWidgets.QPushButton(parent=self.gridLayoutWidget)
        self.send_0.setObjectName("send_0")
        self.gridLayout.addWidget(self.send_0, 1, 1, 1, 1)
        self.input_0 = QtWidgets.QLineEdit(parent=self.gridLayoutWidget)
        self.input_0.setObjectName("input_0")
        self.gridLayout.addWidget(self.input_0, 1, 0, 1, 1)
        self.output_0 = QtWidgets.QTextEdit(parent=self.gridLayoutWidget)
        self.output_0.setObjectName("output_0")
        self.gridLayout.addWidget(self.output_0, 0, 0, 1, 2)
        self.stackedWidget.addWidget(self.page_0)
        self.page_1 = QtWidgets.QWidget()
        self.page_1.setObjectName("page_1")
        self.gridLayoutWidget_2 = QtWidgets.QWidget(parent=self.page_1)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(0, 0, 341, 421))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.input_1 = QtWidgets.QLineEdit(parent=self.gridLayoutWidget_2)
        self.input_1.setObjectName("input_1")
        self.gridLayout_2.addWidget(self.input_1, 1, 0, 1, 1)
        self.new_1 = QtWidgets.QPushButton(parent=self.gridLayoutWidget_2)
        self.new_1.setObjectName("new_1")
        self.gridLayout_2.addWidget(self.new_1, 2, 0, 1, 2)
        self.send_1 = QtWidgets.QPushButton(parent=self.gridLayoutWidget_2)
        self.send_1.setObjectName("send_1")
        self.gridLayout_2.addWidget(self.send_1, 1, 1, 1, 1)
        self.output_1 = QtWidgets.QTextEdit(parent=self.gridLayoutWidget_2)
        self.output_1.setObjectName("output_1")
        self.gridLayout_2.addWidget(self.output_1, 0, 0, 1, 2)
        self.stackedWidget.addWidget(self.page_1)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(parent=self.page_2)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(0, 0, 341, 291))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.input_2 = QtWidgets.QLineEdit(parent=self.gridLayoutWidget_3)
        self.input_2.setObjectName("input_2")
        self.gridLayout_4.addWidget(self.input_2, 1, 0, 1, 1)
        self.send_2 = QtWidgets.QPushButton(parent=self.gridLayoutWidget_3)
        self.send_2.setObjectName("send_2")
        self.gridLayout_4.addWidget(self.send_2, 1, 1, 1, 1)
        self.output_2 = QtWidgets.QTextEdit(parent=self.gridLayoutWidget_3)
        self.output_2.setObjectName("output_2")
        self.gridLayout_4.addWidget(self.output_2, 0, 0, 1, 2)
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=self.page_2)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 290, 341, 131))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.change = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.change.setObjectName("change")
        self.verticalLayout_2.addWidget(self.change)
        self.ban = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.ban.setObjectName("ban")
        self.verticalLayout_2.addWidget(self.ban)
        self.exit = QtWidgets.QPushButton(parent=self.verticalLayoutWidget)
        self.exit.setObjectName("exit")
        self.verticalLayout_2.addWidget(self.exit)
        self.stackedWidget.addWidget(self.page_2)
        self.verticalLayout.addWidget(self.stackedWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 363, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.send_0.setText(_translate("MainWindow", "send"))
        self.new_1.setText(_translate("MainWindow", "new"))
        self.send_1.setText(_translate("MainWindow", "send"))
        self.send_2.setText(_translate("MainWindow", "send"))
        self.change.setText(_translate("MainWindow", "change"))
        self.ban.setText(_translate("MainWindow", "ban"))
        self.exit.setText(_translate("MainWindow", "exit"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
