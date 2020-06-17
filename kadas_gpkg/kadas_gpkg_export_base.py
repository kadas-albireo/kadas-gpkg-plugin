# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *
from qgis.gui import *

import os
import re
import mimetypes
import sqlite3
import shutil
import uuid
from lxml import etree as ET
from abc import abstractmethod


class KadasGpkgExportBase(QObject):

    def __init__(self):
        QObject.__init__(self)

    @abstractmethod
    def run(self):
        pass

    def init_gpkg(self, cursor):
        """ Init geopackage with tables specified in qgis_geopackage_extension """
        # Create gpkg_spatial_ref_sys table
        cursor.execute("""CREATE TABLE IF NOT EXISTS gpkg_spatial_ref_sys (
                srs_name TEXT NOT NULL,
                srs_id INTEGER NOT NULL PRIMARY KEY,
                organization TEXT NOT NULL,
                organization_coordsys_id INTEGER NOT NULL,
                definition  TEXT NOT NULL,
                description TEXT
        )""")
        # Add undefined spatial reference
        cursor.execute('SELECT count(1) FROM gpkg_spatial_ref_sys WHERE srs_id=0')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO gpkg_spatial_ref_sys VALUES (?,?,?,?,?,?)', ("Undefined geographic SRS", 0, "NONE", 0, "undefined", "undefined"))

        # Create gpkg_contents table
        cursor.execute("""CREATE TABLE IF NOT EXISTS gpkg_contents (
                table_name TEXT NOT NULL PRIMARY KEY,
                data_type TEXT NOT NULL,
                identifier TEXT UNIQUE,
                description TEXT DEFAULT '',
                last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
                min_x DOUBLE, min_y DOUBLE,
                max_x DOUBLE, max_y DOUBLE,
                srs_id INTEGER,
                CONSTRAINT fk_gc_r_srs_id FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id)
        )""")

    def write_local_layers(self, selected_layers, gpkg_writefile, pdialog, added_layer_ids, added_layers_by_source, messages, filterExtent=None, filterExtentCrs=None):
        canceled = False
        for layerid in selected_layers:
            QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
            if pdialog.wasCanceled():
                canceled = True
                break

            layer = QgsProject.instance().mapLayer(layerid)

            if layer.source() in added_layers_by_source:
                # Don't add the same layer twice
                continue

            layerFilterExtent = None
            if filterExtent and filterExtentCrs and not filterExtent.isNull():
                layerFilterExtent = QgsCoordinateTransform(filterExtentCrs, layer.crs(), QgsProject.instance()).transformBoundingBox(filterExtent)
                if not layer.extent().intersects(layerFilterExtent):
                    continue

            if layer.type() == QgsMapLayer.VectorLayer:
                pdialog.setRange(0, 100)
                pdialog.setLabelText(self.tr("Writing %s") % layer.name())
                feedback = QgsFeedback()
                feedback.progressChanged.connect(lambda prog: self.updateProgress(prog, pdialog))
                pdialog.canceled.connect(feedback.cancel)

                saveOptions = QgsVectorFileWriter.SaveVectorOptions()
                saveOptions.driverName = 'GPKG'
                saveOptions.layerName = self.safe_name(layer.name())
                saveOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
                saveOptions.fileEncoding = 'utf-8'
                saveOptions.feeedback = feedback
                if layerFilterExtent:
                    saveOptions.filterExtent = layerFilterExtent
                ret = QgsVectorFileWriter.writeAsVectorFormat(
                    layer, gpkg_writefile, saveOptions)
                if ret[0] == 0:
                    added_layer_ids.append(layerid)
                    added_layers_by_source[layer.source()] = layerid
                else:
                    messages.append("%s: %s" % (layer.name(), self.tr(
                        "Write failed: error %d (%s)") % (ret[0], ret[1])))
            elif layer.type() == QgsMapLayer.RasterLayer:
                pdialog.setRange(0, 100)
                pdialog.setLabelText(self.tr("Writing %s") % layer.name())
                feedback = QgsRasterBlockFeedback()
                feedback.progressChanged.connect(lambda prog: self.updateProgress(prog, pdialog))
                pdialog.canceled.connect(feedback.cancel)

                provider = layer.dataProvider()
                writer = QgsRasterFileWriter(gpkg_writefile)
                writer.setBuildPyramidsFlag(QgsRaster.PyramidsFlagYes)
                writer.setOutputFormat('gpkg')
                writer.setCreateOptions(['RASTER_TABLE=%s' % self.safe_name(
                    layer.name()), 'APPEND_SUBDATASET=YES'])
                pipe = QgsRasterPipe()
                pipe.set(provider.clone())

                projector = QgsRasterProjector()
                projector.setCrs(provider.crs(), provider.crs())
                pipe.insert(2, projector)

                exportExtent = provider.extent()
                if layerFilterExtent:
                    exportExtent = layerFilterExtent

                ret = writer.writeRaster(pipe, provider.xSize(),
                                         provider.ySize(),
                                         exportExtent,
                                         provider.crs(), feedback)
                if ret == 0:
                    added_layer_ids.append(layerid)
                    added_layers_by_source[layer.source()] = layerid
                else:
                    messages.append("%s: %s" % (layer.name(),
                                    self.tr("Write failed: error %d") % ret))
        return not canceled and not pdialog.wasCanceled()

    def safe_name(self, name):
        return re.sub(r"\W", "", name)

    def updateProgress(self, progress, pdialog):
        pdialog.setValue(round(progress))
        QApplication.processEvents()
