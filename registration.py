# Form implementation generated from reading ui file 'registration.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_Registration(object):
    def setupUi(self, Registration):
        Registration.setObjectName("Registration")
        Registration.resize(323, 189)
        Registration.setStyleSheet("#centralwidget {\n"
"    background-color: rgb(141, 141, 211);\n"
"}\n"
"QPushButton {\n"
"    background-color: rgb(0, 0, 0);\n"
"    border-radius: 5px;\n"
"    padding: 10px 10px;\n"
"    color: rgb(255, 255, 255);\n"
"}\n"
"QPushButton:hover {\n"
"    color: rgb(0, 0, 0);\n"
"    border: 1px  solid rgb(55, 107, 113);\n"
"    cursor: pointer;\n"
"    background-color: rgb(255, 255, 255);\n"
"}\n"
"QLineEdit {\n"
"    padding: 5px;\n"
"    border-radius:5px;\n"
"    color: rgb(141, 141, 211);\n"
"}")
        self.centralwidget = QtWidgets.QWidget(parent=Registration)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.reg_input = QtWidgets.QLineEdit(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Cascadia Code")
        font.setBold(True)
        self.reg_input.setFont(font)
        self.reg_input.setObjectName("reg_input")
        self.gridLayout_3.addWidget(self.reg_input, 1, 0, 1, 1)
        self.send_name_button = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Cascadia Code")
        font.setPointSize(11)
        font.setBold(True)
        self.send_name_button.setFont(font)
        self.send_name_button.setObjectName("send_name_button")
        self.gridLayout_3.addWidget(self.send_name_button, 1, 1, 1, 1)
        self.reg_header = QtWidgets.QTextEdit(parent=self.centralwidget)
        self.reg_header.setObjectName("reg_header")
        self.gridLayout_3.addWidget(self.reg_header, 0, 0, 1, 2)
        Registration.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=Registration)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 323, 22))
        self.menubar.setObjectName("menubar")
        Registration.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=Registration)
        self.statusbar.setObjectName("statusbar")
        Registration.setStatusBar(self.statusbar)

        self.retranslateUi(Registration)
        QtCore.QMetaObject.connectSlotsByName(Registration)

    def retranslateUi(self, Registration):
        _translate = QtCore.QCoreApplication.translate
        Registration.setWindowTitle(_translate("Registration", "MainWindow"))
        self.send_name_button.setText(_translate("Registration", "SEND"))
        self.reg_header.setHtml(_translate("Registration", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:\'Segoe UI\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt; font-weight:700; color:#000000;\">REGISTRATION</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-style:italic;\">Введите свое имя:</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Registration = QtWidgets.QMainWindow()
    ui = Ui_Registration()
    ui.setupUi(Registration)
    Registration.show()
    sys.exit(app.exec())
