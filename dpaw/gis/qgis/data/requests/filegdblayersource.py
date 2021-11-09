from os import path

from qgis.core import QgsVectorLayer

from ...data.requests.layersource import LayerSource
from ...tools import Tools


class FileGdbLayerSource(LayerSource):

    DEFAULT_DESCRIPTION = "FileGdbLayerSource"
    XML_NODE_NAME = "load_filegdb"

    def __init__(self):
        super(self.__class__, self).__init__()
        self._directory = ""
        self._filegdb = ""
        self._layername = ""
        self._qml = ""

    def _load_from_source(self):
        filegdb_path_snippet = path.join(self._directory, self._filegdb)
        layer = FileGdbLayerSource.load_layer(filegdb_path_snippet, self._layername, qml=self._qml)
        if layer is None:
            Tools.clear_status_bar()
        return layer

    def _is_valid(self):
        return super(self.__class__, self)._is_valid() \
               and len(self._directory) > 0 \
               and len(self._filegdb) > 0 \
               and len(self._layername) > 0

    @staticmethod
    def build(xml_element):
        filegdb_layer_source = FileGdbLayerSource()
        filegdb_layer_source._directory = Tools.getAttributeFromElement(xml_element, "directory")
        filegdb_layer_source._filegdb = Tools.getAttributeFromElement(xml_element, "filegdb")
        filegdb_layer_source._layername = Tools.getAttributeFromElement(xml_element, "layername")
        filegdb_layer_source._qml = Tools.getAttributeFromElement(xml_element, "qml")
        return filegdb_layer_source

    @staticmethod
    def load_layer(relative_path, layername, title="", qml=""):
        filegdb_path = Tools.findData(relative_path)

        if qml == "":
            qml = "{}.qml".format(layername)

        title = Tools.substituteRegion(title, " ")

        if filegdb_path == "":
            Tools.alert("unable to find " + relative_path)
            return None

        uri = "{}|layername={}".format(filegdb_path, layername)
        layer = QgsVectorLayer(uri, title, "ogr")

        if not layer.isValid():
            Tools.alert("Invalid data found at: {}".format(filegdb_path), "Error")
            return None

        qml_path = path.join(path.dirname(filegdb_path), qml)
        if path.isfile(qml_path):
            layer.loadNamedStyle(qml_path)

        return layer
