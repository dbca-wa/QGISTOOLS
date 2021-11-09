from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *
from qgis.gui import *
from ..tools import *

import os
import shutil

import qgis.utils
from ..data.crs.crshelper import CRSHelper
import csv


class ZoomToLocationDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self, Tools.QGISApp)
        self.setupDialog()
        self.exec_()

    def setupDialog(self):
        self.setWindowTitle("Zoom to Location")
        self.resize(720, 367)
        self.groupBox = QtGui.QGroupBox("Zoom Type", self)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 251, 241))

        # Locality Radio Button
        self.localityRadioButton = QtGui.QRadioButton(self)
        self.localityRadioButton.setGeometry(QtCore.QRect(20, 40, 82, 17))
        self.localityRadioButton.setText("Locality")
        self.localityRadioButton.setChecked(True)
        self.localityRadioButton.toggled.connect(self.localityToggleHandler)

        # Locality Line Edit
        self.localityLineEdit = QtGui.QLineEdit(self)
        self.localityLineEdit.setGeometry(QtCore.QRect(110, 40, 141, 20))
        self.localityLineEdit.setObjectName("localityLineEdit")
        self.localityLineEdit.textEdited.connect(self.localityLineEditHandler)
        self.localityLineEdit.setFocus()

        # FD Grid Radio Button
        self.fdGridRadioButton = QtGui.QRadioButton(self)
        self.fdGridRadioButton.setGeometry(QtCore.QRect(20, 80, 82, 17))
        self.fdGridRadioButton.setText("FD Grid Ref")
        self.fdGridRadioButton.toggled.connect(self.fdGridToggleHandler)

        # FD Line Edit
        self.fdLineEdit = QtGui.QLineEdit(self)
        self.fdLineEdit.setGeometry(QtCore.QRect(110, 80, 141, 20))
        self.fdLineEdit.setEnabled(False)
        self.fdLineEdit.textEdited.connect(self.fdLineEditHandler)

        # Coords Radio Button
        self.coordsRadioButton = QtGui.QRadioButton(self)
        self.coordsRadioButton.setText("Coordinates")
        self.coordsRadioButton.setGeometry(QtCore.QRect(20, 120, 82, 17))
        self.coordsRadioButton.toggled.connect(self.coordsToggleHandler)

        # Coords Combo Box
        self.crsComboBox = QtGui.QComboBox(self)
        self.crsComboBox.setGeometry(QtCore.QRect(110, 120, 141, 22))
        self.crsComboBox.addItem("Geographic (Lat/Long)")
        self.crsComboBox.addItem("Grid (Eastings/Northings)")
        self.crsComboBox.currentIndexChanged.connect(self.crsComboIndexChangeHandler)
        self.crsComboBox.setEnabled(False)

        # Lat/Easting Label
        self.latEastingLabel = QtGui.QLabel(self)
        self.latEastingLabel.setGeometry(QtCore.QRect(62, 150, 40, 16))
        self.latEastingLabel.setText("Lat:")

        # Lat/Easting Line Edit
        self.latEastingLineEdit = QtGui.QLineEdit(self)
        self.latEastingLineEdit.setGeometry(QtCore.QRect(110, 150, 113, 20))
        self.latEastingLineEdit.setEnabled(False)

        # Lon/Northing Label
        self.lonNorthingLabel = QtGui.QLabel(self)
        self.lonNorthingLabel.setGeometry(QtCore.QRect(62, 180, 45, 16))
        self.lonNorthingLabel.setText("Long:")

        # Lon/Northing Line Edit
        self.lonNorthingLineEdit = QtGui.QLineEdit(self)
        self.lonNorthingLineEdit.setGeometry(QtCore.QRect(110, 180, 113, 20))
        self.lonNorthingLineEdit.setEnabled(False)

        # MGA Zone Label
        self.zoneLabel = QtGui.QLabel(self)
        self.zoneLabel.setGeometry(QtCore.QRect(55, 210, 52, 16))
        self.zoneLabel.setText("MGA Zone:")
        self.zoneLabel.setVisible(False)

        # Zones Combo Box
        self.zoneComboBox = QtGui.QComboBox(self)
        self.zoneComboBox.setGeometry(QtCore.QRect(110, 210, 41, 22))
        self.zoneComboBox.addItem("50")
        self.zoneComboBox.addItem("51")
        self.zoneComboBox.addItem("52")
        self.zoneComboBox.addItem("49")
        self.zoneComboBox.setVisible(False)

        # Scale Combo Box
        self.scaleComboBox = QtGui.QComboBox(self)
        self.scaleComboBox.setGeometry(QtCore.QRect(100, 270, 111, 22))
        self.scaleComboBox.addItem("Current Scale")
        self.scaleComboBox.addItem("1:500")
        self.scaleComboBox.addItem("1:1000")
        self.scaleComboBox.addItem("1:2000")
        self.scaleComboBox.addItem("1:2500")
        self.scaleComboBox.addItem("1:5000")
        self.scaleComboBox.addItem("1:7500")
        self.scaleComboBox.addItem("1:10,000")
        self.scaleComboBox.addItem("1:12,500")
        self.scaleComboBox.addItem("1:15,000")
        self.scaleComboBox.addItem("1:20,00")
        self.scaleComboBox.addItem("1:25,000")
        self.scaleComboBox.addItem("1:30,000")
        self.scaleComboBox.addItem("1:40,000")
        self.scaleComboBox.addItem("1:50,000")
        self.scaleComboBox.addItem("1:60,000")
        self.scaleComboBox.addItem("1:75,000")
        self.scaleComboBox.addItem("1:80,000")
        self.scaleComboBox.addItem("1:100,000")
        self.scaleComboBox.addItem("1:150,000")
        self.scaleComboBox.addItem("1:200,000")
        self.scaleComboBox.addItem("1:250,000")
        self.scaleComboBox.addItem("1:500,000")
        self.scaleComboBox.addItem("1:1,000,000")
        self.scaleComboBox.addItem("1:2,000,000")
        self.scaleComboBox.addItem("1:3,000,000")

        # Zoom button
        self.zoomButton = QtGui.QPushButton(self)
        self.zoomButton.setGeometry(QtCore.QRect(100, 310, 111, 23))
        self.zoomButton.setText("Zoom")
        self.zoomButton.clicked.connect(self.zoomClickHandler)

        # Locality Table View
        self.localityTable = QtGui.QTableView(self)
        self.localityTable.setGeometry(QtCore.QRect(280, 20, 421, 301))
        header = ['Name', 'Feature', 'Latitude', 'Longitude']
        self.model = QtGui.QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(header)
        self.localityTable.setModel(self.model)
        self.localityTable.resizeColumnsToContents()
        self.localityTable.verticalHeader().setVisible(False)
        self.localityTable.setColumnWidth(0, 161)
        self.localityTable.setColumnWidth(1, 100)
        self.localityTable.setColumnWidth(2, 70)
        self.localityTable.setColumnWidth(3, 70)
        self.localityTable.setFont(QFont("Arial", 7))
        self.localityTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.localityTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.localityTable.doubleClicked.connect(self.zoomClickHandler)

    def zoomClickHandler(self):
        if self.localityRadioButton.isChecked():
            if self.localityLineEdit.text() == "":
                QMessageBox.information(None, "No locality specified!",
                                        "Please type in a locality name")
                self.localityLineEdit.setFocus()
                return
            elif len(self.localityTable.selectedIndexes()) == 0:
                QMessageBox.information(None, "No locality selected!",
                                        "Please select a locality from the table")
                self.localityTable.setFocus()
                return
            else:
                lat = float(self.model.itemFromIndex(self.localityTable.selectedIndexes()[2]).text())
                lon = float(self.model.itemFromIndex(self.localityTable.selectedIndexes()[3]).text())
                self.zoomToLatLon(lat, lon)
        elif self.fdGridRadioButton.isChecked():
            if self.fdLineEdit.text() == "":
                QMessageBox.information(None, "No Grid Ref specified!",
                                        "Please type in an FD Grid Ref")
                self.fdLineEdit.setFocus()
                return
            elif len(self.localityTable.selectedIndexes()) == 0:
                QMessageBox.information(None, "No grid ref selected!",
                                        "Please select a grid reference from the table")
                self.localityTable.setFocus()
                return
            else:
                lat = float(self.model.itemFromIndex(self.localityTable.selectedIndexes()[2]).text())
                lon = float(self.model.itemFromIndex(self.localityTable.selectedIndexes()[3]).text())
                self.zoomToLatLon(lat, lon)
        elif self.coordsRadioButton.isChecked():
            if self.latEastingLineEdit.text() == "" or self.lonNorthingLineEdit.text() == "":
                QMessageBox.information(None, "Coordinates not specified!",
                                        "Please type in both coordinates")
                if self.latEastingLineEdit.text() == "":
                    self.latEastingLineEdit.setFocus()
                elif self.lonNorthingLineEdit.text() == "":
                    self.lonNorthingLineEdit.setFocus()
                return
            else:
                if self.crsComboBox.currentIndex() == 0:    # i.e. Lat/Long
                    try:
                        lat = float(self.latEastingLineEdit.text())
                        lon = float(self.lonNorthingLineEdit.text())
                    # Check that input lat/long have been entered in correct format
                    except:
                        latText = self.latEastingLineEdit.text()
                        lonText = self.lonNorthingLineEdit.text()
                        if not latText.replace("-", "").isnumeric():
                            self.latEastingLineEdit.setFocus()
                        elif not lonText.replace("-", "").isnumeric():
                            self.lonNorthingLineEdit.setFocus()
                        else:
                            self.latEastingLineEdit.setFocus()
                        QMessageBox.information(None, "Incorrect Format!", "Lat/Long must be in decimal degrees - e.g. Lat = -32.123, Long = 115.789")
                        return
                    if lat > 90 or lat < -90:
                        QMessageBox.information(None, "Invalid Latitude!", "Latitude must be between -90 and 90")
                        self.latEastingLineEdit.setText("")
                        self.latEastingLineEdit.setFocus()
                        return
                    if lon > 180 or lon < -180:
                        QMessageBox.information(None, "Invalid Longitude!", "Longitude must be between -180 and 180")
                        self.lonNorthingLineEdit.setText("")
                        self.lonNorthingLineEdit.setFocus()                                                
                        return
                    if lat > 0:
                        reply = QMessageBox.question(self, 'Check latitude', 
                                                    'Latitudes for Western Australia are negative.  Do you want to use latitude -' + str(lat) + " instead?", 
                                                    QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
                        if reply == QMessageBox.Yes:
                            self.latEastingLineEdit.setText("-" + str(lat))
                            lat *= -1
                        elif reply == QMessageBox.Cancel:
                            return
                    if lon < 0:
                        reply = QMessageBox.question(self, 'Check longitude', 
                                                    'Longitudes for Western Australia are positive.  Do you want to use longitude ' + str(lon)[1:] + " instead?", 
                                                    QMessageBox.Yes, QMessageBox.No, QMessageBox.Cancel)
                        if reply == QMessageBox.Yes:
                            self.lonNorthingLineEdit.setText(str(lon)[1:])
                            lon *= -1
                        elif reply == QMessageBox.Cancel:
                            return                            
                    self.zoomToLatLon(lat, lon)
                elif self.crsComboBox.currentIndex() == 1:    # i.e. MGA Easting/Northing
                    try:
                        east = float(self.latEastingLineEdit.text())
                        north = float(self.lonNorthingLineEdit.text())
                    except:
                        # Check that input coords have been entered in correct format
                        eastText = self.latEastingLineEdit.text()
                        northText = self.lonNorthingLineEdit.text()                       
                        if not eastText.replace("-", "").isnumeric():
                            self.latEastingLineEdit.setFocus()
                        elif not northText.replace("-", "").isnumeric():
                            self.lonNorthingLineEdit.setFocus()
                        else:
                            self.latEastingLineEdit.setFocus()
                        QMessageBox.information(None, "Incorrect Format!", "Easting/Northing must be numeric")
                        return
                    if east < 0 or east > 500000:
                        reply = QMessageBox.question(self, 'Check easting', 
                                                    'Eastings are normally between 0 and 500,000.  Do you want to continue with easting ' + str(east) + '?', 
                                                    QMessageBox.Yes, QMessageBox.No)
                        if reply == QMessageBox.No:
                            self.latEastingLineEdit.setFocus()
                            return
                    if north < 6000000 or north > 8600000:
                        reply = QMessageBox.question(self, 'Check northing', 
                                                    'Northings in WA are normally between 6,000,000 and 8,600,000.  Do you want to continue with northing ' + str(north) + '?', 
                                                    QMessageBox.Yes, QMessageBox.No)
                        if reply == QMessageBox.No:
                            self.lonNorthingLineEdit.setFocus()
                            return                                
                    self.zoomToMGACoords(east, north)
        # self.accept()

    def zoomToLatLon(self, lat, lon):
        epsg = 4283
        self.zoomToCoords(lon, lat, epsg)

    def zoomToMGACoords(self, easting, northing):
        epsg = 28300 + int(self.zoneComboBox.currentText())
        self.zoomToCoords(easting, northing, epsg)

    def zoomToCoords(self, x, y, epsg):      # Adapted from http://www.qgis.nl/2014/07/10/qgis-processing-scripts-gebruiken/?lang=en
        canvas = qgis.utils.iface.mapCanvas()
        if self.scaleComboBox.currentText() == "Current Scale":
            scale = canvas.scale()
        else:
            scale = float(self.scaleComboBox.currentText()[2:].replace(",", ""))
        #crsto = canvas.mapRenderer().destinationCrs()
        crsto = canvas.mapSettings().destinationCrs()
        crsfrom = QgsCoordinateReferenceSystem()
        crsfrom.createFromId(epsg)
        crsTransform = QgsCoordinateTransform(crsfrom, crsto)

        point = QgsPoint(x, y)
        geom = QgsGeometry.fromPoint(point)
        geom.transform(crsTransform)

        # a vertex marker
        m = QgsVertexMarker(canvas)
        m.setCenter(geom.asPoint())
        m.setIconSize(8)
        m.setPenWidth(4)

        # zoom to with center is actually setting a point rectangle and then zoom
        center = geom.asPoint()
        rect = QgsRectangle(center, center)
        canvas.setExtent(rect)
        canvas.zoomScale(scale)
        canvas.refresh()

        # some magic to let the marker disappear 4 seconds
        def timerFired():
            qgis.utils.iface.mapCanvas().scene().removeItem(m)
            timer.stop()

        timer = QTimer()
        timer.timeout.connect(timerFired)
        timer.setSingleShot(True)
        timer.start(4000)
        self.close()

    def cancelClickHandler(self):       # This is here just in case a 'Cancel' button is added
        self.reject()

    def localityToggleHandler(self, checked):
        if self.localityRadioButton.isChecked():
            self.model.removeRows(0, self.model.rowCount(), QModelIndex())
            self.localityLineEdit.setEnabled(True)
            self.fdLineEdit.setEnabled(False)
            self.fdLineEdit.setText("")
            self.crsComboBox.setEnabled(False)
            self.latEastingLineEdit.setEnabled(False)
            self.latEastingLineEdit.setText("")
            self.lonNorthingLineEdit.setEnabled(False)
            self.lonNorthingLineEdit.setText("")
            self.zoneComboBox.setEnabled(False)
            self.localityTable.setVisible(True)
            self.resize(720, 367)

    def localityLineEditHandler(self):
        qgisTools2 = os.path.join(os.path.dirname(__file__), ("../../../.."))
        localities = os.path.normpath(qgisTools2) + r"/resources/locations/locality_coords.csv"
        # clear current rows
        self.model.removeRows(0, self.model.rowCount(), QModelIndex())
        if self.localityLineEdit.text() != "":
            with open(localities, "rb") as fileInput:
                csv.reader(fileInput).next()
                for row in csv.reader(fileInput):
                    if row[0][:len(self.localityLineEdit.text())].upper() == self.localityLineEdit.text().upper():
                        items = [
                            QtGui.QStandardItem(field)
                            for field in row
                        ]
                        self.model.appendRow(items)
        self.localityTable.setColumnWidth(0, 161)
        self.localityTable.setColumnWidth(1, 100)
        self.localityTable.setColumnWidth(2, 70)
        self.localityTable.setColumnWidth(3, 70)

    def fdGridToggleHandler(self, checked):
        if self.fdGridRadioButton.isChecked():
            self.model.removeRows(0, self.model.rowCount(), QModelIndex())
            self.localityLineEdit.setEnabled(False)
            self.localityLineEdit.setText("")
            self.fdLineEdit.setEnabled(True)
            self.crsComboBox.setEnabled(False)
            self.latEastingLineEdit.setEnabled(False)
            self.latEastingLineEdit.setText("")
            self.lonNorthingLineEdit.setEnabled(False)
            self.lonNorthingLineEdit.setText("")
            self.zoneComboBox.setEnabled(False)
            self.localityTable.setVisible(True)
            self.resize(720, 367)

    def fdLineEditHandler(self):
        qgisTools2 = os.path.join(os.path.dirname(__file__), ("../../../.."))
        gridRefs = os.path.normpath(qgisTools2) + r"/resources/locations/fd_coords.csv"
        # clear current rows
        self.model.removeRows(0, self.model.rowCount(), QModelIndex())
        if self.fdLineEdit.text() != "":
            with open(gridRefs, "rb") as fileInput:
                csv.reader(fileInput).next()
                for row in csv.reader(fileInput):
                    if row[0][:len(self.fdLineEdit.text())].upper() == self.fdLineEdit.text().upper():
                        items = [
                            QtGui.QStandardItem(field)
                            for field in row
                        ]
                        self.model.appendRow(items)
        self.localityTable.setColumnWidth(0, 100)
        self.localityTable.setColumnWidth(1, 161)
        self.localityTable.setColumnWidth(2, 70)
        self.localityTable.setColumnWidth(3, 70)

    def coordsToggleHandler(self, checked):
        if self.coordsRadioButton.isChecked():
            self.model.removeRows(0, self.model.rowCount(), QModelIndex())
            self.localityLineEdit.setEnabled(False)
            self.localityLineEdit.setText("")
            self.fdLineEdit.setEnabled(False)
            self.fdLineEdit.setText("")
            self.crsComboBox.setEnabled(True)
            self.latEastingLineEdit.setEnabled(True)
            self.lonNorthingLineEdit.setEnabled(True)
            self.zoneComboBox.setEnabled(True)
            self.localityTable.setVisible(False)
            self.resize(271, 367)

    def crsComboIndexChangeHandler(self, index):
        if index == 0:
            self.latEastingLabel.setText("Lat:")
            self.lonNorthingLabel.setText("Long:")
            self.zoneLabel.setVisible(False)
            self.zoneComboBox.setVisible(False)
        elif index == 1:
            self.latEastingLabel.setText("Easting:")
            self.lonNorthingLabel.setText("Northing:")
            self.zoneLabel.setVisible(True)
            self.zoneComboBox.setVisible(True)
