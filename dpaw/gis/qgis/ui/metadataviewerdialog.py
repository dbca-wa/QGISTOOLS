from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from qgis.core import *
from ..tools import Tools
from ..data.metadata.metadatatools import MetadataTools

from os import path, startfile, remove
from shutil import copyfile


import qgis.utils


class MetadataViewerDialog(QDialog):

    def __init__(self, layer, mode):
        assert(isinstance(layer, QgsMapLayer)), "MetadataViewerDialog init attribute type error"

        js_path = "C:/ProgramData/DEC/GIS/jquery-1.12.4.js"
        if not path.isfile(js_path):
            src_path = path.join(Tools.getPluginPath(), "resources\js\jquery-1.12.4.min.js")
            try:
                copyfile(src_path, js_path)
            except:
                pass

        QDialog.__init__(self, Tools.QGISApp)
        self.layer = layer
        self.mode = mode
        self.attachments = {}
        self.setupDialog()
        self.updateMetadata()
        self.webView.setFocus(Qt.OtherFocusReason)
        self.exec_()


##############################################################################
    def setupDialog(self):
        self.printer = None
        self.setWindowTitle("View Metadata")
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.styleSheetPath = path.join(Tools.getPluginPath(), "resources\stylesheets")
        toolsLayout = QHBoxLayout()
        mainLayout.addLayout(toolsLayout)
        menubar = QToolBar(self)
        toolsLayout.addWidget(menubar)

        # Printing
        printButton = menubar.addAction(Tools.iconPrinter, "Print")
        printButton.triggered.connect(self.printWebView)
        pageSetupButton = menubar.addAction(Tools.iconPageSetup, "Page Setup")
        pageSetupButton.triggered.connect(self.pageSetup)
        menubar.addSeparator()

        # Metadata
        menubar.addWidget(QLabel("<b>Additional Metadata:</b>"))
        self.additionalMetadataComboBox = QComboBox(menubar)
        menubar.addWidget(self.additionalMetadataComboBox)
        self.additionalMetadataComboBox.currentIndexChanged.connect(self.additionalMetadataComboBoxChanged)
        self.additionalMetadataViewButton = menubar.addAction("View")
        self.additionalMetadataViewButton.triggered.connect(self.viewAdditionalMetadata)
        menubar.addSeparator()

        # stylesheet selection
        menubar.addWidget(QLabel("<b>Current Style Sheet:</b>"))
        self.styleComboBox = QComboBox(menubar)
        menubar.addWidget(self.styleComboBox)
        self.styleSheetList = [MetadataTools.LegacyMetadataProfile, MetadataTools.NewMetadataProfile]
        for index, style in enumerate(self.styleSheetList):
            self.styleComboBox.addItem(style, None)
            if style == self.mode:
                self.styleComboBox.setCurrentIndex(index)
        self.styleComboBox.currentIndexChanged.connect(self.stylesheetComboBoxChanged)

        # webview
        webView = QWebView()
        self.webView = webView
        mainLayout.addWidget(webView)

        self.finished.connect(self.onDialogClosing)

    def onDialogClosing(self, num):
        for filepath in self.attachments.values():
            Tools.addFileToDeletionList(filepath)
        Tools.deleteFilesOnDeletionList()

    ##############################################################################
    def updateAdditionalMetadata(self):
        self.tree = MetadataTools.getMetadataAsTree(self.layer)
        filenames = MetadataTools.getEmbeddedFileNames(self.tree)
        if len(filenames) > 0:
            self.additionalMetadataComboBox.addItem("-Select File-")
            self.additionalMetadataComboBox.setEnabled(True)
        else:
            self.additionalMetadataComboBox.addItem("-No Files-")
            self.additionalMetadataComboBox.setEnabled(False)
        for filename in filenames:
            self.additionalMetadataComboBox.addItem(filename, None)

    ##############################################################################
    def updateMetadataRender(self):
        xslFilename = str(self.styleComboBox.currentText()) + ".xsl"
        xslLocation = path.join(self.styleSheetPath, xslFilename)
        xmlLocation = MetadataTools.getExistingMetadataFileLocation(self.layer)
        html = MetadataTools.getMetadataAsHtml(xslLocation, xmlLocation)
        self.webView.setHtml(html)
        self.webView.page().mainFrame()

    ##############################################################################
    def updateMetadata(self):
        self.updateAdditionalMetadata()
        self.updateMetadataRender()

    ##############################################################################
    def stylesheetComboBoxChanged(self, index):
        self.updateMetadata()

    ##############################################################################
    def additionalMetadataComboBoxChanged(self, index):
        self.additionalMetadataViewButton.setEnabled(index > 0)

##############################################################################
    def printWebView(self):
        if self.printer is None:
            self.printer = QPrinter()
        printer = self.printer

        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            self.webView.print_(printer)

##############################################################################
    def pageSetup(self):
        if self.printer is None:
            self.printer = QPrinter()
        printer = self.printer

        dialog = QPageSetupDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            pass

##############################################################################
    def viewAdditionalMetadata(self):
        filename = str(self.additionalMetadataComboBox.currentText())
        if filename not in self.attachments.keys():
            self.attachments[filename] = MetadataTools.writeEmbeddedFileToTempLocation(self.tree, filename)
        startfile(self.attachments[filename])
