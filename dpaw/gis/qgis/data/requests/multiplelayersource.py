from qgis.utils import iface

from ...data.requests.layersource import LayerSource
from ...tools import Tools


class MultipleLayerSource(LayerSource):

    DEFAULT_DESCRIPTION = "MultipleLayerSource"
    XML_NODE_NAME = "multi_layer"

    def __init__(self):
        super(self.__class__, self).__init__()
        self._layer_sources = []

    def _load_from_source(self):
        MultipleLayerSource.load_layer(self._layer_sources)
        # skip downstream processing
        return None

    def _is_valid(self):
        return super(self.__class__, self)._is_valid() \
               and len(self._layer_sources) > 0

    @staticmethod
    def build(xml_element):
        multiple_layer_source = MultipleLayerSource()

        for child_element in xml_element:
            child_source = LayerSource.build(child_element)

            if child_source is not None:
                multiple_layer_source._layer_sources.append(child_source)

        return multiple_layer_source

    @staticmethod
    def load_layer(layer_source_list):
        failed = False
        for layer_source in layer_source_list:
            success = layer_source.load()
            if not success:
                failed = True

        if failed:
            Tools.clear_status_bar()
        else:
            iface.mainWindow().statusBar().showMessage("Loading Complete; Rendering...", 1000)
