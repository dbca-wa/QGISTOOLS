from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *
from ..tools import *
from ..data.metadata.metadatatools import MetadataTools
from datetime import *
import os.path
import shutil
import qgis.utils
from ..data.crs.crshelper import CRSHelper
from .selectcrsdialog import SelectCRSDialog

import sys

from lxml import etree as ET

class MetadataEditorDialog(QDialog):
    CREATE = 0
    EDIT = 1
    UPDATE = 2

    def __init__(self, mode, layer):
        assert(mode is not None), "MetadataEditorDialog mode is None"
        assert(layer is not None), "MetadataEditorDialog layer is None"
        assert(isinstance(layer, QgsMapLayer)), "MetadataEditorDialog layer is not QgsMapLayer"
        QgsMessageLog.logMessage("MetadataEditorDialog init\nMode={}\nLayer={}".format(mode, layer))

        QDialog.__init__(self, Tools.QGISApp)
        # QDialog.closeEvent = self.closeEvent

        self.layer = layer
        self.mode = mode

        if mode == MetadataEditorDialog.CREATE:
            if MetadataTools.getExistingMetadataFileLocation(layer) is not None:
                Tools.debug("Metadata already exists.", "Metadata Error")
            # if layer is None:
            #    return None
            layerSource = layer.source()
            xmlTargetLocation = layerSource + ".xml"
            try:
                xmlDefaultLocation = os.path.join(Tools.getPluginPath(), "resources\\metadata\default.xml")
                shutil.copyfile(xmlDefaultLocation, xmlTargetLocation)
            except:
                if not os.path.isfile(xmlLocation):
                    Tools.debug("Error creating metadata file.\n" +
                                "This QGIS Tools installation is missing " +
                                xmlDefaultLocation, "Metadata Error")
                else:
                    Tools.debug("Error creating metadata file.\n" +
                                "Please check your write access to have " +
                                xmlTargetLocation, "Metadata Error")
                return

        # open file in edit mode, abort on failure
        self.openFile = MetadataTools.openMetadataFile(layer)
        if self.openFile is None:
            return

        self.setupDialog()
        self.loadMetadataFromXml()
        self.loadMetadataFromLayer()

        if mode != MetadataEditorDialog.UPDATE:
            self.loadContactsFromFile()
            self.exec_()
        else:
            self.saveMetadata()


##############################################################################
    def setupDialog(self):
        QgsMessageLog.logMessage("MetadataEditorDialog setupDialog")
        self.resize(800, self.height())
        self.setWindowTitle("Edit Metadata")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint |
                            Qt.WindowTitleHint | Qt.WindowSystemMenuHint |
                            Qt.WindowMaximizeButtonHint)  # | Qt.WindowMinMaxButtonHint)

        self.setSizeGripEnabled(True)
        master = QVBoxLayout(self)
        self.setLayout(master)
        mainLayout = QSplitter()
        master.addWidget(mainLayout)

# LeftColoumn
        leftColumn = QVBoxLayout()
        leftWidget = QWidget()
        leftWidget.setLayout(leftColumn)
        mainLayout.addWidget(leftWidget)

# TopLeftForm
        topLeftForm = QFormLayout()
        leftColumn.addLayout(topLeftForm)
        self.titleLineEdit = QLineEdit()
        topLeftForm.addRow("Title", self.titleLineEdit)
        self.custodianLineEdit = QLineEdit()
        topLeftForm.addRow("Custodian", self.custodianLineEdit)
        self.endingDateLineEdit = QLineEdit()
        topLeftForm.addRow("Ending Date", self.endingDateLineEdit)
        self.startingDateLineEdit = QLineEdit()
        topLeftForm.addRow("Starting Date", self.startingDateLineEdit)

# CoordinateSystemBox
        coordinateSystemGroupBox = QGroupBox("Coordinate System", self)
        leftColumn.addWidget(coordinateSystemGroupBox)
        coordinateSystemGroupBox.setLayout(QVBoxLayout())

# CoordinateSystemForm
        coordinateSystemForm = QFormLayout()
        coordinateSystemGroupBox.layout().addLayout(coordinateSystemForm)

        self.datumLineEdit = QLineEdit()
        coordinateSystemForm.addRow("Datum", self.datumLineEdit)
        self.datumLineEdit.setReadOnly(True)
        self.projectionLineEdit = QLineEdit()
        coordinateSystemForm.addRow("Projection", self.projectionLineEdit)
        self.projectionLineEdit.setReadOnly(True)

        self.defineCoordinateSystemButton = QPushButton("Define")
        coordinateSystemGroupBox.layout().addWidget(self.defineCoordinateSystemButton)
        self.defineCoordinateSystemButton.clicked.connect(self.defineCoordinateSystemButtonHandler)

# abstract
        leftColumn.addWidget(QLabel("Abstract"))
        self.abstractTextEdit = QTextEdit()
        leftColumn.addWidget(self.abstractTextEdit)

# buttons
        buttonsLayout = QHBoxLayout()
        leftColumn.addLayout(buttonsLayout)
        self.okButton = QPushButton("OK")
        buttonsLayout.addWidget(self.okButton)
        self.okButton.clicked.connect(self.okButtonHandler)
        self.cancelButton = QPushButton("Cancel")
        buttonsLayout.addWidget(self.cancelButton)
        self.cancelButton.clicked.connect(self.cancelButtonHandler)

# RightColumn
        rightTabSet = QTabWidget(self)
        self.tabset = rightTabSet
        mainLayout.addWidget(rightTabSet)
        rightTabSet.setUsesScrollButtons(False)

# contact tab
# TODO "T:\757-Information Management Branch\GIS Group\METADATA\ArcGIS_Metadata\Metadata_Contacts.txt"
        contactFormWidget = QWidget()
        rightTabSet.addTab(contactFormWidget, "Contact")
        contactFormWidget.setLayout(QFormLayout())

        self.contactOrganisationLineEdit = QLineEdit()
        contactFormWidget.layout().addRow("Contact Organisation", self.contactOrganisationLineEdit)

        self.contactPositionLineEdit = QLineEdit()
        contactFormWidget.layout().addRow("Contact Position", self.contactPositionLineEdit)

        self.contactMailAddressLineEdit = QLineEdit()
        contactFormWidget.layout().addRow("Mail Address", self.contactMailAddressLineEdit)

        self.contactSuburbLineEdit = QLineEdit()
        contactFormWidget.layout().addRow("Suburb/Locality", self.contactSuburbLineEdit)

        self.contactCountryStateLineEdit = QLineEdit()
        contactFormWidget.layout().addRow("Country/State", self.contactCountryStateLineEdit)

        self.contactPostcodeLineEdit = QLineEdit()
        contactFormWidget.layout().addRow("Postcode", self.contactPostcodeLineEdit)

        self.contactTelephoneLineEdit = QLineEdit()
        contactFormWidget.layout().addRow("Telephone", self.contactTelephoneLineEdit)

        self.contactFaxLineEdit = QLineEdit()
        contactFormWidget.layout().addRow("Fax", self.contactFaxLineEdit)

        self.contactEmailLineEdit = QLineEdit()
        contactFormWidget.layout().addRow("Email", self.contactEmailLineEdit)

        contactFormWidget.layout().addRow(" ", QVBoxLayout())

        contactPresetsBox = QGroupBox("Contact Presets")
        contactFormWidget.layout().addRow(contactPresetsBox)
        contactPresetsBox.setLayout(QHBoxLayout())
        contactsPresetsComboBox = QComboBox()
        contactPresetsBox.layout().addWidget(contactsPresetsComboBox)
        contactsPresetsComboBox.addItem("")
        self.contactsPresetsComboBox = contactsPresetsComboBox
        contactsPresetsComboBox.currentIndexChanged.connect(self.contactsPresetsComboBoxHandler)

# access tab
        accessFormWidget = QWidget()
        rightTabSet.addTab(accessFormWidget, "Access")
        accessFormWidget.setLayout(QFormLayout())

        self.accessStoredDataFormatLineEdit = QLineEdit()
        accessFormWidget.layout().addRow("Stored Data Format", self.accessStoredDataFormatLineEdit)

        self.accessAccessConstraintsTextEdit = QTextEdit()
        accessFormWidget.layout().addRow("Access Constraints", self.accessAccessConstraintsTextEdit)

# quality tab
        qualityFormWidget = QWidget()
        rightTabSet.addTab(qualityFormWidget, "Quality")
        qualityFormWidget.setLayout(QFormLayout())

        self.qualityLineageTextEdit = QTextEdit()
        qualityFormWidget.layout().addRow("Lineage", self.qualityLineageTextEdit)

        self.qualityPositionalAccuracyTextEdit = QTextEdit()
        qualityFormWidget.layout().addRow("Positional Accuracy", self.qualityPositionalAccuracyTextEdit)

        self.qualityAttributeAccuracyTextEdit = QTextEdit()
        qualityFormWidget.layout().addRow("Attribute Accuracy", self.qualityAttributeAccuracyTextEdit)

        self.qualityLogicalConsistancyTextEdit = QTextEdit()
        qualityFormWidget.layout().addRow("Logical Consistancy", self.qualityLogicalConsistancyTextEdit)

        self.qualityCompletenessTextEdit = QTextEdit()
        qualityFormWidget.layout().addRow("Completeness", self.qualityCompletenessTextEdit)

# status tab
        statusFormWidget = QWidget()
        rightTabSet.addTab(statusFormWidget, "Status")
        statusFormWidget.setLayout(QFormLayout())

        self.statusProgressTextEdit = QTextEdit()
        statusFormWidget.layout().addRow("Progress", self.statusProgressTextEdit)

        self.statusMaintenanceUpdateTextEdit = QTextEdit()
        statusFormWidget.layout().addRow("Maintenance/Update", self.statusMaintenanceUpdateTextEdit)

# additional tab
        additionalFormWidget = QWidget()
        rightTabSet.addTab(additionalFormWidget, "Additional")
        additionalFormWidget.setLayout(QVBoxLayout())

        geographicExtentGroupBox = QGroupBox("Geographic Extent")
        additionalFormWidget.layout().addWidget(geographicExtentGroupBox)
        geographicExtentGroupBox.setLayout(QFormLayout())

        self.geographicExtentLeftLineEdit = QLineEdit()
        geographicExtentGroupBox.layout().addRow("Left", self.geographicExtentLeftLineEdit)
        self.geographicExtentLeftLineEdit.setReadOnly(True)

        self.geographicExtentRightLineEdit = QLineEdit()
        geographicExtentGroupBox.layout().addRow("Right", self.geographicExtentRightLineEdit)
        self.geographicExtentRightLineEdit.setReadOnly(True)

        self.geographicExtentTopLineEdit = QLineEdit()
        geographicExtentGroupBox.layout().addRow("Top", self.geographicExtentTopLineEdit)
        self.geographicExtentTopLineEdit.setReadOnly(True)

        self.geographicExtentBottomLineEdit = QLineEdit()
        geographicExtentGroupBox.layout().addRow("Bottom", self.geographicExtentBottomLineEdit)
        self.geographicExtentBottomLineEdit.setReadOnly(True)

        additionalMetadataForm = QFormLayout()
        additionalFormWidget.layout().addLayout(additionalMetadataForm)

        self.additionalMetadataDateLineEdit = QLineEdit()
        additionalMetadataForm.addRow("Metadata Date", self.additionalMetadataDateLineEdit)
        self.additionalMetadataDateLineEdit.setEnabled(False)

        self.additionalAdditionalMetadataTextEdit = QTextEdit()
        additionalMetadataForm.addRow("Additional Metadata", self.additionalAdditionalMetadataTextEdit)

# attributes tab
        attributesFormWidget = QWidget()
        rightTabSet.addTab(attributesFormWidget, "Attributes")
        attributesFormWidget.setLayout(QVBoxLayout())

        self.attributesTableWidget = QTableWidget()
        attributesFormWidget.layout().addWidget(self.attributesTableWidget)
        self.attributesTableWidget.insertColumn(0)
        self.attributesTableWidget.insertColumn(0)
        self.attributesTableWidget.setHorizontalHeaderLabels(["Attribute", "Description"])
        self.attributesTableWidget.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.attributesTableWidget.setVerticalScrollMode(QTableWidget.ScrollPerPixel)


##############################################################################
    def loadMetadataFromXml(self):
        QgsMessageLog.logMessage("MetadataEditorDialog loadMetadataFromXml")
        tree = MetadataTools.getMetadataAsTree(self.openFile)
        if tree is None:
            # close?
            return None
        self.tree = tree
# left side
        self.setFormTextValueByQuery(self.titleLineEdit, "idinfo/citation/citeinfo/title")
        self.setFormTextValueByQuery(self.custodianLineEdit, "idinfo/citation/citeinfo/origin")
        self.setFormTextValueByQuery(self.startingDateLineEdit, "idinfo/timeperd/begdate")
        self.setFormTextValueByQuery(self.endingDateLineEdit, "idinfo/timeperd/enddate")
        self.setFormTextValueByQuery(self.abstractTextEdit, "idinfo/descript/abstract")
# contact pane
        self.setFormTextValueByQuery(self.contactOrganisationLineEdit, "metainfo/metc/cntinfo/cntorgp/cntorg")
        self.setFormTextValueByQuery(self.contactPositionLineEdit, "metainfo/metc/cntinfo/cntorgp/cntper")
        self.setFormTextValueByQuery(self.contactMailAddressLineEdit, "metainfo/metc/cntinfo/cntaddr/addrtype")
        self.setFormTextValueByQuery(self.contactSuburbLineEdit, "metainfo/metc/cntinfo/cntaddr/city")
        self.setFormTextValueByQuery(self.contactCountryStateLineEdit, "metainfo/metc/cntinfo/cntaddr/state")
        self.setFormTextValueByQuery(self.contactPostcodeLineEdit, "metainfo/metc/cntinfo/cntaddr/postal")
        self.setFormTextValueByQuery(self.contactTelephoneLineEdit, "metainfo/metc/cntinfo/cntvoice")
        self.setFormTextValueByQuery(self.contactFaxLineEdit, "distinfo/distrib/cntinfo/cntfax")
        self.setFormTextValueByQuery(self.contactEmailLineEdit, "distinfo/distrib/cntinfo/cntemail")

# access pane
        self.setFormTextValueByQuery(self.accessStoredDataFormatLineEdit, "idinfo/citation/citeinfo/geoform")
        self.setFormTextValueByQuery(self.accessAccessConstraintsTextEdit, "idinfo/accconst")

# quality pane
        self.setFormTextValueByQuery(self.qualityLineageTextEdit, "dataqual/lineage")
        self.setFormTextValueByQuery(self.qualityPositionalAccuracyTextEdit, "dataqual/posacc")
        self.setFormTextValueByQuery(self.qualityAttributeAccuracyTextEdit, "dataqual/attracc")
        self.setFormTextValueByQuery(self.qualityLogicalConsistancyTextEdit, "dataqual/logic")
        self.setFormTextValueByQuery(self.qualityCompletenessTextEdit, "dataqual/complete")

# status pane
        self.setFormTextValueByQuery(self.statusProgressTextEdit, "idinfo/status/progress")
        self.setFormTextValueByQuery(self.statusMaintenanceUpdateTextEdit, "idinfo/status/update")

# additional pane
        self.setFormTextValueByQuery(self.geographicExtentLeftLineEdit, "idinfo/spdom/lbounding/leftbc")
        self.setFormTextValueByQuery(self.geographicExtentRightLineEdit, "idinfo/spdom/lbounding/rightbc")
        self.setFormTextValueByQuery(self.geographicExtentTopLineEdit, "idinfo/spdom/lbounding/topbc")
        self.setFormTextValueByQuery(self.geographicExtentBottomLineEdit, "idinfo/spdom/lbounding/bottombc")
        self.setFormTextValueByQuery(self.additionalMetadataDateLineEdit, "metainfo/metd/date")
        self.setFormTextValueByQuery(self.additionalAdditionalMetadataTextEdit, "metainfo/addmeta")

# attributes widget pane
        # attributeDisplayName
        attributes = tree.xpath("eainfo/detailed/attr")

        self.attributesTableWidget.setColumnCount(2)
        # TODO find a better wat to do this with
        layer = self.layer  # utils.iface.activeLayer()
        fieldsCount = 0
        fieldName = str(layer.attributeDisplayName(fieldsCount))
        while fieldName != "":
            self.attributesTableWidget.setRowCount(fieldsCount + 1)
            count = 0
            foundIt = False

            for attribute in attributes:
                l = ""
                labelElement = attribute.find("attrlabl")
                if labelElement is not None:
                    l = labelElement.text
                d = ""
                descElement = attribute.find("attrdef")
                if descElement is not None:
                    d = descElement.text
                if l == fieldName:
                    foundIt = True
                    if l is not None:
                        item = QTableWidgetItem(l)
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        self.attributesTableWidget.setItem(fieldsCount, 0, item)
                    if d is not None:
                        item = QTableWidgetItem(d)
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                        self.attributesTableWidget.setItem(fieldsCount, 1, item)
                    else:
                        item = QTableWidgetItem("")
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                        self.attributesTableWidget.setItem(fieldsCount, 1, item)

                count += 1
            if not foundIt:
                item = QTableWidgetItem(fieldName)
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.attributesTableWidget.setItem(fieldsCount, 0, item)
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)
                self.attributesTableWidget.setItem(fieldsCount, 1, item)
            fieldsCount += 1
            fieldName = str(layer.attributeDisplayName(fieldsCount))

        self.attributesTableWidget.resizeRowsToContents()
        self.attributesTableWidget.resizeColumnsToContents()
        nameW = self.attributesTableWidget.columnWidth(0)
        headW = self.attributesTableWidget.verticalHeader().width()
        descW = 415 - nameW - headW

        self.attributesTableWidget.setColumnWidth(1, descW)
        self.attributesTableWidget.resizeRowsToContents()
        counter = 0
        while counter < self.attributesTableWidget.rowCount():
            height = self.attributesTableWidget.rowHeight(counter)
            item = self.attributesTableWidget.item(counter, 1)
            editor = QTextEdit()
            if item is not None:
                if item.text() is not None:
                    editor.setText(item.text())
            editor.setStyleSheet("QTextEdit{margin:0px; padding:0;border:0px;}")
            editor.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            if height < 30:
                newHeight = height  # +5
            elif height < 60:
                newHeight = height * 1.2
            elif height < 175:
                newHeight = height * 1
            elif height < 200:
                newHeight = height * 0.9
            elif height < 800:
                newHeight = height * 0.75
            else:
                newHeight = height * 0.70
            self.attributesTableWidget.setCellWidget(counter, 1, editor)
            self.attributesTableWidget.setRowHeight(counter, newHeight)
            counter += 1


##############################################################################
    def loadMetadataFromLayer(self):
        QgsMessageLog.logMessage("MetadataEditorDialog loadMetadataFromLayer")
        l = self.layer
# title
        # l.featureCount()
        title = str(self.titleLineEdit.text())
        if len(title) <= 0:
            title = str(l.title())
            if len(title) <= 0:
                title = str(l.name())
                if len(title) <= 0:
                    title = str(l.source()).rsplit("/", 1)[-1].rsplit("\\", 1)[-1].rsplit(".", 1)[0]
            self.titleLineEdit.setText(title)

# CRS
        crs = l.crs()
        if crs is not None:
            crsHelper = CRSHelper(crs)
            self.datumLineEdit.setText(crsHelper.datum)
            self.projectionLineEdit.setText(crsHelper.projection)
# extents
        extent = l.extent()
        self.additionalMetadataDateLineEdit.setText(datetime.now().strftime("%d/%m/%Y"))
        # source extent
        esMinPoint = QgsPoint(extent.xMinimum(), extent.yMinimum())
        esMaxPoint = QgsPoint(extent.xMaximum(), extent.yMaximum())
        # transform to GDA94
        targetCrs = QgsCoordinateReferenceSystem()
        targetCrs.createFromOgcWmsCrs("EPSG:4283")
        transform = QgsCoordinateTransform(crs, targetCrs)
        etMinPoint = transform.transform(esMinPoint)
        etMaxPoint = transform.transform(esMaxPoint)

        # extentInIndexCRS = QgsRectangle(eiMinPoint, eiMaxPoint)
        self.geographicExtentLeftLineEdit.setText(str(etMinPoint.x()))
        self.geographicExtentRightLineEdit.setText(str(etMaxPoint.x()))
        self.geographicExtentBottomLineEdit.setText(str(etMinPoint.y()))
        self.geographicExtentTopLineEdit.setText(str(etMaxPoint.y()))


##############################################################################
    def saveMetadata(self):
        QgsMessageLog.logMessage("MetadataEditorDialog saveMetadata")
        if True:
            self.updateTreeFromForm()
            self.loadMetadataFromLayer()
            xmlString = MetadataTools.treeToString(self.tree)
            self.openFile.seek(0)
            # add a little padding to workaround a DPAW Tools expectation
            self.openFile.write("""<?xml version="1.0"?>
<!--<!DOCTYPE metadata SYSTEM "http://www.esri.com/metadata/esriprof80.dtd">-->
""")
            self.openFile.write(xmlString)
            self.openFile.truncate()
            self.openFile.close()

            self.openFile = None
            return True

##############################################################################
    def updateTreeFromForm(self):
        # left side
            self.setXmlValueFromFormText(self.titleLineEdit, "idinfo/citation/citeinfo/title")
            self.setXmlValueFromFormText(self.custodianLineEdit, "idinfo/citation/citeinfo/origin")
            self.setXmlValueFromFormText(self.startingDateLineEdit, "idinfo/timeperd/begdate")
            self.setXmlValueFromFormText(self.endingDateLineEdit, "idinfo/timeperd/enddate")
            self.setXmlValueFromFormText(self.abstractTextEdit, "idinfo/descript/abstract")

        # contact pane
            self.setXmlValueFromFormText(self.contactOrganisationLineEdit, "metainfo/metc/cntinfo/cntorgp/cntorg")
            self.setXmlValueFromFormText(self.contactPositionLineEdit, "metainfo/metc/cntinfo/cntorgp/cntper")
            self.setXmlValueFromFormText(self.contactMailAddressLineEdit, "metainfo/metc/cntinfo/cntaddr/addrtype")
            self.setXmlValueFromFormText(self.contactSuburbLineEdit, "metainfo/metc/cntinfo/cntaddr/city")
            self.setXmlValueFromFormText(self.contactCountryStateLineEdit, "metainfo/metc/cntinfo/cntaddr/state")
            self.setXmlValueFromFormText(self.contactPostcodeLineEdit, "metainfo/metc/cntinfo/cntaddr/postal")
            self.setXmlValueFromFormText(self.contactTelephoneLineEdit, "metainfo/metc/cntinfo/cntvoice")
            self.setXmlValueFromFormText(self.contactFaxLineEdit, "distinfo/distrib/cntinfo/cntfax")
            self.setXmlValueFromFormText(self.contactEmailLineEdit, "distinfo/distrib/cntinfo/cntemail")

# access pane
            self.setXmlValueFromFormText(self.accessStoredDataFormatLineEdit, "idinfo/citation/citeinfo/geoform")
            self.setXmlValueFromFormText(self.accessAccessConstraintsTextEdit, "idinfo/accconst")

# quality pane
            self.setXmlValueFromFormText(self.qualityLineageTextEdit, "dataqual/lineage")
            self.setXmlValueFromFormText(self.qualityPositionalAccuracyTextEdit, "dataqual/posacc")
            self.setXmlValueFromFormText(self.qualityAttributeAccuracyTextEdit, "dataqual/attracc")
            self.setXmlValueFromFormText(self.qualityLogicalConsistancyTextEdit, "dataqual/logic")
            self.setXmlValueFromFormText(self.qualityCompletenessTextEdit, "dataqual/complete")

# status pane
            self.setXmlValueFromFormText(self.statusProgressTextEdit, "idinfo/status/progress")
            self.setXmlValueFromFormText(self.statusMaintenanceUpdateTextEdit, "idinfo/status/update")

# additional pane
            self.setXmlValueFromFormText(self.geographicExtentLeftLineEdit, "idinfo/spdom/lbounding/leftbc")
            self.setXmlValueFromFormText(self.geographicExtentLeftLineEdit, "idinfo/spdom/bounding/westbc")
            self.setXmlValueFromFormText(self.geographicExtentRightLineEdit, "idinfo/spdom/lbounding/rightbc")
            self.setXmlValueFromFormText(self.geographicExtentRightLineEdit, "idinfo/spdom/bounding/eastbc")
            self.setXmlValueFromFormText(self.geographicExtentTopLineEdit, "idinfo/spdom/lbounding/topbc")
            self.setXmlValueFromFormText(self.geographicExtentTopLineEdit, "idinfo/spdom/bounding/northbc")
            self.setXmlValueFromFormText(self.geographicExtentBottomLineEdit, "idinfo/spdom/lbounding/bottombc")
            self.setXmlValueFromFormText(self.geographicExtentBottomLineEdit, "idinfo/spdom/bounding/southbc")
            self.setXmlValueFromFormText(self.additionalMetadataDateLineEdit, "metainfo/metd/date")
            self.setXmlValueFromFormText(self.additionalAdditionalMetadataTextEdit, "metainfo/addmeta")

# attributes widget pane
            attributes = self.tree.xpath("eainfo/detailed/attr")

            if len(attributes) == 0:
                self.createXmlElement("eainfo/detailed/attr")

            count = 0
            while count < self.attributesTableWidget.rowCount():
                label = str(self.attributesTableWidget.item(count, 0).text())
                foundIt = False
                description = unicode(str(self.attributesTableWidget.cellWidget(count, 1).toPlainText()), "utf-8")
                for attribute in attributes:
                    l = attribute.find("attrlabl").text
                    d = attribute.find("attrdef")
                    if l.lower() == label.lower():
                        if d is None:
                            d = ET.SubElement(attribute, "attrdef")
                        d.text = description
                        foundIt = True
                if not foundIt:
                    attribParent = self.tree.xpath("eainfo/detailed")[0]
                    attr = ET.SubElement(attribParent, "attr")
                    attrlabl = ET.SubElement(attr, "attrlabl")
                    attrlabl.text = label
                    attralias = ET.SubElement(attr, "attralias")
                    attralias.text = label
                    attrdef = ET.SubElement(attr, "attrdef")
                    attrdef.text = description
                count += 1

            for attribute in attributes:
                xmlLabel = attribute.find("attrlabl").text
                if xmlLabel.lower() == "fid" or xmlLabel.lower() == "shape":
                    next
                count = 0
                foundIt = False
                while count < self.attributesTableWidget.rowCount() and not foundIt:
                    tableLabel = str(self.attributesTableWidget.item(count, 0).text())
                    if tableLabel.lower() == xmlLabel.lower():
                        foundIt = True
                    count += 1
                if not foundIt:
                    # attribute.getParent().remove(attribute)
                    self.tree.xpath("eainfo/detailed")[0].remove(attribute)

# CRS
            crsHelper = CRSHelper(self.layer.crs())
            self.setXmlValueFromString(crsHelper.geogcsn, "Esri/DataProperties/coordRef/geogcsn")
            self.setXmlValueFromString(crsHelper.geogcsn, "spref/horizsys/cordsysn/geogcsn")
            self.setXmlValueFromString(crsHelper.projcsn, "Esri/DataProperties/coordRef/projcsn")
            self.setXmlValueFromString(crsHelper.projcsn, "spref/horizsys/cordsysn/projcsn")

            if crsHelper.projected:
                self.setXmlValueFromString("Geographic", "Esri/DataProperties/coordRef/type")
            else:
                self.setXmlValueFromString("Projected", "Esri/DataProperties/coordRef/type")


##############################################################################
    def setFormTextValue(self, formElement, value):
        formElement.setText(value)
        try:
            formElement.setCursorPosition(0)
        except:
            pass


###############################################################################
    def setFormTextValueByQuery(self, formElement, query):
        result = self.tree.xpath(query)
        if len(result) > 0:
            value = result[0].text
            if value is not None:
                if len(value) > 0:
                    self.setFormTextValue(formElement, result[0].text)
                    return
        self.setFormTextValue(formElement, "")


##############################################################################
    def setXmlValueFromFormText(self, formElement, query):
        if type(formElement) is QLineEdit:
            value = str(formElement.text())
        elif type(formElement) is QTextEdit:
            value = str(formElement.toPlainText().encode('ascii', 'ignore'))
        else:
            Tools.debug(str(type(formElement)) + "=" + str(formElement))
        if value is not None:
            if len(value) > 0:
                self.setXmlValueFromString(value, query)
                return
        self.setXmlValueFromString("", query)


##############################################################################
    def setXmlValueFromString(self, string, query):
        resultElements = self.tree.xpath(query)

        if resultElements is None or len(resultElements) == 0:
            resultElements = self.createXmlElement(query)
        if len(resultElements) > 0:
            if string is not None:
                if len(string) > 0:
                    resultElements[0].text = string
                    return
            resultElements[0].text = ""


##############################################################################
    def createXmlElement(self, query):
        tokens = query.split("/")
        if len(tokens) == 0:
            Tools.debug("Invalid XPath query:" + query, "XML ERROR")
            return []   # empty set
        validSearch = ""
        searchString = tokens[0]
        searchResults = self.tree.xpath(searchString)
        while (searchResults is not None) and (len(searchResults) > 0):
            validSearch = searchString
            tokens.pop(0)
            searchString += "/" + tokens[0]
            searchResults = self.tree.xpath(searchString)

        if len(validSearch) > 0:
            returnResult = self.tree.xpath(validSearch)[0]
        else:
            returnResult = self.tree

        while len(tokens) > 0:
            returnResult = ET.SubElement(returnResult, tokens.pop(0))

        return [returnResult]


##############################################################################
    def okButtonHandler(self):
        confirm = Tools.showYesNoDialog("Are you ready to save any changes?",
                                        "Save Metadata")
        if confirm:
            success = self.saveMetadata()
            if success:
                self.accept()


##############################################################################
    def cancelButtonHandler(self):
        confirm = Tools.showYesNoDialog("Do you want to discard any changes?",
                                        "Discard Changes")
        if confirm:
            if self.mode == MetadataEditorDialog.CREATE:
                path = self.openFile.name
                self.openFile.close()
                os.remove(path)
            else:
                self.openFile.close()
            self.reject()
        else:
            self.show()

##############################################################################
    def defineCoordinateSystemButtonHandler(self):
        SelectCRSDialog(SelectCRSDialog.LAYER, self.layer)
        self.loadMetadataFromLayer()


##############################################################################
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            e.accept()
            self.cancelButtonHandler()
        else:
            pass

    def loadContactsFromFile(self):
        fileLocation = "T:/757-Information Management Branch/GIS Group/METADATA/QGIS_Metadata/Metadata_Contacts.txt"
        self.contactsDictonary = dict()
        eof = False
        try:
            f = open(fileLocation, "r")
            while not eof:
                contact = Contact()
                try:
                    line = f.readline()
                    contact.title = line.strip()
                    line = f.readline()
                    contact.organisation = line.split(":", 1)[1].strip()
                    line = f.readline()
                    contact.position = line.split(":", 1)[1].strip()
                    line = f.readline()
                    contact.address = line.split(":", 1)[1].strip()
                    line = f.readline()
                    contact.suburb = line.split(":", 1)[1].strip()
                    line = f.readline()
                    contact.state = line.split(":", 1)[1].strip()
                    line = f.readline()
                    contact.postcode = line.split(":", 1)[1].strip()
                    line = f.readline()
                    contact.telephone = line.split(":", 1)[1].strip()
                    line = f.readline()
                    contact.fax = line.split(":", 1)[1].strip()
                    line = f.readline()
                    contact.email = line.split(":", 1)[1].strip()
                except:
                    pass
                if contact.ok():
                    self.contactsDictonary[contact.title] = contact
                    self.contactsPresetsComboBox.addItem(contact.title)
                    f.readline()
                else:
                    eof = True
        except:
            try:
                f.close()
            except:
                pass
        if self.contactsPresetsComboBox.count() == 0:
            self.contactsPresetsComboBox.addItem("Error loading contacts: please map T drive")

    def contactsPresetsComboBoxHandler(self, i):
        key = str(self.contactsPresetsComboBox.itemText(i))
        # if self.contactsDictonary.has_key(key):
        if key in self.contactsDictonary:
            contact = self.contactsDictonary[key]
            confirm = Tools.showYesNoDialog("Do you want to load contact details for {?}".format(contact.title),
                                            "Overwrite Contacts")
            if confirm:
                self.contactOrganisationLineEdit.setText(contact.organisation)
                self.contactPositionLineEdit.setText(contact.position)
                self.contactMailAddressLineEdit.setText(contact.address)
                self.contactSuburbLineEdit.setText(contact.suburb)
                self.contactCountryStateLineEdit.setText(contact.state)
                self.contactPostcodeLineEdit.setText(contact.postcode)
                self.contactTelephoneLineEdit.setText(contact.telephone)
                self.contactFaxLineEdit.setText(contact.fax)
                self.contactEmailLineEdit.setText(contact.email)
            else:
                self.contactsPresetsComboBox.setCurrentIndex(0)


class Contact():
    def __init__(self):
        self.title = ""
        self.organisation = ""
        self.position = ""
        self.address = ""
        self.suburb = ""
        self.state = ""
        self.postcode = ""
        self.telephone = ""
        self.fax = ""
        self.email = ""

    def ok(self):
        length = 0
        length += self.getLength(self.title)
        length += self.getLength(self.organisation)
        length += self.getLength(self.position)
        length += self.getLength(self.postcode)
        length += self.getLength(self.address)
        length += self.getLength(self.suburb)
        length += self.getLength(self.state)
        length += self.getLength(self.postcode)
        length += self.getLength(self.telephone)
        length += self.getLength(self.fax)
        length += self.getLength(self.email)
        return length > 0

    def getLength(self, field):
        if field is None:
            return 0
        return len(field)
