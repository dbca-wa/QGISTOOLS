# -*- coding: utf-8 -*-
"""
/***************************************************************************
 SearchCadastre

 Selects and zooms to user-specified location
                             -------------------
        begin                : 2015-08-11
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Pat Maslen, GIS Branch
        email                : Patrick.Maslen@dpaw.wa.gov.au
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import ConfigParser, csv, getpass, os, sys, shapefile, shutil, sqlite3

from qgis.core import *
from qgis.gui import *
import qgis.utils
import datetime, time
from PyQt4 import uic
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from osgeo import ogr

thisFolder = os.path.dirname(os.path.realpath(__file__))
sys.path.append(thisFolder)

class DatabaseSettings():
    # Search cadastre gdb and feature class
    #cadastre_gdb = r"\\corporateict\dfs\shareddata\GIS-CALM\GIS1-Corporate\Data\GDB\\SCDB_Tenure\State_Cadastre\State_Cadastre.gdb"
    #cadastre_fc = "CPT_CADASTRE_SCDB"
    #cadastre_qml = "//corporateict/dfs/shareddata/GIS-CALM/GIS1-Corporate/Data/GDB/SCDB_Tenure/State_Cadastre/cpt_cadastre_scdb.qml"
    search_cadastre_folder = r"C:\Users\Public\Documents"
    search_cadastre_config_file = "search_cadastre_config.cfg"
    dest = os.path.join(search_cadastre_folder, search_cadastre_config_file)
    if not os.path.isfile(dest):
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", search_cadastre_config_file)
        shutil.copyfile(src, dest)
    config = ConfigParser.ConfigParser()
    config.read(dest)
    cadastre_gdb = config.get("DatabaseSettings", "cadastre_gdb")
    cadastre_fc = config.get("DatabaseSettings", "cadastre_fc")
    cadastre_qml = config.get("DatabaseSettings", "cadastre_qml")    
    local_cadastre_db = "C:/Users/Public/Documents/Search_Cadastre.sqlite"
    estate_db = "//corporateict/dfs/shareddata/GIS-CALM/GIS3-Systems/Data_Management/Tenure_data/Tenure_2.sqlite"
    
def check_cadastre_gdb(cadastre_gdb, cadastre_fc):
    if not os.path.isdir(cadastre_gdb):
        QMessageBox.information(None, "State Cadastre GDB not found!", "\nThe tool is looking for a geodatabase at " + cadastre_gdb + " but it was not found.  Only the Locations tab can be used.  Contact GIS Apps in OIM.")
        return False
    else:
        driver = ogr.GetDriverByName("OpenFileGDB")
        data_source = driver.Open(cadastre_gdb)
        cadastre_fc_layer = data_source.GetLayer(cadastre_fc)
        if cadastre_fc_layer is None:
            QMessageBox.information(None, "State Cadastre layer not found!", "\nThe tool is looking for a layer named " + cadastre_fc + " in " + cadastre_gdb + " but it was not found.  Contact GIS Apps in OIM.")
            return False
    return True

def finalZoom(ids, db_settings):
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    canvas = qgis.utils.iface.mapCanvas()
    #db_settings = DatabaseSettings()
    proceed = check_cadastre_gdb(db_settings.cadastre_gdb, db_settings.cadastre_fc)
    if not proceed:
        QMessageBox.information(None, "Cadastral data missing!", "The cadastral data is not available.  Contact GIS Apps in OIM and tell them that finalZoom in searchcadastre.py has failed.")
        return
    #Following is Fri arvo code and could be improved; should be OK for small datasets
    # Initialise bounding box settings
    xMax = -10000000
    yMax = -10000000
    xMin = 10000000
    yMin = 10000000
    # Determine whether cadastre_gdb/state_cadastre layer is already displayed; if not then add it.
    layer = None
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.source().lower() == (db_settings.cadastre_gdb + "|layername=" + db_settings.cadastre_fc).lower():
            layer = lyr
            break

    if layer is None:
        layer = qgis.utils.iface.addVectorLayer(db_settings.cadastre_gdb + "|layername=" + db_settings.cadastre_fc, "State Cadastre (GDB)", "ogr")
        #layer.setName("State Cadastre (GDB)")
        try:
            layer.loadNamedStyle(db_settings.cadastre_qml)
        except:
            pass

    qgis.utils.iface.legendInterface().setLayerVisible(layer, True)
    
    layer.setSelectedFeatures(ids)
    # Label selected features
    palyr = QgsPalLayerSettings()
    palyr.readFromLayer(layer)
    palyr.enabled = True
    palyr.fieldName = "CASE WHEN " + searchString + " THEN 'PIN ' || PIN END"
    palyr.isExpression = True
    palyr.placement = QgsPalLayerSettings.OverPoint
    palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','')
    palyr.writeToLayer(layer)
    
    #Update xMin etc to accommodate each cadastre
    box = layer.boundingBoxOfSelected()
    if box.xMinimum() < xMin:
        xMin = box.xMinimum()
    if box.xMaximum() > xMax:
        xMax = box.xMaximum()
    if box.yMinimum() < yMin:
        yMin = box.yMinimum()
    if box.yMaximum() > yMax:
        yMax = box.yMaximum()

    # Size viewport
    xMin = 1.1*xMin - 0.1*xMax
    xMax = 1.1*xMax - 0.1*xMin
    yMin = 1.1*yMin - 0.1*yMax
    yMax = 1.1*yMax - 0.1*yMin
    extent = QgsRectangle(xMin, yMin, xMax, yMax)   # This will be in GDA94
    # check for canvas CRS and transform extent if need be.
    canvasCRS = canvas.mapSettings().destinationCrs()
    gda94 = QgsCoordinateReferenceSystem(4283, QgsCoordinateReferenceSystem.EpsgCrsId)
    if canvasCRS != gda94:
        crsTransformer = QgsCoordinateTransform(gda94, canvasCRS)
        extent = crsTransformer.transform(extent)
    canvas.setExtent(extent)
    
    # Ensure active layer is activeCadastre
    for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
        if lyr.source() == db_settings.cadastre_gdb:
            qgis.utils.iface.setActiveLayer(lyr)
    
    # If WA_box layer exists, remove it.
    try:
        QgsMapLayerRegistry.instance().removeMapLayer(waBoxLayer.id())
    except:
        pass
    canvas.refresh()
    QApplication.restoreOverrideCursor()


class SearchCadastreDialog(QDialog):
    def __init__(self, db_settings, parent=None):
        self.db_settings = db_settings
        cadastre_gdb_ok = check_cadastre_gdb(self.db_settings.cadastre_gdb, self.db_settings.cadastre_fc)

        self.canvas = qgis.utils.iface.mapCanvas()
        self.waBoxAdded = False     # Used to track whether WA_box.shp has been added to canvas
        self.typesList = [' AGRICULTURAL ', ' ESTATE ', ' LOCATION ', ' SUBURBAN ', ' TOWNSITE ', ' PART ']

        super(SearchCadastreDialog, self).__init__(parent)
        
        semiBoldFont = QFont()
        semiBoldFont.setWeight(63)
        normalFont = QFont()
        normalFont.setWeight(50)
        
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        self.setWindowTitle("Zoom to Location")
        
        self.tabWidget = QTabWidget()
        parcelsTab = QWidget()
        parcelsLayout = QFormLayout(parcelsTab)
        addressTab = QWidget()
        addressLayout = QFormLayout(addressTab)
        reservesTab = QWidget()
        reservesLayout = QFormLayout(reservesTab)
        pinTab = QWidget()
        pinTabLayout = QVBoxLayout(pinTab)
        ownerTab = QWidget()
        ownerTabLayout = QVBoxLayout(ownerTab)
        locationsTab = QWidget()
        self.locationsLayout = QHBoxLayout(locationsTab)
        settingsTab = QWidget()
        settingsLayout = QVBoxLayout(settingsTab)
        self.tabWidget.addTab(locationsTab, "Locations")
        self.tabWidget.addTab(parcelsTab, "Parcels")
        self.tabWidget.addTab(addressTab, "Addresses")
        self.tabWidget.addTab(reservesTab, "Reserves")
        self.tabWidget.addTab(pinTab, "PIN")
        self.tabWidget.addTab(ownerTab, "Owners")
        self.tabWidget.addTab(settingsTab, "Settings")
        self.tabWidget.setUsesScrollButtons(False)
        self.tabWidget.currentChanged.connect(self.tabDefaultButton)
        if not cadastre_gdb_ok:
            parcelsTab.setEnabled(False)
            addressTab.setEnabled(False)
            reservesTab.setEnabled(False)
            pinTab.setEnabled(False)
            ownerTab.setEnabled(False)
            settingsTab.setEnabled(False)
        mainLayout.addWidget(self.tabWidget)
        
        scalingWidth = self.requiredWidth()
        
        # LOCATIONS TAB
        self.leftSide = QVBoxLayout()
        self.leftSide.setAlignment(Qt.AlignHCenter) 
        self.locationsLayout.addLayout(self.leftSide)
        self.rightSide = QVBoxLayout()
        self.locationsLayout.addLayout(self.rightSide)
        #self.rightSide.setGeometry(QRect(271, 10, 421, 301))
        self.groupBox = QGroupBox("Location Type", self)
        #self.groupBox.setGeometry(QRect(10, 10, 251, 241))
        ###self.groupBox.setFixedWidth(251)
        self.groupBox.setFixedWidth(scalingWidth * 0.67)
        self.leftSide.addWidget(self.groupBox)

        # Locality Radio Button
        self.localityRadioButton = QRadioButton(self.groupBox)
        ###self.localityRadioButton.setGeometry(QRect(10, 40, 82, 17))
        self.localityRadioButton.setGeometry(QRect(scalingWidth * 0.027, scalingWidth * 0.107, scalingWidth * 0.22, scalingWidth * 0.045))
        self.localityRadioButton.setText("Locality")
        self.localityRadioButton.setChecked(True)
        self.localityRadioButton.toggled.connect(self.localityToggleHandler)

        # Locality Line Edit
        self.localityLineEdit = QLineEdit(self.groupBox)
        ###self.localityLineEdit.setGeometry(QRect(100, 40, 141, 20))
        self.localityLineEdit.setGeometry(QRect(scalingWidth * 0.27, scalingWidth * 0.107, scalingWidth * 0.38, scalingWidth * 0.053))
        ###self.localityLineEdit.setFixedWidth(141)
        self.localityLineEdit.setFixedWidth(scalingWidth * 0.38)
        self.localityLineEdit.setObjectName("localityLineEdit")
        self.localityLineEdit.textEdited.connect(self.localityLineEditHandler)
        self.localityLineEdit.setFocus()

        # FD Grid Radio Button
        self.fdGridRadioButton = QRadioButton(self.groupBox)
        ###self.fdGridRadioButton.setGeometry(QRect(10, 80, 82, 17))
        self.fdGridRadioButton.setGeometry(QRect(scalingWidth * 0.027, scalingWidth * 0.214, scalingWidth * 0.22, scalingWidth * 0.045))
        self.fdGridRadioButton.setText("FD Grid Ref")
        self.fdGridRadioButton.toggled.connect(self.fdGridToggleHandler)

        # FD Line Edit
        self.fdLineEdit = QLineEdit(self.groupBox)
        ###self.fdLineEdit.setGeometry(QRect(100, 80, 141, 20))
        self.fdLineEdit.setGeometry(QRect(scalingWidth * 0.27, scalingWidth * 0.214, scalingWidth * 0.38, scalingWidth * 0.053))
        self.fdLineEdit.setEnabled(False)
        self.fdLineEdit.textEdited.connect(self.fdLineEditHandler)

        # Coords Radio Button
        self.coordsRadioButton = QRadioButton(self.groupBox)
        self.coordsRadioButton.setText("Coordinates")
        ###self.coordsRadioButton.setGeometry(QRect(10, 120, 82, 17))
        self.coordsRadioButton.setGeometry(QRect(scalingWidth * 0.027, scalingWidth * 0.32, scalingWidth * 0.22, scalingWidth * 0.045))
        self.coordsRadioButton.toggled.connect(self.coordsToggleHandler)

        # Coords Combo Box
        self.crsComboBox = QComboBox(self.groupBox)
        ###self.crsComboBox.setGeometry(QRect(100, 120, 141, 22))
        self.crsComboBox.setGeometry(QRect(scalingWidth * 0.27, scalingWidth * 0.32, scalingWidth * 0.38, scalingWidth * 0.059))
        self.crsComboBox.addItem("Geographic (Lat/Long)")
        self.crsComboBox.addItem("Grid (Eastings/Northings)")
        self.crsComboBox.currentIndexChanged.connect(self.crsComboIndexChangeHandler)
        self.crsComboBox.setEnabled(False)

        # Lat/Easting Label
        self.latEastingLabel = QLabel(self.groupBox)
        ###self.latEastingLabel.setGeometry(QRect(52, 150, 40, 16))
        self.latEastingLabel.setGeometry(QRect(scalingWidth * 0.14, scalingWidth * 0.4 , scalingWidth * 0.107, scalingWidth * 0.045))
        self.latEastingLabel.setText("Lat:")

        # Lat/Easting Line Edit
        self.latEastingLineEdit = QLineEdit(self.groupBox)
        ###self.latEastingLineEdit.setGeometry(QRect(100, 150, 113, 20))
        self.latEastingLineEdit.setGeometry(QRect(scalingWidth * 0.27, scalingWidth * 0.4, scalingWidth * 0.3, scalingWidth * 0.054))
        self.latEastingLineEdit.setEnabled(False)

        # Lon/Northing Label
        self.lonNorthingLabel = QLabel(self.groupBox)
        ###self.lonNorthingLabel.setGeometry(QRect(52, 180, 45, 16))
        self.lonNorthingLabel.setGeometry(QRect(scalingWidth * 0.14, scalingWidth * 0.48, scalingWidth * 0.12, scalingWidth * 0.045))
        self.lonNorthingLabel.setText("Long:")

        # Lon/Northing Line Edit
        self.lonNorthingLineEdit = QLineEdit(self.groupBox)
        ###self.lonNorthingLineEdit.setGeometry(QRect(100, 180, 113, 20))
        self.lonNorthingLineEdit.setGeometry(QRect(scalingWidth * 0.27, scalingWidth * 0.48, scalingWidth * 0.3, scalingWidth * 0.054))
        self.lonNorthingLineEdit.setEnabled(False)

        # MGA Zone Label
        self.zoneLabel = QLabel(self.groupBox)
        ###self.zoneLabel.setGeometry(QRect(45, 210, 52, 16))
        self.zoneLabel.setGeometry(QRect(scalingWidth * 0.12, scalingWidth * 0.56, scalingWidth * 0.14, scalingWidth * 0.045))
        self.zoneLabel.setText("MGA Zone:")
        self.zoneLabel.setVisible(False)

        # Zones Combo Box
        self.zoneComboBox = QComboBox(self.groupBox)
        ###self.zoneComboBox.setGeometry(QRect(100, 210, 41, 22))
        self.zoneComboBox.setGeometry(QRect(scalingWidth * 0.27, scalingWidth * 0.56, scalingWidth * 0.11, scalingWidth * 0.059))
        self.zoneComboBox.addItem("50")
        self.zoneComboBox.addItem("51")
        self.zoneComboBox.addItem("52")
        self.zoneComboBox.addItem("49")
        self.zoneComboBox.setVisible(False)

        # Scale Combo Box
        self.scaleComboBox = QComboBox(self)
        #self.scaleComboBox.setGeometry(QRect(100, 270, 111, 22))
        ###self.scaleComboBox.setFixedWidth(111)
        self.scaleComboBox.setFixedWidth(scalingWidth * 0.3)
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
        self.leftSide.addWidget(self.scaleComboBox)
        self.leftSide.setAlignment(self.scaleComboBox, Qt.AlignHCenter)

        # Zoom button
        self.zoomButton = QPushButton(self)
        #self.zoomButton.setGeometry(QRect(100, 310, 111, 23))
        ###self.zoomButton.setFixedWidth(111)
        self.zoomButton.setFixedWidth(scalingWidth * 0.3)
        self.zoomButton.setText("Zoom")
        self.zoomButton.clicked.connect(self.zoomClickHandler)
        self.leftSide.addWidget(self.zoomButton)
        self.leftSide.setAlignment(self.zoomButton, Qt.AlignHCenter)

        # Locality Table View
        self.localityTable = QTableView(locationsTab)
        ###self.localityTable.setFixedWidth(421)
        self.localityTable.setFixedWidth(scalingWidth * 1.126)
        #self.localityTable.setGeometry(QRect(280, 20, 421, 301))
        header = ['Name', 'Feature', 'Latitude', 'Longitude']
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(header)
        self.localityTable.setModel(self.model)
        self.localityTable.resizeColumnsToContents()
        self.localityTable.verticalHeader().setVisible(False)
        #self.localityTable.setColumnWidth(0, 161)
        #self.localityTable.setColumnWidth(1, 100)
        #self.localityTable.setColumnWidth(2, 70)
        #self.localityTable.setColumnWidth(3, 70)
        self.localityTable.setColumnWidth(0, scalingWidth * 0.43)
        self.localityTable.setColumnWidth(1, scalingWidth * 0.27)
        self.localityTable.setColumnWidth(2, scalingWidth * 0.187)
        self.localityTable.setColumnWidth(3, scalingWidth * 0.187)
        self.localityTable.setFont(QFont("Arial", 7))
        self.localityTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.localityTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.localityTable.doubleClicked.connect(self.zoomClickHandler)
        self.rightSide.addWidget(self.localityTable)
        
            
        # PARCELS TAB
        # Survey Lot group
        self.surveyLotGroupBox = QGroupBox("Survey Lot", self)
        self.surveyLotGroupBox.setFont(semiBoldFont)
        surveyLotLayout = QFormLayout(self.surveyLotGroupBox)
        # 'Lot No' textbox & label
        self.lotNumberEdit = QLineEdit("", self)
        self.lotNumberEdit.setFont(normalFont)
        self.lotNumberLabel = QLabel("Lot No.:")
        self.lotNumberLabel.setFont(normalFont)
        surveyLotLayout.addRow(self.lotNumberLabel, self.lotNumberEdit)
        
        # Plan / Diagram radio buttons
        self.planDiagramGroupBox = QGroupBox("Plan / Diagram", self.surveyLotGroupBox)
        self.planDiagramGroupBox.setFont(normalFont)
        surveyLotLayout.addWidget(self.planDiagramGroupBox)
        self.radioButtonLayout = QHBoxLayout()
        self.planDiagramGroupBox.setLayout(self.radioButtonLayout)
        
        self.diagramRadioButton = QRadioButton(self)
        self.diagramRadioButton.setText("Diagram")
        self.diagramRadioButton.setFont(normalFont)
        self.radioButtonLayout.addWidget(self.diagramRadioButton)
        
        self.planRadioButton = QRadioButton(self)
        self.planRadioButton.setText("Plan")
        self.planRadioButton.setFont(normalFont)
        self.radioButtonLayout.addWidget(self.planRadioButton)
        
        self.eitherRadioButton = QRadioButton(self)
        self.eitherRadioButton.setText("Either")
        self.eitherRadioButton.setFont(normalFont)
        self.eitherRadioButton.setChecked(True)
        self.radioButtonLayout.addWidget(self.eitherRadioButton)        

        # 'Plan/Diag No' textbox & label
        self.planNumberEdit = QLineEdit("", self)
        self.planNumberEdit.setFont(normalFont)
        self.planNumberEdit.setToolTip("Plan or Diagram Number")
        self.planNumberLabel = QLabel("Number:")
        self.planNumberLabel.setFont(normalFont)
        self.planNumberLabel.setToolTip("Plan or Diagram Number")
        surveyLotLayout.addRow(self.planNumberLabel, self.planNumberEdit)

        # Crown Allotment group
        crnGroupBox = QGroupBox("Crown Allotment", self)
        crnGroupBox.setFont(semiBoldFont)
        crnLayout = QFormLayout(crnGroupBox)

        crnLocalityModel = self.populateCALocationCombo()
        self.CALocationCombo = QComboBox(self)
        self.CALocationCombo.setFont(normalFont)
        self.CALocationCombo.setModel(crnLocalityModel)
        self.CALocationLabel = QLabel("Location:")
        self.CALocationLabel.setFont(normalFont)
        crnLayout.addRow(self.CALocationLabel, self.CALocationCombo)
        self.CALocationCombo.currentIndexChanged.connect(self.CALocationChanged)

        self.CANumberCombo = QComboBox(self)
        self.CANumberCombo.setFont(normalFont)
        self.CANumberCombo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.CANumberLabel = QLabel("Number:")
        self.CANumberLabel.setFont(normalFont)
        crnLayout.addRow(self.CANumberLabel, self.CANumberCombo)     
        
        # Strata Plan group
        strataPlanGroupBox = QGroupBox("Strata Plan", self)
        strataPlanGroupBox.setFont(semiBoldFont)
        strataPlanLayout = QFormLayout(strataPlanGroupBox)
        # 'Strata Plan' textbox & label
        self.strataPlanEdit = QLineEdit("", self)
        self.strataPlanEdit.setFont(normalFont)
        self.strataPlanEdit.setToolTip("Just the number e.g. 12345")
        self.strataPlanLabel = QLabel("Strata Plan No.:")
        self.strataPlanLabel.setFont(normalFont)
        self.strataPlanLabel.setToolTip("Just the number e.g. 12345")
        strataPlanLayout.addRow(self.strataPlanLabel, self.strataPlanEdit)
        
        parcelsLayout.addRow(self.surveyLotGroupBox)
        parcelsLayout.addRow(crnGroupBox)
        parcelsLayout.addRow(strataPlanGroupBox)
        
        buttonsLayout = QHBoxLayout()
        parcelsLayout.addRow(buttonsLayout)
        self.parcelsOkButton = QPushButton("OK", self)
        self.parcelsOkButton.setToolTip("Returns records matching Survey Lot input OR Crown Allotment input OR Strata Plan input.")
        self.cancelButton = QPushButton("Cancel", self)
        self.clearButton = QPushButton("Clear", self)
        buttonsLayout.addWidget(self.parcelsOkButton)
        buttonsLayout.addWidget(self.clearButton)
        buttonsLayout.addWidget(self.cancelButton)

        self.parcelsOkButton.clicked.connect(self.validityCheck)
        self.clearButton.clicked.connect(self.parcelsClear)
        self.cancelButton.clicked.connect(self.reject)
        
        # ADDRESS TAB
        # Address group
        addressGroupBox = QGroupBox("Street Address", self)
        addressGroupBox.setFont(semiBoldFont)
        streetAddressLayout = QFormLayout(addressGroupBox)
        # 'Street No' textbox & label
        self.streetNumberEdit = QLineEdit("", self)
        self.streetNumberEdit.setToolTip("28, 28a, 28 A are all valid")
        self.streetNumberEdit.setFont(normalFont)
        self.streetNumberLabel = QLabel("No.:")
        self.streetNumberLabel.setFont(normalFont)
        streetAddressLayout.addRow(self.streetNumberLabel, self.streetNumberEdit)
        
        # 'Street Name' textbox & label
        self.streetNameEdit = QLineEdit("", self)
        self.streetNameEdit.setFont(normalFont)
        self.streetNameEdit.setToolTip("Do not include 'Rd', 'St' etc")
        self.streetNameLabel = QLabel("Street Name:")
        self.streetNameLabel.setFont(normalFont)
        self.streetNameEdit.setToolTip("Do not include 'Rd', 'St' etc")
        self.streetNameEdit.editingFinished.connect(self.populateLocalityCombo)
        streetAddressLayout.addRow(self.streetNameLabel, self.streetNameEdit)
        
        # 'Locality' model, combobox & label
        #localityModel = self.populateLocalityCombo()
        self.localityCombo = QComboBox(self)
        self.localityCombo.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.localityCombo.setFont(normalFont)
        localityModel = self.populateLocalityCombo()
        self.localityCombo.setModel(localityModel)
        self.localityCombo.insertItem(0, "")
        self.localityLabel = QLabel("Locality:")
        self.localityLabel.setFont(normalFont)
        streetAddressLayout.addRow(self.localityLabel, self.localityCombo)
        
        addressLayout.addRow(addressGroupBox)

        addressButtonsLayout = QHBoxLayout()
        addressLayout.addRow(addressButtonsLayout)
        self.addressOkButton = QPushButton("OK", self)
        self.addressCancelButton = QPushButton("Cancel", self)
        self.addressClearButton = QPushButton("Clear", self)
        addressButtonsLayout.addWidget(self.addressOkButton)
        addressButtonsLayout.addWidget(self.addressClearButton)
        addressButtonsLayout.addWidget(self.addressCancelButton)

        self.addressOkButton.clicked.connect(self.validityCheck)
        self.addressClearButton.clicked.connect(self.addressClear)
        self.addressCancelButton.clicked.connect(self.reject)

        # RESERVES TAB
        # Reserve Name / No group
        rsvNameNoGroupBox = QGroupBox("Reserve Name / Number", self)
        rsvNameNoGroupBox.setFont(semiBoldFont)
        rsvNameNoLayout = QGridLayout(rsvNameNoGroupBox)

        # 'Reserve Name' combobox & label
        rsvNameLabel = QLabel("Name:")
        reserveNameModel = self.populateRsvNameCombo()
        self.rsvNameCombo = QComboBox(self)
        self.rsvNameCombo.setFont(normalFont)
        self.rsvNameCombo.setModel(reserveNameModel)
        rsvNameNoLayout.addWidget(rsvNameLabel, 0, 0)
        rsvNameNoLayout.addWidget(self.rsvNameCombo, 0, 1)
        
        # 'Reserve Number' textbox & label
        rsvNumberLabel = QLabel("No.:")
        self.rsvNumberEdit = QLineEdit("", self)
        self.rsvNumberEdit.setFont(normalFont)
        rsvNameNoLayout.addWidget(rsvNumberLabel, 1, 0)
        rsvNameNoLayout.addWidget(self.rsvNumberEdit, 1, 1)
        
        # State Forest / Timber Reserve / Marine Reserve group
        # Group box
        stateForestEtcGroupBox = QGroupBox("State Forest / Timber Reserve / Marine Reserve", self)
        stateForestEtcGroupBox.setFont(semiBoldFont)
        stateForestEtcLayout = QGridLayout(stateForestEtcGroupBox)
        
        #State Forest
        self.stateForestRadioButton = QRadioButton(self)
        self.stateForestRadioButton.setText("State Forest")
        self.stateForestRadioButton.setChecked(True)
        self.stateForestRadioButton.setFont(normalFont)
        self.stateForestRadioButton.toggled.connect(self.stateForestToggled)
        self.stateForestCombo = QComboBox(self)
        self.stateForestCombo.setFont(normalFont)
        self.stateForestCombo.setEnabled(True)
        stateForestModel = self.populateStateForestCombo()
        self.stateForestCombo.setModel(stateForestModel)
        stateForestEtcLayout.addWidget(self.stateForestRadioButton, 0, 0)
        stateForestEtcLayout.addWidget(self.stateForestCombo, 0, 1)
        
        # Timber Reserve 
        self.timberRsvRadioButton = QRadioButton(self)
        self.timberRsvRadioButton.setText("Timber Reserve")
        self.timberRsvRadioButton.setFont(normalFont)
        self.timberRsvRadioButton.toggled.connect(self.timberRsvToggled)
        self.timberRsvCombo = QComboBox(self)
        self.timberRsvCombo.setFont(normalFont)
        self.timberRsvCombo.setEnabled(False)
        timberRsvModel = self.populateTimberRsvCombo()
        self.timberRsvCombo.setModel(timberRsvModel)
        stateForestEtcLayout.addWidget(self.timberRsvRadioButton, 1, 0)
        stateForestEtcLayout.addWidget(self.timberRsvCombo, 1, 1)
        
        # Marine Reserve
        self.marineRsvRadioButton = QRadioButton(self)
        self.marineRsvRadioButton.setText("Marine Reserve")
        self.marineRsvRadioButton.setFont(normalFont)
        self.marineRsvRadioButton.toggled.connect(self.marineRsvToggled)
        self.marineRsvCombo = QComboBox(self)
        self.marineRsvCombo.setFont(normalFont)
        self.marineRsvCombo.setEnabled(False)
        marineRsvModel = self.populateMarineRsvCombo()
        self.marineRsvCombo.setModel(marineRsvModel)
        stateForestEtcLayout.addWidget(self.marineRsvRadioButton, 2, 0)
        stateForestEtcLayout.addWidget(self.marineRsvCombo, 2, 1)
        
        rsvButtonsLayout = QHBoxLayout()
        self.rsvOKButton = QPushButton("OK", self)
        self.rsvOKButton.setToolTip("Returns records matching ANY above criteria ('OR' search)")
        self.rsvCancelButton = QPushButton("Cancel", self)
        self.rsvClearButton = QPushButton("Clear", self)
        rsvButtonsLayout.addWidget(self.rsvOKButton)
        rsvButtonsLayout.addWidget(self.rsvClearButton)
        rsvButtonsLayout.addWidget(self.rsvCancelButton)

        self.rsvOKButton.clicked.connect(self.validityCheck)
        self.rsvClearButton.clicked.connect(self.rsvClear)
        self.rsvCancelButton.clicked.connect(self.reject)

        reservesLayout.addRow(rsvNameNoGroupBox)
        reservesLayout.addRow(stateForestEtcGroupBox)
        reservesLayout.addRow(rsvButtonsLayout)
        
        # PIN TAB
        pinLayout = QFormLayout()
        pinTabLayout.addLayout(pinLayout)

        # PIN textbox & label
        self.pinEdit = QLineEdit("", self)
        self.pinEdit.setFont(normalFont)
        self.pinLabel = QLabel("PIN:")
        self.pinLabel.setFont(normalFont)
        pinLayout.addRow(self.pinLabel, self.pinEdit)
        
        pinButtonsLayout = QHBoxLayout()
        pinLayout.addRow(pinButtonsLayout)
        self.pinOkButton = QPushButton("OK", self)
        self.pinCancelButton = QPushButton("Cancel", self)
        self.pinClearButton = QPushButton("Clear", self)
        pinButtonsLayout.addWidget(self.pinOkButton)
        pinButtonsLayout.addWidget(self.pinClearButton)
        pinButtonsLayout.addWidget(self.pinCancelButton)

        self.pinOkButton.clicked.connect(self.validityCheck)
        self.pinClearButton.clicked.connect(self.pinClear)
        self.pinCancelButton.clicked.connect(self.reject)
        
        # OWNER TAB
        ownerLayout = QFormLayout()
        ownerTabLayout.addLayout(ownerLayout)

        # Owner textbox & label
        self.ownerEdit = QLineEdit("", self)
        self.ownerEdit.setFont(normalFont)
        self.ownerLabel = QLabel("Owner:")
        self.ownerLabel.setFont(normalFont)
        ownerLayout.addRow(self.ownerLabel, self.ownerEdit)
        
        ownerButtonsLayout = QHBoxLayout()
        ownerLayout.addRow(ownerButtonsLayout)
        self.ownerOkButton = QPushButton("OK", self)
        self.ownerCancelButton = QPushButton("Cancel", self)
        self.ownerClearButton = QPushButton("Clear", self)
        ownerButtonsLayout.addWidget(self.ownerOkButton)
        ownerButtonsLayout.addWidget(self.ownerClearButton)
        ownerButtonsLayout.addWidget(self.ownerCancelButton)

        self.ownerOkButton.clicked.connect(self.validityCheck)
        self.ownerClearButton.clicked.connect(self.ownerClear)
        self.ownerCancelButton.clicked.connect(self.reject)
        
        # SETTINGS TAB
        
        # Local database info
        databaseLayout = QFormLayout()
        settingsLayout.addLayout(databaseLayout)
        self.localDatabaseEdit = QLineEdit("", self)
        self.localDatabaseEdit.setText(self.db_settings.local_cadastre_db)
        self.localDatabaseEdit.setReadOnly(True)
        self.databaseLabel = QLabel("Local database:")
        databaseLayout.addRow(self.databaseLabel, self.localDatabaseEdit)
        self.lastUpdateEdit = QLineEdit("", self)
        last_update = self.get_last_update()
        self.lastUpdateEdit.setText(last_update)
        self.lastUpdateEdit.setReadOnly(True)
        databaseLayout.addRow("Last update:", self.lastUpdateEdit)
        self.cadastreGdbText = QTextEdit("", self)
        self.cadastreGdbText.setText(self.db_settings.cadastre_gdb)
        self.cadastreGdbText.setReadOnly(True)
        databaseLayout.addRow("Master geodatabase:", self.cadastreGdbText)
        
        # Reset Button
        resetLayout = QFormLayout()
        resetLayout.setFormAlignment(Qt.AlignHCenter)
        settingsLayout.addLayout(resetLayout)
        self.resetButton = QPushButton("Reset", None)
        resetLayout.addRow(self.resetButton)
        self.resetButton.clicked.connect(self.resetCadastre)
            
        #self.tabWidget.setFixedWidth(720)
        #self.setFixedWidth(744)
        self.tabWidget.setFixedWidth(self.requiredWidth() * 1.925)
        self.setFixedWidth(self.requiredWidth() * 2)
        self.setModal(False)
        
    def get_last_update(self):
        if os.path.isfile(self.db_settings.local_cadastre_db):
            try:
                last_update_sql = "SELECT MAX(last_update) FROM last_update"
                conn = sqlite3.connect(self.db_settings.local_cadastre_db)
                with conn:
                    csr = conn.cursor()
                    csr.execute(last_update_sql)
                    last_update = csr.fetchall()[0][0]
                    csr.close()
                conn.close()
                # last_update is in unix time, convert to human-readable string
                return datetime.datetime.fromtimestamp(last_update).strftime('%Y-%m-%d %H:%M:%S')
            except:
                return ""
        else:
            return ""

    def resetCadastre(self):
        response = QMessageBox.warning(None, "Reset", "Make sure no other instances of QGIS are open on your computer.  The cadastre database on this machine will be restored.  This should take less than 10 minutes.  Do you wish to continue?", QMessageBox.Ok|QMessageBox.Cancel)
        if response == QMessageBox.Ok:
            # Additional code 15-Aug-2018 to beef up reset
            currentDirectory = os.path.dirname(os.path.abspath(__file__))
            parentDirectory = os.path.abspath(os.path.join(currentDirectory, os.pardir))
            usageLocation = self.db_settings.local_cadastre_db
            templateLocation = os.path.join(parentDirectory, "searchcadastre/resources/cadastre.sqlite")
            # Close connection if it exists
            #if conn:
            #    conn.close()
                #conn = None
           #     QMessageBox.information(None, "", "conn closed")
            # Check if usage file exists and if so, copy
            if os.path.isfile(usageLocation):
                try:
                    os.remove(usageLocation)
                    QMessageBox.information(None, "Old database removed!", "Old database removed!")
                except:
                    QMessageBox.information(None, "Old database could not be removed!", "There is an existing connection to the database.  The tool will attempt to overwrite the current data.")
            # Check if usage file exists and if not, copy
            if not os.path.isfile(usageLocation):
                shutil.copyfile(templateLocation, usageLocation)
            else:   # Check for 0kb
                if os.path.isfile(usageLocation):
                    if os.path.getsize(usageLocation) == 0:
                        try:
                            shutil.copyfile(templateLocation, usageLocation)
                            if os.path.getsize(usageLocation) == 0:
                                QMessageBox.information(None, "", "Local database is empty.  Contact GIS Apps for assistance.")
                                return
                        except:
                            QMessageBox.information(None, "", "Copying to local database failed.  Contact GIS Apps for assistance.")
                            return
            # End of additional code

            v_drive_mod_date = os.path.getmtime(self.db_settings.cadastre_gdb)
            success = self.copyCadastre(v_drive_mod_date)
            
            # Show completion message then close and delete current dialogue
            if success:
                QMessageBox.information(None, "Reset complete!", "The local cadastre database has been updated and is now ready to use.")
            else:
                QMessageBox.information(None, "Reset failed!", "The local cadastre database could not be updated.  Contact GIS Apps.")
            self.close()
            self = None
    
    def requiredWidth(self):
        width = 0
        tabCount = self.tabWidget.count()
        for tab in range(tabCount):
            width += self.tabWidget.tabBar().tabRect(tab).width()
        return width

    def stateForestToggled(self):
        self.stateForestCombo.setEnabled(True)
        self.timberRsvCombo.setCurrentIndex(0)
        self.timberRsvCombo.setEnabled(False)
        self.marineRsvCombo.setCurrentIndex(0)
        self.marineRsvCombo.setEnabled(False)

    def timberRsvToggled(self):
        #self.stateForestEdit.setEnabled(False)
        #self.stateForestEdit.setText("")
        self.stateForestCombo.setEnabled(False)
        self.stateForestCombo.setCurrentIndex(0)
        self.timberRsvCombo.setEnabled(True)
        self.marineRsvCombo.setCurrentIndex(0)
        self.marineRsvCombo.setEnabled(False)

    def marineRsvToggled(self):
        #self.stateForestEdit.setEnabled(False)
        #self.stateForestEdit.setText("")
        self.stateForestCombo.setEnabled(False)
        self.stateForestCombo.setCurrentIndex(0)
        self.timberRsvCombo.setCurrentIndex(0)
        self.timberRsvCombo.setEnabled(False)
        self.marineRsvCombo.setEnabled(True)   

    def tabDefaultButton(self):
        requiredWidth = self.requiredWidth()
        if self.tabWidget.currentIndex() == 0:    # Locations
            self.tabWidget.setFixedWidth(requiredWidth * 1.925)
            self.tabWidget.setFixedHeight(requiredWidth * 0.98)
            self.setFixedWidth(requiredWidth * 2)
            self.setFixedHeight(requiredWidth * 1.09)
            self.setWindowTitle("Zoom to Location")
        elif self.tabWidget.currentIndex() == 1:      # Parcels
            self.parcelsOkButton.setDefault(True)
            self.tabWidget.setFixedWidth(requiredWidth)
            self.tabWidget.setFixedHeight(requiredWidth * 1.02)
            self.setFixedWidth(requiredWidth * 1.07)
            self.setFixedHeight(requiredWidth * 1.12)
            self.setWindowTitle("Search Cadastre")
        elif self.tabWidget.currentIndex() == 2:    # Addresses
            self.addressOkButton.setDefault(True)
            self.tabWidget.setFixedWidth(requiredWidth)
            self.tabWidget.setFixedHeight(requiredWidth * 0.48)
            self.setFixedWidth(requiredWidth * 1.07)
            self.setFixedHeight(requiredWidth * 0.59)
            self.setWindowTitle("Search Cadastre")
        elif self.tabWidget.currentIndex() == 3:    # Reserves
            self.rsvOKButton.setDefault(True)
            self.tabWidget.setFixedWidth(requiredWidth * 1.05)
            self.tabWidget.setFixedHeight(requiredWidth * 0.65)
            self.setFixedWidth(requiredWidth * 1.1)
            self.setFixedHeight(requiredWidth * 0.75)            
            self.setWindowTitle("Search Cadastre")
        elif self.tabWidget.currentIndex() == 4:    # PIN
            self.pinOkButton.setDefault(True)
            self.tabWidget.setFixedWidth(requiredWidth)
            self.tabWidget.setFixedHeight(requiredWidth * 0.27)
            self.setFixedWidth(requiredWidth * 1.07)
            self.setFixedHeight(requiredWidth * 0.37)
            self.setWindowTitle("Search Cadastre")
        elif self.tabWidget.currentIndex() == 5:    # Owner
            self.ownerOkButton.setDefault(True)
            self.tabWidget.setFixedWidth(requiredWidth)
            self.tabWidget.setFixedHeight(requiredWidth * 0.27)
            self.setFixedWidth(requiredWidth * 1.07)
            self.setFixedHeight(requiredWidth * 0.37)
            self.setWindowTitle("Search Cadastre")
        elif self.tabWidget.currentIndex() == 6:    # Settings
            self.tabWidget.setFixedWidth(requiredWidth)
            self.tabWidget.setFixedHeight(requiredWidth * 0.48)
            self.setFixedWidth(requiredWidth * 1.07)
            self.setFixedHeight(requiredWidth * 0.59)
            self.resetButton.setFixedWidth(requiredWidth * 0.2)
            self.setWindowTitle("Search Cadastre")
    
    def copyCadastre(self, v_drive_mod_date):
        success = False
        try:
            # delete existing data from table
            conn = sqlite3.connect(self.db_settings.local_cadastre_db)
            with conn:
                conn.execute('DELETE FROM state_cadastre')
            conn.close()
            # for timing during development:
            start_hr = time.localtime()[3]
            start_min = time.localtime()[4]
            start_sec = time.localtime()[5]
            #
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
            driver = ogr.GetDriverByName("OpenFileGDB")
            data_source = driver.Open(self.db_settings.cadastre_gdb)
            cadastre_fc = data_source.GetLayer(self.db_settings.cadastre_fc)
            # Check whether all expected fields are present
            layer_definition = cadastre_fc.GetLayerDefn()
            # list of tuples of sqlite/ GDB field name pairs
            expected_fields = {"CAD_PIN": "PIN",
                               "CAD_CENT_LONGITUDE": "CENTLONG", 
                               "CAD_CENT_LATITUDE": "CENTLAT", 
                               "CAD_LOT_NUMBER": "LOTNO", 
                               "CAD_HOUSE_NUMBER": "HOUSE_NUMB", 
                               "CAD_ROAD_NAME": "ROAD_NAME", 
                               "CAD_ROAD_TYPE": "ROAD_TYPE", 
                               "CAD_ROAD_SUFFIX": "ROAD_SUFFI", 
                               "CAD_LOCALITY": "LOCALITY", 
                               "CAD_POSTCODE": "POSTCODE", 
                               "CAD_PITYPE_1": "PITYPE_1", 
                               "CAD_PITYPE_2": "PITYPE_2", 
                               "CAD_PITYPE_3_1": "PITYPE_3_1", 
                               "CAD_PITYPE_3_2": "PITYPE_3_2", 
                               "CAD_REG_NUMBER": "REGNO", 
                               "CAD_REG_NUMBER_FORMATED": "REGNO_FORM",
                               "CAD_OWNER_NAME": "OWNER_NAME", 
                               "CAD_STRATA": "STRATA", 
                               "CAD_OWNERSHIP": "OWNERSHIP"}
            gdb_cadastre_fields = []
            sqlite_fields = []
            numeric_fields = ["PIN", "CENTLAT", "CENTLONG", "LOTNO", "POSTCODE"]
            for i in range(layer_definition.GetFieldCount()):
                field_name = layer_definition.GetFieldDefn(i).GetName()
                if field_name in expected_fields:
                    gdb_cadastre_fields.append(field_name)
                    sqlite_fields.append(expected_fields[field_name])
            for field in expected_fields:
                if field not in gdb_cadastre_fields:
                    QMessageBox.information(None, "Missing field!", field + " column not found in state_cadastre layer.  Contact GIS Apps. Filling the database will continue but some search functions may not work correctly.")
                #else:
                    # ensure correct order
                #    found_fields_ordered.append(expected_fields[field])
            #i = 0  #For testing
            record_lists = []
            for feature in cadastre_fc:
                #if i < 50000:   #For testing
                fid = feature.GetFID()
                values = [feature.GetField(field_name) for field_name in gdb_cadastre_fields]
                record_lists.append([str(fid)] + values)
                #i += 1
                #else:    #For testing
                #    break    #For testing
            sql = "INSERT INTO state_cadastre (OBJECTID, " + str(sqlite_fields)[1:-1] + ") VALUES(" + ("?," * (len(sqlite_fields) + 1))[:-1] + ")"        # +1 is for OBJECTID
            conn = sqlite3.connect(self.db_settings.local_cadastre_db)
            with conn:
                conn.executemany(sql, record_lists)
                conn.execute("DELETE FROM last_update")
                conn.execute("INSERT INTO last_update VALUES(" + str(v_drive_mod_date) + ")")
            conn.close()
            crnLocalityModel = self.populateCALocationCombo()
            self.CALocationCombo.setModel(crnLocalityModel)
            localityModel = self.populateLocalityCombo()
            self.localityCombo.setModel(localityModel)
            reserveNameModel = self.populateRsvNameCombo()
            self.rsvNameCombo.setModel(reserveNameModel)
            timberRsvModel = self.populateTimberRsvCombo()
            self.timberRsvCombo.setModel(timberRsvModel)
            success = True
        except:
            QMessageBox.information(None, "Error copying data", "There was a problem copying the cadastre data from V: drive to the local database.")
        finally:
            QApplication.restoreOverrideCursor()
            # Following code is for test purposes
            #end_hr = time.localtime()[3]
            #end_min = time.localtime()[4]
            #end_sec = time.localtime()[5]
            #elapsed = (end_hr - start_hr)*3600 + (end_min - start_min)*60 + (end_sec - start_sec)
            #QMessageBox.information(None, "", str(elapsed))
            return success
            
    def populateLocalityCombo(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        localityList = []
        if self.streetNameEdit.text().strip() == "":
            sqlString = "SELECT DISTINCT locality FROM state_cadastre ORDER BY LOCALITY"
        else:
            sqlString = "SELECT DISTINCT locality FROM state_cadastre WHERE road_name = ? ORDER BY LOCALITY"
        rows = []
        conn = sqlite3.connect(self.db_settings.local_cadastre_db)
        if conn is not None:
            try:
                with conn:
                    csr = conn.cursor()
                    csr.execute(sqlString, (self.streetNameEdit.text().strip().upper(),))
                    #csr.execute(sqlString)
                    rows = csr.fetchall()
                    csr.close()
                for row in rows:
                    localityList.append(row[0])
            except:
                pass
        conn.close()
        self.localityCombo.setModel(QStringListModel(localityList))
        QApplication.restoreOverrideCursor()
        return QStringListModel(localityList)

    def populateCALocationCombo(self):
        locationList = [""] 
        sqlString = "SELECT district_name FROM crn_allt_dist_codes ORDER BY district_name"
        rows = []
        conn = sqlite3.connect(self.db_settings.local_cadastre_db)
        if conn is not None:
            try:
                with conn:
                    csr = conn.cursor()
                    csr.execute(sqlString)
                    rows = csr.fetchall()
                    csr.close()
                for row in rows:
                    locationList.append(row[0])
            except:
                pass
        conn.close()
        return QStringListModel(locationList)

    def CALocationChanged(self):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        prelimList = []
        interimList = []
        location = self.CALocationCombo.currentText()
        if location == "":
            self.CANumberCombo.setModel(QStringListModel([""]))
            QApplication.restoreOverrideCursor()
            return
        sqlString = "SELECT DISTINCT PITYPE_2 FROM state_cadastre WHERE PITYPE_2 LIKE '" + (location + "   ")[:5] + "%'"
        rows = []
        conn = sqlite3.connect(self.db_settings.local_cadastre_db)
        with conn:
            csr = conn.cursor()
            csr.execute(sqlString)
            rows = csr.fetchall()
            csr.close()
        conn.close()
        for row in rows:
            finalPart = row[0][row[0].strip().rfind(" "):]
            if finalPart not in prelimList:
                prelimList.append(finalPart)
        # prelimList consists of strings; if these can be converted to integers do so.  
        # Then sort and convert back to strings (required for model).
        for item in prelimList:
            try:
                interimList.append(int(item))
            except:
                interimList.append(item.strip())
        lotList = [str(item) for item in sorted(interimList)]
        self.CANumberCombo.setModel(QStringListModel(lotList))
        QApplication.restoreOverrideCursor()

    def populateTimberRsvCombo(self):
        prelimList = []
        interimList = []
        rows = []
        sqlString = "SELECT DISTINCT identifier FROM dept_info_legislated WHERE identifier LIKE 'O %' ORDER BY identifier"
        estate_conn = sqlite3.connect(self.db_settings.estate_db)
        try:
            with estate_conn:
                csr = estate_conn.cursor()
                csr.execute(sqlString)
                rows = csr.fetchall()
                csr.close()
            for row in rows:
                prelimList.append(row[0])
        except:
            pass
        if len(prelimList) == 0:
            return QStringListModel([])
        else:
            return QStringListModel([""] + prelimList)

    def populateStateForestCombo(self):
        prelimList = []
        interimList = []
        rows = []
        sqlString = "SELECT DISTINCT identifier FROM dept_info_legislated WHERE identifier LIKE 'F %' ORDER BY identifier"
        estate_conn = sqlite3.connect(self.db_settings.estate_db)
        try:
            with estate_conn:
                csr = estate_conn.cursor()
                csr.execute(sqlString)
                rows = csr.fetchall()
                csr.close()
            for row in rows:
                prelimList.append(row[0])
        except:
            pass
        if len(prelimList) == 0:
            return QStringListModel([])
        else:
            return QStringListModel([""] + prelimList)
            
    def populateMarineRsvCombo(self):
        prelimList = []
        interimList = []
        rows = []
        sqlString = "SELECT DISTINCT identifier FROM dept_info_legislated WHERE purpose LIKE 'Marine %' ORDER BY identifier"
        estate_conn = sqlite3.connect(self.db_settings.estate_db)
        try:
            with estate_conn:
                csr = estate_conn.cursor()
                csr.execute(sqlString)
                rows = csr.fetchall()
                csr.close()
            for row in rows:
                prelimList.append(row[0])
        except:
            pass
        if len(prelimList) == 0:
            return QStringListModel([])
        else:
            return QStringListModel([""] + prelimList)

    def populateRsvNameCombo(self):
        reserveNameList = [""]
        sqlString = "SELECT DISTINCT name FROM dept_info_legislated ORDER BY name"
        rows = []
        estate_conn = sqlite3.connect(self.db_settings.estate_db)
        #try:
        with estate_conn:
            csr = estate_conn.cursor()
            csr.execute(sqlString)
            rows = csr.fetchall()
            csr.close()
        for row in rows:
            if row[0].strip() != "":
                reserveNameList.append(row[0])
        #except:
        #    pass
        del estate_conn
        return QStringListModel(sorted(reserveNameList))

    def validityCheck(self):
        # Check valid input for parcel search
        if self.tabWidget.currentIndex() == 1:
            if self.lotNumberEdit.text().strip() == "" and self.planNumberEdit.text().strip() == "" and self.CALocationCombo.currentText().strip() == "" and self.CANumberCombo.currentText().strip() == "" and self.strataPlanEdit.text().strip() == "":
                self.lotNumberEdit.setFocus()
                QMessageBox.information(None, "Invalid input", "You must enter a value for one or more of:\n\tLot No,\n\tPlan/Diagram No,\n\tCrown Allotment or\n\tStrata Plan No." )
                return
        # Check valid input for address search
        elif self.tabWidget.currentIndex() == 2:
            if self.streetNumberEdit.text().strip() == "" and self.streetNameEdit.text().strip() == "":
                self.streetNumberEdit.setFocus()
                QMessageBox.information(None, "Invalid input", "You must enter a value for one or more of:\n\tStreet No or\n\tStreet Name" )
                return
        # Check valid input for reserve search
        elif self.tabWidget.currentIndex() == 3:
            if self.stateForestCombo.currentText().strip() == "" and self.timberRsvCombo.currentText().strip() == "" and self.marineRsvCombo.currentText().strip() == "" and self.rsvNameCombo.currentText().strip() == "" and self.rsvNumberEdit.text().strip() == "":
                QMessageBox.information(None, "Invalid input", "You must enter a value for one or more of:\n\tState Forest No,\n\tTimber Reserve No,\n\tMarine Reserve No,\n\tReserve Name or\n\tReserve No." )
                return
        # Check valid input for PIN search
        elif self.tabWidget.currentIndex() == 4:
            if not self.pinEdit.text().isnumeric():
                self.pinEdit.setText("")
                self.pinEdit.setFocus()
                QMessageBox.information(None, "Invalid input", "You must enter a numeric value for PIN")
                return
        # Check valid input for owner search
        elif self.tabWidget.currentIndex() == 5:
            if self.ownerEdit.text().strip() == "":
                self.ownerEdit.setFocus()
                QMessageBox.information(None, "Invalid input", "You must enter a value for Owner")
                return
        # If no layers in canvas, add WA_box (speeds up process; will be removed asap)
        layerCount = QgsMapLayerRegistry.instance().count()
        if layerCount == 0:
            # Get location of this file and use it to determine location of WA_box shp
            currentDirectory = os.path.dirname(os.path.abspath(__file__))
            waBoxLocation = os.path.join(currentDirectory, "resources/WA_box.shp")
            global waBoxLayer
            waBoxLayer = QgsVectorLayer(waBoxLocation, "WA_box", "ogr")
            mapCanvasLayer = QgsMapCanvasLayer(waBoxLayer)
            QgsMapLayerRegistry.instance().addMapLayer(waBoxLayer)
            self.canvas.setLayerSet([mapCanvasLayer])
            self.waBoxAdded = True
            self.canvas.mapCanvasRefreshed.connect(self.accept)
            self.canvas.refresh()
        else:
            self.accept()
            
    def removeWaBox(self):
        registry = QgsMapLayerRegistry.instance()
        layers = registry.mapLayersByName("WA_box")
        for layer in layers:
            try:
                if layer.name() == "WA_box":
                    registry.removeMapLayer(layer.id())
            except:
                pass
        
    def accept(self):
        # redirect to appropriate handler
        try:
            self.canvas.mapCanvasRefreshed.disconnect(self.accept)
        except:
            pass
        if self.tabWidget.currentIndex() == 1:
            self.parcelSearch()
        elif self.tabWidget.currentIndex() == 2:
            self.addressSearch()            
        elif self.tabWidget.currentIndex() == 3:
            self.reserveSearch()
        elif self.tabWidget.currentIndex() == 4:
            self.pinSearch()
        elif self.tabWidget.currentIndex() == 5:
            self.ownerSearch()

    def parcelSearch(self):
        global searchString
        searchString = ""
        surveyLotSQL = ""
        crownAllotmentSQL = ""        
        strataSQL = ""
        
        # survey lot part of search string
        either = False
        if self.eitherRadioButton.isChecked():
            either = True
        if self.lotNumberEdit.text().strip().lstrip("0") != "" or self.planNumberEdit.text().strip() != "":
            if self.lotNumberEdit.text().strip().lstrip("0") != "":
                surveyLotSQL += "lotno = '" + self.lotNumberEdit.text().strip() + "'"
                if self.diagramRadioButton.isChecked():
                    surveyLotSQL += " AND PITYPE_1 LIKE 'D"
                elif self.planRadioButton.isChecked():
                    surveyLotSQL += " AND PITYPE_1 LIKE 'P"
                if self.planNumberEdit.text().strip() != "":
                    if either:
                        surveyLotSQL += " AND (PITYPE_1 LIKE 'D" + ("000000" + self.planNumberEdit.text().strip())[-6:] + " %' OR PITYPE_1 LIKE 'P" + ("000000" + self.planNumberEdit.text().strip())[-6:] + " %')"
                    else:
                        surveyLotSQL += ("000000" + self.planNumberEdit.text().strip())[-6:] + " %'"
                else:
                    if not either:
                        surveyLotSQL += "%'"
            else:
                if self.diagramRadioButton.isChecked():
                    surveyLotSQL += "PITYPE_1 LIKE 'D" + ("000000" + self.planNumberEdit.text().strip())[-6:] + " %'"
                elif self.planRadioButton.isChecked():
                    surveyLotSQL += "PITYPE_1 LIKE 'P" + ("000000" + self.planNumberEdit.text().strip())[-6:] + " %'"
                else:
                    surveyLotSQL += "PITYPE_1 LIKE 'D" + ("000000" + self.planNumberEdit.text().strip())[-6:] + " %' OR PITYPE_1 LIKE 'P" + ("000000" + self.planNumberEdit.text().strip())[-6:] + " %'"
            searchString += surveyLotSQL
            
        # Crown Allotment part of search string
        if self.CALocationCombo.currentText() != "" and self.CANumberCombo.currentText() != "":
            crn_allt_dist_sql = "SELECT abbr_district_name FROM crn_allt_dist_codes WHERE district_name = '" + self.CALocationCombo.currentText() + "'"
            dist_abbr = None
            conn = sqlite3.connect(self.db_settings.local_cadastre_db)
            with conn:
                csr = conn.cursor()
                csr.execute(crn_allt_dist_sql)
                dist_abbr = csr.fetchall()[0][0] 
                csr.close()
            conn.close()
            if dist_abbr is None:
                QMessageBox.information(None, "Error reading database!", "A code for " + self.CALocationCombo.currentText() + " could not be found in table crn_allt_dist_codes.  Contact GIS Apps.")
                return
            crownAllotmentSQL += "PITYPE_2 LIKE '" + dist_abbr + "% " + ("0000" + self.CANumberCombo.currentText())[-5:] + "'"
            if searchString == "":
                searchString = crownAllotmentSQL
            else:
                searchString += " OR " + crownAllotmentSQL            
        
        # strata plan part of search string
        if self.strataPlanEdit.text().strip() != "":
            strataSQL = "PITYPE_1 = 'S" + ("00000" + self.strataPlanEdit.text().strip())[-6:] + "'"
            if searchString == "":
                searchString = strataSQL
            else:
                searchString += " OR " + strataSQL

        # Perform final search
        self.finalSearch("parcel")
        
    def addressSearch(self):
        global searchString
        searchString = ""

        if self.streetNumberEdit.text().strip() != "" or self.streetNameEdit.text().strip() != "" or self.localityCombo.currentText().strip() != "":
            if self.streetNumberEdit.text().strip() != "":
                if self.streetNumberEdit.text().strip()[-1].isalpha():
                    numberPart = self.streetNumberEdit.text()[:-1].strip()
                    searchString = "HOUSE_NUMB = '" + numberPart + "'"
                else:
                    searchString = "HOUSE_NUMB = '" + self.streetNumberEdit.text().strip() + "'"
            if self.streetNameEdit.text().strip() != "":
                if searchString != "":
                    searchString += " AND"
                searchString += " ROAD_NAME = '" + self.streetNameEdit.text().strip().upper() + "'"
            if self.localityCombo.currentText().strip() != "":
                if searchString != "":
                    searchString += " AND"
                searchString += " LOCALITY = '" + self.localityCombo.currentText().strip().upper() + "'"

        # Perform final search
        self.finalSearch("address")        

    def reserveSearch(self):    # Updated
        global searchString
        searchString = ""
        # State Forest etc part
        if self.stateForestCombo.currentText().strip() != "":
            #searchString += "RESERVE LIKE '%STATE FOREST " + self.stateForestEdit.text().strip() + "'"
            searchString += "IDENTIFIER = '" + self.stateForestCombo.currentText() + "'"
        elif self.timberRsvCombo.currentText() != "":
            #searchString += "RESERVE LIKE '%TIMBER RESERVE " + self.timberRsvCombo.currentText() + "'"
            searchString += "IDENTIFIER = '" + self.timberRsvCombo.currentText() + "'"
        elif self.marineRsvCombo.currentText() != "":
            #searchString += "RESERVE LIKE '%MARINE RESERVE " + self.marineRsvEdit.text().strip() + "'"
            searchString += "IDENTIFIER = '" + self.marineRsvCombo.currentText() + "'"
        # 'OR' clause (if required)
        if searchString != "":
            if self.rsvNameCombo.currentText() != "" or self.rsvNumberEdit.text().strip() != "":
                searchString += " OR "            
        if self.rsvNameCombo.currentText() != "" or self.rsvNumberEdit.text().strip() != "":
            if self.rsvNameCombo.currentText() != "":
                #searchString += "RES_NAME = '" + self.rsvNameCombo.currentText() + "'"
                searchString += "NAME = '" + self.rsvNameCombo.currentText() + "'"
                if self.rsvNumberEdit.text().strip() != "":
                    searchString += " OR "
            if self.rsvNumberEdit.text().strip() != "":
                #searchString += "RES_NO = '" + self.rsvNumberEdit.text() + "' OR RES_NO = '" + self.rsvNumberEdit.text() + ";'"
                searchString += "IDENTIFIER = 'R" + ("      " + self.rsvNumberEdit.text())[-6:] + "'"
        pins = self.interimReserveSearch()
        searchString = "PIN IN (" + pins + ")"
        self.finalSearch("reserve")

    def interimReserveSearch(self):
        sql = "SELECT pin FROM lands_and_waters_legislated WHERE " + searchString
        rows = []
        pinList = []
        estate_conn = sqlite3.connect(self.db_settings.estate_db)
        with estate_conn:
            csr = estate_conn.cursor()
            csr.execute(sql)
            rows = csr.fetchall()
            csr.close()
        for row in rows:
            pinList.append(row[0])
        del estate_conn
        return str(pinList)[1:-1]

    def pinSearch(self):    # Updated
        global searchString
        searchString = "PIN = " + self.pinEdit.text()
        self.finalSearch("pin")

    def ownerSearch(self):
        global searchString
        searchString = "OWNER_NAME LIKE '%" + self.ownerEdit.text() + "%'"
        self.finalSearch("owner")
        
    def finalSearch(self, searchType):
        # Get count of records meeting search criteria 
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        global totalCount
        totalCount = 0
        rows = []
        objectids = []
        conn = sqlite3.connect(self.db_settings.local_cadastre_db)
        with conn:
            csr = conn.cursor()
            csr.execute("SELECT objectid FROM state_cadastre WHERE " + searchString)
            rows = csr.fetchall()
            csr.close()
        conn.close()
        totalCount = len(rows)
        QApplication.restoreOverrideCursor()
               
        if totalCount == 0:
            self.removeWaBox()            
            QMessageBox.information(None, "result", searchString + " not found.")
            return
        if totalCount > 1:
            for row in rows:
                objectids.append(row[0])
            multipleResults = MultipleResultsDialog(self, searchType, objectids)
        elif totalCount == 1:
            self.zoomToCadastralUnit(rows)
            
    def zoomToCadastralUnit(self, objectids):
        id = objectids[0][0]
        finalZoom([id], self.db_settings)
        self.pointTool = ShowAttributesTool(self.canvas, [id], self.db_settings)
        self.pointTool.canvasClicked.connect(lambda: self.pointTool.canvasPressEvent([id]))
        self.canvas.setMapTool(self.pointTool)

        #QApplication.restoreOverrideCursor()
        self.close()

    def parcelsClear(self):
        self.lotNumberEdit.setText("")
        self.eitherRadioButton.setChecked(True)
        self.planNumberEdit.setText("")
        self.CALocationCombo.setCurrentIndex(0)
        self.strataPlanEdit.setText("")
        
    def addressClear(self):
        self.streetNumberEdit.setText("")
        self.streetNameEdit.setText("")
        self.localityCombo.setCurrentIndex(0)
        
    def rsvClear(self):
        self.stateForestRadioButton.setChecked(False)
        self.timberRsvRadioButton.setChecked(False)
        self.marineRsvRadioButton.setChecked(False)
        self.stateForestCombo.setCurrentIndex(0)
        self.timberRsvCombo.setCurrentIndex(0)
        self.marineRsvCombo.setCurrentIndex(0)
        self.rsvNameCombo.setCurrentIndex(0)
        self.rsvNumberEdit.setText("")

    def pinClear(self):
        self.pinEdit.setText("")

    def ownerClear(self):
        self.ownerEdit.setText("")

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

    def zoomToLatLon(self, lat, lon):
        epsg = 4283
        self.zoomToCoords(lon, lat, epsg)

    def zoomToMGACoords(self, easting, northing):
        epsg = 28300 + int(self.zoneComboBox.currentText())
        self.zoomToCoords(easting, northing, epsg)

    def zoomToCoords(self, x, y, epsg):      # Adapted from http://www.qgis.nl/2014/07/10/qgis-processing-scripts-gebruiken/?lang=en
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
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

        # some magic to let the marker disappear 5 seconds
        def timer_fired():
            qgis.utils.iface.mapCanvas().scene().removeItem(m)
            timer.stop()

        timer = QTimer()
        timer.timeout.connect(timer_fired)
        timer.setSingleShot(True)
        timer.start(4000)
        self.close()
        QApplication.restoreOverrideCursor()

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
                            QStandardItem(field)
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
                            QStandardItem(field)
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

    def dataCurrencyCheck(self):
        if not os.path.exists(self.db_settings.cadastre_gdb):
            #QMessageBox.information(None, "Source data not found!", "The tool expected to find a file geodatabase holding state-wide cadastre data at " + self.db_settings.cadastre_gdb + " but it could not be found.  The search tool will work, but your search data may be out of date.  Contact GIS Apps.")
            return
        v_drive_mod_date = os.path.getmtime(self.db_settings.cadastre_gdb)
        last_update_sql = "SELECT MAX(last_update) FROM last_update"
        state_cadastre_sql = "SELECT COUNT (*) FROM state_cadastre"
        state_cadastre_count = 0
        conn = sqlite3.connect(self.db_settings.local_cadastre_db)
        with conn:
            csr = conn.cursor()
            csr.execute(last_update_sql)
            last_update = csr.fetchall()[0][0]
            csr.execute(state_cadastre_sql)
            state_cadastre_count += csr.fetchall()[0][0]
            csr.close()
        conn.close()
        if state_cadastre_count == 0:
            reply = QMessageBox.question(None, "Database not populated yet!", "The database needed for the Search Cadastre tool has not yet been populated.  Filling will take 10 minutes or so.  Do you wish to continue?", QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.copyCadastre(str(int(v_drive_mod_date)))
            else:
                self.close()
        elif last_update is not None and int(v_drive_mod_date) > last_update:
            reply = QMessageBox.question(None, "Database out of date!", "The database needed for the Search Cadastre must be updated.  This will take 10 minutes or so.  Do you wish to continue?", QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.copyCadastre(str(int(v_drive_mod_date)))
            else:
                self.close()
            

class MultipleResultsDialog(QDialog):
    def __init__(self, initialDialog, searchType, objectids):
        QDialog.__init__(self, parent=None)
        self.initialDialog = initialDialog
        self.db_settings = self.initialDialog.db_settings
        self.setWindowFlags(self.windowFlags() | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.setupDialog(initialDialog, searchType, objectids)
        self.canvas = qgis.utils.iface.mapCanvas()
        self.show()

    def setupDialog(self, initialDialog, searchType, objectids):
        self.setWindowTitle(str(totalCount) + " matching records found")
        self.resize(900, 400)

        # Results Table View
        self.resultsTable = QTableView(self)
        self.resultsTable.setGeometry(QRect(15, 15, 870, 360))
        self.resultsTable.setToolTip("Double click on a row to zoom directly to that site;\nUse 'Ctrl' or 'Shift' key for multiple selection.")
        self.resultsTable.horizontalHeader().setToolTip("Click on column header to sort; click again to sort descending.")
        if searchType != "address":
            header = ['PK', 'PIN', 'LOCALITY', 'ROAD_NAME', 'PITYPE_1', 'PITYPE_2', 'PITYPE_3_1', 'PITYPE_3_2', 'REGNO_FORM', 'OWNER_NAME']
        else:
            header = ['PK', 'PIN', 'HOUSE_NO', 'LOT_NO', 'ROAD_NAME', 'LOCALITY', 'REGNO_FORM', 'OWNER_NAME']
        self.model = QStandardItemModel(self)
        self.model.setHorizontalHeaderLabels(header)
        self.resultsTable.setModel(self.model)
        self.resultsTable.verticalHeader().setVisible(False)
        if searchType != "address":
            self.resultsTable.setColumnWidth(0, 0)
            self.resultsTable.setColumnWidth(1, 50)
            self.resultsTable.setColumnWidth(2, 90)
            self.resultsTable.setColumnWidth(3, 90)
            self.resultsTable.setColumnWidth(4, 80)
            self.resultsTable.setColumnWidth(5, 80)
            self.resultsTable.setColumnWidth(6, 80)
            self.resultsTable.setColumnWidth(7, 80)
            self.resultsTable.setColumnWidth(8, 80)
            self.resultsTable.setColumnWidth(9, 200)
        else:
            self.resultsTable.setColumnWidth(0, 0)
            self.resultsTable.setColumnWidth(1, 50)
            self.resultsTable.setColumnWidth(2, 70)
            self.resultsTable.setColumnWidth(3, 50)
            self.resultsTable.setColumnWidth(4, 100)
            self.resultsTable.setColumnWidth(5, 130)
            self.resultsTable.setColumnWidth(6, 80)
            self.resultsTable.setColumnWidth(7, 350)
        self.resultsTable.setFont(QFont("Arial", 7))
        self.resultsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.resultsTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.resultsTable.setSortingEnabled(True)
        self.resultsTable.doubleClicked.connect(lambda: self.doubleClickHandler(initialDialog))
        
        # clear current rows
        self.model.removeRows(0, self.model.rowCount(), QModelIndex())
        
        # fill
        #db_settings = DatabaseSettings()
        check_cadastre_gdb(self.db_settings.cadastre_gdb, self.db_settings.cadastre_fc)
        conn = sqlite3.connect(self.db_settings.local_cadastre_db)
        with conn:
            csr = conn.cursor()
            csr.execute("SELECT * FROM state_cadastre WHERE objectid IN (" + str(objectids)[1:-1] + ")")
            rows = csr.fetchall()
            csr.close()
            if searchType != "address": 
                for row in rows:
                    if row[7] is None:
                        street = ""
                    elif row[8] is None:
                        street = row[7]
                    elif row[9] is None:
                        street = row[7] + " " + row[8]
                    else:
                        street = row[7] + " " + row[8] + " " + row[9]
                    items = [QStandardItem(field) for field in [str(row[1]), str(row[2]), row[10], street, row[12], row[13],row[14],row[15], row[17], row[18]]]
                    self.model.appendRow(items)
            else:
                for row in rows:
                    if row[9] is None:
                        street = row[7] + " " + row[8]
                    else:
                        street = row[7] + " " + row[8] + " " + row[9]
                    items = [QStandardItem(field) for field in [str(row[1]), str(row[2]), row[6], row[5], street, row[10], row[17], row[18]]]
                    self.model.appendRow(items)
        conn.close()    
            
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        mainLayout.addWidget(self.resultsTable)
        buttonLayout = QHBoxLayout()
        buttonLayout.setAlignment(Qt.AlignHCenter)
        self.zoomToAllButton = QPushButton("Zoom to all", self)
        self.zoomToAllButton.setFixedWidth(110)
        self.zoomToAllButton.clicked.connect(self.zoomToAll)
        self.zoomToAllButton.clicked.connect(self.closeForms)
        self.zoomButton = QPushButton("Zoom to selection", self)
        self.zoomButton.setFixedWidth(110)
        self.zoomButton.setToolTip("This table will remain available but minimised")
        self.zoomButton.clicked.connect(self.zoomToSelection)
        self.zoomCloseButton = QPushButton("Zoom and Close", self)
        self.zoomCloseButton.setFixedWidth(110)
        self.zoomCloseButton.setToolTip("This table will close and map will zoom to selected site")
        self.zoomCloseButton.clicked.connect(self.zoomToSelection)
        self.zoomCloseButton.setDefault(True)
        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.setFixedWidth(110)
        self.cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(self.zoomToAllButton)
        buttonLayout.addWidget(self.zoomButton)
        buttonLayout.addWidget(self.zoomCloseButton)
        buttonLayout.addWidget(self.cancelButton)
        mainLayout.addLayout(buttonLayout)

    def selectAll(self):
        self.resultsTable.setSelectionMode(QAbstractItemView.MultiSelection)
        for row in range(self.resultsTable.model().rowCount()):
            self.resultsTable.selectRow(row)
        self.resultsTable.setSelectionMode(QAbstractItemView.ExtendedSelection)
        return True
        
    def zoomToAll(self):
        #
        self.selectAll()
        self.zoomToSelection()

    def doubleClickHandler(self, initialDialog):
        # extract id and cadastre file from selected row
        id = int(self.model.itemFromIndex(self.resultsTable.selectedIndexes()[0]).text())
        finalZoom([id], self.db_settings)
        
        self.pointTool = ShowAttributesTool(self.canvas, [id], self.db_settings)
        self.pointTool.canvasClicked.connect(self.pointTool.canvasPressEvent)
        self.canvas.setMapTool(self.pointTool)

        # Clean up
        searchString = ""
        self.close()
        initialDialog.close()
            
    def zoomToSelection(self):
        self.initialDialog.close()
        selectedIdList = []

        # Build selectedIdList: extract id and cadastre file info from selected row
        selectedRows = []
        for item in self.resultsTable.selectedIndexes():
            if item.column() == 0:
                row = item.row()
                selectedRows.append(row)
        if len(selectedRows) == 0:
            QMessageBox.information(None, "No rows selected", "You have not selected any rows from the table.")
            return "No rows selected"
        else:
            for row in selectedRows:
                idIndex = self.model.index(row, 0)
                id = int(self.model.data(idIndex))
                selectedIdList.append(id)

            self.showMinimized()            
            finalZoom(selectedIdList, self.db_settings)
            
            self.pointTool = ShowAttributesTool(self.canvas, selectedIdList, self.db_settings)
            self.pointTool.canvasClicked.connect(self.pointTool.canvasPressEvent)
            self.canvas.setMapTool(self.pointTool)

    def closeForms(self):
    # Close both forms
        self.close()
        if self.parent() is not None:
            self.parent().close()
            
    def zoomAndClose(self):
        if self.zoomToSelection() != "No rows selected":
            self.closeForms()

    def buildFullIdList(self, cadastreColumn):
        fullIdList = []
        # Build fullIdList of (feat ID, cadastre) tuples 
        for row in range(self.model.rowCount()):
            fullIdList.append((int(self.model.item(row, 0).text()), self.model.item(row, cadastreColumn).text()))
        return fullIdList


class ShowAttributesTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, idList, db_settings):
        self.idList = idList
        self.canvas = canvas
        self.db_settings = db_settings
        QgsMapToolEmitPoint.__init__(self, self.canvas)
    
    def canvasPressEvent(self, e):
        registry = QgsMapLayerRegistry.instance()
        #db_settings = DatabaseSettings()
        check_cadastre_gdb(self.db_settings.cadastre_gdb, self.db_settings.cadastre_fc)
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            # Get clicked point
            self.point = self.toMapCoordinates(e.pos())
            pointGeometry = QgsGeometry.fromPoint(self.point)
            self.isEmittingPoint = True
            
            layer = None
            for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
                if lyr.source().lower() == (self.db_settings.cadastre_gdb + "|layername=" + self.db_settings.cadastre_fc).lower():
                    layer = lyr
                    break
            
            if layer is not None:
                for id in self.idList:
                    request = QgsFeatureRequest(id)
                    for f in layer.getFeatures(request):
                        geom = f.geometry()
                        fields = f.fields()
                        if pointGeometry.within(f.geometry()):
                            attributes = f.attributes()
                            attributeString = ""
                            for i in range(len(attributes)):
                                if fields[i].name() == "CAD_PIN":
                                    attributes[i] = int(attributes[i])
                                attributeString += fields[i].name() + ":\t\t" + str(attributes[i]) + "\n"
                            attributeString = attributeString[:-1]
                            QApplication.restoreOverrideCursor()
                            QMessageBox.information(None, "Attributes", attributeString)
                            break
            else:
                QMessageBox.information(None, "Error", "There was a problem opening the attribute list - try the QGIS 'Identify' tool instead.")
        except:
            QMessageBox.information(None, "Error", "There was a problem opening the attribute list - try the QGIS 'Identify' tool instead.")
            self.pointTool = None
            QApplication.restoreOverrideCursor()
        finally:
            QApplication.restoreOverrideCursor()
