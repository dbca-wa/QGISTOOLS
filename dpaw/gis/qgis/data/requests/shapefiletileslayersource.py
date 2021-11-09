from os import path

from qgis.core import QgsMapLayerRegistry
from qgis.core import QgsProject
from qgis.utils import iface

from ...data.requests.layersource import LayerSource
from ...data.requests.shapefilelayersource import ShapefileLayerSource
from ...tools import Tools


class ShapefileTilesLayerSource(LayerSource):

    DEFAULT_DESCRIPTION = "ShapefileTilesLayerSource"
    XML_NODE_NAME = "load_shapefile_tiles"

    def __init__(self):
        super(self.__class__, self).__init__()
        self._index_file = ""
        self._field_index = -1

    def _is_valid(self):
        return super(self.__class__, self)._is_valid() \
               and len(self._index_file) > 0 \
               and self._field_index >= 0

    def _load_from_source(self):
        ShapefileTilesLayerSource.load_layer(self._index_file, self._field_index, self._title)
        # skip downstream processing
        return None

    @staticmethod
    def build(xml_element):
        shapefile_layer_source = ShapefileTilesLayerSource()
        shapefile_layer_source._index_file = Tools.getAttributeFromElement(xml_element, "indexfile")
        shapefile_layer_source._field_index = int(Tools.getAttributeFromElement(xml_element, "field_index"))
        return shapefile_layer_source

    @staticmethod
    def load_layer(relative_path_index, field_index, title):
        sb = iface.mainWindow().statusBar()

        index = ShapefileLayerSource.load_layer(relative_path_index)
        if index is None:
            Tools.clear_status_bar()
            return None

        extent = Tools.get_visible_extents(index.crs())
        if extent is None:
            Tools.clear_status_bar()
            return None

        index.selectByRect(extent)
        visible_count = index.selectedFeatureCount()

        if visible_count == 0:
            Tools.alert("No dataset tiles are located in the area you are looking at.", "No Dataset Tiles")
            Tools.clear_status_bar()
            return None

        elif visible_count > 9:
            msg = "There are {0} individual dataset tiles.\nLoading these could take quite a long time.\n\nWould you like to continue loading the data?".format(visible_count)
            confirm_load = Tools.showYesNoDialog(msg, "Numerous Dataset Tiles")
            if not confirm_load:
                Tools.clear_status_bar()
                return None

        group = QgsProject.instance().layerTreeRoot().findGroup(title)
        if group is None:
            group = QgsProject.instance().layerTreeRoot().addGroup(title)

        child_names = [l.name() for l in group.findLayers()]

        shapefile_layers = []

        for feature in index.selectedFeatures():
            shapefile_path = feature.attributes()[field_index - 2]
            shapefile_name = path.splitext(path.basename(shapefile_path))[0]
            if shapefile_name in child_names:
                continue

            shapefile_layer = ShapefileLayerSource.load_layer(shapefile_path, shapefile_name)
            if shapefile_layer is not None:
                shapefile_layers.append(shapefile_layer)

        QgsMapLayerRegistry.instance().addMapLayers(shapefile_layers, addToLegend=False)
        for shapefile_layer in shapefile_layers:
            group.addLayer(shapefile_layer)

        sb.showMessage("Loading Complete; Rendering...", 1000)
        # skip downstream processing
        return None
