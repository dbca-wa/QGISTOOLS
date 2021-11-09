# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtXml import *   # For QDomDocument (to read map composer template)
from qgis.core import *
from qgis.gui import *
import qgis.utils

import getpass, os, shutil
from ..tools import Tools
from ..data.metadata.metadatatools import MetadataTools
from .datamenu import DataMenu
from ..ui.deptnamesdialog import DeptNamesDialog
from .datalocationsdialog import DataLocationsDialog
from .metadataviewerdialog import MetadataViewerDialog
from .metadataeditordialog import MetadataEditorDialog
from .selectcrsdialog import SelectCRSDialog
from .convertlayertocrsdialog import ConvertLayerToCRSDialog
from ..mapproduction.mapproduction import MapProduction, MapLabelDialog
from ..searchcadastre.searchcadastre import SearchCadastreDialog, DatabaseSettings
from ..data.crs.crshelper import CRSHelper
from ..ui.aboutdialog import AboutDialog

# from pydevd import*

##############################################################################


class DockableWindow():
    @staticmethod
    def getDockable(display=True):
        mw = qgis.utils.iface.mainWindow()
        dock = mw.findChild(QDockWidget, Tools.get_application_name())
        if dock is not None:
            dock.setVisible(not dock.isVisible())
            return dock
        else:
            # dockable
            dock = QDockWidget(Tools.get_application_name(), mw)
            dock.setObjectName(Tools.get_application_name())
            dock.dockLocationChanged.connect(DockableWindow.dockAreaChange)

            qgis.utils.iface.addDockWidget(Tools.getDockArea(), dock)
            dockCanvas = QWidget()
            dock.setWidget(dockCanvas)
            dockLayout = QVBoxLayout()
            dockCanvas.setLayout(dockLayout)
            dockLayout.setContentsMargins(0, 0, 0, 0)

            # toolbar
            topLayout = QBoxLayout(QBoxLayout.LeftToRight, dock)
            searchLayout = QBoxLayout(QBoxLayout.LeftToRight, dock)
            dockLayout.addLayout(topLayout)
            dockLayout.addLayout(searchLayout)
            toolbar = QToolBar(dock)
            topLayout.addWidget(toolbar)
            menubar = QMenuBar(toolbar)
            toolbar.addWidget(menubar)
            barLayout = QBoxLayout(QBoxLayout.LeftToRight, toolbar)
            menubar.setLayout(barLayout)
            
    # TOOL MENU
            toolsMenu = QMenu("Tools", menubar)
            toolsMenu.setToolTip("Click for more tools")
            menubar.addMenu(toolsMenu)

    # Settings
            settingsMenu = QMenu("Settings", toolsMenu)
            toolsMenu.addMenu(settingsMenu)

            # data locations
            dl = settingsMenu.addAction("Data Locations")
            dl.triggered.connect(DockableWindow.dataLocations)

            dn = settingsMenu.addAction("Department Names")
            dn.triggered.connect(DockableWindow.dept_names)

    # default project
            defaultProjectMenu = QMenu("Default Project", toolsMenu)
            defProject = settingsMenu.addMenu(defaultProjectMenu)
            
            disableLink = defaultProjectMenu.addAction("Disable use of Default Project")
            disableLink.triggered.connect(DockableWindow.disableDefaultProject)

            setCurrentLink = defaultProjectMenu.addAction("Set current project as the Default Project")
            setCurrentLink.triggered.connect(DockableWindow.setCurrentProjectAsDefault)

            restoreInitialLink = defaultProjectMenu.addAction("Reset")
            restoreInitialLink.triggered.connect(DockableWindow.setDPaWProjectAsDefault)
            
            
    # coord ref systems
            coordinatesMenu = QMenu("Coordinate Systems", toolsMenu)
            coordinatesMenu.aboutToShow.connect(DockableWindow.showCoordinateSystemsMenu)
            toolsMenu.addMenu(coordinatesMenu)

            cltdcrs = coordinatesMenu.addAction("Convert Layer to Different Coordinate Reference System")
            DockableWindow.convertLayerToCoordinateSystemAction = cltdcrs
            cltdcrs.triggered.connect(DockableWindow.convertLayerToCoordinateSystem)

            coordinatesMenu.addSeparator()

            dlcs = coordinatesMenu.addAction("Define Layer Coordinate Reference System")
            DockableWindow.defineLayerCoordinateSystemAction = dlcs
            dlcs.triggered.connect(DockableWindow.defineLayerCoordinateSystem)

            dfcs = coordinatesMenu.addAction("Set Data Frame Coordinate Reference System")
            DockableWindow.defineFrameCoordinateSystemAction = dfcs
            dfcs.triggered.connect(DockableWindow.defineFrameCoordinateSystem)

    # metadata
            metadataMenu = QMenu("Metadata", toolsMenu)
            metadataMenu.aboutToShow.connect(DockableWindow.showNewMetadataMenu)
            metadataMenu.aboutToHide.connect(DockableWindow.hideNewMetadataMenu)
            toolsMenu.addMenu(metadataMenu)

            vmd = metadataMenu.addAction("View Metadata")
            vmd.triggered.connect(DockableWindow.viewNewMetadata)
            DockableWindow.viewNewMetadataMenuAction = vmd

            metadataMenu.addSeparator()

            legacyMetadataMenu = QMenu("Legacy Metadata", toolsMenu)
            legacyMetadataMenu.aboutToShow.connect(DockableWindow.showLegacyMetadataMenu)
            legacyMetadataMenu.aboutToHide.connect(DockableWindow.hideLegacyMetadataMenu)
            metadataMenu.addMenu(legacyMetadataMenu)

            clmd = legacyMetadataMenu.addAction("Create Metadata")
            clmd.triggered.connect(DockableWindow.createLegacyMetadata)
            DockableWindow.createLegacyMetadataMenuAction = clmd


            vlmd = legacyMetadataMenu.addAction("View Metadata")
            vlmd.triggered.connect(DockableWindow.viewLegacyMetadata)
            DockableWindow.viewLegacyMetadataMenuAction = vlmd

            elmd = legacyMetadataMenu.addAction("Edit Metadata")
            elmd.triggered.connect(DockableWindow.editLegacyMetadata)
            DockableWindow.editLegacyMetadataMenuAction = elmd

            #add these actions fo the context menu for the layer list
            #this will need modification for qgis 3.0
            legendInterface = Tools.iface.legendInterface()


            title = "Legacy Metadata"
            id = "id1"

            legendInterface.addLegendLayerAction(clmd, "Legacy Metadata", "clmd", QgsMapLayer.VectorLayer, True)
            legendInterface.addLegendLayerAction(vlmd, "Legacy Metadata", "vlmd", QgsMapLayer.VectorLayer, True)
            legendInterface.addLegendLayerAction(elmd, "Legacy Metadata", "elmd", QgsMapLayer.VectorLayer, True)
            legendInterface.addLegendLayerAction(vmd, "Metadata", "vmd", QgsMapLayer.VectorLayer, True)
            Tools.vmd = vmd

            # Dept QGIS Home Page
            dqhp = toolsMenu.addAction("{} QGIS Home Page".format(Tools.get_dept_acronym()))
            dqhp.triggered.connect(DockableWindow.QGISWebpage)

    # About info
            adb = toolsMenu.addAction("About")
            adb.triggered.connect(DockableWindow.aboutDialogBox)

# ZOOM TO LOCATION BUTTON
            zoomLocationButton = QAction(toolsMenu)
            zoomLocationButton.setIcon(Tools.iconZoomLocation)
            zoomLocationButton.setText("Zoom to Location")
            zoomLocationButton.setToolTip("Zoom to Location / Search Cadastre")
            zoomLocationButton.triggered.connect(DockableWindow.openSearchCadastre)
            toolbar.addAction(zoomLocationButton)
            

# MAP PROD BUTTON
            mapProButton = QAction(toolsMenu)
            mapProButton.setIcon(Tools.iconMapPro)
            mapProButton.setText("MapPro")
            mapProButton.setToolTip("Map Production")
            mapProButton.triggered.connect(DockableWindow.mapProduction)
            toolbar.addAction(mapProButton)
            
# REGION SELECTOR
            regionComboBox = QComboBox(toolbar)
            regionComboBox.setToolTip("{} Region selector".format(Tools.get_dept_acronym()))
            topLayout.addWidget(regionComboBox)
            target = Tools.getRegion()
            for r in Tools.regions:
                regionComboBox.addItem(r.replace("_", " "), None)
                if r == target:
                    regionComboBox.setCurrentIndex(regionComboBox.count() - 1)
            regionComboBox.currentIndexChanged.connect(DockableWindow.regionChange)

# SEARCH CDDP
            searchbar = QMenuBar(dock)
            searchLayout.addWidget(searchbar)
            searchbar.setLayout(searchLayout)

            searchLabel = QLabel("Search data menu for:", searchbar)
            searchText = QLineEdit(searchbar)
            searchText.setToolTip("Start typing search text")
            searchLayout.addWidget(searchLabel)
            searchLayout.addWidget(searchText)
            searchText.textChanged.connect(DockableWindow.searchTextChange)

# CLEAR SEARCH BUTTON
            clearSearchButton = QPushButton(Tools.iconRefresh, "", searchbar)
            clearSearchButton.setToolTip("Clear search text")
            clearSearchButton.clicked.connect(lambda: searchText.setText(""))
            searchLayout.addWidget(clearSearchButton)

            topLayout.addStretch(99)
            searchLayout.addStretch(99)
            Tools.dm = DataMenu(dockLayout)

            Tools.flushErrors()
            # No reg settings at this point
            return dock


##################################
##
#  Window management
##
##############################################################################
    @staticmethod
    def regionChange(index):
        Tools.setRegion(Tools.regions[index])

##############################################################################
    @staticmethod
    def dockAreaChange(location):
        Tools.setDockArea(location)


###################################
##
#  Click Handlers
##
##############################################################################
    @staticmethod
    def DECGISWebpage():
        QDesktopServices.openUrl(QUrl("http://intranet/csd/gis/default.aspx"))

##############################################################################
    @staticmethod
    def QGISWebpage():
        QDesktopServices.openUrl(QUrl("http://intranet/csd/gis/Pages/DEC%20QGIS%20Home%20Page.aspx"))

##############################################################################
    @staticmethod
    def QGISQuickStart():
        QDesktopServices.openUrl(QUrl("http://intranet/csd/gis/Documents/QGIS%20Quick%20Start.pdf"))

##############################################################################
    @staticmethod
    def viewNewMetadata():
        layer = Tools.activeLayer()
        if MetadataTools.canView(layer):
            MetadataViewerDialog(layer, MetadataTools.NewMetadataProfile)
        else:
            Tools.alert("No metadata exits", "Metadata")

##############################################################################
    @staticmethod
    def viewLegacyMetadata():
        layer = Tools.activeLayer()
        if MetadataTools.canView(layer):
            MetadataViewerDialog(layer, MetadataTools.LegacyMetadataProfile)
        else:
            Tools.alert("No metadata exits", "Metadata")

##############################################################################
    @staticmethod
    def editLegacyMetadata():
        layer = Tools.activeLayer()
        if MetadataTools.canEdit(layer):
            MetadataEditorDialog(MetadataEditorDialog.EDIT, Tools.activeLayer())
        else:
            Tools.alert("No metadata exits or read only location", "Metadata")

##############################################################################
    @staticmethod
    def createLegacyMetadata():
        layer = Tools.activeLayer()
        if MetadataTools.canCreate(layer):
            MetadataEditorDialog(MetadataEditorDialog.CREATE, Tools.activeLayer())
        else:
            Tools.alert("Metadata already exits", "Metadata")


##############################################################################
    @staticmethod
    def dataLocations(checked):
        DataLocationsDialog()

    @staticmethod
    def dept_names(checked):
        DeptNamesDialog()

##############################################################################
    @staticmethod
    def defineLayerCoordinateSystem(checked):
        SelectCRSDialog(SelectCRSDialog.LAYER, Tools.activeLayer())

##############################################################################
    @staticmethod
    def defineFrameCoordinateSystem(checked):
        SelectCRSDialog(SelectCRSDialog.FRAME)

##############################################################################
    @staticmethod
    def convertLayerToCoordinateSystem(checked):
        ConvertLayerToCRSDialog(Tools.activeLayer())

##############################################################################
    @staticmethod
    def aboutDialogBox(checked):
        AboutDialog()

##############################################################################
    @staticmethod
    def disableDefaultProject(checked):
        Tools.setSetting('newProjectDefault', 'false', 'QGis')
        registry = QgsMapLayerRegistry.instance()
        #registry.removeAllMapLayers()
        # Replaced with following code 20150911 to avoid losing additional layers (quick fix just looking to see if SMB is only layer)
        names = [layer.name() for layer in QgsMapLayerRegistry.instance().mapLayers().values()]
        if names == [u'State Map Base 250k (State)']:
            registry.removeAllMapLayers()
        else:
            query = "Would you like to start a new project immediately?"
            decision = QMessageBox.question(None, "Question", query, QMessageBox.Yes, QMessageBox.No)
            if decision == QMessageBox.Yes:
                registry.removeAllMapLayers()

        ##############################################################################
    @staticmethod
    def setCurrentProjectAsDefault(checked):
        Tools.setSetting('newProjectDefault', 'true', 'QGis')
        user_project_default_path = os.path.join("C:/Users", Tools.username, ".qgis2/project_default.qgs")
        if os.path.exists(user_project_default_path):
            shutil.copyfile(user_project_default_path, user_project_default_path + '~')
        project = QgsProject.instance()
        project.setFileName(user_project_default_path)
        project.write()


##############################################################################
    @staticmethod
    def setDPaWProjectAsDefault(checked):
        Tools.setSetting('newProjectDefault', 'true', 'QGis')
        Tools.setSetting('showDefaultMapDialog', 'true', 'DEC')
        user_project_default_path = os.path.join("C:/Users/", Tools.username, ".qgis2/project_default.qgs")
        plugin_project_default_location = os.path.join(Tools.getPluginPath(), "resources/project_default_DPaW.qgs")
        shutil.copyfile(plugin_project_default_location, user_project_default_path)

            
##############################################################################
##
#  Context Management
##
##############################################################################
    @staticmethod
    def showLegacyMetadataMenu():
        canEdit = False
        canView = False
        canCreate = False
        layer = Tools.activeLayer()
        if layer is not None:
            canCreate, canView, canEdit = MetadataTools.getMetadataActions(layer)

        DockableWindow.viewLegacyMetadataMenuAction.setEnabled(canView)
        DockableWindow.editLegacyMetadataMenuAction.setEnabled(canEdit)
        DockableWindow.createLegacyMetadataMenuAction.setEnabled(canCreate)

    @staticmethod
    def showNewMetadataMenu():
        canEdit = False
        canView = False
        canCreate = False
        layer = Tools.activeLayer()
        if layer is not None:
            canCreate, canView, canEdit = MetadataTools.getMetadataActions(layer)

        DockableWindow.viewNewMetadataMenuAction.setEnabled(canView)

    @staticmethod
    def hideLegacyMetadataMenu():
        DockableWindow.viewLegacyMetadataMenuAction.setEnabled(True)
        DockableWindow.editLegacyMetadataMenuAction.setEnabled(True)
        DockableWindow.createLegacyMetadataMenuAction.setEnabled(True)

    @staticmethod
    def hideNewMetadataMenu():
        DockableWindow.viewNewMetadataMenuAction.setEnabled(True)

    @staticmethod
    def showCoordinateSystemsMenu():
        canConvertLayer = False
        canDefineLayer = False
        canSetDataFrame = True

        layer = Tools.activeLayer()
        if layer is not None:
            if isinstance(layer, QgsVectorLayer):
                canConvertLayer = True
                layerSource = str(layer.source())
                if layerSource.rsplit(".", 1)[-1] == "shp":
                    prjLocation = layerSource[0:-4] + ".prj"
                    if os.path.isfile(prjLocation):
                        try:
                            # check for write access
                            f = open(prjLocation, "r+")
                            f.close()
                            canDefineLayer = True
                        except:
                            canDefineLayer = False
                    else:
                        try:
                            # check for write access
                            f = open(prjLocation, "w+")
                            f.close()
                            canDefineLayer = True
                        except:
                            canDefineLayer = False
                        try:
                            os.remove(prjLocation)
                        except:
                            pass

        DockableWindow.convertLayerToCoordinateSystemAction.setEnabled(canConvertLayer)
        DockableWindow.defineLayerCoordinateSystemAction.setEnabled(canDefineLayer)
        DockableWindow.defineFrameCoordinateSystemAction.setEnabled(canSetDataFrame)


##############################################################################
##
# Search management  #New code 20140908 to add search facility to CDDP
##
##############################################################################
    @staticmethod
    def searchTextChange(text):
        DataMenu.loadMenuData(Tools.dm, text)


###########################################################################
##
# Open Zoom to location  #New code 20140908 to add search facility to CDDP
# Updated 2018 with change of tenure data from multiple shapefiles to statewide gdb
##
##############################################################################
    @staticmethod
    def openSearchCadastre():
        # Check at least one layer loaded
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        if len(QgsMapLayerRegistry.instance().mapLayers()) != 0:
            # Get location of this file and use it to determine location of template sqlite file
            db_settings = DatabaseSettings()
            currentDirectory = os.path.dirname(os.path.abspath(__file__))
            parentDirectory = os.path.abspath(os.path.join(currentDirectory, os.pardir))
            usageLocation = db_settings.local_cadastre_db
            templateLocation = os.path.join(parentDirectory, "searchcadastre/resources/cadastre.sqlite")
            
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
              
            #if DockableWindow.searchCadastreDialog is not None:     # i.e. if object has already been created
            #    searchDialog = DockableWindow.searchCadastreDialog
            #else:
            Tools.searchDialog = SearchCadastreDialog(db_settings)
            #Tools.searchDialog.db_settings = db_settings
            Tools.searchDialog.show()
            Tools.searchDialog.dataCurrencyCheck()
            ##### Should prob check for and delete old db and registry settings
            QApplication.restoreOverrideCursor()
        else:
            QApplication.restoreOverrideCursor()
            QMessageBox.information(None, "Map Requirements", "Please load at least one layer to map first!")

##############################################################################
##
# Map Production
# New code by PWM; 20140923
##
##############################################################################

    @staticmethod
    def mapProduction():
        # Tools.mapProdTool = True
        # check  at least one layer
        if len(QgsMapLayerRegistry.instance().mapLayers()) == 0:
            Tools.alert("Please load at least one layer to map first!",
                        "Map Requirements")
        else:
            # validate CRS
            # if Tools.iface.mapCanvas().mapRenderer().destinationCrs().mapUnits() != QGis.Meters:
                # Tools.debug("It looks like you are using an unprojected Coordinate Reference System.\n" +
                            # "Change to a projected CRS then retry the Map Production Tool.",
                            # "Invalid Coordinate Reference System")
                # crsDialog = SelectCRSDialog(SelectCRSDialog.PROJECTEDFRAME, None, None)
                # #return     #removed this so user not required to again click on Map Prod Tool icon
            dlg = MapLabelDialog()
            if dlg.result != QDialog.Rejected:
                MapProduction().createMap(dlg)
            else:
                return
