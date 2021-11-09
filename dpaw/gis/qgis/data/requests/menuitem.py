from PyQt4.QtCore import Qt
from PyQt4.QtGui import QMessageBox, QStandardItemModel, QStandardItem
from qgis.core import *
import os.path

import qgis.utils
import xml.etree.ElementTree as ET

from .layersource import LayerSource

from ...tools import Tools
from ...data.requests.wmslayersource import WmsLayerSource


class MenuItem(object):

    def __init__(self):
        """ Initialises the required data structures. """
        self.requests = []

    def isValid(self):
        """ Returns false if the MenuItem contains no data requests. """
        return len(self.requests) > 0

    def addRequest(self, request):
        """ Appends the data request to the list """
        if request is not None:
            self.requests.append(request)

        if isinstance(request, WmsLayerSource):
            # Extract 'url' and 'layers' from wms layer
            url = request._url
            layers = request._layer_name
            title = request._title
            # Used to assemble list of WMS layers in data menu (on opening QGIS)
            Tools.WMSinCDDP[(url, layers)] = title

    def getDescriptions(self):
        return [r.description for r in self.requests]

    def doLoad(self, index=0):
        """ Performs the data request. """
        sb = qgis.utils.iface.mainWindow().statusBar()
        sb.showMessage("Loading data...")
        success = self.requests[index].load()
        if success:
            sb.showMessage("Loading Complete; Rendering...", 1000)

    @staticmethod
    def parseXML(XMLMenuElement, targetModel, text):
        """ Attach a MenuItem to the targetModel then populate it with data from the XMLMenuElement. """
        assert isinstance(XMLMenuElement, ET.Element), "Bad Parameter"
        assert (isinstance(targetModel, QStandardItemModel) or
                isinstance(targetModel, QStandardItem)), "Bad Parameter" + str(type(targetModel))

        quite = False

        # early exit if searching, but this is not a hit
        if text != "" and not (text.lower() in Tools.getAttributeFromElement(XMLMenuElement, "TITLE").lower()):
            return

        modelNode = QStandardItem()
        modelNode.setIcon(Tools.iconGlobe)
        targetModel.appendRow(modelNode)
        modelNode.setFlags(Qt.ItemIsEnabled)
        modelNode.setText(Tools.getAttributeFromElement(XMLMenuElement,"TITLE"))
        menuItem = MenuItem()
        for child in XMLMenuElement:
            tag = child.tag.lower()
            if tag[0] == "q":
                tag = tag[1:]
            elif tag[0] == "a":
                continue

            if tag in LayerSource.KNOWN_NODE_TYPES:
                layer_source = LayerSource.build(child)
                if layer_source is not None:
                    menuItem.addRequest(layer_source)
                continue

            elif tag == "layer_group":
                quite = True
                # This tag is now depreciated

            elif tag == "load_gdb":
                quite = True
                # This tag is used in ArcGIS but not supported here

            elif tag == "load_orthophotos":
                quite = True
                # This tag is used in ArcGIS but not supported here

            else:
                Tools.logError("Menu Error: unknown xml element " + tag)

        if menuItem.isValid():
            # TODO: handle hash conflicts
            id = Tools.getModelNodePath(modelNode)
            if id not in Tools.dataMenuDict:
                Tools.dataMenuDict[id] = menuItem
            else:
                Tools.logError("Menu Error: duplicate menu path " + id)
                targetModel.removeRow(targetModel.rowCount()-1)
        else:
            if quite is False:
                Tools.logError("Menu Error: No data requests found for " + modelNode.text())
            targetModel.removeRow(targetModel.rowCount() - 1)
