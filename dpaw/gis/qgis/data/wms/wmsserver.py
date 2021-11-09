from datetime import datetime
from ...tools import Tools


class WMSLayerSummary():

    def __init__(self, title="", name=""):
        self.name = name
        self.title = title
        self.layers = []
        self.referenceSystems = []

    @staticmethod
    def fromElement(grandparent, element):
        wmsls = WMSLayerSummary()
        for child in element:
            tag = child.tag.lower()
            #if tag == "name":
            if tag.endswith("name"):
                wmsls.name = child.text
            #elif tag == "title":
            elif tag.endswith("title"):
                wmsls.title = child.text
            #elif tag == "srs":
            elif tag.endswith("srs") or tag.endswith("crs"):
                wmsls.referenceSystems.append(child.text)
            #elif tag == "layer":
            elif tag.endswith("layer"):
                wmsls.layers.append(WMSLayerSummary.fromElement(element, child))
        if wmsls.referenceSystems == []:    # This code was written to accommodate SPOT mosaic but may be more widely applicable
            for sibling in grandparent:
                tag = sibling.tag.lower()
                if tag.endswith("srs") or tag.endswith("crs"):
                    wmsls.referenceSystems.append(sibling.text)
        return wmsls


class WMSServerSummary(WMSLayerSummary):

    def __init__(self, title="", name=""):
        WMSLayerSummary.__init__(self, title, name)
        self.timestamp = datetime.now(None)

    @staticmethod
    def fromElement(element):
        wmsss = WMSServerSummary()
        for child in element:
            tag = child.tag.lower()
            #if tag == "name":
            if tag.endswith("name"):
                wmsss.name = child.text
            #elif tag == "title":
            elif tag.endswith("title"):
                wmsss.title = child.text
            #elif tag == "layer":
            elif tag.endswith("layer"):
                wmsss.layers.append(WMSLayerSummary.fromElement(element, child))    # NB this element becomes 'grandparent' variable, and child becomes 'element' variable
        return wmsss
