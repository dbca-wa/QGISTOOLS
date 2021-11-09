from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *
from ..tools import *
from ..data.metadata.metadatatools import MetadataTools

import os
import shutil
import qgis.utils
from ..data.crs.crshelper import CRSHelper


class SelectCRSDialog(QDialog):
    LAYER = 0
    FRAME = 1
    QUERY = 2
    PROJECTEDFRAME = 3

    def __init__(self, mode, layer=None, crs=None):
        if layer is not None:
            assert(isinstance(layer, QgsMapLayer)), "SelectCRSDialog bad layer param"
        if crs is not None:
            assert(isinstance(crs, QgsCoordinateReferenceSystem)), "SelectCRSDialog bad crs param"
        QDialog.__init__(self, Tools.QGISApp)

        self.mode = mode
        self.setupDialog()

        self.crs = None

        if self.mode == SelectCRSDialog.FRAME:
            #self.crs = qgis.utils.iface.mapCanvas().mapRenderer().destinationCrs()
            self.crs = qgis.utils.iface.mapCanvas().mapSettings().destinationCrs()
        elif self.mode == SelectCRSDialog.LAYER:
            assert(layer is not None), "SelectCRSDialog in layerMode but layer param is None"
            self.layer = layer
            self.crs = layer.crs()
        elif self.mode == SelectCRSDialog.QUERY:
            self.crs = crs
        else:
            #self.crs = qgis.utils.iface.mapCanvas().mapRenderer().destinationCrs()
            self.crs = qgis.utils.iface.mapCanvas().mapSettings().destinationCrs()

        self.projectedComboBox.setEnabled(False)
        self.zoneComboBox.setEnabled(False)
        self.geographicComboBox.setEnabled(False)
        self.okButton.setEnabled(False)

        if self.crs is not None:
            self.setDialogToCrs()

        if self.mode == SelectCRSDialog.PROJECTEDFRAME:
            self.mode = SelectCRSDialog.FRAME
            self.geographicRadioButton.setEnabled(False)
            self.projectedRadioButton.setChecked(True)

        self.exec_()

    def setupDialog(self):
        hints = self.windowFlags()
        hints &= Qt.CustomizeWindowHint
        hints ^= Qt.WindowSystemMenuHint
        hints ^= Qt.WindowCloseButtonHint
        self.setWindowFlags(hints)

        if self.mode == SelectCRSDialog.FRAME:
            self.setWindowTitle("Set Data Frame Coordinate System")
        elif self.mode == SelectCRSDialog.LAYER:
            self.setWindowTitle("Set Layer Coordinate System")
        elif self.mode == SelectCRSDialog.QUERY:
            self.setWindowTitle("Select target Coordinate System")
        else:
            self.setWindowTitle("Select Projected Coordinate System")

        self.setLayout(QVBoxLayout())
        if self.mode == SelectCRSDialog.PROJECTEDFRAME:     #???Get rid of these 2 lines now GCS can be used in Map prod Tool
            self.layout().addWidget(QLabel("<b>The map production tool requires a projected coordinate system:</b>"))

        groupBox = QGroupBox("Coordinate System", self)
        self.layout().addWidget(groupBox)
        groupBox.setLayout(QVBoxLayout())

        self.projectedRadioButton = QRadioButton("Projected Coordinate System", self)
        groupBox.layout().addWidget(self.projectedRadioButton)
        self.projectedRadioButton.toggled.connect(self.projectedToggleHandler)
        self.projectedRadioButton.setChecked(False)
        self.projectedComboBox = QComboBox(self)
        groupBox.layout().addWidget(self.projectedComboBox)
        self.projectedComboBox.addItem("Map Grid of Australia (MGA)")
        self.projectedComboBox.addItem("Albers Equal Area (GDA)")
        self.projectedComboBox.addItem("Web Mercator")
        self.projectedComboBox.addItem("Australian Map Grid (AMG)")
        self.projectedComboBox.addItem("Albers Equal Area (AGD)")

        zoneLayout = QHBoxLayout()
        groupBox.layout().addLayout(zoneLayout)
        zoneLayout.addWidget(QLabel("Zone:"))
        self.zoneComboBox = QComboBox(self)
        zoneLayout.addWidget(self.zoneComboBox)
        self.zoneComboBox.addItem("49")
        self.zoneComboBox.addItem("50")
        self.zoneComboBox.addItem("51")
        self.zoneComboBox.addItem("52")
        index = self.zoneComboBox.findText("50")
        self.zoneComboBox.setCurrentIndex(index)

        groupBox.layout().addSpacerItem(QSpacerItem(5, 5))
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        groupBox.layout().addWidget(line)

        self.geographicRadioButton = QRadioButton("Geographic Coordinate System", self)
        groupBox.layout().addWidget(self.geographicRadioButton)
        self.geographicRadioButton.toggled.connect(self.geographicToggleHandler)

        self.geographicComboBox = QComboBox(self)
        groupBox.layout().addWidget(self.geographicComboBox)
        self.geographicComboBox.addItem("Geocentric Datum of Australia 1994 (GDA)")
        self.geographicComboBox.addItem("World Geodetic System 1984 (WGS84)")
        self.geographicComboBox.addItem("Australian Geodetic Datum 1984 (AGD)")

        buttonLayout = QHBoxLayout()
        self.layout().addLayout(buttonLayout)
        self.okButton = QPushButton("OK")
        buttonLayout.addWidget(self.okButton)
        self.okButton.clicked.connect(self.okClickHandler)
        self.cancelButton = QPushButton("Cancel")
        buttonLayout.addWidget(self.cancelButton)
        self.cancelButton.clicked.connect(self.cancelClickHandler)

        self.projectedComboBox.currentIndexChanged.connect(self.projectedComboIndexChangeHandler)

    def okClickHandler(self):
        from .metadataeditordialog import MetadataEditorDialog
        newCrs = self.deriveCrsFromDialog()
        if newCrs is not None:
            if self.mode == SelectCRSDialog.FRAME:
                canvas = qgis.utils.iface.mapCanvas()
                #oldExtent = canvas.extent()
                #oldCrs = canvas.mapSettings().destinationCrs()
                #transformer = QgsCoordinateTransform()
                #transformer.setSourceCrs(oldCrs)
                #transformer.setDestCRS(newCrs)
                #newExtent = transformer.transform(oldExtent)
                canvas.setCrsTransformEnabled(True)
                canvas.setDestinationCrs(newCrs)
                canvas.setMapUnits(newCrs.mapUnits())
                #canvas.setExtent(newExtent)
            elif self.mode == SelectCRSDialog.LAYER:
                # convert in memory -  for current app lifecycle
                self.layer.setCrs(newCrs)
                # copy prj file to shapefile location
                if self.layer is not None:
                    layerSource = str(self.layer.source())
                    if layerSource[-4:].lower() == ".shp":
                        prjTarget = layerSource[:-4] + ".prj"
                        prjSource = os.path.join(Tools.getPluginPath(), "resources\\prjfiles\\", CRSHelper(newCrs).prjfilename)
                        try:
                            shutil.copyfile(prjSource, prjTarget)
                        except:
                            if not os.path.isfile(prjSource):
                                Tools.debug("Error creating .prj file.\n" +
                                            "This QGIS Tools installation is missing " +
                                            prjSource, "CRS Error")
                            else:
                                Tools.debug("Error creating .prj file.\n" +
                                            "Please check your write access to have " +
                                            prjTarget, "CRS Error")
                            return
# delete the .qpj file so that arc users wont create conflicting data
                        qpjLocation = layerSource[:-4] + ".qpj"
                        try:
                            if os.path.isfile(qpjLocation):
                                os.remove(qpjLocation)
                        except:
                            Tools.debug("Error deleting .qpj file.\n" +
                                        "Please delete " + qpjLocation + " manually.",
                                        "CRS Error")
                            return
                    if MetadataTools.getExistingMetadataFileLocation(self.layer) is not None:
                        MetadataEditorDialog(MetadataEditorDialog.UPDATE, self.layer)
            else:  # mode = query
                self.crs = newCrs
        self.accept()

    def cancelClickHandler(self):
        self.reject()

    def projectedToggleHandler(self, checked):
        self.projectedComboBox.setEnabled(checked)
        self.zoneComboBox.setEnabled(checked)
        self.okButton.setEnabled(True)

    def projectedComboIndexChangeHandler(self, index):
        #self.zoneComboBox.setEnabled(index % 2 == 0)
        self.zoneComboBox.setEnabled(index == 0 or index == 3)

    def geographicToggleHandler(self, checked):
        self.geographicComboBox.setEnabled(checked)
        self.okButton.setEnabled(True)

    def setDialogToCrs(self):
        helper = CRSHelper(self.crs)
        if helper.authid == "EPSG:4203":
            self.geographicRadioButton.setChecked(True)
            self.geographicComboBox.setCurrentIndex(2)
        elif helper.authid == "EPSG:4326":
            self.geographicRadioButton.setChecked(True)
            self.geographicComboBox.setCurrentIndex(1)
        elif helper.authid == "EPSG:4283":
            self.geographicRadioButton.setChecked(True)
            self.geographicComboBox.setCurrentIndex(0)
        elif helper.authid[:8] == "EPSG:283":
            zone = helper.authid[-2:]
            self.projectedRadioButton.setChecked(True)
            self.projectedComboBox.setCurrentIndex(0)
            self.zoneComboBox.setCurrentIndex(int(zone)-49)

        elif helper.authid[:8] == "EPSG:283":
            zone = helper.authid[-2:]
            self.projectedRadioButton.setChecked(True)
            self.projectedComboBox.setCurrentIndex(0)
            self.zoneComboBox.setCurrentIndex(int(zone)-49)

        elif helper.authid[:8] == "EPSG:203":
            zone = helper.authid[-2:]
            self.projectedRadioButton.setChecked(True)
            self.projectedComboBox.setCurrentIndex(3)
            self.zoneComboBox.setCurrentIndex(int(zone)-49)

        elif helper.proj4 == ("+proj=aea +lat_1=-17.5 +lat_2=-31.5 +lat_0=0 " +
                              "+lon_0=121 +x_0=5000000 +y_0=10000000 " +
                              "+ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m " +
                              "+no_defs"):
            self.projectedRadioButton.setChecked(True)
            self.projectedComboBox.setCurrentIndex(1)

        elif helper.proj4 == ("+proj=aea +lat_1=-17.5 +lat_2=-31.5 +lat_0=0 " +
                              "+lon_0=121 +x_0=5000000 +y_0=10000000 " +
                              "+ellps=aust_SA +towgs84=-134,-48,149,0,0,0,0 " +
                              "+units=m +no_defs"):
            self.projectedRadioButton.setChecked(True)
            self.projectedComboBox.setCurrentIndex(4)

        elif helper.authid == "EPSG:3857":
            self.projectedRadioButton.setChecked(True)
            self.projectedComboBox.setCurrentIndex(2)

    def deriveCrsFromDialog(self):
        if self.geographicRadioButton.isChecked():
            if self.geographicComboBox.currentIndex() == 0:
                return QgsCoordinateReferenceSystem("EPSG:4283")
            elif self.geographicComboBox.currentIndex() == 1:
                return QgsCoordinateReferenceSystem("EPSG:4326")
            elif self.geographicComboBox.currentIndex() == 2:
                return QgsCoordinateReferenceSystem("EPSG:4203")             
        elif self.projectedRadioButton.isChecked():
            if self.projectedComboBox.currentIndex() == 0:
                zone = self.zoneComboBox.currentIndex() + 49
                return QgsCoordinateReferenceSystem("EPSG:283" + str(zone))
            elif self.projectedComboBox.currentIndex() == 1:
                # use createfromproj4 so that it will reconcile with user crs db
                newCrs = QgsCoordinateReferenceSystem()
                newCrs.createFromProj4("+proj=aea +lat_1=-17.5 +lat_2=-31.5 " +
                                       "+lat_0=0 +lon_0=121 +x_0=5000000 " +
                                       "+y_0=10000000 +ellps=GRS80 " +
                                       "+towgs84=0,0,0,0,0,0,0 +units=m +no_defs")
                if newCrs.findMatchingProj() == 0:  # i.e. if not yet in user crs db
                    newCrs.saveAsUserCRS("WA Albers Equal Conic (GDA)")
                return newCrs
            elif self.projectedComboBox.currentIndex() == 2:
                return QgsCoordinateReferenceSystem("EPSG:3857")
            elif self.projectedComboBox.currentIndex() == 3:
                zone = self.zoneComboBox.currentIndex() + 49
                return QgsCoordinateReferenceSystem("EPSG:203"+str(zone))
            elif self.projectedComboBox.currentIndex() == 4:
                # use createfromproj4 so that it will reconcile with user crs db
                newCrs = QgsCoordinateReferenceSystem()
                newCrs.createFromProj4("+proj=aea +lat_1=-17.5 +lat_2=-31.5 " +
                                       "+lat_0=0 +lon_0=121 +x_0=5000000 " +
                                       "+y_0=10000000 +ellps=aust_SA " +
                                       "+towgs84=-134,-48,149,0,0,0,0 " +
                                       "+units=m +no_defs")
                if newCrs.findMatchingProj() == 0:  # i.e. if not yet in user crs db
                    newCrs.saveAsUserCRS("WA Albers Equal Conic (AGD)")
                return newCrs

        Tools.debug("ERROR DETERMINING WINDOW STATE")
