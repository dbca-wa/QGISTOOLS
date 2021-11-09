from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import os
import sys
import tempfile

from base64 import b64decode
from tempfile import mkdtemp
from os import path, startfile

import qgis.utils
from osgeo import ogr
from qgis.core import *
from ...tools import Tools

from lxml import etree as ET

class MetadataTools:

    LegacyMetadataProfile ="DPaW"
    NewMetadataProfile = "DBCA"

    @staticmethod
    def getExistingMetadataFileLocation(layer):
        sourceType = Tools.getLayerSourceType(layer)

        if sourceType == "shapefile":
            return MetadataTools.getExistingMetadataFileLocationForShapefile(layer)

        if sourceType == "filegdb":
            return MetadataTools.getExistingMetadataFileLocationForFileGDB(layer)

        return None

    @staticmethod
    def getExistingMetadataFileLocationForShapefile(layer):
        layerSource = layer.source()

        xmlLocation = layerSource + ".xml"
        if not os.path.isfile(xmlLocation):
            if layerSource[-4] == ".":
                xmlLocation = layerSource[:-4] + ".xml"
                if not os.path.isfile(xmlLocation):
                    return None
        return xmlLocation

    @staticmethod
    def getExistingMetadataFileLocationForFileGDB(layer):
        metadata_string = MetadataTools.getMetadataStringForFileGDB(layer)
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.xml')
        temp.write(metadata_string)
        temp.flush()
        return temp.name


# ############################################################################
    @staticmethod
    def openMetadataFile(source=None):
        if source is None:
            source = MetadataTools.getExistingMetadataFileLocation(Tools.iface.activeLayer())
        elif isinstance(source, QgsMapLayer):
            source = MetadataTools.getExistingMetadataFileLocation(source)

        if source is None:
            Tools.alert("Unable to locate the metadata file.", "Metadata Error")
            return None
        try:
                openFile = open(source, "r+")   # r+ = read-write
                return openFile
        except:
            Tools.alert("Unable to open metadata file for editing.\n" +
                        "Please check your write privileges for location:\n" +
                        source, "Metadata Error")
            return None

#############################################################################
    @staticmethod
    def canEdit(layer):
        if layer is None:
            return False
        canCreate, canView, canEdit = MetadataTools.getMetadataActions(layer)
        return canEdit

    @staticmethod
    def canView(layer):
        if layer is None:
            return False
        canCreate, canView, canEdit = MetadataTools.getMetadataActions(layer)
        return canView

    @staticmethod
    def canCreate(layer):
        if layer is None:
            return False
        canCreate, canView, canEdit = MetadataTools.getMetadataActions(layer)
        return canCreate

    @staticmethod
    def getMetadataActions(layer=None):
        sourceType = Tools.getLayerSourceType(layer)
        if sourceType == "shapefile":
            return MetadataTools.getMetadataActionsForShapefile(layer)
        elif sourceType == "filegdb":
            return MetadataTools.getMetadataActionsForFileGDB(layer)
        elif sourceType == "none":
            return False, False, False
        elif sourceType == "other":
            return False, False, False
        else:
            Tools.debug("unknown layer type")

    @staticmethod
    def getMetadataActionsForShapefile(layer=None):
        canEdit = False
        canView = False
        canCreate = False

        layerSource = layer.source()
        if layerSource.rsplit(".", 1)[-1].lower() == "shp":
            metadataLocation = MetadataTools.getExistingMetadataFileLocation(layer)
            if metadataLocation is not None:
                canView = True
                try:
                    # check for write access
                    f = open(metadataLocation, "r+")
                    f.close()
                    canEdit = True
                except:
                    canEdit = False
            else:
                try:
                    # check for write access
                    metadataLocation = layerSource + ".xml"
                    f = open(metadataLocation, "w+")
                    f.close()
                    os.remove(metadataLocation)
                    canCreate = True
                except:
                    canCreate = False

        return canCreate, canView, canEdit


    @staticmethod
    def getMetadataActionsForFileGDB(layer=None):
        canEdit = False
        canView = False
        canCreate = False

        metadata_string = MetadataTools.getMetadataStringForFileGDB(layer)
        canView = len(metadata_string) > 0

        return canCreate, canView, canEdit

 ############################################################################
    @staticmethod
    def treeToString(tree):
        #from lxml import etree as ET
        return ET.tostring(tree)

 ############################################################################
    @staticmethod
    def getMetadataStringForFileGDB(layer):
        layerSource = layer.source()
        layer_name = MetadataTools.getLayerNameForFileGDBSource(layerSource)
        fgdb_path = layerSource.split("|")[0]

        if layer_name is not None:
            driver = ogr.GetDriverByName("FileGDB")
            if driver is None:
                driver = ogr.GetDriverByName("OpenFileGDB")
            data_source = driver.Open(fgdb_path)
            metadata_layer = data_source.ExecuteSQL("GetLayerMetadata {}".format(layer_name))
            return metadata_layer.GetFeature(0).GetFieldAsString(0)


    @staticmethod
    def getLayerNameForFileGDBSource(layerSource):
        from osgeo import ogr
        driver = ogr.GetDriverByName("FileGDB")
        if driver is None:
            driver = ogr.GetDriverByName("OpenFileGDB")

        if '|' in layerSource:
            fgdb_path, layer_specifier = layerSource.split('|')
            specifier_type, specifier_value = layer_specifier.split('=')
            if specifier_type == 'layername':
                layer_name = specifier_value
            elif specifier_type == 'layerid':
                data_source = driver.Open(fgdb_path)
                layer_name = data_source.GetLayerByIndex(int(specifier_value)).GetName()
        else:
            # no layer specifier, must be single layer database
            from osgeo import ogr
            driver = ogr.GetDriverByName("FileGDB")  # or "OpenFileGDB"
            if driver is None:
                driver = ogr.GetDriverByName("OpenFileGDB")
            data_source = driver.Open(layerSource)
            layer_name = data_source.GetLayer().GetName()

        return layer_name

#############################################################################
    @staticmethod
    def getMetadataAsHtml(xslLocation, xmlLocation):
        #from lxml import etree as ET

        xmltree = MetadataTools.getMetadataAsTree(xmlLocation)
        if xmltree is None:
            return

        try:
            xsltree = ET.parse(xslLocation)
            transform = ET.XSLT(xsltree)
            result = transform(xmltree)
            txt = str(result)
            txt = txt.replace("\n", "")
            return txt
        except:
            Tools.alert("A problem has been encountered parsing:\n" +
                        xslLocation + "." + str(sys.exc_info()[0]), "Style Sheet Error")
            return

# ############################################################################
    @staticmethod
    def getMetadataAsTree(param):
        #from lxml import etree as ET
        if param is None:
            Tools.debug("getMetadataAsTree attrib is None!")
        # handle param as file
        if type(param) is file:
            try:
                xmltree = ET.fromstring(param.read())
                return xmltree
            except:
                Tools.alert("A problem has been encountered parsing:\n" +
                            param.name + ".", "Metadata Error")
                return None
        # handle param as None
        if isinstance(param, QgsMapLayer):
            param = MetadataTools.getExistingMetadataFileLocation(param)
        if param is None:
            Tools.alert("Unable to locate metadata for current layer.",
                        "Metadata Error")
            return
        # handle param as string
        try:
            xmltree = ET.parse(str(param))
            return xmltree
        except:
            Tools.alert("A problem has been encountered parsing:\n" +
                        param + ".", "Metadata Error")
            return None

    @staticmethod
    def getEmbeddedFileNames(tree):
        return [a.get("OriginalFileName") for a in tree.findall("/Binary/Enclosure/Data")]

    @staticmethod
    def getEmbeddedDataByFileName(tree, filename):
        element = tree.find("/Binary/Enclosure/Data[@OriginalFileName='{0}']".format(filename))
        return b64decode(element.text)

    @staticmethod
    def writeEmbeddedFileToTempLocation(tree, filename):
        filepath = path.join(mkdtemp(), filename)
        data = MetadataTools.getEmbeddedDataByFileName(tree, filename)
        with open(filepath, "wb") as output:
            output.write(data)
        return filepath