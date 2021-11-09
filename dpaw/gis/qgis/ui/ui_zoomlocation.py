# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ZoomLocation.ui'
#
# Created: Wed Sep 17 16:24:20 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(689, 332)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 251, 211))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.localityRadioButton = QtGui.QRadioButton(self.groupBox)
        self.localityRadioButton.setGeometry(QtCore.QRect(10, 20, 82, 17))
        self.localityRadioButton.setObjectName(_fromUtf8("localityRadioButton"))
        self.fdGridRadioButton = QtGui.QRadioButton(self.groupBox)
        self.fdGridRadioButton.setGeometry(QtCore.QRect(10, 60, 82, 17))
        self.fdGridRadioButton.setObjectName(_fromUtf8("fdGridRadioButton"))
        self.coordsRadioButton = QtGui.QRadioButton(self.groupBox)
        self.coordsRadioButton.setGeometry(QtCore.QRect(10, 100, 82, 17))
        self.coordsRadioButton.setObjectName(_fromUtf8("coordsRadioButton"))
        self.localityLineEdit = QtGui.QLineEdit(self.groupBox)
        self.localityLineEdit.setGeometry(QtCore.QRect(100, 20, 141, 20))
        self.localityLineEdit.setObjectName(_fromUtf8("localityLineEdit"))
        self.fdLineEdit = QtGui.QLineEdit(self.groupBox)
        self.fdLineEdit.setGeometry(QtCore.QRect(100, 60, 141, 20))
        self.fdLineEdit.setObjectName(_fromUtf8("fdLineEdit"))
        self.crsComboBox = QtGui.QComboBox(self.groupBox)
        self.crsComboBox.setGeometry(QtCore.QRect(100, 100, 141, 22))
        self.crsComboBox.setObjectName(_fromUtf8("crsComboBox"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(80, 130, 21, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(80, 160, 21, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.xLineEdit = QtGui.QLineEdit(self.groupBox)
        self.xLineEdit.setGeometry(QtCore.QRect(100, 130, 113, 20))
        self.xLineEdit.setObjectName(_fromUtf8("xLineEdit"))
        self.yLineEdit = QtGui.QLineEdit(self.groupBox)
        self.yLineEdit.setGeometry(QtCore.QRect(100, 160, 113, 20))
        self.yLineEdit.setObjectName(_fromUtf8("yLineEdit"))
        self.scaleComboBox = QtGui.QComboBox(Dialog)
        self.scaleComboBox.setGeometry(QtCore.QRect(100, 240, 111, 22))
        self.scaleComboBox.setObjectName(_fromUtf8("scaleComboBox"))
        self.zoomButton = QtGui.QPushButton(Dialog)
        self.zoomButton.setGeometry(QtCore.QRect(100, 280, 111, 23))
        self.zoomButton.setObjectName(_fromUtf8("zoomButton"))
        self.tableWidget = QtGui.QTableWidget(Dialog)
        self.tableWidget.setGeometry(QtCore.QRect(280, 20, 391, 301))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.groupBox.setTitle(_translate("Dialog", "ZoomType", None))
        self.localityRadioButton.setText(_translate("Dialog", "Locality", None))
        self.fdGridRadioButton.setText(_translate("Dialog", "FD Grid Ref", None))
        self.coordsRadioButton.setText(_translate("Dialog", "Coordinates", None))
        self.label.setText(_translate("Dialog", "X:", None))
        self.label_2.setText(_translate("Dialog", "Y:", None))
        self.zoomButton.setText(_translate("Dialog", "Zoom", None))
