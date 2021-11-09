from qgis.core import *
from ...tools import Tools

class CRSHelper:

    def __init__(self, crs):
        self.datum = ""
        self.projection = ""
        self.geogcsn = ""
        self.projcsn = ""
        self.prjfilename = ""

        self.crs = crs
        self.authid = str(crs.authid())
        self.proj4 = str(crs.toProj4())
        self.projected = not crs.geographicFlag()

        if self.authid == "EPSG:4203":
            self.datum = "AGD84"
            self.projection = ""
            self.geogcsn = "AGD84"
            self.projcsn = None
            self.prjfilename = "4203.prj"

        elif self.authid == "EPSG:4283":
            self.datum = "GDA94"
            self.projection = ""
            self.geogcsn = "GDA94"
            self.projcsn = None
            self.prjfilename = "4283.prj"

        elif self.authid == "EPSG:4326":
            self.datum = "WGS84"
            self.projection = ""
            self.geogcsn = "WGS84"
            self.projcsn = None
            self.prjfilename = "4326.prj"
            
        elif self.authid == "EPSG:3857":
            self.datum = "WGS84"
            self.projection = "Web Mercator"
            self.geogcsn = "WGS84"
            self.projcsn = "WGS_1984_Web_Mercator"
            self.prjfilename = "7483.prj"            

        elif self.authid[:8] == "EPSG:203":
            zone = str(self.authid[-2:])
            self.datum = "AGD84"
            self.projection = "AMG Zone " + zone
            self.geogcsn = "GCS_Australian_1984"
            self.projcsn = "AGD_1984_AMG_Zone_" + zone
            self.prjfilename = "203" + zone + ".prj"

        elif self.authid[:8] == "EPSG:283":
            zone = str(self.authid[-2:])
            self.datum = "GDA94"
            self.projection = "MGA Zone " + zone
            self.geogcsn = "GCS_GDA_1994"
            self.projcsn = "GDA_1994_MGA_Zone_" + zone
            self.prjfilename = "283" + zone + ".prj"

        elif self.proj4 == ("+proj=aea +lat_1=-17.5 +lat_2=-31.5 +lat_0=0 " +
                            "+lon_0=121 +x_0=5000000 +y_0=10000000 " +
                            "+ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"):
            self.datum = "GDA94"
            self.projection = "{} Albers WA".format(Tools.get_dept_acronym())
            self.geogcsn = "GCS_GDA_1994"
            self.projcsn = "Albers_Equal_Conic_Area_GDA_Western_Australia"
            self.prjfilename = "AlbersGDA94.prj"

        elif self.proj4 == ("+proj=aea +lat_1=-17.5 +lat_2=-31.5 +lat_0=0 " +
                            "+lon_0=121 +x_0=5000000 +y_0=10000000 +ellps=aust_SA " +
                            "+towgs84=-134,-48,149,0,0,0,0 +units=m +no_defs"):
            self.datum = "AGD84"
            self.projection = "{} Albers WA".format(Tools.get_dept_acronym())
            self.geogcsn = "GCS_Australian_1984"
            self.projcsn = "Albers_Equal_Conic_Area_AGD_Western_Australia"
            self.prjfilename = "AlbersAGD84.prj"

        else:
            description = "unrecognised"
            if self.authid[:3] != "USER":
                description = str(crs.description())
            self.datum = description
            self.geogcsn = description
            if self.projected:
                self.projection = description
                self.projcsn = description
            else:
                self.projection = ""
                self.projcsn = None

    def friendlyName(self):
        if len(self.projection) > 0:
            name = self.projection
            if len(self.datum) > 0:
                name += " " + self.datum
        else:
            if len(self.datum) > 0:
                name = self.datum
        if name == "unrecognised unrecognised":
            name = "unrecognised"
        return name
