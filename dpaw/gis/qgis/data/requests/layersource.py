from qgis.core import QgsMapLayerRegistry
from PyQt4.QtGui import *
import xml.etree.ElementTree as ET

from ...tools import Tools


class LayerSource(object):

    DEFAULT_DESCRIPTION = "Unknown Source"

    KNOWN_NODE_TYPES = {
        "load_filegdb",
        "load_imagery",
        "load_imagery_tiles",
        "load_shapefile",
        "load_shapefile_tiles",
        "load_wms_layer",
        "multi_layer",
        "load_agol_feature_server_layer"
    }

    def __init__(self):
        self._description = ""
        self._caveat = ""
        self._title_raw = ""

    @property
    def description(self):
        desc = self._description if len(self._description) > 0 else self.DEFAULT_DESCRIPTION
        return Tools.substituteRegion(desc, " ")

    @property
    def _title(self):
        return Tools.substituteRegion(self._title_raw, " ")

    def _is_valid(self):
        return len(self._title_raw) > 0

    def _load_from_source(self):
        return None

    def load(self):
        if self._caveat:
            result = self.show_caveat()
            if result != QMessageBox.Ok:
                return False

        layer = self._load_from_source()

        if layer is None:
            return False

        layer.setName(self._title)
        QgsMapLayerRegistry.instance().addMapLayer(layer)
        return True

    def show_caveat(self):
        message_box = QMessageBox()
        message_box.setText(self._caveat)
        message_box.setWindowTitle("Caveat")
        message_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        message_box.setDefaultButton(QMessageBox.Ok)
        if "?" in self._caveat:
            message_box.setIcon(QMessageBox.Question)
        if "!" in self._caveat:
            message_box.setIcon(QMessageBox.Warning)
        return message_box.exec_()

    def _register_for_logging(self):
        pass

    @staticmethod
    def build(xml_element):
        # import layer sources here to resolve circular dependencies
        from .filegdblayersource import FileGdbLayerSource
        from .imagerylayersource import ImageryLayerSource
        from .imagerytileslayersource import ImageryTilesLayerSource
        from .multiplelayersource import MultipleLayerSource
        from .shapefilelayersource import ShapefileLayerSource
        from .shapefiletileslayersource import ShapefileTilesLayerSource
        from .wmslayersource import WmsLayerSource
        from .agolfeatureserverlayersource import AgolFeatureServerLayerSource

        assert isinstance(xml_element, ET.Element), "Bad Parameter"

        caveat = Tools.getAttributeFromElement(xml_element, "caveat")
        description = Tools.getAttributeFromElement(xml_element, "description")
        title = Tools.getAttributeFromElement(xml_element, "title")

        tag = xml_element.tag.lower()
        if tag[0] == "q":
            tag = tag[1:]
        elif tag[0] == "a":
            return None

        if tag == FileGdbLayerSource.XML_NODE_NAME:
            layer_source = FileGdbLayerSource.build(xml_element)
        elif tag == ImageryLayerSource.XML_NODE_NAME:
            layer_source = ImageryLayerSource.build(xml_element)
        elif tag == ImageryTilesLayerSource.XML_NODE_NAME:
            layer_source = ImageryTilesLayerSource.build(xml_element)
        elif tag == MultipleLayerSource.XML_NODE_NAME:
            layer_source = MultipleLayerSource.build(xml_element)
        elif tag == ShapefileLayerSource.XML_NODE_NAME:
            layer_source = ShapefileLayerSource.build(xml_element)
        elif tag == ShapefileTilesLayerSource.XML_NODE_NAME:
            layer_source = ShapefileTilesLayerSource.build(xml_element)
        elif tag == WmsLayerSource.XML_NODE_NAME:
            layer_source = WmsLayerSource.build(xml_element)
        elif tag == AgolFeatureServerLayerSource.XML_NODE_NAME:
            layer_source = AgolFeatureServerLayerSource.build(xml_element)
        else:
            return None

        layer_source._caveat = caveat
        layer_source._description = description
        layer_source._title_raw = title

        if not layer_source._is_valid():
            return None
        layer_source._register_for_logging()
        return layer_source
