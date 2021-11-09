from qgis.core import *
from qgis.gui import *
import qgis.utils
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4.QtXml import *

from ..tools import *
from ..data.metadata.metadatatools import MetadataTools
import os
import shutil
from ..data.crs.crshelper import CRSHelper
from ..data.requests.shapefilelayersource import ShapefileLayerSource
from datetime import datetime
from ..data.crs.crshelper import CRSHelper
import sys


class MapLabelDialog(QDialog):
    _composerTitle = ""
    _template = ""
    _mapTitle = ""
    _showGrid = False
    _gridStyle = "Solid"
    _showGrat = False
    _gratStyle = "Cross"    
    _author = ""
    _jobRef = ""
    _dept = Tools.get_dept_long_name()
    _acro = Tools.get_dept_acronym()
    _date = ""
    _time = ""

    def __init__(self):
        QDialog.__init__(self, Tools.QGISApp)
        # validate
        self.setupDialog()
        self.result = self.exec_()

    def setupDialog(self):
        self.setMinimumWidth(380)
        self.setWindowTitle("Map Production")
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        from datetime import datetime
        now = datetime.now()
        
        # Set fonts
        boldFont = QFont()
        boldFont.setWeight(90)
        semiBoldFont = QFont()
        semiBoldFont.setWeight(63)
        normalFont = QFont()
        normalFont.setWeight(50)

# COMPOSER PROPERTIES GROUP
        composerPropertiesGroupBox = QGroupBox("COMPOSER PROPERTIES", self)
        composerPropertiesGroupBox.setFont(boldFont)
        mainLayout.addWidget(composerPropertiesGroupBox)
        composerPropertiesLayout = QFormLayout()
        composerPropertiesGroupBox.setLayout(composerPropertiesLayout)
        self.composerTitleLineEdit = QLineEdit("", self)
        self.composerTitleLineEdit.setFont(normalFont)
        self.composerTitleLabel = QLabel("Composer Title\n(optional)")
        self.composerTitleLabel.setFont(normalFont)
        composerPropertiesLayout.addRow(self.composerTitleLabel, self.composerTitleLineEdit)

    # Page Size Group
        pageSizeGroupBox = QGroupBox("Page Size", self)
        pageSizeGroupBox.setFont(semiBoldFont)
        composerPropertiesLayout.addWidget(pageSizeGroupBox)
        pageSizeLayout = QHBoxLayout()
        pageSizeGroupBox.setLayout(pageSizeLayout)

        # A5 Radio Button
        self.a5RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a5RadioButton)
        self.a5RadioButton.setFont(normalFont)
        self.a5RadioButton.setText("A5")
        if Tools.lastPageSize == "A5":
            self.a5RadioButton.setChecked(True)
        else:
            self.a5RadioButton.setChecked(False)
        
        # A4 Radio Button
        self.a4RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a4RadioButton)
        self.a4RadioButton.setFont(normalFont)
        self.a4RadioButton.setText("A4")
        if Tools.lastPageSize == "A4":
            self.a4RadioButton.setChecked(True)
        else:
            self.a4RadioButton.setChecked(False)

        # A3 Radio Button
        self.a3RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a3RadioButton)
        self.a3RadioButton.setFont(normalFont)
        self.a3RadioButton.setText("A3")
        if Tools.lastPageSize == "A3":
            self.a3RadioButton.setChecked(True)
        else:
            self.a3RadioButton.setChecked(False)

        # A2 Radio Button
        self.a2RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a2RadioButton)
        self.a2RadioButton.setFont(normalFont)
        self.a2RadioButton.setText("A2")
        if Tools.lastPageSize == "A2":
            self.a2RadioButton.setChecked(True)
        else:
            self.a2RadioButton.setChecked(False)

        # A1 Radio Button
        self.a1RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a1RadioButton)
        self.a1RadioButton.setFont(normalFont)
        self.a1RadioButton.setText("A1")
        if Tools.lastPageSize == "A1":
            self.a1RadioButton.setChecked(True)
        else:
            self.a1RadioButton.setChecked(False)

        # A0 Radio Button
        self.a0RadioButton = QRadioButton(self)
        pageSizeLayout.addWidget(self.a0RadioButton)
        self.a0RadioButton.setFont(normalFont)
        self.a0RadioButton.setText("A0")
        if Tools.lastPageSize == "A0":
            self.a0RadioButton.setChecked(True)
        else:
            self.a0RadioButton.setChecked(False)

    # Orientation Group
        orientationGroupBox = QGroupBox("Orientation", self)
        orientationGroupBox.setFont(semiBoldFont)
        composerPropertiesLayout.addWidget(orientationGroupBox)
        orientationLayout = QHBoxLayout()
        orientationGroupBox.setLayout(orientationLayout)

        # Landscape Radio Button
        self.landscapeRadioButton = QRadioButton(self)
        orientationLayout.addWidget(self.landscapeRadioButton)
        self.landscapeRadioButton.setFont(normalFont)
        self.landscapeRadioButton.setText("Landscape")
        if Tools.lastPageOrientation == "Landscape":
            self.landscapeRadioButton.setChecked(True)
        else:
            self.landscapeRadioButton.setChecked(False)

        # Portrait Radio Button
        self.portraitRadioButton = QRadioButton(self)
        orientationLayout.addWidget(self.portraitRadioButton)
        self.portraitRadioButton.setFont(normalFont)
        self.portraitRadioButton.setText("Portrait")
        if Tools.lastPageOrientation == "Portrait":
            self.portraitRadioButton.setChecked(True)
        else:
            self.portraitRadioButton.setChecked(False)
        
# GRIDS GROUP
        gridsGroupBox = QGroupBox("COORDINATE GRIDS", self)
        gridsGroupBox.setFont(boldFont)
        mainLayout.addWidget(gridsGroupBox)
        gridsLayout = QFormLayout()
        gridsGroupBox.setLayout(gridsLayout)       

    # Grid Group
        # Only show if using a projected CRS
        canvas = qgis.utils.iface.mapCanvas()
        gcs = canvas.mapSettings().destinationCrs().geographicFlag()
        gridGroupBox = QGroupBox("Eastings / Northings", self)
        gridGroupBox.setFont(semiBoldFont)
        if not gcs:
            gridsLayout.addWidget(gridGroupBox)
        else:
            gridGroupBox.resize(0, 0)
        gridLayout = QHBoxLayout()
        gridGroupBox.setLayout(gridLayout)

        # 'No Grid' Radio Button
        self.noGridRadioButton = QRadioButton(self)
        gridLayout.addWidget(self.noGridRadioButton)
        self.noGridRadioButton.setFont(normalFont)
        self.noGridRadioButton.setText("No grid")
        self.noGridRadioButton.setChecked(False)

        # 'Lines' Radio Button
        self.linesRadioButton = QRadioButton(self)
        gridLayout.addWidget(self.linesRadioButton)
        self.linesRadioButton.setFont(normalFont)
        self.linesRadioButton.setText("Lines")
        self.linesRadioButton.setChecked(True)

        # 'Crosses' Radio Button
        self.crossesRadioButton = QRadioButton(self)
        gridLayout.addWidget(self.crossesRadioButton)
        self.crossesRadioButton.setFont(normalFont)
        self.crossesRadioButton.setText("Crosses")
        self.crossesRadioButton.setChecked(False)
        
        # 'Coords' Radio Button
        self.gridCoordsRadioButton = QRadioButton(self)
        gridLayout.addWidget(self.gridCoordsRadioButton)
        self.gridCoordsRadioButton.setFont(normalFont)
        self.gridCoordsRadioButton.setText("Coords only")
        self.gridCoordsRadioButton.setChecked(False)

    # Graticule Group
        gratGroupBox = QGroupBox("Lats / Longs", self)
        gratGroupBox.setFont(semiBoldFont)
        gridsLayout.addWidget(gratGroupBox)
        gratLayout = QHBoxLayout()
        gratGroupBox.setLayout(gratLayout)

        # 'No Grat' Radio Button
        self.noGratRadioButton = QRadioButton(self)
        gratLayout.addWidget(self.noGratRadioButton)
        self.noGratRadioButton.setFont(normalFont)
        self.noGratRadioButton.setText("No grid")
        self.noGratRadioButton.setChecked(False)

        # 'Lines' Radio Button
        self.gratLinesRadioButton = QRadioButton(self)
        gratLayout.addWidget(self.gratLinesRadioButton)
        self.gratLinesRadioButton.setFont(normalFont)
        self.gratLinesRadioButton.setText("Lines")
        self.gratLinesRadioButton.setChecked(False)

        # 'Crosses' Radio Button
        self.gratCrossesRadioButton = QRadioButton(self)
        gratLayout.addWidget(self.gratCrossesRadioButton)
        self.gratCrossesRadioButton.setFont(normalFont)
        self.gratCrossesRadioButton.setText("Crosses")
        self.gratCrossesRadioButton.setChecked(True)

        # 'Coords' Radio Button
        self.gratCoordsRadioButton = QRadioButton(self)
        gratLayout.addWidget(self.gratCoordsRadioButton)
        self.gratCoordsRadioButton.setFont(normalFont)
        self.gratCoordsRadioButton.setText("Coords only")
        self.gratCoordsRadioButton.setChecked(False)        

# MAP TEXT GROUP
        mapDetailsGroupBox = QGroupBox("MAP TEXT", self)
        mapDetailsGroupBox.setFont(boldFont)
        mainLayout.addWidget(mapDetailsGroupBox)
        mapDetailsLayout = QFormLayout()
        mapDetailsGroupBox.setLayout(mapDetailsLayout)
        self.mapTitleLineEdit = QLineEdit(MapLabelDialog._mapTitle, self)
        self.mapTitleLineEdit.setFont(normalFont)
        self.authorLineEdit = QLineEdit(MapLabelDialog._author, self)
        self.authorLineEdit.setFont(normalFont)
        self.jobRefLineEdit = QLineEdit(MapLabelDialog._jobRef, self)
        self.jobRefLineEdit.setFont(normalFont)
        self.departmentLineEdit = QLineEdit(MapLabelDialog._dept, self)
        self.departmentLineEdit.setFont(normalFont)
        self.acronymLineEdit = QLineEdit(MapLabelDialog._acro, self)
        self.acronymLineEdit.setFont(normalFont)
        self.dateLineEdit = QLineEdit(now.strftime("%B ") + now.strftime("%d, %Y").lstrip("0"), self)
        self.dateLineEdit.setFont(normalFont)
        self.timeLineEdit = QLineEdit(now.strftime("%I:%M %p").lstrip("0"), self)
        self.timeLineEdit.setFont(normalFont)
        self.mapTitleLabel = QLabel("Map Title")
        self.mapTitleLabel.setFont(normalFont)
        mapDetailsLayout.addRow(self.mapTitleLabel, self.mapTitleLineEdit)
        self.authorLabel = QLabel("Author")
        self.authorLabel.setFont(normalFont)
        mapDetailsLayout.addRow(self.authorLabel, self.authorLineEdit)
        self.jobRefLabel = QLabel("Job Reference")
        self.jobRefLabel.setFont(normalFont)        
        mapDetailsLayout.addRow(self.jobRefLabel, self.jobRefLineEdit)
        self.deptLabel = QLabel("Department")
        self.deptLabel.setFont(normalFont)          
        mapDetailsLayout.addRow(self.deptLabel, self.departmentLineEdit)
        self.acronymLabel = QLabel("Acronym")
        self.acronymLabel.setFont(normalFont)         
        mapDetailsLayout.addRow(self.acronymLabel, self.acronymLineEdit)
        self.dateLabel = QLabel("Date")
        self.dateLabel.setFont(normalFont)             
        mapDetailsLayout.addRow(self.dateLabel, self.dateLineEdit)
        self.timeLabel = QLabel("Time")
        self.timeLabel.setFont(normalFont) 
        mapDetailsLayout.addRow(self.timeLabel, self.timeLineEdit)

        buttonsLayout = QHBoxLayout()
        mainLayout.addLayout(buttonsLayout)
        self.okButton = QPushButton("Create Map", self)
        self.cancelButton = QPushButton("Cancel", self)
        buttonsLayout.addWidget(self.okButton)
        buttonsLayout.addWidget(self.cancelButton)

        self.okButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)

    def accept(self):
        # validate
        if len(self.mapTitleLineEdit.text()) == 0 or \
           len(self.authorLineEdit.text()) == 0 or \
           len(self.jobRefLineEdit.text()) == 0 or \
           len(self.departmentLineEdit.text()) == 0 or \
           len(self.acronymLineEdit.text()) == 0 or \
           len(self.dateLineEdit.text()) == 0 or \
           len(self.timeLineEdit.text()) == 0:
                Tools.alert("Please complete all Map fields.", "Input Error")
                return


        # save values
        pageSize = ""
        orientation = ""
        showGrid = False
        gridStyle = None
        showGrat = False
        gratStyle = None
        if self.a5RadioButton.isChecked():
            pageSize = "A5"
        elif self.a4RadioButton.isChecked():
            pageSize = "A4"
        elif self.a3RadioButton.isChecked():
            pageSize = "A3"
        elif self.a2RadioButton.isChecked():
            pageSize = "A2"
        elif self.a1RadioButton.isChecked():
            pageSize = "A1"
        elif self.a0RadioButton.isChecked():
            pageSize = "A0"
        if self.landscapeRadioButton.isChecked():
            orientation = "Landscape"
        elif self.portraitRadioButton.isChecked():
            orientation = "Portrait"
        Tools.lastPageSize = pageSize
        Tools.lastPageOrientation = orientation
        if self.noGridRadioButton.isChecked():
            showGrid = False
        else:
            showGrid = True
            if self.linesRadioButton.isChecked():
                gridStyle = QgsComposerMapGrid.Solid
            elif self.crossesRadioButton.isChecked():
                gridStyle = QgsComposerMapGrid.Cross
            elif self.gridCoordsRadioButton.isChecked():
                gridStyle = QgsComposerMapGrid.FrameAnnotationsOnly
        if self.noGratRadioButton.isChecked():
            showGrat = False
        else:
            showGrat = True
            if self.gratLinesRadioButton.isChecked():
                gratStyle = QgsComposerMapGrid.Solid
            elif self.gratCrossesRadioButton.isChecked():
                gratStyle = QgsComposerMapGrid.Cross
            elif self.gratCoordsRadioButton.isChecked():
                gratStyle = QgsComposerMapGrid.FrameAnnotationsOnly


        # COMPOSER TITLE CHECKS
        # Get list of existing composer titles
        composers = Tools.iface.activeComposers()
        composerTitles = []
        for item in composers:
            composerTitles.append(item.composerWindow().windowTitle())
        # If user does not specify title, construct one based on page size and orientation
        if self.composerTitleLineEdit.text() == "":
            i = 1
            string = pageSize + "_" + orientation + "_" + str(i)
            while string in composerTitles:
                i += 1
                string = pageSize + "_" + orientation + "_" + str(i)
            self.composerTitleLineEdit.setText(string)    

        else:   #i.e. if user has entered a composer title  
            # Check composer title not already in use
            for item in composers:
                if item.composerWindow().windowTitle() == self.composerTitleLineEdit.text():
                    Tools.alert("This project already has a composer with that name.  " +
                                "Please choose another.", "Duplicate Composer Name")
                    self.composerTitleLineEdit.setText("")
                    self.composerTitleLineEdit.setFocus()
                    return
                
                
        MapLabelDialog._composerTitle = self.composerTitleLineEdit.text()
        MapLabelDialog._template = "DPAW_" + pageSize + "_" + orientation + ".qpt"
        MapLabelDialog._showGrid = showGrid
        MapLabelDialog._gridStyle = gridStyle
        MapLabelDialog._showGrat = showGrat
        MapLabelDialog._gratStyle = gratStyle        
        MapLabelDialog._mapTitle = self.mapTitleLineEdit.text()
        MapLabelDialog._author = self.authorLineEdit.text()
        MapLabelDialog._jobRef = self.jobRefLineEdit.text()
        MapLabelDialog._dept = self.departmentLineEdit.text()
        MapLabelDialog._acro = self.acronymLineEdit.text()
        MapLabelDialog._date = self.dateLineEdit.text()
        MapLabelDialog._time = self.timeLineEdit.text()
        QDialog.accept(self)


class MapProduction(QObject):
    _QGISVersion = float(qgis.core.QGis.QGIS_VERSION[:3])
    qgisTools2Folder = os.path.join(os.path.dirname(__file__), ("../../../.."))
    xMin = None
    xMax = None
    yMin = None
    yMax = None
    mainScale = None

    def __init__(self):
        QObject.__init__(self, Tools.iface.mainWindow())
        self.crs = None
        self.cv = None
        self.localityMap = None
        self.mainMap = None
        self.scalebars = []
        self.scalebarPosn = None
        self.paperSize = None
        self.lambdaUpdateLocalityMap = lambda: self.updateLocalityMap(self.cv, self.localityMap, self.mainMap)
        self.lambdaUpdateScaleBars = lambda: self.updateScaleBars(self.cv, self.mainMap, self.scalebars, self.scalebarPosn, self.paperSize)        

    def createMap(self, dlg):
        iface = qgis.utils.iface
        statusBar = iface.mainWindow().statusBar()
        statusBar.showMessage("Step 1 underway: Loading template...")
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

        # Freeze main canvas so it doesn't render changes while map production underway
        canvas = iface.mapCanvas()
        canvas.freeze(True)

        # import input from user
        composer = dlg._composerTitle
        templateFilename = dlg._template
        title = dlg._mapTitle
        author = dlg._author
        jobRef = dlg._jobRef
        dept = dlg._dept
        acro = dlg._acro

        # get bounding rectangle of canvas and use to specify initial extents
        canvas = qgis.utils.iface.mapCanvas()
        extent = canvas.extent()
        xMin = str(canvas.extent().xMinimum())
        xMax = str(canvas.extent().xMaximum())
        yMin = str(canvas.extent().yMinimum())
        yMax = str(canvas.extent().yMaximum())
        extentString = 'ymin="' + yMin + '" xmin="' + xMin + '" ymax="' + yMax + '" xmax="' + xMax + '"'

        # create composer from template (based on user-specified page size and orientation) and extentString
        template = os.path.normpath(self.qgisTools2Folder) + r"/resources/composer_templates/" + templateFilename
        templateFile = file(template, 'rt')
        templateContent = str(templateFile.read())
        templateFile.close()
        templateContent = templateContent.replace(r'<Extent/>', r'<Extent ' + extentString + '/>')

        document = QDomDocument()
        document.setContent(templateContent)
        self.cv = Tools.iface.createNewComposer(composer)
        self.cv.composerWindow().hide()

        #Need to get location of scalebar from template file - scalebar moves on loading.
        scaleLocStart = templateContent.find("<ScalebarCentre>") + 16
        scaleLocEnd = templateContent.find("</ScalebarCentre>", scaleLocStart)
        location = templateContent[scaleLocStart:scaleLocEnd]
        comma = location.find(",")
        scalebarX = float(location[:comma])
        scalebarY = float(location[comma + 1:])
        self.scalebarPosn = QPointF(scalebarX, scalebarY)

        # Load template
        self.cv.composition().loadFromTemplate(document)

        # Initialise variables
        if dlg is None:
            return
        maps = []
        images = []
        paper = None
        legend = None
        mainMapLayers = None
        locMapReqd = True

        # other resources
        self.crs = canvas.mapSettings().destinationCrs()
        crsHelper = CRSHelper(self.crs)
        wellKnownScales = [500, 1000,  2000,  2500, 5000, 7500, 10000, 12500,
                           15000, 20000, 25000, 30000, 40000, 50000, 60000,
                           75000, 80000, 100000, 150000, 200000, 250000, 300000, 400000, 500000,
                           600000, 800000, 1000000, 1250000, 1500000, 1750000, 2000000, 3000000, 4000000, 5000000, 
                           6000000, 8000000, 10000000, 12000000, 15000000, 18000000, 20000000, 25000000]
        
        # get main map, locality map, and legend
        for item in self.cv.items():
            if type(item) == QgsComposerMap:
                item.setPreviewMode(QgsComposerMap.Rectangle)
                maps.append(item)
            elif type(item) == QgsComposerLegend:
                legend = item
           
        if len(maps) == 2:
            if maps[0].boundingRect().width() > maps[1].boundingRect().width():
                self.mainMap = maps[0]
                self.localityMap = maps[1]
            else:
                self.mainMap = maps[1]
                self.localityMap = maps[0]

        elif len(maps) > 0:
                self.mainMap = maps[0]
        else:
            Tools.alert("There is no map in this composer; map production tool will be closed.")
            return
        
        # keep current layers for main map
        statusBar.showMessage("Step 2 underway: Loading layers...")
        self.mainMap.storeCurrentLayerSet()
        self.mainMap.setKeepLayerSet(True)

        # set to appropriate well known scale
        self.mainScale = self.mainMap.scale()
        for scale in wellKnownScales:
            if scale >= self.mainScale:
                self.mainScale = scale
                self.mainMap.setNewScale(self.mainScale)
                break

        # Check whether locality map will be required, based on area covered by main map.
        # If main map covers large area cf WA, locality map is set to transparent and no 
        # further updates are made to it.

        # if area shown by main map is large relative to area shown by locality map, make locality map transparent.
        #mainMapArea = (self.mainScale**2) * self.mainMap.rect().width() * self.mainMap.rect().height() / 1000000     # in sqm
        mainMapArea = self.mainMap.extent().height() * self.mainMap.extent().width()
        if (self.crs.geographicFlag() and mainMapArea > 125) or ((not self.crs.geographicFlag()) and mainMapArea > 1.25 * 10**12):
            self.localityMap.setTransparency(100)
            locMapReqd = False

        # iterate through composer items
        for item in self.cv.items():
            if type(item) == QgsComposerScaleBar:
                # assign scalebar to correct map
                item.setComposerMap(self.mainMap)
                self.scalebars.append(item)
            elif type(item) == QgsPaperItem:
                paper = item
            elif type(item) == QgsComposerPicture:
                images.append(item)
            elif type(item) == QgsComposerLabel:
                text = item.text()
                text = text.replace("%T%", title)
                text = text.replace("%DATUM%", crsHelper.datum)
                if crsHelper.projection != "":
                    text = text.replace("%PROJ%", crsHelper.projection)
                else:
                    text = text.replace("Projection: %PROJ%", "Geographic Projection")
                text = text.replace("%A%", author)
                text = text.replace("%DA%", acro)
                text = text.replace("%DEPT%", dept)
                text = text.replace("%J%", jobRef)
                text = text.replace("%TIME%", datetime.now().strftime("%I:%M %p"))
                text = text.replace("%D%", datetime.now().strftime("%B ") + datetime.now().strftime("%d, %Y"))
                item.setText(text)
        
        # determine Paper Size
        self.paperSize = ""
        if paper.boundingRect().width() > paper.boundingRect().height():
            orientation = "L"
            longSide = paper.boundingRect().width()
        else:
            orientation = "P"
            longSide = paper.boundingRect().height()
        if longSide < (210 + 5):        # In QGIS 2.x, seems that paper.boundingRect().width() = actual paper size + 4mm
            self.paperSize = "A5" + orientation
        elif longSide < (297 + 5):
            self.paperSize = "A4" + orientation
        elif longSide < (420 + 5):
            self.paperSize = "A3" + orientation
        elif longSide < (594 + 5):
            self.paperSize = "A2" + orientation
        elif longSide < (841 + 5):
            self.paperSize = "A1" + orientation
        elif longSide < (1189 + 5):
            self.paperSize = "A0" + orientation
        else:
            Tools.alert("It looks like you are using an invalid template.", "Invalid Template")
            return
        
        # reallocate picture source
        for image in images:
            pictureFile = str(image.pictureFile()).rsplit("\\", 1)[-1].rsplit("/", 1)[-1]
            pictureLocation = os.path.join(Tools.getPluginPath(), "resources\\logos\\",  pictureFile)
            image.setPictureFile(pictureLocation)

        self.cv.composerWindow().showMaximized()
        self.cv.composerWindow().findChild(QAction, "mActionZoomAll").trigger()
        self.cv.composerWindow().statusBar().message("Step 3: Adding main map...")
        self.mainMap.setPreviewMode(QgsComposerMap.Render)
        
        # UPDATE LOCALITY MAP, GRID(S) AND SCALE BARS
        if self.localityMap is not None and locMapReqd == True:
            self.cv.composerWindow().statusBar().showMessage("Step 4 may take a minute: creating locality map...")
            self.createLocalityMap(self.localityMap, self.mainMap)
            self.localityMap.setPreviewMode(QgsComposerMap.Render)
            self.localityMap.updateItem()
        
        # Get grid stack (should be just 'Lat-Long Graticule' and 'East-North Grid' from template)
        eastNorthGrid = None
        latLongGraticule = None
        grids = self.mainMap.grids()
        for grid in grids.asList():
            if grid.name() == "East-North Grid":
                eastNorthGrid = grid
            elif grid.name() == "Lat-Long Graticule":
                latLongGraticule = grid

        if eastNorthGrid is not None:
            if dlg._showGrid is False or self.crs.geographicFlag() == True:
                grids.removeGrid(eastNorthGrid.id())
            else:
                self.cv.composerWindow().statusBar().showMessage("Step 5: creating grid(s)...")
                self.updateGrid(self.cv, self.mainMap, eastNorthGrid, "East-North Grid", dlg._gridStyle)
        
        if latLongGraticule is not None:
            if dlg._showGrat is False :
                grids.removeGrid(latLongGraticule.id())
            else:
                self.cv.composerWindow().statusBar().showMessage("Step 5: creating grid(s)...")
                self.updateGrid(self.cv, self.mainMap, latLongGraticule, "Lat-Long Graticule", dlg._gratStyle)

        self.cv.composerWindow().statusBar().showMessage("Step 6: creating scalebars...")
        self.initialiseScalebars(self.cv, self.mainMap, self.scalebars, self.scalebarPosn, self.paperSize)
        self.mainMap.extentChanged.connect(self.lambdaUpdateLocalityMap)
        self.mainMap.extentChanged.connect(self.lambdaUpdateScaleBars)
      
        # Populate legend then prevent it from automatically changing when inset layers are added
        self.cv.composerWindow().statusBar().showMessage("Step 7: creating legend...")
        legend.setAutoUpdateModel(True)
        legend.setAutoUpdateModel(False)
        # Remove rasters and locality map layers from legend
        model = legend.modelV2()
        rootGroup = model.rootGroup()
        ids = rootGroup.findLayerIds()
        for id in ids:
            registryLayer = QgsMapLayerRegistry.instance().mapLayer(id)
            if isinstance(registryLayer, QgsRasterLayer):
                legendLayer = rootGroup.findLayer(id)
                parent = legendLayer.parent()
                parent.removeLayer(registryLayer)
        rootGroup.removeChildrenGroupWithoutLayers()
                
        for r in range(0, model.rowCount()):
            for c in range(0, model.columnCount()):
                if model.index(r,c).data() == "Locality Map Layers":
                    model.removeRows(r, 1)
        legend.setLegendFilterByMapEnabled(True)

        statusBar.message("")
        self.cv.composerWindow().statusBar().showMessage("")
        self.cv.composerWindow().showMaximized()
        self.cv.composerWindow().findChild(QAction, "mActionZoomAll").trigger()
        canvas.freeze(False)
        QApplication.restoreOverrideCursor()
        
    def createLocalityMap(self, localityMap, mainMap):
        # SETTINGS AND WIDELY USED VARIABLES
        localityMap.setTransparency(0)
        localityMap.setPreviewMode(QgsComposerMap.Rectangle)
        mapCRS = Tools.iface.mapCanvas().mapSettings().destinationCrs()
        
        # GET AREA AND CENTROID OF MAIN MAP
        mainMapXMax = mainMap.extent().xMaximum()
        mainMapXMin = mainMap.extent().xMinimum()
        mainMapYMax = mainMap.extent().yMaximum()
        mainMapYMin = mainMap.extent().yMinimum()       
        mainMapWidth = mainMapXMax - mainMapXMin
        mainMapHeight = mainMapYMax - mainMapYMin
        mainMapArea = mainMapWidth * mainMapHeight
        mainMapCentreX = (mainMapXMax + mainMapXMin) / 2
        mainMapCentreY = (mainMapYMax + mainMapYMin) / 2
        
        # SET INITIAL EXTENT OF LOCALITY MAP
        # First define rectangle with same centre as main map, 5x width and height
        locMapXMin = mainMapCentreX - 2.5 * mainMapWidth
        locMapXMax = mainMapCentreX + 2.5 * mainMapWidth
        locMapYMin = mainMapCentreY - 2.5 * mainMapHeight
        locMapYMax = mainMapCentreY + 2.5 * mainMapHeight        
        
        # Check to ensure WA is not being 'pushed out' of the locality map
        initialExtent = self.waBoundaryCheck(mapCRS, locMapXMin, locMapXMax, locMapYMin, locMapYMax)
        localityMap.zoomToExtent(initialExtent)

        # CREATE IN-MEMORY LAYER HOLDING JUST THE CENTROID - MAY NEED TO USE THIS IN LOCALITY MAP
        # First check whether such a layer already exists, and if so, remove it.
        layers = qgis.utils.iface.legendInterface().layers()
        for layer in layers:
            if layer.name() == "__LAYER5":
                QgsMapLayerRegistry.instance().removeMapLayer(layer.id())
        # Create layer
        centroid = QgsPoint(mainMapCentreX, mainMapCentreY)
        centroidLayer = QgsVectorLayer("Point?crs=" + mapCRS.toWkt(), "__LAYER5", "memory")
        memoryProvider = centroidLayer.dataProvider()
        # Create feature
        feature = QgsFeature()
        feature.setGeometry(QgsGeometry.fromPoint(centroid))
        memoryProvider.addFeatures([feature])
        # Transform CRS if need be - need centroid Lat/Long for deciding whether in SW zone for locality layers.
        if mapCRS.geographicFlag() == False:
            gda94 = QgsCoordinateReferenceSystem(4283)
            xform = QgsCoordinateTransform(mapCRS, gda94)
            centroid = QgsPoint(xform.transform(centroid))

        # CHECK WHETHER LOCALITY MAP LAYERS ARE IN PLACE; IF NOT, ADD THEM TO THE CANVAS.
        dataLegend = qgis.utils.iface.legendInterface()
        if "Locality Map Layers" not in dataLegend.groups():      
            localityLayers = dataLegend.addGroup("Locality Map Layers")
            dataLegend.setGroupVisible(localityLayers, False)
            dataLegend.setGroupExpanded(localityLayers, False)

            # State boundary - no labels required
            stateBoundary = ShapefileLayerSource.load_layer(r"\Hydrography\State\WA_coast_smoothed.shp", "__LAYER1")
            stateBoundaryQml = os.path.normpath(self.qgisTools2Folder) + r"/resources/composer_templates/wa_inset_style.qml"
            stateBoundary.loadNamedStyle(stateBoundaryQml)
            if stateBoundary is not None:
                QgsMapLayerRegistry.instance().addMapLayer(stateBoundary)
                dataLegend.moveLayer(stateBoundary, localityLayers)
                dataLegend.setLayerVisible(stateBoundary, False)

            # regions layer
            regions = ShapefileLayerSource.load_layer(r"\Administration_Boundaries\State\dec_regions.shp", "__LAYER2")
            if regions is not None:
                QgsMapLayerRegistry.instance().addMapLayer(regions)
                dataLegend.moveLayer(regions, localityLayers)
                dataLegend.setLayerVisible(regions, False)

            # LGA layer
            lgas = ShapefileLayerSource.load_layer(r"\Administration_Boundaries\State\local_gov_authority.shp", "__LAYER3")
            if lgas is not None:
                QgsMapLayerRegistry.instance().addMapLayer(lgas)
                dataLegend.moveLayer(lgas, localityLayers)
                dataLegend.setLayerVisible(lgas, False)
                #lgaQml = os.path.normpath(self.qgisTools2Folder) + r"/resources/composer_templates/lga_style.qml"
                #lgas.loadNamedStyle(lgaQml)

            # Localities layer
            localities = ShapefileLayerSource.load_layer(r"\Administration_Boundaries\State\locality_boundary.shp", "__LAYER4")
            if localities is not None:
                QgsMapLayerRegistry.instance().addMapLayer(localities)
                dataLegend.moveLayer(localities, localityLayers)
                dataLegend.setLayerVisible(localities, False)

        # Centroid layer - always added even if locality layers have alread been created (centroid may be in different place)
        if centroidLayer is not None:
            QgsMapLayerRegistry.instance().addMapLayer(centroidLayer)
            centroidQml = os.path.normpath(self.qgisTools2Folder) + r"/resources/composer_templates/centroid_marker.qml"
            centroidLayer.loadNamedStyle(centroidQml)
            groups = qgis.utils.iface.legendInterface().groups()
            for group in groups:
                if group == "Locality Map Layers":
                    groupIndex = groups.index(group)
                    dataLegend.moveLayer(centroidLayer, groupIndex)
                    dataLegend.setLayerVisible(centroidLayer, False)
            # May need error handling for case where no group named "Locality Map Layers" - but this situation would not normally arise
        
        # STORE EXISTING VISIBILITY SETTINGS THEN CHANGE THEM FOR PREPARATION OF LOCALITY MAP
        # Get list of all layers and their visibility, then set all main map
        # layers to not visible.  Visibility settings for locality map layers will be set later.
        mainMapLayers = []
        layerSet = []
        layers = qgis.utils.iface.legendInterface().layers()    # Need to re-do as layers may have changed with new __LAYER5
        for layer in layers:
            isVisible = qgis.utils.iface.legendInterface().isLayerVisible(layer)
            mainMapLayers.append((layer.id(), isVisible))
            if layer.name()[:7] == "__LAYER":
                layerSet.append(layer.id()) #Fills layerSet with ALL potential locality map layers - will be filtered later.
            else:
                qgis.utils.iface.legendInterface().setLayerVisible(layer, False)

        # CHOICE OF LOCALITY MAP LAYERS WILL VARY WITH LOCATION (IN OR OUT OF SW CORNER) AND SIZE OF AREA COVERED BY LOCALITY MAP
        # Get approx area of locality map in sqm - locMapArea already holds this if CRS is in metres.  If CRS is geographic:
        locMapWidth = localityMap.extent().width()
        locMapHeight= localityMap.extent().height()
        locMapArea = locMapWidth * locMapHeight
        if mapCRS.geographicFlag() == True:
            mga51 = QgsCoordinateReferenceSystem(28351)     # MGA 51 used as a convenient proxy
            xform = QgsCoordinateTransform(mapCRS, mga51)
            projectedExtent = QgsRectangle(xform.transform(localityMap.extent()))
            locMapArea = projectedExtent.height() * projectedExtent.width()
        visibleLayers = []
        if centroid.x() < 119 and centroid.y() < -30:   # i.e. in SW section (larger than SW region)        NB could change these to 'Constants'
            # List layers to be made visible (excluding centroid layer at this stage)
            if locMapArea <= 5*10**7:
                visibleLayers = ["__LAYER1", "__LAYER4"]    # WA boundary + localities
            elif locMapArea <= 5*10**9:
                visibleLayers = ["__LAYER1", "__LAYER3"]    # WA boundary + LGAs
            else:
                visibleLayers = ["__LAYER1", "__LAYER2"]    # WA boundary + DBCA Regions
        else:
            if locMapArea <= 5*10**8:
                visibleLayers = ["__LAYER1", "__LAYER4"]    # WA boundary + localities
            elif locMapArea <= 5*10**10:
                visibleLayers = ["__LAYER1", "__LAYER3"]    # WA boundary + LGAs
            else:
                visibleLayers = ["__LAYER1", "__LAYER2"]    # WA boundary + DBCA Regions

        # Set layers for locality map
        for layer in layers:
            if layer.name()in visibleLayers:
                qgis.utils.iface.legendInterface().setLayerVisible(layer, True)
            else:
                if layer.id() in layerSet:
                    layerSet.remove(layer.id())

        # RESIZE LOCALITY MAP IF NOT ENOUGH CONTEXT (I.E. TOO FEW BORDERS BETWEEN REGIONS / LGAS / LOCALITIES ARE DISPLAYED
        request = QgsFeatureRequest()
        for layer in layers:
            if layer.name() == visibleLayers[1]:
                count = 0
                layerCRS = layer.crs()
                locMapExtent = localityMap.extent()
                j = 0   # Loop counter
                while count < 4:     # i.e. if < 4 polys show in locality map
                    xform = QgsCoordinateTransform(mapCRS, layerCRS)
                    filterRectangle = QgsRectangle(xform.transform(locMapExtent))
                    request.setFilterRect(filterRectangle)
                    i = 0
                    for f in layer.getFeatures(request):
                        i += 1
                        #if i >= 3:
                            #break
                    count = i
                    if count < 4:
                        locMapExtent.scale(1.4)   # Will approximately double the area covered by locality map
                    j += 1
                if j > 1:
                    localityMap.zoomToExtent(locMapExtent)
                    # THIS MAY CAUSE BOX SHOWING MAIN MAP AREA TO DIMINISH TO INVISIBILITY - IF SO SWITCH ON CENTROID LAYER TO INDICATE LOCATION.
                    locMapArea = locMapExtent.width() * locMapExtent.height()
                    if locMapArea / mainMapArea > 400:
                        #add cross at centroid
                        for layer in layers:
                            if layer.name() == "__LAYER5":
                                qgis.utils.iface.legendInterface().setLayerVisible(layer, True)
                                layerSet.insert(0, layer.id())
        
        # LABEL LOCALITY MAP LAYERS AS APPROPRIATE
        contextLayer = None
        labelField = None
        contextLayerName = visibleLayers[1]
        if contextLayerName == "__LAYER2":
            labelField = "REGION"
        elif contextLayerName == "__LAYER3":
            labelField = "LGA_NAME2"
        elif contextLayerName == "__LAYER4":
            labelField = "LOC_NAME"
        for layer in layers:
            if layer.name() == contextLayerName:
                contextLayer = layer
        if contextLayer is not None and labelField is not None:
            self.labelContextLayer(contextLayer, labelField)
        
        # SWITCH OFF ALL LOCALITY MAP LAYERS AND RETURN MAINMAP LAYERS' VISIBILITY STATUS TO WHAT THEY WERE BEFORE.
        localityMap.setLayerSet(layerSet)
        localityMap.setKeepLayerSet(True)
        
        for layer in layers:
            if layer.name()[:7] == "__LAYER":
                qgis.utils.iface.legendInterface().setLayerVisible(layer, False)
            else:
                for mapLayerInfo in mainMapLayers:
                    if layer.id() == mapLayerInfo[0]:
                        qgis.utils.iface.legendInterface().setLayerVisible(layer, mapLayerInfo[1])
        
    def labelContextLayer(self, contextLayer, labelField):
        palyr = QgsPalLayerSettings()
        palyr.readFromLayer(contextLayer) 
        palyr.enabled = True 
        palyr.fieldName = labelField
        palyr.writeToLayer(contextLayer)

    def waBoundaryCheck(self, mapCRS, xMin, xMax, yMin, yMax):
        # ENSURE WA BOUNDARIES ARE NOT TOO FAR FROM EDGE OF MAP - IF NEED BE, PAN MAP
        # Specify min & max Lat/Long - do not want locality map to extend beyond these.
        yMaxWA = -13
        xMaxWA = 132
        yMinWA = -36
        xMinWA = 109
        
        inputExtent = QgsRectangle(xMin, yMin, xMax, yMax)
        
        # Convert inputs to GDA94
        if mapCRS.geographicFlag() == False:
            gda94 = QgsCoordinateReferenceSystem(4283)
            xform = QgsCoordinateTransform(mapCRS, gda94)
            inputExtent = QgsRectangle(xform.transform(inputExtent))
        xShift = 0
        yShift = 0
        if inputExtent.xMinimum() < xMinWA and inputExtent.xMaximum() <= xMaxWA:
            xShift = xMinWA - inputExtent.xMinimum()
        elif inputExtent.xMaximum() > xMaxWA and inputExtent.xMinimum() >= xMinWA:
            xShift = xMaxWA - inputExtent.xMaximum()
        if inputExtent.yMinimum() < yMinWA and inputExtent.yMaximum() <= yMaxWA:
            yShift = yMinWA - inputExtent.yMinimum()
        elif inputExtent.yMaximum() > yMaxWA and inputExtent.yMinimum() >= yMinWA:
            yShift = yMaxWA - inputExtent.yMaximum()
        gdaXMin = max(inputExtent.xMinimum() + xShift, xMinWA)
        gdaXMax = min(inputExtent.xMaximum() + xShift, xMaxWA)
        gdaYMin = max(inputExtent.yMinimum() + yShift, yMinWA)
        gdaYMax = min(inputExtent.yMaximum() + yShift, yMaxWA)
        gdaExtent = QgsRectangle(gdaXMin, gdaYMin, gdaXMax, gdaYMax)
        if mapCRS.geographicFlag() == False:
            gda94 = QgsCoordinateReferenceSystem(4283)
            xform = QgsCoordinateTransform(gda94, mapCRS)
            outputExtent = QgsRectangle(xform.transform(gdaExtent))
        else:
            outputExtent = gdaExtent
        return outputExtent

    def updateLocalityMap(self, cv, localityMap, mainMap):
        mainMap.setPreviewMode(QgsComposerMap.Rectangle)
        mainMap.updateItem()
        mainMapArea = mainMap.extent().height() * mainMap.extent().width()
        # Do not update if current locality map suffices (it will autoupdate the size and location of the red square)       
        if self.localityMap.extent().contains(self.mainMap.extent()):
            localityMapArea = self.localityMap.extent().height() * self.localityMap.extent().width()
            if 0.01 < mainMapArea / localityMapArea < 0.5:
                self.localityMap.setTransparency(0)
                return
        
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.cv.composerWindow().statusBar().message("Updating locality map...")

        #mainMapAreaM2 = (self.mainScale**2) * self.mainMap.rect().width() * self.mainMap.rect().height() / 1000000     # in sqm (even if canvas in GCS)
        if (self.crs.geographicFlag() and mainMapArea > 125) or ((not self.crs.geographicFlag()) and mainMapArea > 1.25 * 10**12):
        #if mainMapAreaM2 > 1.25 * 10**12:   # i.e. > 1.25 million sqkm (approx area of WA is 2.5M sqkm)
            self.localityMap.setTransparency(100)
        else:
            self.createLocalityMap(self.localityMap, self.mainMap)

        self.localityMap.setPreviewMode(QgsComposerMap.Render)
        self.localityMap.updateItem()
        self.cv.composerWindow().statusBar().message("")
        QApplication.restoreOverrideCursor()

    def initialiseScalebars(self, cv, mainMap, scalebars, scalebarPosn, paperSize):
        scale = mainMap.scale()
        relScale = scale
        factor = 1.0

        while relScale >= 10:
            relScale /= 10
            factor *= 10

        while relScale < 1:
            relScale *= 10
            factor /= 10

        # adjust scalebars
        for scalebar in scalebars:
            scalebar.setUnits(QgsComposerScaleBar.Meters)
            scalebar.setComposerMap(mainMap)
            Tools.log(scalebar.style())
            if scalebar.style() != "Numeric":
                # scalebar units
                if scale > 40000:
                    scalebar.setNumMapUnitsPerScaleBarUnit(1000)
                    scalebar.setUnitLabeling("km")
                else:
                    scalebar.setNumMapUnitsPerScaleBarUnit(1)
                    scalebar.setUnitLabeling("m")

                # page and scale specific parameters
                if paperSize[:2] == "A0":
                    numSegments = 5
                    scaleRange = 140
                    if relScale > 8.95:
                        barInterval = 0.25
                    elif relScale >= 3.58:
                        barInterval = 0.1
                    elif relScale >= 1.75:
                        barInterval = 0.05
                    else:
                        barInterval = 0.025

                elif paperSize[:2] == "A1":
                    numSegments = 5
                    scaleRange = 100
                    if relScale > 4.66:
                        barInterval = 0.1
                    elif relScale >= 2.36:
                        barInterval = 0.05
                    elif relScale >= 1.16:
                        barInterval = 0.025
                    else:
                        barInterval = 0.01

                elif paperSize[:2] == "A2":
                    numSegments = 5
                    scaleRange = 70
                    if relScale >= 5.359:
                        barInterval = 0.1
                    elif relScale >= 2.729:
                        barInterval = 0.05
                    elif relScale >= 1.06:
                        barInterval = 0.025
                    else:
                        barInterval = 0.01

                elif paperSize[:2] == "A3":
                    numSegments = 5
                    scaleRange = 50
                    if relScale >= 7.95:
                        barInterval = 0.1
                    elif relScale >= 3.98:
                        barInterval = 0.05
                    elif relScale >= 1.58:
                        barInterval = 0.025
                    else:
                        barInterval = 0.01

                elif paperSize[:2] == "A4" or paperSize[:2] == "A5":    # Initial test for A5; may have to change
                    numSegments = 3
                    scaleRange = 30
                    if relScale >= 9.19:
                        barInterval = 0.1
                    elif relScale >= 4.599:
                        barInterval = 0.05
                    elif relScale >= 2.2:
                        barInterval = 0.025
                    else:
                        barInterval = 0.01

                scalebar.setNumUnitsPerSegment(barInterval * float(factor))

                # apply bar settings
                scalebar.setNumSegments(numSegments)
                scalebar.adjustBoxSize()
                width = scalebar.rect().width()
                while width > scaleRange:
                    numSegments -= 1
                    scalebar.setNumSegments(numSegments)
                    scalebar.adjustBoxSize()
                    width = scalebar.rect().width()
                scalebar.setItemPosition(scalebarPosn.x(), scalebarPosn.y(), QgsComposerItem.Middle)
                return

    def updateScaleBars(self, cv, mainMap, scalebars, scalebarPosn, paperSize):     # NB Also updates grids
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        cv.composerWindow().statusBar().showMessage("Updating scale bars...")
        for grid in mainMap.grids().asList():
            grid.setEnabled(False)
        scale = mainMap.scale()
        
        if int(scale) != int(self.mainScale):   # int is used to avoid triggering via rounding error
            if 0.95 < scale/self.mainScale < 1.05:      # Normally due to panning a map with GCS
                self.restoreScale(mainMap)
            elif 0.85 < scale/self.mainScale < 1.15 and str(scale)[-2:] != "00":   #i.e. where scale has changed by 5 - 15% and is not a round number
                reply = QMessageBox.question(None, "Scale changed", "Scale has changed from " + str(self.mainScale) + \
                        " to " + str(int(scale)) + ".\nWould you like to revert to a scale of " + str(self.mainScale) + "?", 
                        QMessageBox.Yes|QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.restoreScale(mainMap)
                else:
                    self.changeScale(cv, mainMap, scalebars, scalebarPosn, paperSize, scale)
            else:
                self.changeScale(cv, mainMap, scalebars, scalebarPosn, paperSize, scale)
        for grid in mainMap.grids().asList():
            grid.setEnabled(True)
        mainMap.setPreviewMode(QgsComposerMap.Render)
        mainMap.updateCachedImage()
        mainMap.updateItem()        

        QApplication.restoreOverrideCursor()
        cv.composerWindow().statusBar().showMessage("")
        return
        
    def restoreScale(self, mainMap):
        mainMap.extentChanged.disconnect()
        mainMap.setPreviewMode(QgsComposerMap.Rectangle)
        mainMap.setNewScale(self.mainScale)
        mainMap.extentChanged.connect(self.lambdaUpdateLocalityMap)
        mainMap.extentChanged.connect(self.lambdaUpdateScaleBars)
        
    def changeScale(self, cv, mainMap, scalebars, scalebarPosn, paperSize, scale):
        mainMap.setPreviewMode(QgsComposerMap.Rectangle)
        self.mainScale = scale                  # Assume genuine change in scale
        self.initialiseScalebars(cv, mainMap, scalebars, scalebarPosn, paperSize)

        # update grid intervals
        for grid in mainMap.grids().asList():
            if grid.name() in ["East-North Grid", "Lat-Long Graticule"]:
                self.updateGrid(cv, mainMap, grid, grid.name(), grid.style())
                        
    def updateGrid(self, cv, mainMap, grid, gridName, gridStyle):
        cv.composerWindow().statusBar().showMessage("Updating grids...")
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        scale = mainMap.scale()
        # determine relative scale & factor
        relScale = scale
        factor = 1
        eastNorthGrid = None
        latLongGraticule = None
        canvas = qgis.utils.iface.mapCanvas()
        
        while relScale > 10:
            relScale /= 10
            factor *= 10

        while relScale < 1:
            relScale *= 10
            factor /= 10

        # set grid interval
        if relScale > 7:
            gridInterval = 0.50
        elif relScale > 4:
            gridInterval = 0.25
        elif relScale > 2:
            gridInterval = 0.1
        else:
            gridInterval = 0.05
        
        if gridName == "East-North Grid":
            # Get canvas's CRS
            crs = canvas.mapSettings().destinationCrs()
            grid.setCrs(crs)
            gridInterval *= factor
            if gridInterval < 1:
                gridInterval = 1.0
                
        elif gridName == "Lat-Long Graticule":
            # Get canvas's associated GCS
            gcsEPSG = 4283  # default is GDA94
            gcs = canvas.mapSettings().destinationCrs().geographicCRSAuthId()
            if gcs[:4] == "EPSG" and gcs[5:].isnumeric():
                gcsEPSG = int(gcs[5:])
            grid.setCrs(QgsCoordinateReferenceSystem(gcsEPSG, QgsCoordinateReferenceSystem.EpsgCrsId))
            gridInterval *= factor/100000.0
            #get 'precision' of gridInterval, and set annotation precision based on this  (if gridInterval < 1)
            if gridInterval >= 1:
                grid.setAnnotationPrecision(0)
            else:
                if len(str(gridInterval).split(".")) > 1:    # i.e. if grid interval includes decimal point - NB this code is to accommodate e.g. 5 e-05
                    precision = max([len(str(gridInterval).split(".")[1])-3, 0])
                else:
                    precision = int(str(gridInterval).split("e-")[1]) - 4
                grid.setAnnotationPrecision(precision)
        else:   # i.e. if different grid name
            return
        grid.setStyle(gridStyle)
        grid.setIntervalY(gridInterval)
        grid.setIntervalX(gridInterval)
        mainMap.updateItem()
        cv.composerWindow().statusBar().showMessage("")
        QApplication.restoreOverrideCursor()
