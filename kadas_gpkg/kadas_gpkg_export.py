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

from .kadas_gpkg_export_dialog import KadasGpkgExportDialog
from .kadas_gpkg_export_base_class import KadasGpkgExportBase


class KadasGpkgExport(KadasGpkgExportBase):

    def __init__(self, iface):
        KadasGpkgExportBase.__init__(self)
        self.iface = iface

    def run(self):
        dialog = KadasGpkgExportDialog(self.find_local_layers(), self.iface.mainWindow())
        if dialog.exec_() != QDialog.Accepted:
            return

        # Write project to temporary file
        tmpdir = QTemporaryDir()

        gpkg_filename = dialog.getOutputFile()
        selected_layers = dialog.getSelectedLayers()
        gpkg_writefile = gpkg_filename

        if dialog.clearOutputFile():
            gpkg_writefile = tmpdir.filePath(os.path.basename(gpkg_filename))

        # Open database
        try:
            conn = sqlite3.connect(gpkg_writefile)
        except:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("Error"), self.tr("Unable to create or open output file"))
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
        added_layer_ids = []
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
                saveOptions = QgsVectorFileWriter.SaveVectorOptions()
                saveOptions.driverName = 'GPKG'
                saveOptions.layerName = self.safe_name(layer.name())
                saveOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
                saveOptions.fileEncoding = 'utf-8'
                ret = QgsVectorFileWriter.writeAsVectorFormat(
                    layer, gpkg_writefile, saveOptions)
                if ret[0] == 0:
                    added_layer_ids.append(layerid)
                    added_layers_by_source[layer.source()] = layerid
                else:
                    messages.append("%s: %s" % (layer.name(), self.tr("Write failed: error %d (%s)") % (ret[0], ret[1])))
            elif layer.type() == QgsMapLayer.RasterLayer:
                provider = layer.dataProvider()
                writer = QgsRasterFileWriter(gpkg_writefile)
                writer.setOutputFormat('gpkg')
                writer.setCreateOptions(['RASTER_TABLE=%s' % self.safe_name(layer.name()), 'APPEND_SUBDATASET=YES'])
                pipe = QgsRasterPipe()
                pipe.set(provider.clone())

                projector = QgsRasterProjector()
                projector.setCrs(provider.crs(), provider.crs())
                pipe.insert(2, projector)

                ret = writer.writeRaster(pipe, provider.xSize(), provider.ySize(), provider.extent(), provider.crs())
                if ret == 0:
                    added_layer_ids.append(layerid)
                    added_layers_by_source[layer.source()] = layerid
                else:
                    messages.append("%s: %s" % (layer.name(), self.tr("Write failed: error %d") % ret))
        if canceled:
            pdialog.hide()
            QMessageBox.warning(self.iface.mainWindow(), self.tr("GPKG Export"), self.tr("The operation was canceled."))
            conn.rollback()
            return

        project = QgsProject.instance()
        prev_filename = project.fileName()
        prev_dirty = project.isDirty()
        tmpfile = tmpdir.filePath("gpkg_project.qgs")
        project.setFileName(tmpfile)
        additional_resources = {}
        preprocessorId = QgsPathResolver.setPathWriter(lambda path: self.rewriteProjectPaths(path, gpkg_filename, added_layers_by_source, layer_sources, additional_resources))
        project.write()
        QgsPathResolver.removePathWriter(preprocessorId)
        project.setFileName(prev_filename if prev_filename else None)
        project.setDirty(prev_dirty)

        # Parse project and replace data sources if necessary
        parser = ET.XMLParser(strip_cdata=False)
        doc = ET.parse(tmpfile, parser=parser)
        if not doc:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("Error"), self.tr("Invalid project"))
            return

        # Replace layer provider types in project file
        sources = []
        for projectlayerEl in doc.find("projectlayers"):
            layerId = projectlayerEl.find("id").text
            if layerId in added_layer_ids:
                layer = QgsProject.instance().mapLayer(layerId)
                if layer.type() == QgsMapLayer.VectorLayer:
                    projectlayerEl.find("provider").text = "ogr"
                elif layer.type() == QgsMapLayer.RasterLayer:
                    projectlayerEl.find("provider").text = "gdal"

        # Add additional resources
        conn = sqlite3.connect(gpkg_writefile)
        cursor = conn.cursor()
        for path, resource_id in additional_resources.items():
            self.add_resource(cursor, path, resource_id)

        # Write project file to GPKG
        project_xml = ET.tostring(doc.getroot())
        self.write_project(cursor, project_xml)

        conn.commit()
        conn.close()

        if dialog.clearOutputFile():
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

    def rewriteProjectPaths(self, path, gpkg_filename, added_layers_by_source, layer_sources, additional_resources):
        if not path:
            return path
        if path in added_layers_by_source:
            # Datasource newly added to GPKG: rewrite as GPKG path
            layer = QgsProject.instance().mapLayer(added_layers_by_source[path])
            if layer.type() == QgsMapLayer.VectorLayer:
                return "@gpkg_file@|layername=" + self.safe_name(layer.name())
            elif layer.type() == QgsMapLayer.RasterLayer:
                return "GPKG:@gpkg_file@:" + self.safe_name(layer.name())
        elif path and (path.startswith(gpkg_filename) or path.startswith("GPKG:" + gpkg_filename)):
            # Previous GPKG sources: replace GPKG path with placeholder
            return path.replace(gpkg_filename, "@gpkg_file@")
        elif os.path.isfile(path) and not path in layer_sources:
            # Other resource: Add it to resources,
            if not path in additional_resources:
                additional_resources[path] = str(uuid.uuid1()) + os.path.splitext(path)[1]
            return "@qgis_resources@/%s" % additional_resources[path]
        else:
            # No action
            return path

    def add_resource(self, cursor, path, resource_id):
        """ Add a resource file to qgis_resources """
        with open(path, 'rb') as fh:
            blob = fh.read()
            mime_type = mimetypes.MimeTypes().guess_type(path)[0]
            cursor.execute('SELECT count(1) FROM qgis_resources WHERE name=?', (resource_id,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO qgis_resources VALUES(?, ?, ?)', (resource_id, mime_type, sqlite3.Binary(blob)))
            else:
                cursor.execute('UPDATE qgis_resources SET mime_type=?, content=? WHERE name=?', (mime_type, sqlite3.Binary(blob), resource_id))
