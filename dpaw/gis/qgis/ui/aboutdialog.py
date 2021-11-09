from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ..tools import Tools
from string import ascii_uppercase


class AboutDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, Tools.QGISApp)

        self.setWindowTitle("About {0}".format(Tools.get_application_name()))

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        text = """{4}
Version: {1}
Release Date: {2}
Geographic Information Services Branch
{3}

The {4} application provides adds
functionality so that users may more
effectively view, query and manipulate {0}
corporate data and project datasets within
QGIS Desktop.""".format(Tools.get_dept_acronym(), Tools.versionNumber, Tools.releaseDate, Tools.get_dept_long_name(), Tools.get_application_name())

        mainLayout.addWidget(QLabel(text))
        okButton = QPushButton("OK", self)
        mainLayout.addWidget(okButton)
        okButton.setAutoDefault(True)
        okButton.clicked.connect(self.accept)

        self.exec_()
