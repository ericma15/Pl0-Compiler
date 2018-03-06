# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pcodeRun.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_runCodeForm(object):
    def setupUi(self, runCodeForm):
        runCodeForm.setObjectName("runCodeForm")
        runCodeForm.setWindowModality(QtCore.Qt.ApplicationModal)
        runCodeForm.resize(441, 254)
        self.verticalLayout = QtWidgets.QVBoxLayout(runCodeForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.runMonitporTextEdit = QtWidgets.QTextEdit(runCodeForm)
        self.runMonitporTextEdit.setReadOnly(True)
        self.runMonitporTextEdit.setObjectName("runMonitporTextEdit")
        self.horizontalLayout.addWidget(self.runMonitporTextEdit)
        self.errorMonitortextEdit = QtWidgets.QTextEdit(runCodeForm)
        self.errorMonitortextEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.errorMonitortextEdit.setReadOnly(True)
        self.errorMonitortextEdit.setObjectName("errorMonitortextEdit")
        self.horizontalLayout.addWidget(self.errorMonitortextEdit)
        self.horizontalLayout.setStretch(0, 3)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.inputHorizontalLayout = QtWidgets.QHBoxLayout()
        self.inputHorizontalLayout.setObjectName("inputHorizontalLayout")
        self.inputLineEdit = QtWidgets.QLineEdit(runCodeForm)
        self.inputLineEdit.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.inputLineEdit.setPlaceholderText("")
        self.inputLineEdit.setObjectName("inputLineEdit")
        self.inputHorizontalLayout.addWidget(self.inputLineEdit)
        self.sendPushButton = QtWidgets.QPushButton(runCodeForm)
        self.sendPushButton.setMaximumSize(QtCore.QSize(75, 16777215))
        self.sendPushButton.setObjectName("sendPushButton")
        self.inputHorizontalLayout.addWidget(self.sendPushButton)
        self.inputHorizontalLayout.setStretch(0, 6)
        self.inputHorizontalLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.inputHorizontalLayout)

        self.retranslateUi(runCodeForm)
        self.sendPushButton.clicked.connect(runCodeForm.sendData)
        QtCore.QMetaObject.connectSlotsByName(runCodeForm)

    def retranslateUi(self, runCodeForm):
        _translate = QtCore.QCoreApplication.translate
        runCodeForm.setWindowTitle(_translate("runCodeForm", "Pcode运行窗口"))
        self.sendPushButton.setText(_translate("runCodeForm", "发送"))
        self.sendPushButton.setShortcut(_translate("runCodeForm", "Return"))

