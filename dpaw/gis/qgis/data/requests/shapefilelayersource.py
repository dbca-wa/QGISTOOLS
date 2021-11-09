from os import path

from qgis.core import QgsVectorLayer

from ...data.requests.layersource import LayerSource
from ...tools import Tools


class ShapefileLayerSource(LayerSource):

    DEFAULT_DESCRIPTION = "ShapefileLayerSource"
    XML_NODE_NAME = "load_shapefile"

    def __init__(self):
        super(self.__class__, self).__init__()
        self._directory = ""
        self._shapefile = ""
        self._qml = ""

    def _load_from_source(self):
        shp_path_snippet = path.join(self._directory, self._shapefile)
        layer = ShapefileLayerSource.load_layer(shp_path_snippet, qml=self._qml)
        if layer is None:
            Tools.clear_status_bar()
        return layer

    def _is_valid(self):
        return super(self.__class__, self)._is_valid() \
               and len(self._directory) > 0 \
               and len(self._shapefile) > 0

    @staticmethod
    def build(xml_element):
        shapefile_layer_source = ShapefileLayerSource()
        shapefile_layer_source._directory = Tools.getAttributeFromElement(xml_element, "directory")
        shapefile_layer_source._shapefile = Tools.getAttributeFromElement(xml_element, "shapefile")
        shapefile_layer_source._qml = Tools.getAttributeFromElement(xml_element, "qml")
        return shapefile_layer_source

    @staticmethod
    def load_layer(relative_path, title="", qml=""):
        shp_path = Tools.findData(relative_path)

        if shp_path == "":
            Tools.alert("unable to find " + relative_path)
            return None

        layer = QgsVectorLayer(shp_path, baseName=title, providerLib="ogr")

        if not layer.isValid():
            Tools.alert("bad data at " + shp_path)
            return None

        if qml != "":
            qml_location = path.join(path.dirname(shp_path), qml)
            if path.isfile(qml_location):
                layer.loadNamedStyle(qml_location)
            else:
                Tools.alert("unable to find " + qml_location)

        return layer