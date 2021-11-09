from collections import namedtuple
from xml.etree import ElementTree

from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QMessageBox, QTextDocument
from PyQt4.QtNetwork import QNetworkRequest

from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsMapLayerRegistry
from qgis.core import QgsNetworkAccessManager
from qgis.core import QgsVectorLayer
from qgis.utils import iface

from ...data.requests.layersource import LayerSource
from ...tools import Tools


class AgolFeatureServerLayerSource(LayerSource):
    DEFAULT_DESCRIPTION = "AgolFeatureServerLayerSource"
    XML_NODE_NAME = "load_agol_feature_server_layer"

    def __init__(self):
        super(self.__class__, self).__init__()
        self._url = ""
        self._qml = ""

    def _load_from_source(self):
        layer = AgolFeatureServerLayerSource.load_layer(self._url, self._title, self._qml)

        if layer is None:
            Tools.clear_status_bar()
        return layer

    def _is_valid(self):
        return super(self.__class__, self)._is_valid() \
               and len(self._url) > 0 

    @staticmethod
    def build(xml_element):
        agol_feature_server_layer_source = AgolFeatureServerLayerSource()
        agol_feature_server_layer_source._url = Tools.getAttributeFromElement(xml_element, "url")
        #agol_feature_server_layer_source._title = Tools.getAttributeFromElement(xml_element, "title")
        agol_feature_server_layer_source._qml = Tools.getAttributeFromElement(xml_element, "qml")
        return agol_feature_server_layer_source

    @staticmethod
    def load_layer(url, title="", qml=""):
        layer = QgsVectorLayer(url, baseName=title, providerLib="arcgisfeatureserver")

        if not layer.isValid():
            Tools.alert("Invalid layer for " + title + ".  Contact GIS Administrator.")
            return None

        if qml != "":
            qml_location = path.join(path.dirname(shp_path), qml)
            if path.isfile(qml_location):
                layer.loadNamedStyle(qml_location)
            else:
                Tools.alert("Unable to find style file " + qml_location)
        #QMessageBox.information(None, "", "about to return layer")
        return layer    

    
