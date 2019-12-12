# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *
from qgis.gui import *

from kadas.kadasgui import *

import os
import re
import mimetypes
import sqlite3
import shutil
import uuid
from lxml import etree as ET

from .kadas_gpkg_export_dialog import KadasGpkgExportDialog
from .kadas_gpkg_export_base_class import KadasGpkgExportBase


class KadasGpkgExportByExtent(KadasMapToolSelectRect, KadasGpkgExportBase):

    def __init__(self, iface):
        KadasMapToolSelectRect.__init__(self, iface.mapCanvas())

        self.dialog = KadasGpkgExportDialog(self.find_local_layers(),
                                            iface.mainWindow())
        self.dialog.accepted.connect(self.export)
        self.dialog.rejected.connect(self.close)

        self.iface = iface
        self.setRect(iface.mapCanvas().extent())

    def close(self):
        self.iface.mapCanvas().unsetMapTool(self)

    def activate(self):
        KadasMapToolSelectRect.activate(self)
        self.dialog.show()

    def deactivate(self):
        self.clear()
        KadasMapToolSelectRect.deactivate(self)
        self.dialog.hide()

    def export(self):
        # Write project to temporary file
        tmpdir = QTemporaryDir()

        gpkg_filename = self.dialog.getOutputFile()
        selected_layers = self.dialog.getSelectedLayers()
        gpkg_writefile = gpkg_filename

        if self.dialog.clearOutputFile():
            gpkg_writefile = tmpdir.filePath(os.path.basename(gpkg_filename))

        # Open database
        try:
            conn = sqlite3.connect(gpkg_writefile)
        except:
            QMessageBox.warning(self.iface.mainWindow(),
                                self.tr("Error"),
                                self.tr("Unable to create or open output file"))
            return

        pdialog = QProgressDialog(
            self.tr("Writing %s...") % os.path.basename(gpkg_filename),
            self.tr("Cancel"), 0, 0,  self.iface.mainWindow())
        pdialog.setWindowModality(Qt.WindowModal)
        pdialog.setWindowTitle(self.tr("GPKG Export"))
        pdialog.show()

        cursor = conn.cursor()
        self.init_gpkg(cursor)
        conn.commit()
        conn.close()
        QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        # Collect layer sources
        layer_sources = []
        for layerId, layer in QgsProject.instance().mapLayers().items():
            layer_sources.append(layer.source())

        # Copy all selected local layers to the database
        added_layers_by_source = {}
        canceled = False
        messages = []
        for layerid in selected_layers:
            QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
            if pdialog.wasCanceled():
                canceled = True
                break

            layer = QgsProject.instance().mapLayer(layerid)

            if layer.source() in added_layers_by_source:
                # Don't add the same layer twice
                continue

            if layer.type() == QgsMapLayer.VectorLayer:

                # Skip layers with no features in the specified extent
                if len(list(layer.getFeatures(self.rect()))) == 0:
                    continue
                saveOptions = QgsVectorFileWriter.SaveVectorOptions()
                saveOptions.driverName = 'GPKG'
                saveOptions.layerName = self.safe_name(layer.name())
                saveOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
                saveOptions.fileEncoding = 'utf-8'
                saveOptions.filterExtent = self.rect()
                ret = QgsVectorFileWriter.writeAsVectorFormat(
                    layer, gpkg_writefile, saveOptions)
                if ret[0] == 0:
                    added_layers_by_source[layer.source()] = layerid
                else:
                    messages.append("%s: %s" % (layer.name(), self.tr(
                        "Write failed: error %d (%s)") % (ret[0], ret[1])))
            elif layer.type() == QgsMapLayer.RasterLayer:
                provider = layer.dataProvider()
                writer = QgsRasterFileWriter(gpkg_writefile)
                writer.setOutputFormat('gpkg')
                writer.setCreateOptions(['RASTER_TABLE=%s' % self.safe_name(
                    layer.name()), 'APPEND_SUBDATASET=YES'])
                pipe = QgsRasterPipe()
                pipe.set(provider.clone())

                projector = QgsRasterProjector()
                projector.setCrs(provider.crs(), provider.crs())
                pipe.insert(2, projector)

                ret = writer.writeRaster(pipe, provider.xSize(),
                                         provider.ySize(),
                                         self.rect(),
                                         provider.crs())
                if ret == 0:
                    added_layers_by_source[layer.source()] = layerid
                else:
                    messages.append("%s: %s" % (layer.name(),
                                    self.tr("Write failed: error %d") % ret))
        if canceled:
            pdialog.hide()
            QMessageBox.warning(
                self.iface.mainWindow(),
                self.tr("GPKG Export"),
                self.tr("The operation was canceled."))
            conn.rollback()
            return

        if self.dialog.clearOutputFile():
            try:
                os.remove(gpkg_filename)
            except:
                pass
            try:
                shutil.move(gpkg_writefile, gpkg_filename)
            except:
                QMessageBox.warning(self.iface.mainWindow(), self.tr("Error"), self.tr("Unable to create output file"))
                return

        pdialog.hide()
        self.iface.messageBar().pushMessage(
            self.tr("GPKG export completed"), "", Qgis.Info, 5)

        if messages:
            QMessageBox.warning(
                self.iface.mainWindow(),
                self.tr("GPKG Export"),
                self.tr("The following layers were not exported to the GeoPackage:\n- %s") % "\n- ".join(messages))
