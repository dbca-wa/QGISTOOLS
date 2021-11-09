from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *
from ..tools import Tools
from ..data.metadata.metadatatools import MetadataTools
import os
import shutil
import qgis.utils
from ..data.crs.crshelper import CRSHelper
from .selectcrsdialog import SelectCRSDialog
from .metadataeditordialog import MetadataEditorDialog


class ConvertLayerToCRSDialog(QDialog):
    def __init__(self, layer):
        QDialog.__init__(self, Tools.QGISApp)
        assert(isinstance(layer, QgsMapLayer))

        self.layer = layer
        if layer is not None:
            self.sourceLocation = str(layer.source())
            self.sourceCRS = CRSHelper(layer.crs()).friendlyName()

        else:
            self.sourceLocation = ""
            self.sourceCRS = ""

        self.targetLocation = ""
        self.targetCRSText = ""
        self.targetCRS = None
        self.setupDialog()
        self.exec_()


    def setupDialog(self):
        hints = self.windowFlags()
        hints &= Qt.CustomizeWindowHint
        hints ^= Qt.WindowSystemMenuHint
        hints ^= Qt.WindowCloseButtonHint
        self.setWindowFlags(hints)

        self.setMinimumWidth(500)

        self.setWindowTitle("Convert layer to different Coordinate Reference System")
        self.setLayout(QVBoxLayout())

        groupBox = QGroupBox("", self)
        self.layout().addWidget(groupBox)
        grid = QGridLayout()
        groupBox.setLayout(grid)

        grid.addWidget(QLabel("<b><center>Original Layer</center></b>"), 0, 0, 1, 3)
        grid.addWidget(QLabel("<b>Location:</b>"), 1, 0)
        grid.addWidget(QLabel("<b>CRS:</b>"), 2, 0)
        grid.addWidget(QLabel("<b><center>Converted Layer</center></b>"), 3, 0, 1, 3)
        grid.addWidget(QLabel("<b>Location:</b>"), 4, 0)
        grid.addWidget(QLabel("<b>CRS:</b>"), 5, 0)

        self.sourceLocationLineEdit = QLineEdit(self.sourceLocation)
        self.sourceLocationLineEdit.setText(self.sourceLocation)
        self.sourceLocationLineEdit.setReadOnly(True)
        grid.addWidget(self.sourceLocationLineEdit, 1, 1, 1, 2)

        self.sourceCrsLineEdit = QLineEdit(self.sourceCRS)
        self.sourceCrsLineEdit.setText(self.sourceCRS)
        self.sourceCrsLineEdit.setReadOnly(True)
        grid.addWidget(self.sourceCrsLineEdit, 2, 1, 1, 2)

        self.targetLocationLineEdit = QLineEdit()
        grid.addWidget(self.targetLocationLineEdit, 4, 1)
        self.targetLocationLineEdit.setReadOnly(True)

        self.targetCrsLineEdit = QLineEdit()
        grid.addWidget(self.targetCrsLineEdit, 5, 1)
        self.targetCrsLineEdit.setReadOnly(True)

        self.targetLocationBrowseButton = QToolButton()
        self.targetLocationBrowseButton.setIcon(qgis.utils.iface.actionOpenProject().icon())
        self.targetLocationBrowseButton.clicked.connect(self.browseButtonHandler)
        grid.addWidget(self.targetLocationBrowseButton, 4, 2)

        self.targetCrsBrowseButton = QToolButton()
        self.targetCrsBrowseButton.setIcon(qgis.utils.iface.actionOptions().icon())
        self.targetCrsBrowseButton.clicked.connect(self.selectCRSButtonHandler)
        grid.addWidget(self.targetCrsBrowseButton, 5, 2)

        self.loadConvertedLayerCheckBox = QCheckBox("Load converted layer")
        self.loadConvertedLayerCheckBox.setChecked(True)
        grid.addWidget(self.loadConvertedLayerCheckBox, 6, 0, 1, 3, Qt.AlignCenter)

        buttonLayout = QHBoxLayout()
        self.layout().addLayout(buttonLayout)
        buttonLayout.addStretch()
        buttonLayout.addStretch()
        self.okButton = QPushButton("OK")
        buttonLayout.addWidget(self.okButton)
        self.okButton.clicked.connect(self.okClickHandler)
        buttonLayout.addStretch()
        self.cancelButton = QPushButton("Cancel")
        buttonLayout.addWidget(self.cancelButton)
        self.cancelButton.clicked.connect(self.cancelClickHandler)
        buttonLayout.addStretch()
        buttonLayout.addStretch()
        self.firstPassValidation()

        # self.projectedComboBox.currentIndexChanged.connect(self.projectedComboIndexChangeHandler)

    def browseButtonHandler(self):
        if len(self.targetLocation) == 0:
            startingLocation = self.sourceLocation.rsplit("\\", 1)[0]
        else:
            startingLocation = self.targetLocation
            
        result = QFileDialog.getSaveFileName(None,
                                             "Save converted layer as...",
                                             startingLocation,
                                             "ESRI Shapefile (*.shp *.SHP)",
                                             QFileDialog.DontConfirmOverwrite)

        while os.path.isfile(result):
			# TODO self.targetLocation? or result?
            Tools.debug("A file already exists in the selected location:\n" +
                        self.targetLocation + "\n\n" +
                        "Please select a new location and try again.",
                        "File already exists")
            result = QFileDialog.getSaveFileName(None,
                                                 "Save converted layer as...",
                                                 startingLocation,
                                                 "ESRI Shapefile (*.shp *.SHP)",
                                                 QFileDialog.DontConfirmOverwrite)

        if len(result) > 0:
            self.targetLocation = str(result.replace("/", "\\"))

        self.targetLocationLineEdit.setText(self.targetLocation)
        self.firstPassValidation()

    def selectCRSButtonHandler(self):
        dialog = SelectCRSDialog(SelectCRSDialog.QUERY, None, self.targetCRS)
        if dialog.crs is not None:
           self.targetCRS = dialog.crs
           self.targetCRSText = CRSHelper(self.targetCRS).friendlyName()
           self.targetCrsLineEdit.setText(self.targetCRSText)
        self.firstPassValidation()

    def firstPassValidation(self):
        if len(self.targetCRSText) > 0:
            if len(self.targetLocation) > 0:
                if self.targetLocation.lower() != self.sourceLocation.lower():
                    self.okButton.setEnabled(True)
                    return
        self.okButton.setEnabled(False)

    def okClickHandler(self):
        if os.path.isfile(self.targetLocation):
            Tools.debug("A file already exists in the target location:\n" +
                        self.targetLocation + "\n\n" +
                        "Please select a new location and try again.",
                        "File already exists")
            return
        self.okButton.setEnabled(False)

        if True:
            # write new .dbf .prj .qpj .shp .shx
            # Tools.debug(CRSHelper(self.targetCRS).friendlyName())
            response  = QgsVectorFileWriter.writeAsVectorFormat(self.layer,self.targetLocation,
                                                                "System", self.targetCRS)
            if response != QgsVectorFileWriter.NoError:
                Tools.debug("Error converting layer!\nError Code:" + response,
                            "Error")
                return

            # remove .qpj
            os.remove(self.targetLocation[:-4]+".qpj")

            prjTarget = self.targetLocation[:-4] + ".prj"
            prjSource = os.path.join(Tools.getPluginPath(), "resources\\prjfiles\\", CRSHelper(self.targetCRS).prjfilename)

            try:
                shutil.copyfile(prjSource,prjTarget)
            except:
                if not os.path.isfile(prjSource):
                    Tools.debug("Error creating .prj file.\n" +
                    "This QGIS Tools installation is missing "+ prjSource,
                    "CRS Error")
                else:
                    Tools.debug("Error creating .prj file.\n" +
                    "Please check your write access to have " + prjTarget,
                    "CRS Error")
                return

            # copy qml
            self.copyMatchedFile(self.sourceLocation, self.targetLocation, ".qml")
            self.copyMatchedFile(self.sourceLocation, self.targetLocation, ".sld")
            self.copyMatchedFile(self.sourceLocation, self.targetLocation, ".lyr")
            metadataExists = self.copyMatchedFile(self.sourceLocation, self.targetLocation, ".xml")
            metadataExists |= self.copyMatchedFile(self.sourceLocation, self.targetLocation, ".xml", False)

            fileName = self.targetLocation.rsplit("\\", 1)[1].rsplit(".", 1)[0]
            newLayer = QgsVectorLayer(self.targetLocation, fileName, "ogr")

            if metadataExists:
                MetadataEditorDialog(MetadataEditorDialog.UPDATE, newLayer)

            # update metadata
            if self.loadConvertedLayerCheckBox.isChecked():
                QgsMapLayerRegistry.instance().addMapLayer(newLayer)
            else:
                Tools.debug("File Conversion Successful")

            self.accept()

    def copyFileIfSourceExists(self, source, dest):
        # QgsMessageLog.logMessage(source + ">>"+ dest)
        if os.path.isfile(source):
            # QgsMessageLog.logMessage(source + " exists")
            try:
                shutil.copy(source, dest)
                return True
            except:
                pass
        return False

    def copyMatchedFile(self, source, dest, extension, trim=True):
        # QgsMessageLog.logMessage("start CMF")
        if trim:
            # QgsMessageLog.logMessage("trim")
            return self.copyFileIfSourceExists(source[:-4] + extension, dest[:-4] + extension)
        else:
            # QgsMessageLog.logMessage("raw")
            return self.copyFileIfSourceExists(source + extension, dest + extension)

    def cancelClickHandler(self):
        self.reject()
