# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISTools2
                                 A QGIS plugin
 DPAW Tools for QGIS v 2.x
                              -------------------
        begin                : 2014-08-15
        copyright            : (C) 2014 by GIS Apps, Dept of Parks and Wildlife
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

from os import path
import sys

# add resources path for native libs for current environment
qgisTools2Folder = path.normpath(path.join(path.dirname(__file__)))
if sys.maxsize == 2147483647:
    sys.path.append(path.join(qgisTools2Folder, "resources/lib/x86"))
elif sys.maxsize == 9223372036854775807L:
    sys.path.append(path.join(qgisTools2Folder, "resources/lib/x64"))
else:
    pass

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from os import makedirs
import time
import win32com.client  # Used to obtain V: drive address on starting QGIS (see QGISTools2.__init__)
import shutil           # Used to copy project_default.qgs from resources folder to new user's .qgis2 folder
from dpaw.gis.qgis.ui.dockablewindow import DockableWindow
from dpaw.gis.qgis.tools import Tools
from dpaw.gis.qgis.mapproduction.mapproduction import MapProduction


# import sys
# sys.path.append("C:\\Users\\patrickm\\Desktop\\GISTools\\eclipseNEW\\plugins\\org.python.pydev_3.8.0.201409251235\\pysrc\\")
# from pydevd import*


class QGISTools2:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        Tools.iface = iface

        # Clean up any temp files that remain on the file system
        Tools.deleteFilesOnDeletionList()

        # initialize plugin directory
        self.plugin_dir = path.normpath(path.join(path.dirname(__file__), ("..")))
        if not QFileInfo(self.plugin_dir).exists():
            self.plugin_dir = path.normpath(path.join(QgsApplication.prefixPath(), "python/plugins/qgistools"))
        
        # Check whether this user has a .qgis2 folder containing project_default.qgs
        userProjDefaultLocation = path.normpath(path.join(QgsApplication.qgisSettingsDirPath(), "project_default.qgs"))
        pluginProjDefaultLocation = path.normpath(path.join(path.dirname(__file__), "resources/project_default_DPaW.qgs"))
        if not path.exists(userProjDefaultLocation) or Tools.getSetting("initialised_default_project", "false") == "false":
            shutil.copyfile(pluginProjDefaultLocation, userProjDefaultLocation)
            Tools.setSetting("initialised_default_project", "true")

        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = path.join(self.plugin_dir, 'i18n', 'qgistools2_{}.qm'.format(locale))

        if path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

               # Upload local WMS counter data to central counter
        # Check if local WMS log file exists; if not then create it.
        try:
            makedirs(Tools.localLogFolder())
        except:
            pass
        text = ""
        localWmsFilename = path.normpath(Tools.localLogFolder()) + Tools.localWMSLogFilename
        try:
            if not path.exists(localWmsFilename):
                fromFile = open(localWmsFilename, "w+")    # Creates local log file if it does not exist"
            else:
                fromFile = open(localWmsFilename, "r+")    # Allows us to overwrite (to empty string)
            text = fromFile.read()
        except:
            pass
        
        if text != "":
            # check for central log file for this month
            try:
                centralWMSFilename = str(Tools.centralLogFolder()) + "\wms_" + time.strftime("%Y%m") + ".log"
                if not path.exists(centralWMSFilename):
                    toFile = open(centralWMSFilename, "w+")
                else:
                    toFile = open(centralWMSFilename, "a")
                toFile.write(text)
                toFile.close()
                fromFile.seek(0, 0)     # Return cursor to start of file
                fromFile.truncate()     # Remove contents
            except:
                pass
            fromFile.close()

        
        # Upload local CDDP counter data to central counter
        # Check if local log file exists; if not then create it.
        text = ""
        localFilename = path.normpath(Tools.localLogFolder()) + Tools.localLogFilename
        try:
            if not path.exists(localFilename):
                fromFile = open(localFilename, "w+")    # Creates file if it does not exist"
            else:
                fromFile = open(localFilename, "r+")    # Allows us to overwrite (to empty string)
            text = fromFile.read()
        except:
            pass

        if text != "":
            # check for central log file for this month
            try:
                centralFilename = str(Tools.centralLogFolder()) + "\cddp_" + time.strftime("%Y%m") + ".log"
                if not path.exists(centralFilename):
                    toFile = open(centralFilename, "w+")
                else:
                    toFile = open(centralFilename, "a")
                toFile.write(text)
                toFile.close()
                fromFile.seek(0, 0)     # Return cursor to start of file
                fromFile.truncate()     # Remove contents
            except:
                pass
            fromFile.close()

        # Get V: drive address if it exists - see http://www.thescriptlibrary.com/Default.asp?Action=Display&Level=Category3&ScriptLanguage=Python&Category1=Storage&Category2=Disk%20Drives%20and%20Volumes&Title=List%20Mapped%20Network%20Drives
        #strComputer = "."
        #objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        #objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2")
        #mappedDrives = objSWbemServices.ExecQuery("Select * from Win32_MappedLogicalDisk")
        #for drive in mappedDrives:
        #    if drive.Name == "V:":
                # This became ineffective due to IT changes (to DFS)
                #Tools.corporateDataDrive = drive.ProviderName
                #QSettings().setValue("DEC/vDriveSite", "Kensington")
                #Tools.debug(QSettings().value("DEC/vDriveSite"))

        # Get corporate data site
        #Tools.corporateDataDrive = Tools.readSiteLocationFile()


    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(path.join(Tools.getPluginPath(), r"resources\icons\DBCA.png")),
            Tools.get_application_name(),
            Tools.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.run)

        # Add toolbar button and menu item
        Tools.iface.addToolBarIcon(self.action)
        Tools.iface.addPluginToMenu(u"&QGIS Tools 2", self.action)

        Tools.iface.newProjectCreated.connect(Tools.newProject)
        Tools.iface.projectRead.connect(Tools.loadProject)
        QgsMapLayerRegistry.instance().layersAdded.connect(Tools.layersAdded)
        
        Tools.loadWMSPresets()
        Tools.loadWFSPresets()
        DockableWindow.getDockable(True)
        
    def unload(self):
        # Remove the plugin menu item, icon and interface
        Tools.iface.removePluginMenu(u"&QGIS Tools 2", self.action)
        Tools.iface.removeToolBarIcon(self.action)
        mw = Tools.iface.mainWindow()
        dock = mw.findChild(QDockWidget, Tools.get_application_name())
        mw.removeDockWidget(dock)

    def run(self):
        DockableWindow.getDockable()
