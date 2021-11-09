# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGISTools2
                                 A QGIS plugin
 DPAW Tools for QGIS v 2.x
                             -------------------
        begin                : 2014-08-15
        copyright            : (C) 2014 by GIS Apps, Dept of Parks and Wildlife
        email                : Patrick.Maslen@dpaw.wa.gov.au
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

def classFactory(iface):
    # store plugin directory for later reference
    import os
    from dpaw.gis.qgis.tools import Tools
    Tools.setPluginPath(os.path.dirname(os.path.abspath(__file__)))

    # load QGISTools2 class from file QGISTools2
    from qgistools2 import QGISTools2
    return QGISTools2(iface)
