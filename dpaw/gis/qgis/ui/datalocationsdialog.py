from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ..tools import Tools
from string import ascii_uppercase
import win32api


class DataLocationsDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self, Tools.QGISApp)

        self.setWindowTitle("Data Locations")

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        drivesLayout = QFormLayout()
        mainLayout.addLayout(drivesLayout)

        drivesString = win32api.GetLogicalDriveStrings()
        #drives = []
        #for letter in ascii_uppercase:
        #    drives.append(letter + ":")
        drives = drivesString.split("\\\000")[:-1]
        if len(drives) == 0:
            Tools.debug("You have no mapped drives.")
            return

        drive1ComboBox = QComboBox(self)
        self.drive1ComboBox = drive1ComboBox
        target = Tools.getDataDrive1().upper()
        for drive in drives:
            drive1ComboBox.addItem(drive, None)
            if drive == target:
                drive1ComboBox.setCurrentIndex(drive1ComboBox.count() - 1)

        drivesLayout.addRow("Corporate Data Drive:", drive1ComboBox)

        drive2ComboBox = QComboBox(self)
        self.drive2ComboBox = drive2ComboBox
        target = Tools.getDataDrive2().upper()
        for drive in drives:
            drive2ComboBox.addItem(drive, None)
            if drive == target:
                drive2ComboBox.setCurrentIndex(drive2ComboBox.count() - 1)

        drivesLayout.addRow("External Corporate Data Drive:", drive2ComboBox)

        buttonsLayout = QHBoxLayout()
        mainLayout.addLayout(buttonsLayout)

        okButton = QPushButton("OK", self)
        buttonsLayout.addWidget(okButton)
        okButton.setAutoDefault(True)
        okButton.clicked.connect(self.accept)

        cancelButton = QPushButton("Cancel", self)
        buttonsLayout.addWidget(cancelButton)
        cancelButton.clicked.connect(self.reject)

        self.exec_()

    def accept(self):
        QDialog.accept(self)
        d1cb = self.drive1ComboBox
        Tools.setDataDrive1(str(d1cb.itemText(d1cb.currentIndex())))

        d2cb = self.drive2ComboBox
        Tools.setDataDrive2(str(d2cb.itemText(d2cb.currentIndex())))

        # Update SVG search path
        settings = QSettings()
        # Tools.debug("Settings parent is " + settings.parent())
        svgPath1 = Tools.getDataDrive1() + "\\GIS1-Corporate\\Data\\Symbology"
        svgPath2 = Tools.getDataDrive2() + "\\GIS1-Corporate\\Data\\Symbology"
        if svgPath1 != svgPath2:
            settings.setValue('svg/searchPathsForSVG', svgPath1 + '|' + svgPath2)
        else:
            settings.setValue('svg/searchPathsForSVG', svgPath1)

        # Call Tools to load data
        Tools.dm.loadMenuData()

        # Update Tools.corporateDataDrive
        # Tools.corporateDataDrive = Tools.readSiteLocationFile()
