# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
import qgis.utils
import os.path
import datetime

import xml.etree.ElementTree as ET
from ..tools import Tools
from ..data.requests.menuitem import MenuItem


class DataMenu:

    ###############################
    def __init__(self, layout):
        # TODO assert treeview
        self.view = QTreeView()
        layout.addWidget(self.view)

        self.view.setUniformRowHeights(True)
        self.view.setHeaderHidden(True)
        self.view.setSelectionMode(QAbstractItemView.NoSelection)
        self.view.setExpandsOnDoubleClick(False)
        self.view.setRootIsDecorated(False)

        self.view.pressed.connect(self.handleDataMenuPressed)
        self.view.customContextMenuRequested.connect(self.openContextMenu)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)

        self.viewModel = QStandardItemModel()
        self.view.setModel(self.viewModel)

        self.loadMenuData()

    def openContextMenu(self, position):
        model_index = self.view.indexAt(position)
        model_node = self.viewModel.itemFromIndex(model_index)
        model_node_path = Tools.getModelNodePath(model_node)

        if model_node_path not in Tools.dataMenuDict:
            return

        menu_item = Tools.dataMenuDict[model_node_path]

        menu = QMenu()
        for index, desc in enumerate(menu_item.getDescriptions()):
            action = menu.addAction(desc)
            action.setData(index)
        action = menu.exec_(self.view.mapToGlobal(position))
        if action is None:
            return
        Tools.selectTopLegendItem()
        menu_item.doLoad(action.data())

    def loadMenuData(self, text=""):
        Tools.dataMenuDict = {}
        self.viewModel.clear()

        # load from v drive
        corpMenuPath = Tools.findData(r"Index\Config\menu_3.0.xml")
        #corpMenuPath = r"C:\Users\patrickm\Desktop\menu_3.0.xml"
        corpMenuSuccess = self.parseMenu(corpMenuPath, text)

        # check for XP
        personalMenuPath = os.path.join(Tools.getUsersDocumentsDirectory(), "menu_3.0.xml")
        personalMenuSuccess = False
        if os.path.isfile(personalMenuPath):
            personalMenuSuccess = self.parseMenu(personalMenuPath, text)

        if not (corpMenuSuccess or personalMenuSuccess):
            Tools.debug("Unable to load menu.xml files.\nPlease check your V: drive is mapped or USB drive connected.\nIf these are correct please check the settings under QGIS Tools > Tools > Settings > Data Locations.")
###########################################

    def handleDataMenuPressed(self, index):
        """ Action a MenuItem or expand/collapse a menu branch as required. """
        assert isinstance(index, QModelIndex), "Bad Parameter"

        if QApplication.mouseButtons() != Qt.LeftButton:
            return

        Tools.cddpTechnique = "menu"
        modelNode = self.viewModel.itemFromIndex(index)

        if (modelNode.columnCount() == 0):
            # menu leaf, will correspond with a menu item
            menuItem = Tools.dataMenuDict[Tools.getModelNodePath(modelNode)]
            Tools.selectTopLegendItem()
            menuItem.doLoad()
        else:
            # menu branch, will correspond with a menu branch
            self.view.setExpanded(index, not self.view.isExpanded(index))
        Tools.flushErrors()
        

############################################################
    def parseMenuElement(self, xml_menu_element, target_model, text):
        """ Attach a node to the targetModel then populate it with data from the XMLMenuElement. """
        assert isinstance(xml_menu_element, ET.Element), "Bad Parameter"
        assert (isinstance(target_model, QStandardItemModel) or
                isinstance(target_model, QStandardItem)), "Bad Parameter" + str(type(target_model))

        # Tools.debug(str(xml_menu_element))

        model_node = QStandardItem()
        model_node.setIcon(Tools.iconFolder)
        target_model.appendRow(model_node)
        model_node.setFlags(Qt.ItemIsEnabled)
        model_node.setText(Tools.getAttributeFromElement(xml_menu_element, "TITLE"))

        for child in xml_menu_element:
            tag = child.tag.lower()
            if tag[0] == "q":
                tag = tag[1:]
            elif tag[0] == "a":
                continue
            if tag == "menu":
                self.parseMenuElement(child, model_node, text)
            elif tag == "item":
                MenuItem.parseXML(child, model_node, text)
            else:
                # unknown xml
                Tools.logError("Menu Error: unknown xml element " + tag)

        # validate menu element
        if model_node.rowCount() == 0:
            # Tools.logError("Menu Error: No children found for " + model_node.text())
            target_model.removeRow(target_model.rowCount() - 1)


########################
    def parseMenu(self, xml_location, text=""):
        if xml_location == "":
            return False

        min_search_length = 1

        if len(text) < min_search_length:
            text = ""

        tree = ET.parse(xml_location)
        root = tree.getroot()
        for child in root:
            tag = child.tag.lower()
            if tag[0] == "q":
                tag = tag[1:]
            elif tag[0] == "a":
                continue
            if tag == "menu":
                self.parseMenuElement(child, self.viewModel, text)
            elif tag == "item":
                MenuItem.parseXML(child, self.viewModel, text)
            else:
                # unknown xml
                Tools.logError("Menu Error: unknown xml element " + tag)

        if text != "":
            self.view.expandAll()

        return True
