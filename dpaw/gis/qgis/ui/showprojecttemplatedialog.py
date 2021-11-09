from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

# Note: this module is called from qgistools2.py i.e too early to use Tools

class ShowProjectTemplateDialog(QDialog):

    def __init__(self):
        QDialog.__init__(self)  #, Tools.QGISApp)
        self.setupDialog()
        self.exec_()

    def setupDialog(self):
        self.setWindowTitle("New Project default map")

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(QLabel("<b>All new projects open with the WA State Map Base layer loaded by default.</b>"))
        self.layout().addWidget(QLabel(""))
        self.layout().addWidget(QLabel("<b>Use the options below to control this feature.</b>"))
        self.layout().addWidget(QLabel(""))
        self.layout().addWidget(QLabel("<b>Alternatively you can choose other layers or zoom levels to open by default by going</b>"))
        self.layout().addWidget(QLabel("<b>to the DBCA QGIS Tools menu and selecting 'Settings | Default Project | Set current project...'</b>"))
        self.layout().addWidget(QLabel(""))

        groupBox = QGroupBox("", self)
        self.layout().addWidget(groupBox)
        groupBox.setLayout(QVBoxLayout())

        self.alwaysUseSMB = QRadioButton("Continue to open new projects with this base map (you won't see this dialogue in future)", self)
        groupBox.layout().addWidget(self.alwaysUseSMB)
        self.alwaysUseSMB.setChecked(False)

        self.neverUseDefault = QRadioButton("Don't use a default base map in new projects (you won't see this dialogue in future)", self)
        groupBox.layout().addWidget(self.neverUseDefault)
        self.neverUseDefault.setChecked(False)

        self.askNextTime = QRadioButton("Use this base map, and give me these options, again next time (use this if unsure)", self)
        groupBox.layout().addWidget(self.askNextTime)
        self.askNextTime.setChecked(True)
        
        self.layout().addWidget(QLabel(""))
        
        buttonLayout = QHBoxLayout()
        self.layout().addLayout(buttonLayout)
        buttonLayout.addStretch()
        buttonLayout.addStretch()
        self.okButton = QPushButton("OK")
        buttonLayout.addWidget(self.okButton)
        self.okButton.clicked.connect(self.okClickHandler)
        buttonLayout.addStretch()
        self.cancelButton = QPushButton("Cancel")
        buttonLayout.addWidget(self.cancelButton)
        self.cancelButton.clicked.connect(self.cancelClickHandler)
        buttonLayout.addStretch()
        buttonLayout.addStretch()

    def okClickHandler(self):
        if self.alwaysUseSMB.isChecked() == True:
            self.alwaysUseSMBHandler()
        elif self.neverUseDefault.isChecked() == True:
            self.neverUseDefaultHandler()
        elif self.askNextTime.isChecked() == True:
            self.askNextTimeHandler()
        self.accept()

    def cancelClickHandler(self):
        self.reject()

    def alwaysUseSMBHandler(self):
        # Just need to switch off dialogue from showing in future
        self.setSetting("showDefaultMapDialog", "false")

    def neverUseDefaultHandler(self):
        # Need to change settings and switch off dialogue from showing in future
        QSettings().setValue("QGis/newProjectDefault", "false")
        self.setSetting("showDefaultMapDialog", "false")
        registry = QgsMapLayerRegistry.instance()
        registry.removeAllMapLayers()

    def askNextTimeHandler(self):
        # Tools.debug("Next time")
        pass    # No need to make any changes at this time
        
    # Folowing is a duplicate of tools.setSetting - used here to abvoid circular imports
    def setSetting(self, name, value):
        settings = QSettings()
        settings.setValue("DEC/" + name, value)




