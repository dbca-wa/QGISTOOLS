# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_qgistools2.ui'
#
# Created: Fri Aug 15 15:47:22 2014
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


class Ui_QGISTools2(object):
    def setupUi(self, QGISTools2):
        QGISTools2.setObjectName(_fromUtf8("QGISTools2"))
        QGISTools2.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(QGISTools2)
        self.buttonBox.setGeometry(QtCore.QRect(30, 240, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))

        self.retranslateUi(QGISTools2)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), QGISTools2.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), QGISTools2.reject)
        QtCore.QMetaObject.connectSlotsByName(QGISTools2)

    def retranslateUi(self, QGISTools2):
        QGISTools2.setWindowTitle(_translate("QGISTools2", "QGISTools2", None))
