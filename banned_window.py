# Form implementation generated from reading ui file 'banned_window.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_BannedWindow(object):
    def setupUi(self, BannedWindow):
        BannedWindow.setObjectName("BannedWindow")
        BannedWindow.resize(324, 224)
        BannedWindow.setStyleSheet("#centralwidget {\n"
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
"    color: rgb(55, 107, 113);\n"
"}")
        self.centralwidget = QtWidgets.QWidget(parent=BannedWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.button_send = QtWidgets.QPushButton(parent=self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Cascadia Code")
        font.setPointSize(12)
        font.setBold(True)
        self.button_send.setFont(font)
        self.button_send.setObjectName("button_send")
        self.gridLayout_3.addWidget(self.button_send, 2, 0, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(parent=self.centralwidget)
        self.textBrowser.setStyleSheet("QTextBrowser {\n"
"    padding-top: 5px;\n"
"}")
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout_3.addWidget(self.textBrowser, 1, 0, 1, 1)
        BannedWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=BannedWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 324, 22))
        self.menubar.setObjectName("menubar")
        BannedWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=BannedWindow)
        self.statusbar.setObjectName("statusbar")
        BannedWindow.setStatusBar(self.statusbar)

        self.retranslateUi(BannedWindow)
        QtCore.QMetaObject.connectSlotsByName(BannedWindow)

    def retranslateUi(self, BannedWindow):
        _translate = QtCore.QCoreApplication.translate
        BannedWindow.setWindowTitle(_translate("BannedWindow", "MainWindow"))
        self.button_send.setText(_translate("BannedWindow", "OK"))
        self.textBrowser.setHtml(_translate("BannedWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:\'Segoe UI\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:28pt; font-weight:700;\">YOU</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:28pt; font-weight:700;\">WERE BANNED</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BannedWindow = QtWidgets.QMainWindow()
    ui = Ui_BannedWindow()
    ui.setupUi(BannedWindow)
    BannedWindow.show()
    sys.exit(app.exec())
