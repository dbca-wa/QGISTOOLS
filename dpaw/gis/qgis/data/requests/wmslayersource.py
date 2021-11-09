from collections import namedtuple
from xml.etree import ElementTree

from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QTextDocument
from PyQt4.QtNetwork import QNetworkRequest

from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsMapLayerRegistry
from qgis.core import QgsNetworkAccessManager
from qgis.core import QgsRasterLayer
from qgis.utils import iface

from ...data.requests.layersource import LayerSource
from ...tools import Tools


class WmsLayerSource(LayerSource):
    WmsRequest = namedtuple('WmsRequest', [
        'base_url',
        'layer_name',
        'title',
        'layer_group',
        'user',
        'password',
    ])

    DEFAULT_DESCRIPTION = "WmsLayerSource"
    XML_NODE_NAME = "load_wms_layer"

    _pending_wms_requests = []
    _capabilities_by_url = {}
    _pending_network_requests_by_url = {}
    _process_network_replies_active = False

    def __init__(self):
        super(self.__class__, self).__init__()
        self._layer_group = ""
        self._layer_name = ""
        self._password = ""
        self._url = ""
        self._user = ""

    def _load_from_source(self):
        WmsLayerSource.load_layer(self._url, self._layer_name, self._title, self._layer_group, self._user, self._password)

        # skip downstream processing
        return None

    def _is_valid(self):
        return super(self.__class__, self)._is_valid() \
               and len(self._layer_group) > 0 \
               and len(self._url) > 0 \
               and len(self._layer_name) > 0

    @staticmethod
    def build(xml_element):
        wms_layer_source = WmsLayerSource()
        wms_layer_source._layer_group = Tools.getAttributeFromElement(xml_element, "layergroup")
        wms_layer_source._layer_name = Tools.getAttributeFromElement(xml_element, "layername")
        wms_layer_source._password = Tools.getAttributeFromElement(xml_element, "password")
        wms_layer_source._url = Tools.getAttributeFromElement(xml_element, "url")
        wms_layer_source._user = Tools.getAttributeFromElement(xml_element, "user")

        if "?" not in wms_layer_source._url:
            # if url is missing the question mark separator we add it now
            wms_layer_source._url += "?"

        return wms_layer_source

    @staticmethod
    def load_layer(url, layer_name, title, layer_group, user="", password=""):
        # In order to load a WMS layer into QGIS we first have to query the capabilities of the server to ensure we are
        # using supported parameters.  This GetCapabilities document must be requested asynchronously which add some
        # complexity as their may be additional calls to this method before the network request is complete.

        if iface.mapCanvas().layerCount() == 0:
            Tools.alert("Unable to determine the Map Extents.\n" +
                        "Please load a base layer in order to establish a " +
                        "context (e.g. {} regions, WA Coast etc.)".format(Tools.get_dept_acronym()),
                        "No data in area")
            return None

        wms_request = WmsLayerSource.WmsRequest(url, layer_name, title, layer_group, user, password)

        if url in WmsLayerSource._capabilities_by_url:
            # We already have the WMS capabilities for this server so we can load the layer directly
            WmsLayerSource._process_wms_request(wms_request)
            return None

        # We don't have the WMS capabilities so we will add the request to the list
        WmsLayerSource._pending_wms_requests.append(wms_request)

        if url in WmsLayerSource._pending_network_requests_by_url:
            # We already have a network request for the servers capabilities so are done for now.
            # The event handler for the existing network request will find our wms request later.
            return None

        # We don't have a network request so we build one and add it to our collection
        getcapabilities_url = WmsLayerSource._build_getcapabilities_url(url, user, password)
        request = QNetworkRequest(getcapabilities_url)
        reply = QgsNetworkAccessManager.instance().createRequest(QgsNetworkAccessManager.GetOperation, request)
        WmsLayerSource._pending_network_requests_by_url[url] = reply

        # this event handler will process our network replies and wms request collections in a batch manner
        reply.connect(reply, SIGNAL("finished()"), WmsLayerSource._process_network_replies)

        return None

    @staticmethod
    def _process_network_replies():
        if WmsLayerSource._process_network_replies_active:
            # This method will be called once per network request, however having several parallel executions can lead
            # to race conditions.  To resolve this I am using this guard clause to block any duplicates and have the
            # core of the method structured as a repeating loop to ensure the same steps are repeated in the correct
            # order until all completed network requests are processed.
            return

        WmsLayerSource._process_network_replies_active = True

        network_requests_are_unstable = True
        while network_requests_are_unstable:
            network_requests_are_unstable = False
            network_requests_to_process = []

            # check replies
            for url, reply in WmsLayerSource._pending_network_requests_by_url.iteritems():
                if reply.isFinished():
                    network_requests_to_process.append((url, reply))

            if len(network_requests_to_process) > 0:
                network_requests_are_unstable = True

                # process finished replies
                for url, reply in network_requests_to_process:
                    WmsLayerSource._process_network_reply(url, reply)
                    del WmsLayerSource._pending_network_requests_by_url[url]

                # process all wms requests
                WmsLayerSource._process_wms_requests()

        WmsLayerSource._process_network_replies_active = False

    @staticmethod
    def _process_network_reply(url, reply):
        capabilities_text = reply.readAll()
        try:
            root = ElementTree.fromstring(capabilities_text)
            WmsLayerSource._capabilities_by_url[url] = capabilities_text
        except:
            doc = QTextDocument()
            doc.setHtml(str(capabilities_text))
            snippet = Tools.truncate_string(doc.toPlainText(), 1000)
            message_text = ("Invalid network response:\n\n" + snippet + "\n\n"
                            + "---\n\n"
                            + "Possible causes include:\n\n"
                            + "1.  Your computer may not be connected to the {0} network - ensure your blue network cable is plugged into your computer. If yes then call {0} Helpdesk 9334 0334\n\n"
                            + "2.  You may not be connected to the internet - contact {0} Helpdesk 9334 0334\n\n"
                            + "3.  The WMS server (" + url + ") may be offline.  Contact the GIS Application Section.\n\n"
                            + "4.  QGIS network settings may be mis-configured. Contact the GIS Applications Section.\n").format(Tools.get_dept_acronym())
            Tools.alert(message_text, "WMS Error")
            for wms_request in WmsLayerSource._pending_wms_requests[:]:
                if wms_request.base_url == url:
                    WmsLayerSource._pending_wms_requests.remove(wms_request)

    @staticmethod
    def _process_wms_requests():
        for wms_request in WmsLayerSource._pending_wms_requests[:]:
            if wms_request.base_url in WmsLayerSource._capabilities_by_url:
                WmsLayerSource._pending_wms_requests.remove(wms_request)
                WmsLayerSource._process_wms_request(wms_request)

    @staticmethod
    def _process_wms_request(wms_request):
        root = ElementTree.fromstring(WmsLayerSource._capabilities_by_url[wms_request.base_url])

        if WmsLayerSource._clean_tag(root.tag) not in ["wmt_ms_capabilities", "wms_capabilities"]:
            Tools.debug("bad root: " + root.tag)
            return

        capability = [child for child in root if WmsLayerSource._clean_tag(child.tag) == "capability"][0]

        request = [child for child in capability if WmsLayerSource._clean_tag(child.tag) == "request"][0]
        getmap = [child for child in request if WmsLayerSource._clean_tag(child.tag) == "getmap"][0]
        format_set = set([child.text for child in getmap if WmsLayerSource._clean_tag(child.tag) == "format"])

        layer_root = [child for child in capability if WmsLayerSource._clean_tag(child.tag) == "layer"][0]
        crs_set = WmsLayerSource._find_layer_crs_capabilities(wms_request.layer_name, layer_root, set())
        if crs_set is None:
            Tools.alert("Layer not found on server.\n\nLayer: {}\nServer: {}".format(wms_request.layer_name, wms_request.base_url), "Error")
            return

        crs_code = WmsLayerSource._select_crs_from_set(crs_set)
        format_code = WmsLayerSource._select_format_from_set(format_set)

        connection_string = "url={}&crs={}&format={}&styles=&transparent=true&layers={}".format(wms_request.base_url, crs_code, format_code, wms_request.layer_name)
        if wms_request.user != "" and wms_request.password != "":
            connection_string += "&username={}&password={}".format(wms_request.user, wms_request.password)

        wms_layer = QgsRasterLayer(connection_string, wms_request.title, 'wms')

        if not wms_layer.isValid():
            Tools.debug("bad layer")
            return

        Tools.cddpTechnique = "menu"
        QgsMapLayerRegistry.instance().addMapLayer(wms_layer)
        if len(WmsLayerSource._pending_wms_requests) == 0:
            iface.mainWindow().statusBar().showMessage("Loading Complete", 1000)

    @staticmethod
    def _build_getcapabilities_url(base_url, user="", password=""):
        if len(base_url) - 1 > base_url.index("?"):
            # if url already contains a partial query string it must end with the key-value pair delimiter
            if not base_url.endswith("&"):
                base_url += "&"

        base_url += "REQUEST=GetCapabilities&SERVICE=WMS"

        url = QUrl(base_url)

        if user != "" and password != "":
            url.setUserName(user)
            url.setPassword(password)

        return url

    @staticmethod
    def _find_layer_crs_capabilities(name, element, crs_set):
        crs_set |= set([child.text for child in element if WmsLayerSource._clean_tag(child.tag) in ["srs", "crs"]])

        if name in [child.text for child in element if WmsLayerSource._clean_tag(child.tag) == "name"]:
            return crs_set

        for child_layer in [child for child in element if WmsLayerSource._clean_tag(child.tag) == "layer"]:
            result = WmsLayerSource._find_layer_crs_capabilities(name, child_layer, crs_set)
            if result is not None:
                return result

        return None

    @staticmethod
    def _clean_tag(text):
        # trim any leading namespace
        if "{" in text and text.index("{") == 0 and "}" in text:
            text = text[text.index("}") + 1:]
        # flatten to lower case
        return text.lower()

    @staticmethod
    def _select_crs_from_set(crs_set):
        preferred_crs_list = [
            iface.mapCanvas().mapSettings().destinationCrs().authid(),
            "EPSG:4283",  # GDA94
        ]

        # try to use preferred CRSs
        for crs_code in preferred_crs_list:
            if crs_code in crs_set:
                return crs_code

        # fallback to any recognised CRS
        for crs_code in crs_set:
            test_crs = QgsCoordinateReferenceSystem()
            test_crs.createFromString(crs_code)
            if test_crs.isValid():
                return crs_code

        Tools.debug("no recognised CRS")
        return None

    @staticmethod
    def _select_format_from_set(format_set):
        preferred_format_list = [
            'image/png',
            'image/png8',
            'image/gif',
            'image/jpeg',
            'image/tiff',
            'image/svg',
        ]

        # try to use preferred format
        for format_code in preferred_format_list:
            if format_code in format_set:
                return format_code

        # fallback to any available format
        for item in format_set:
            return item
