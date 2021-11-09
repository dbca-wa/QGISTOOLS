from qgis.core import QgsRasterLayer

from ...data.requests.layersource import LayerSource
from ...tools import Tools


class ImageryLayerSource(LayerSource):

    DEFAULT_DESCRIPTION = "ImageryLayerSource"
    XML_NODE_NAME = "load_imagery"

    def __init__(self):
        super(self.__class__, self).__init__()
        self._image_file = ""

    def _load_from_source(self):
        layer = ImageryLayerSource.load_layer(self._image_file)
        if layer is None:
            Tools.clear_status_bar()
        return layer

    def _is_valid(self):
        return super(self.__class__, self)._is_valid() \
               and len(self._image_file) > 0

    @staticmethod
    def build(xml_element):
        imagery_layer_source = ImageryLayerSource()
        imagery_layer_source._image_file = Tools.getAttributeFromElement(xml_element, "imagefile")
        return imagery_layer_source

    @staticmethod
    def load_layer(relative_path, title=""):
        imagery_path = Tools.findData(relative_path)

        if imagery_path == "":
            Tools.alert("unable to find " + relative_path)
            return None

        layer = QgsRasterLayer(imagery_path, baseName=title)

        if not layer.isValid():
            Tools.alert("bad data at " + imagery_path)
            return None

        return layer
