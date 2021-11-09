from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from PyQt4.QtXml import *
from PyQt4.QtNetwork import QNetworkAccessManager

import os.path
import os
import xml.etree.ElementTree as ET

import platform     # Used to get machine name for counter
import socket       # Used to get IP address for counter
import getpass      # Used to get username for counter
from datetime import datetime
import time
import ctypes.wintypes
import qgis.utils
import string
import traceback

from ui.showprojecttemplatedialog import ShowProjectTemplateDialog
from searchcadastre.searchcadastre import SearchCadastreDialog


class Tools():
    net_manager = QNetworkAccessManager()     # TODO: Clean up after alt data source work
    isNewProject = True
    regions = ["Goldfields",
               "Kimberley",
               "Midwest",
               "Pilbara",
               "South_Coast",
               "South_West",
               "Swan",
               "Warren",
               "Wheatbelt"]
    errorList = ""
    _region = None
    _dataDrive1 = None
    _dataDrive2 = None
    _showDefaultMapDialogue = True
    _dept_long_name = None
    _dept_acronym = None
    dataPath = "\\GIS1-Corporate\\Data\\"
    lastID = 0
    releaseDate = "10-Jun-2019"
    versionNumber = "2.5.5"
    QGISApp = None
    dataMenuDict = dict({"null": 0})
    #WMSServerSummaryDict = dict({"null": 0})
    dockableWidgetManager = None
    _pluginPath = ""
    composers = []
    #localLogFolder = r"C:\ProgramData\DEC\GIS"
    localLogFilename = r"\cddp.log"
    localWMSLogFilename = r"\wms.log"
    #centralLogFolder = os.path.abspath(r"\\kens-dfs-002\Layer_Counter")
    machineName = platform.node()
    username = getpass.getuser()
    cddpTechnique = "manual"    # Default for counter method
    lastProject = ""        # Used in cddpTechnique decision
    lastPageSize = "A3"     # Used to decide which radio button is selected on opening the map prod tool (updates so previous one used is checked)
    lastPageOrientation = "Portrait"    # As above but for orientation
    WMSinCDDP = {}
    corporateDataDrive = "External"     # Normally this will be overwritten on starting QGIS, with the V: drive address


    iconApp = QIcon(":/plugins/qgistools2/DPAW.png")
    iconFolder = QIcon(":/plugins/qgistools2/folder.png")
    iconGlobe = QIcon(":/plugins/qgistools2/globe.png")
    iconPrinter = QIcon(":/plugins/qgistools2/printer.png")
    iconPageSetup = QIcon(":/plugins/qgistools2/page_white_gear.png")
    iconMapPro = QIcon(":/plugins/qgistools2/map_edit.png")
    iconMapCog = QIcon(":/plugins/qgistools2/map_cog.png")
    iconMapLabel = QIcon(":/plugins/qgistools2/map_edit.png")
    iconZoomLocation = QIcon(":/plugins/qgistools2/binocs.png")
    iconRefresh = QIcon(":/plugins/qgistools2/refresh.png")
    startTime = None
    stopTime = None
    # Create SearchCadastreDialog object if search has been created before (checked by looking for database setting)
    #s = QSettings()
    #db = s.value(r"SearchCadastre/database")
    searchCadastreDialog = None
    #if db is not None:
    #searchCadastreDialog = SearchCadastreDialog()   # This is here because too slow if initialised in SearchCadastreDialog.__init__


#######################
    def __init__(self):
        # Does not appear to be called
        #QMessageBox.information(None, "", "Tools.__init__")
        self.dockableWidgetManager = DataMenu()
        Tools._region = Tools.getRegion()

####################
    @staticmethod
    def getNextID():
        """ Generates a unique string ID. """
        Tools.lastID += 1
        return str(Tools.lastID)

########################
    @staticmethod
    def dataLocation1():
        """ Primary data location. """
        path = Tools.getDataDrive1() + Tools.dataPath
        return Tools.endWithSlash(path)

########################
    @staticmethod
    def dataLocation2():
        """ Secondary data location. """
        path = Tools.getDataDrive2() + Tools.dataPath
        return Tools.endWithSlash(path)

###################################
    @staticmethod
    def findData(relative_location, zone=""):
        # Searches the dataDrives for the required file,
        # then returns complete path.

        if relative_location.startswith("?"):
            relative_location = relative_location[1:]
            relative_location = Tools.substituteRegion(relative_location)
            relative_location = Tools.substituteZones(relative_location, zone)
            if os.path.isfile(relative_location) or os.path.isdir(relative_location):
                return relative_location
            else:
                return ""

        # pine plantations imagery tile index has the data path stored in the
        # attribute table.  This will correct:
        if relative_location.lower().startswith(Tools.dataPath.lower()):
            relative_location = relative_location[len(Tools.dataPath):]

        while relative_location[0] == "\\":
            relative_location = relative_location[1:]
        relative_location = Tools.substituteRegion(relative_location)
        relative_location = Tools.substituteZones(relative_location, zone)

        path = Tools.dataLocation1() + relative_location
        if os.path.isfile(path) or os.path.isdir(path):
            return path

        path = Tools.dataLocation2() + relative_location
        if os.path.isfile(path) or os.path.isdir(path):
            return path

        return ""

    #############
    @staticmethod
    def format_title(title):
        return Tools.substituteRegion(title, " ")

    @staticmethod
    def get_dept_long_name():
        if Tools._dept_long_name is None:
            Tools._dept_long_name = Tools.getSetting("dept_long_name", "Department of Biodiversity, Conservation and Attractions")
        return Tools._dept_long_name

    @staticmethod
    def set_dept_long_name(value):
        Tools.setSetting("dept_long_name", value)
        Tools._dept_long_name = value

    @staticmethod
    def get_dept_acronym():
        if Tools._dept_acronym is None:
            Tools._dept_acronym = Tools.getSetting("dept_acronym", "DBCA")
        return Tools._dept_acronym

    @staticmethod
    def set_dept_acronym(value):
        Tools.setSetting("dept_acronym", value)
        Tools._dept_acronym = value

    @staticmethod
    def get_application_name():
        return "{0} QGIS Tools".format(Tools.get_dept_acronym())

    ############################
    @staticmethod
    def endWithSlash(input):
        """ Returns the input with trailing slash appended as necessary. """
        if input[-1:] != "\\":
            input += "\\"
        return input

###################################################
    @staticmethod
    def substituteRegion(input, spaceDelimiter="_"):
        """ Replaces %REG% with the current region. """
        region = Tools.getRegion()
        if spaceDelimiter != "_":
            region = region.replace("_", spaceDelimiter)
        return input.replace("%REG%", region)

###################################################
    @staticmethod
    def substituteZones(input, zone=""):
        """ Replaces %REG% with the current region. """
        if zone != "":
            zoneNumber = zone.replace("z", "")
            return input.replace("%ZONE%", zone).replace("%ZONE#%", zoneNumber)
        else:
            return input

###################################
    @staticmethod
    def debug(text="trace", title="Debug"):
        """ Immediately display text for debugging purposes. """

        # import inspect
        # curframe = inspect.currentframe()
        # calframe = inspect.getouterframes(curframe, 2)
        # title += str(calframe[1][1][-20:]) + str(calframe[1][2])

        if text is None:
            text = "None"
        if not isinstance(text, str):
            try:
                text = str(text)
            except:
                text = "unable to display text\n"

        # show call stack for debug
        if True:
            text += "\n" + "---"
            lines = traceback.format_stack()
            lines = lines[:-1]
            i = 0
            for line in lines:
                text += "\n{0}: {1}".format(i, line.rstrip())
                i += 1

        QMessageBox.information(None, title, Qt.convertFromPlainText(text))

###################################
    @staticmethod
    def alert(text, title="Alert"):
        """ Immediately display text for notification purposes. """
        if not isinstance(text, str):
            text = str(text)

        # show call stack for debug
        if False:
            text += "\n" + "---"
            lines = traceback.format_stack()
            lines = lines[:-1]
            i = 0
            for line in lines:
                text += "\n{0}: {1}".format(i, line.rstrip())
                i += 1

        QMessageBox.information(None, title, Qt.convertFromPlainText(text))

###################################
    @staticmethod
    def showYesNoDialog(text, title="Question"):
        """ Ask the user a Yes/No question. """
        if not isinstance(text, str):
            text = str(text)
        messageBox = QMessageBox()
        messageBox.setText(text)
        messageBox.setWindowTitle(title)
        messageBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        messageBox.setDefaultButton(QMessageBox.Yes)
        return messageBox.exec_() == QMessageBox.Yes

##########################
    @staticmethod
    def logError(message):
        """ Stores an error to be displayed later. """
        if message != "":
            Tools.errorList += message+"\n"

###################################
    @staticmethod
    def flushErrors(title="Error"):
        """ Presents any logged errors to the user. """
        if Tools.errorList != "":
            QMessageBox.information(None, title, Tools.errorList)
            Tools.errorList = ""

##################################
    @staticmethod
    def checkForOTFReprojection():
        """ Check for on the fly reprojection ann CRS conflicts,
            will advise the user if conflict is detected """
        return
        mc = qgis.utils.iface.mapCanvas()
        if not mc.hasCrsTransformEnabled():
            crs = None
            for layer in mc.layers():
                if crs is None:
                    crs = layer.crs()
                elif layer.crs() != crs:
                    #mc.mapRenderer().setProjectionsEnabled(True)
                    mc.mapSettings().setCrsTransformEnabled(True)
                    Tools.alert("""
The current project contains layers of different coordinate reference
systems.  "On the fly projection" has been enabled so that they will display
correctly.

On the fly projection can be enabled/disabled for the current project by
selecting:
Settings - Project Properties... - Coordinate Reference Systems (CRS) - Enable
'on the fly' CRS transformations
OR clicking clicking on the "Globe" icon second right icon of the status bar,
then ticking Enable 'on the fly' CRS transformations

On the fly projection can be enabled/disabled for future projects by
selecting:
Settings - Options... - CRS - Enable 'on the fly' reprojection by default.
                    """)
                    break

################################################
    # TODO: Clean up after alt data source work
    @staticmethod
    def moveLayersToNewGroup(title, layerCount):
        legend = qgis.utils.iface.legendInterface()
        groupLayer = legend.addGroup(title)
        movedCount = 0
        nextLayer = 0
        while movedCount < layerCount:
            if nextLayer != groupLayer:
                legend.moveLayer(legend.layers()[nextLayer], groupLayer)
                movedCount += 1
            # find group
            layerList = legend.groupLayerRelationship()
            for index, item in enumerate(layerList):
                if item[0] == str(title):
                    groupLayer = index
                    break
            nextLayer += 1
        legend.setGroupExpanded(groupLayer, False)
        return groupLayer

##################################
    @staticmethod
    def getFilenameFromPath(path):
        return os.path.basename(path).split('.', 1)[0]

##################################
    @staticmethod
    def selectTopLegendItem():
        legend = qgis.utils.iface.legendInterface()
        layers = legend.layers()
        if len(layers) > 0:
            legend.setCurrentLayer(layers[0])

##################################
    @staticmethod
    def moveTopLegendItemToBottom():
        #Check but seems only to have been formerly used in map production; QGIS crashes 2.8
        legend = Tools.iface.mainWindow().findChildren(QTreeWidget)[0]
        legend.insertTopLevelItems(legend.topLevelItemCount()-1,
                                   [legend.takeTopLevelItem(0)])

###################################################
    @staticmethod
    def getAttributeFromElement(XMLMenuElement, tag):
        # Gets attributes value from XML element (tag is case insensitive)
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"
        assert isinstance(tag, str), "Bad Parameter"

        tag = tag.lower()
        value = None
        value = XMLMenuElement.get(tag)
        if value is None:
            for key in XMLMenuElement.keys():
                if key.lower() == tag.lower():
                    value = XMLMenuElement.get(key)
                    break
        if value is None:
            value = ""
        return value

##################################
    @staticmethod
    def getModelNodePath(modelNode):
        """ Returns the absolute path of the modelNode. """
        assert isinstance(modelNode, QStandardItem), "Bad Parameter"

        path = modelNode.text()
        parent = modelNode.parent()
        while (parent != 0 and parent is not None):
            path = parent.text() + "\\" + path
            parent = parent.parent()
        return "\\" + path

#####################
    @staticmethod
    def startTimer():
        Tools.startTime = datetime.now()
        Tools.stopTime = None

####################
    @staticmethod
    def stopTimer():
        Tools.stopTime = datetime.now()

####################
    @staticmethod
    def showTimer():
        if Tools.startTime is not None:
            if Tools.stopTime is not None:
                delta = Tools.stopTime - Tools.startTime
                Tools.debug(delta)

######################################
    @staticmethod
    def getSetting(name, default=None, namespace='DEC'):
        key = "{}/{}".format(namespace, name)
        return str(QSettings().value(key, default))

################################
    @staticmethod
    def setSetting(name, value, namespace='DEC'):
        key = "{}/{}".format(namespace, name)
        QSettings().setValue(key, value)

####################
    @staticmethod
    def getRegion():
        # check member variable
        if Tools._region is not None:
            if Tools._region in Tools.regions:
                return Tools._region
        # check QSettings
        reg = Tools.getSetting("region", Tools.regions[0])
        if reg in Tools.regions:
            Tools._region = reg
            return reg
        # default value
        reg = Tools.regions[0]
        Tools.setRegion(reg)
        return reg

#########################
    @staticmethod
    def setRegion(value):
        assert value in Tools.regions, "Bad Region value"
        Tools._region = value
        Tools.setSetting("region", value)

#############################
    @staticmethod
    def setDataDrive1(value):
        assert Tools.validateDataDrive(value), "Bad datadrive value"
        Tools._dataDrive1 = value
        Tools.setSetting("datadrive1", value)

#############################
    @staticmethod
    def getDataDrive1():
        # check member variable
        if Tools._dataDrive1 is not None:
            if Tools.validateDataDrive(Tools._dataDrive1):
                return Tools._dataDrive1
        # check QSettings
        dd = Tools.getSetting("datadrive1", "V:")
        if Tools.validateDataDrive(dd):
            Tools._dataDrive1 = dd
            return dd
        # default value
        dd = "V:"
        Tools.setDataDrive1(dd)
        return dd

#############################
    @staticmethod
    def setDataDrive2(value):
        assert Tools.validateDataDrive(value), "Bad datadrive value"
        Tools._dataDrive2 = value
        Tools.setSetting("datadrive2", value)

#############################
    @staticmethod
    def getDataDrive2():
        # check member variable
        if Tools._dataDrive2 is not None:
            if Tools.validateDataDrive(Tools._dataDrive2):
                return Tools._dataDrive2
        # check QSettings
        dd = Tools.getSetting("datadrive2", "V:")
        if Tools.validateDataDrive(dd):
            Tools._dataDrive2 = dd
            return dd
        # default value
        dd = "V:"
        Tools.setDataDrive2(dd)
        return dd

#################################
    @staticmethod
    def validateDataDrive(value):
        if not isinstance(value, str):
            Tools.debug("not str")
        if (not isinstance(value, str) or len(value) != 2 or
                value[0] not in string.ascii_letters or value[1] != ":"):
            return False
        else:
            return True

#################################
    @staticmethod
    def setPluginPath(path):
        Tools._pluginPath = str(path)

#################################
    @staticmethod
    def getPluginPath():
        if len(Tools._pluginPath) > 0:
            return Tools._pluginPath


        # report missing plugin
        Tools.debug("This plugin is in an invalid state and is unable to locate the plugin directory!" +
                    "\nPlease contact GIS Applications for further advice.",
                    "Plugin Error")

#############################
    @staticmethod
    def setDockArea(value):
        Tools.setSetting("dockarea", value)

#############################
    @staticmethod
    def getDockArea():
        # check QSettings with default, faster that checking length of
        # returned value, then returning default as needed
        dd = int(Tools.getSetting("dockarea", Qt.LeftDockWidgetArea))
        return dd

#################################
    @staticmethod
    def activeLayer():
        if len(qgis.utils.iface.legendInterface().selectedLayers()) == 1:
            return qgis.utils.iface.activeLayer()

#################################
    @staticmethod
    def getLayerSourceType(layer):
        if layer is None:
            return "none"

        layer_source = layer.source()

        if layer_source.rsplit(".", 1)[-1].lower() == "shp":
            return "shapefile"

        if layer_source.split("|", 1)[0].rsplit(".", 1)[-1] == "gdb":
            return "filegdb"

        return "other"

#################################
    @staticmethod
    def log(message):
        return
        message = str(message)
        location = "E:/temp/QGISTOOLSLOG.txt"
        try:
            with open(location, "a") as myfile:
                myfile.write(str(datetime.now())+"\t"+message + "\r\n")
        except:
            from time import sleep
            sleep(1)
            Tools.log("log file access Error!\r\n"+message)

#################################
    @staticmethod
    def loadWMSPresets():
        settings = QSettings()
        settings.beginGroup("/QGis")

        location = Tools.findData(r"Index\Config\SLIP_WMS_connections.xml")
        xmlFile = QFile(location)
        if not xmlFile.open(QIODevice.ReadOnly | QIODevice.Text):
            return

        domDoc = QDomDocument()
        if not domDoc.setContent(xmlFile, True):
            return

        root = domDoc.documentElement()
        if root.tagName() == "qgsWMSConnections":
            child = root.firstChildElement()
            while not child.isNull():
                connectionName = child.attribute("name")
                settings.setValue("/connections-wms/" + connectionName +
                                  "/url", child.attribute("url"))
                settings.setValue("/connections-wms/" + connectionName +
                                  "/ignoreGetMapURI",
                                  child.attribute("ignoreGetMapURI") == "true")
                settings.setValue("/connections-wms/" + connectionName +
                                  "/ignoreGetFeatureInfoURI",
                                  child.attribute("ignoreGetFeatureInfoURI") == "true")
                # if not child.attribute( "username" ).isEmpty():
                if child.attribute("username") != "":
                    settings.setValue("/WMS/" + connectionName + "/username",
                                      child.attribute("username"))
                    settings.setValue("/WMS/" + connectionName + "/password",
                                      child.attribute("password"))
                child = child.nextSiblingElement()

#################################
    @staticmethod
    def loadWFSPresets():
        settings = QSettings()
        settings.beginGroup("/QGis")

        location = Tools.findData(r"Index\Config\SLIP_WFS_connections.xml")
        xmlFile = QFile(location)
        if not xmlFile.open(QIODevice.ReadOnly | QIODevice.Text):
            return

        domDoc = QDomDocument()
        if not domDoc.setContent(xmlFile, True):
            return

        root = domDoc.documentElement()
        if root.tagName() == "qgsWFSConnections":
            child = root.firstChildElement()
            while not child.isNull():
                connectionName = child.attribute("name")
                settings.setValue("/connections-wfs/" + connectionName +
                                  "/url", child.attribute("url"))
                settings.setValue("/connections-wfs/" + connectionName +
                                  "/ignoreGetMapURI",
                                  child.attribute("ignoreGetMapURI") == "true")
                settings.setValue("/connections-wfs/" + connectionName +
                                  "/ignoreGetFeatureInfoURI",
                                  child.attribute("ignoreGetFeatureInfoURI") == "true")
                if child.attribute("username") != "":
                    settings.setValue("/WFS/" + connectionName + "/username",
                                      child.attribute("username"))
                    settings.setValue("/WFS/" + connectionName + "/password",
                                      child.attribute("password"))
                child = child.nextSiblingElement()

#######################################
    @staticmethod
    def getFilesForDeletionList():
        files_list = Tools.getSetting("FilesForDeletion", "").split(";")
        if len(files_list) == 1 and len(files_list[0]) == 0:
            return []
        return files_list

#######################################
    @staticmethod
    def setFilesForDeletionList(file_list):
        Tools.setSetting("FilesForDeletion", ";".join(file_list))

#######################################
    @staticmethod
    def addFileToDeletionList(filepath):
        file_list = Tools.getFilesForDeletionList()
        for existing_filepath in file_list:
            if filepath == existing_filepath:
                return
        file_list.append(filepath)
        Tools.setFilesForDeletionList(file_list)

#######################################
    @staticmethod
    def removeFileFromDeletionList(filepath):
        file_list = Tools.getFilesForDeletionList()
        file_list[:] = [f for f in file_list if f != filepath]
        Tools.setFilesForDeletionList(file_list)

#################################
    @staticmethod
    def deleteFilesOnDeletionList():
        # Background:
        #   A scenario may occur where a file is open for viewing in another application when os.remove() is called.
        # Sometimes os.remove() will complete without error but the file will remain on the file system (maybe the other
        # app has an non-exclusive lock) until the other app is closed.
        # Under these circumstances path.isfile() will return False for this path, os.remove() will raise exceptions and
        # the (non-empty) parent directory can't be removed.
        #
        # Solution:
        #   As we can't trust path.isfile() we just try to remove the directory anyway, if this fails then we know this
        # item will need to be processed later.
        error_list = []
        for filepath in Tools.getFilesForDeletionList():
            Tools.deleteFile(filepath)
            if not Tools.deleteDir(os.path.dirname(filepath)):
                error_list.append(filepath)
        Tools.setFilesForDeletionList(error_list)

#################################
    @staticmethod
    def deleteFile(filepath):
        # see notes under deleteFilesOnDeletionList()
        try:
            os.remove(filepath)
        except:
            pass

#################################
    @staticmethod
    def deleteDir(dirpath):
        if not os.path.isdir(dirpath):
            return True
        try:
            os.rmdir(dirpath)
        except:
            return False
        return not os.path.isdir(dirpath)

#################################
    @staticmethod
    def updateCounter(cddpLayer):
        # Check no commas in cddpLayer
        cddpLayer = cddpLayer.replace(", ", "_").replace(",", "_")
        # get path to counter.txt
        folder = os.path.abspath(Tools.localLogFolder())
        counter = os.path.normpath(folder) + Tools.localLogFilename
        project = QgsProject.instance()
        if project.fileName().replace("\\", "").replace("/","").endswith(".qgis2project_default.qgs"):
            Tools.cddpTechnique = "template"
        #if project.fileName() != "" and Tools.projectRead == False:    Initial line but did not cater for >1 project per session
        elif project.fileName() != "" and project.fileName() != Tools.lastProject: # Tools.lastProject is set to project.fileName() once all project layers have been loaded
            Tools.cddpTechnique = "project"
        try:
            user = Tools.username
            machine = Tools.machineName
            firstPipe = cddpLayer.find(r"|")
            if firstPipe > -1:
                cddpLayer = cddpLayer[:firstPipe]
            date = time.strftime("%Y%m%d")
            string = cddpLayer + ", " + user + ", " + machine + ", " + Tools.corporateDataDrive + ", " + date + ", QGIS, " + Tools.cddpTechnique + "\n"
            # open counter.txt in 'append' mode:
            with open(counter, "a") as counterFile:
                counterFile.write(string)
                counterFile.close()
            Tools.cddpTechnique = "manual"
        except IOError:
            # triggered if unable to write to file.
            # NB layer still loads but is not counted
            Tools.debug("cddp.log is open - " +
                        "please close it so that CDDP counts can be made.")
            return

#################################
    @staticmethod
    def updateWMSCounter(wmsLayer, url, wmsInCDDP):
        # Check no commas in wmsLayer
        wmsLayer = wmsLayer.replace(", ", "_").replace(",", "_")
        # get path to counter.txt
        folder = os.path.abspath(Tools.localLogFolder())
        wmsCounter = os.path.normpath(folder) + Tools.localWMSLogFilename
        project = QgsProject.instance()
        #if project.fileName() != "" and Tools.projectRead == False:    Initial line but did not cater for >1 project per session
        if project.fileName() != Tools.lastProject: # Tools.lastProject is set to project.fileName() once all project layers have been loaded
            Tools.cddpTechnique = "project"
        try:
            user = Tools.username
            machine = Tools.machineName
            date = time.strftime("%Y%m%d")
            string = wmsLayer + ", " + url + ", " + user + ", " + machine + ", " + Tools.corporateDataDrive + ", " + date + ", QGIS, " + Tools.cddpTechnique + wmsInCDDP + "\n"
            # open counter.txt in 'append' mode:
            with open(wmsCounter, "a") as counterFile:
                counterFile.write(string)
                counterFile.close()
            Tools.cddpTechnique = "manual"
        except IOError:
            # triggered if unable to write to file.
            # NB layer still loads but is not counted
            Tools.debug("wms.log is open - " +
                        "please close it so that WMS counts can be made.")
            return

    @staticmethod
    def clear_status_bar():
        Tools.iface.mainWindow().statusBar().clearMessage()

        #################################
    @staticmethod
    def readSiteLocationFile(drive):
        site = "Unknown"
        #siteFileLocation = Tools.findData(r"Index\Config\site_location.txt")
        siteFileLocation = drive + r"\GIS1-Corporate\Data\Index\Config\site_location.txt"
        #Tools.debug(siteFileLocation)
        if os.path.isfile(siteFileLocation):
            with open(siteFileLocation) as file:
                data = file.read()
            strippedData = data.strip()
            if len(strippedData) > 0:
                site = strippedData
        return site

#################################
    @staticmethod
    def newProject():
        Tools.isNewProject = True
        Tools.projectRead = False
        sb = Tools.iface.mainWindow().statusBar()
        sb.messageChanged.connect(Tools.showProjectTemplateDialog)

#################################
    @staticmethod
    def getUsersDocumentsDirectory():
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

        return buf.value

################################3#
    @staticmethod
    def truncate_string(text, max_length):
        if max_length < 3:
            return text[:max_length]
        return (text[:max_length - 3] + '...') if len(text) > max_length else text

#################################
    @staticmethod
    def showProjectTemplateDialog():
        setting = Tools.getSetting("showDefaultMapDialog", "DEC")
        if setting == "false":
            return
        sb = Tools.iface.mainWindow().statusBar()
        if sb.currentMessage() == "Project loaded":
            sb.messageChanged.disconnect()
            templateDialog = ShowProjectTemplateDialog()
            #self.previousStatusMessage = "Project loaded"
        #elif sb.currentMessage() == "":
        #    if self.previousStatusMessage == "Project loaded":
                #dialogue = ShowProjectTemplateDialog()
                #self.previousStatusMessage == ""
        else:
            pass
            #self.previousStatusMessage == ""

#################################
    @staticmethod
    def loadProject():
        Tools.isNewProject = False
        project = QgsProject.instance()
        #Tools.debug(project.fileName())
        Tools.lastProject = project.fileName()

#################################
    @staticmethod
    def layersAdded(layers):
        layer = layers[-1]
        if Tools.isNewProject:
            crs = layer.crs()
            settings = Tools.iface.mapCanvas().mapSettings()
            settings.setDestinationCrs(crs)
            settings.setCrsTransformEnabled(True)
            Tools.isNewProject = False

        source = layer.source().replace("\\", "/")
        dataLocation1 = Tools.dataLocation1().replace("\\", "/")
        dataLocation2 = Tools.dataLocation2().replace("\\", "/")
        #dataLocations = [dataLocation1, dataLocation2]
        #for dataLocation in dataLocations:
        if source.startswith(dataLocation1):     # i.e. (usually) if starts with "V:/GIS1-Corporate/Data/"
            start = len(dataLocation1)
            cddpLayer = source[start:]
            Tools.corporateDataDrive = Tools.readSiteLocationFile(Tools.getDataDrive1())
            Tools.updateCounter(cddpLayer)
        elif source.startswith(dataLocation2):     # i.e. if starts with "X:/GIS1-Corporate/Data/"
            start = len(dataLocation2)
            cddpLayer = source[start:]
            Tools.corporateDataDrive = Tools.readSiteLocationFile(Tools.getDataDrive2())
            Tools.updateCounter(cddpLayer)
        if layer.type() == QgsMapLayer.RasterLayer and layer.dataProvider().name() == "wms":
            url = ""
            layerList = []
            src = layer.source()
            srcParams = src.split("&")
            for param in srcParams:
                if param[:4] == "url=":
                    url = param[4:]
                elif param[:7] == "layers=":
                    layerList.append(param[7:])
            layersCount = len(layerList)

            if layersCount == 1:
                useParsedNames = True
                layerNames = [layer.name()]
            if layersCount > 1:
                # Try parsing (multi-)layer name - if count of names is same as layers count proceed,
                # else just use 'layers' variable
                layerNames = layer.name().split("/")
                if len(layerNames) == layersCount:
                    useParsedNames = True
                else:
                    useParsedNames = False

            i = 0
            for thisLayer in layerList:
                wmsParams = (url, thisLayer)
                wmsInCDDP = "start value"   # Used in development to check that code is working as expected
                title = None
                if Tools.cddpTechnique == "menu":
                    wmsInCDDP = ""
                else:
                    if wmsParams in Tools.WMSinCDDP:
                        wmsInCDDP = " - CDDP layer"
                        title = Tools.WMSinCDDP[wmsParams]
                    else:
                        wmsInCDDP = " - Non-CDDP layer"

                if useParsedNames:
                    if title is not None:
                        Tools.updateWMSCounter(title, url, wmsInCDDP)
                    else:
                        Tools.updateWMSCounter(layerNames[i], url, wmsInCDDP)
                    i += 1
                else:
                    Tools.updateWMSCounter(thisLayer, url, wmsInCDDP)

#################################
    @staticmethod
    def centralLogFolder():
        dpawGisUserSettings = QSettings("HKEY_CURRENT_USER\\SOFTWARE\\DPaW\\GIS", QSettings.NativeFormat)
        centralLogFolder = dpawGisUserSettings.value("CentralLogFolder")
        if centralLogFolder is None:
            dpawGisMachineSettings = QSettings("HKEY_LOCAL_MACHINE\\SOFTWARE\\DPaW\\GIS", QSettings.NativeFormat)
            centralLogFolder = dpawGisMachineSettings.value("CentralLogFolder")
            dpawGisUserSettings.setValue("CentralLogFolder", centralLogFolder)
        if centralLogFolder is None:
            dpawGisUserSettings.setValue("CentralLogFolder", r"\\kens-dfs-002\Layer_Counter")
            centralLogFolder = dpawGisUserSettings.value("CentralLogFolder")
        return centralLogFolder

#################################
    @staticmethod
    def localLogFolder():
        dpawGisUserSettings = QSettings("HKEY_CURRENT_USER\\SOFTWARE\\DPaW\\GIS", QSettings.NativeFormat)
        localLogFolder = dpawGisUserSettings.value("LocalLogFolder")
        if localLogFolder is None:
            dpawGisMachineSettings = QSettings("HKEY_LOCAL_MACHINE\\SOFTWARE\\DPaW\\GIS", QSettings.NativeFormat)
            localLogFolder = dpawGisMachineSettings.value("LocalLogFolder")
            dpawGisUserSettings.setValue("LocalLogFolder", localLogFolder)
        if localLogFolder is None:
            dpawGisUserSettings.setValue("LocalLogFolder", "C:\ProgramData\DEC\GIS")
            localLogFolder = dpawGisUserSettings.value("LocalLogFolder")
        return localLogFolder

#################################
    @staticmethod   # Can prob delete
    def setCadastreRegistry(cadastre):
        firstTenureLocation = Tools.dataLocation1() + r"Tenure\scdb" + "\\"
        secondTenureLocation = Tools.dataLocation2() + r"Tenure\scdb" + "\\"
        cadastreFilename = firstTenureLocation + cadastre[0] + ".shp"

        if os.path.isfile(cadastreFilename):
            QSettings().setValue(r"SearchCadastre/Cadastres/" + cadastre[1], firstTenureLocation + cadastre[0])
        elif os.path.isfile(cadastreFilename.replace(firstTenureLocation, secondTenureLocation)):
            QSettings().setValue(r"SearchCadastre/Cadastres/" + cadastre[1], secondTenureLocation + cadastre[0])
        elif os.path.isfile("V:" + cadastreFilename[2:]):
            QSettings().setValue(r"SearchCadastre/Cadastres/" + cadastre[1], "V:" + cadastreFilename[2:-4])

    @staticmethod
    def get_visible_extents(target_crs=None):
        canvas = qgis.utils.iface.mapCanvas()

        if canvas.layerCount() == 0:
            message_text = """Unable to determine the Map Extents.
Please load a base layer in order to establish a 
context (e.g. {} regions, WA Coast etc.)""".format(Tools.get_dept_acronym())
            Tools.alert(message_text, "No data in area")
            qgis.utils.iface.mainWindow().statusBar().showMessage("")
            return None

        extent_canvas_crs = canvas.extent()
        min_extent = QgsPoint(extent_canvas_crs.xMinimum(), extent_canvas_crs.yMinimum())
        max_extent = QgsPoint(extent_canvas_crs.xMaximum(), extent_canvas_crs.yMaximum())

        if target_crs is not None:
            canvas_crs = canvas.mapSettings().destinationCrs()
            transform = QgsCoordinateTransform(canvas_crs, target_crs)
            min_extent = transform.transform(min_extent)
            max_extent = transform.transform(max_extent)

        return QgsRectangle(min_extent, max_extent)
