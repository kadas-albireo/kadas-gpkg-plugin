# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

import logging
import glob
import os
import mimetypes
import sqlite3
import shutil
import subprocess
import sys
import tempfile
from xml.etree import ElementTree as ET

from kadas_gpkg_export_dialog import KadasGpkgExportDialog


class KadasGpkgExport(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface

    def run(self):
        dialog = KadasGpkgExportDialog(self.find_local_layers(), self.iface.mainWindow())
        if dialog.exec_() != QDialog.Accepted:
            return


        # Write project to temporary file
        tmpdir = tempfile.mkdtemp()

        gpkg_filename = dialog.getOutputFile()
        local_layers = dialog.getSelectedLayers()
        gpkg_writefile = gpkg_filename

        if dialog.clearOutputFile():
            gpkg_writefile = os.path.join(tmpdir, os.path.basename(gpkg_filename))

        # Open database
        try:
            conn = sqlite3.connect(gpkg_writefile)
        except:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("Error"), self.tr("Unable to create or open output file"))
            return

        cursor = conn.cursor()
        self.init_gpkg(cursor)

        # Look for local layers which are not already in the GPKG
        new_gpkg_layers = []

        # Copy all local layers to the database
        canceled = False
        messages = []
        for layerid in local_layers:
            layer = QgsMapLayerRegistry.instance().mapLayer(layerid)
            if layer.type() == QgsMapLayer.VectorLayer:
                saveOptions = QgsVectorFileWriter.SaveVectorOptions()
                saveOptions.driverName = 'GPKG'
                saveOptions.layerName = layer.name()
                saveOptions.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteLayer
                saveOptions.fileEncoding = 'utf-8'
                ret = QgsVectorFileWriter.writeAsVectorFormat(layer, gpkg_writefile, saveOptions)
                if ret == 0:
                    new_gpkg_layers.append(layerid)
                else:
                    messages.append("%s: %s" % (layer.name(), self.tr("Write failed")))
            elif layer.type() == QgsMapLayer.RasterLayer:
                filename = layer.source()
                cmd = ["gdal_translate", "-of", "GPKG", "-co", "APPEND_SUBDATASET=YES", filename, gpkg_writefile]
                creationFlags = 0
                if sys.platform == 'win32':
                    creationFlags = 0x08000000  # CREATE_NO_WINDOW
                process = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, creationflags=creationFlags)
                pdialog = QProgressDialog(self.tr("Writing %s...") % layer.name(), self.tr("Cancel"), 0, 0,  self.iface.mainWindow())
                pdialog.setWindowModality(Qt.WindowModal)
                pdialog.setWindowTitle(self.tr("GPKG Export"))
                timer = QTimer()
                timer.setSingleShot(True)
                # Poll every 100ms until done
                while process.returncode is None:
                    process.poll()
                    loop = QEventLoop()
                    timer.timeout.connect(loop.quit)
                    timer.start(100)
                    loop.exec_()
                    if pdialog.wasCanceled():
                        canceled = True
                        break
                if canceled:
                    process.kill()
                    break
                elif process.returncode == 0:
                    new_gpkg_layers.append(layerid)
                else:
                    messages.append("%s: %s" % (layer.name(), self.tr("Write failed. Does the GeoPackage already contain a table with the same name as an exported layer?")))
                pdialog.reset()
                # FIXME: Use QgsRasterFileWriter
                #provider = layer.dataProvider()
                #writer = QgsRasterFileWriter(gpkg_writefile)
                #writer.setOutputFormat('gpkg')
                #writer.setCreateOptions(['RASTER_TABLE=%s' % layer.name(), 'APPEND_SUBDATASET=YES'])
                #pipe = QgsRasterPipe()
                #pipe.set(provider.clone())

                #projector = QgsRasterProjector()
                #projector.setCRS(provider.crs(), provider.crs())
                #pipe.insert(2, projector)

                #writer.writeRaster(pipe, provider.xSize(), provider.ySize(), provider.extent(), provider.crs())
                #new_gpkg_layers.append(layerid)

        if canceled:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("GPKG Export"), self.tr("The operation was canceled."))
            conn.rollback()
            return

        project = QgsProject.instance()
        prev_filename = project.fileName()
        prev_dirty = project.isDirty()
        tmpfile = os.path.join(tmpdir, "qgpkg.qgs")
        project.setFileName(tmpfile)
        project.write()
        project.setFileName(prev_filename if prev_filename else None)
        project.setDirty(prev_dirty)

        # Parse project and replace data sources if necessary
        doc = ET.parse(tmpfile)
        if not doc:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("Error"), self.tr("Invalid project"))
            return

        # Replace layer sources in project file if neccessary
        sources = []
        for projectlayerEl in doc.find("projectlayers"):
            layerId = projectlayerEl.find("id").text
            datasource = projectlayerEl.find("datasource")
            if layerId in new_gpkg_layers:
                layer = QgsMapLayerRegistry.instance().mapLayer(layerId)
                if local_layers[layerId] == QgsMapLayer.VectorLayer:
                    datasource.text = "@gpkg_file@|layername=" + layer.name()
                    projectlayerEl.find("provider").text = "ogr"
                elif local_layers[layerId] == QgsMapLayer.RasterLayer:
                    datasource.text = "GPKG:@gpkg_file@:" + layer.name()
                    projectlayerEl.find("provider").text = "gdal"
            elif datasource.text.startswith(gpkg_filename) or datasource.text.startswith("GPKG:" + gpkg_filename):
                datasource.text = datasource.text.replace(gpkg_filename, "@gpkg_file@")


        ### Search for referenced images in project file and add them to the GPKG
        images = {}
        # Composer images
        for composer in doc.findall("Composer"):
            for composition in composer:
                for composer_picture in composition.findall("ComposerPicture"):
                    img = composer_picture.attrib['file']
                    if not img.startswith(":"):
                        gpkg_path = '@qgis_resources@/%s' % os.path.basename(img)
                        images[gpkg_path] = self.ensure_absolute(tmpdir, img)
                        composer_picture.set('file', gpkg_path)

        # Image annotation items
        for annotation in doc.findall("GeoImageAnnotationItem"):
            img = annotation.attrib['file']
            if not img.startswith(":"):
                gpkg_path = '@qgis_resources@/%s' % os.path.basename(img)
                images[gpkg_path] = self.ensure_absolute(tmpdir, img)
                annotation.set('file', gpkg_path)

        # Add images to GPKG
        for gpkg_path, abspath in images.iteritems():
            self.add_resource(cursor, gpkg_path, abspath)

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
                shutil.rmtree(tmpdir)
                return

        shutil.rmtree(tmpdir)

        self.iface.messageBar().pushMessage( self.tr( "GPKG Export Completed" ), "", QgsMessageBar.INFO, 5 )

        if messages:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("GPKG Export"), self.tr("The following layers were not exported to the GeoPackage:\n- %s") % "\n- ".join(messages))

    def find_local_layers(self):
        local_layers = {}
        local_providers = ["delimitedtext", "gdal", "gpx", "mssql", "ogr",
        "postgres", "spatialite"]

        for layerid, layer in QgsMapLayerRegistry.instance().mapLayers().iteritems():
            provider = "unknown"
            if layer.type() == QgsMapLayer.VectorLayer or layer.type() == QgsMapLayer.RasterLayer:
                provider = layer.dataProvider().name()
            elif layer.type() == QgsMapLayer.PluginLayer:
                provider = "plugin"

            # Local layers which are not already saved in the gpkg databse
            if provider in local_providers:
                local_layers[layer.id()] = layer.type()

        return local_layers

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

        # Create extension
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS gpkg_extensions (table_name TEXT,column_name TEXT,extension_name TEXT NOT NULL,definition TEXT NOT NULL,scope TEXT NOT NULL,CONSTRAINT ge_tce UNIQUE (table_name, column_name, extension_name))')
        extension_record = (None, None, 'qgis',
                            'http://github.com/pka/qgpkg/blob/master/'
                            'qgis_geopackage_extension.md',
                            'read-write')
        cursor.execute('SELECT count(1) FROM gpkg_extensions WHERE extension_name=?', (extension_record[2],))
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO gpkg_extensions VALUES (?,?,?,?,?)', extension_record)

        # Create qgis_projects table
        cursor.execute('CREATE TABLE IF NOT EXISTS qgis_projects (name TEXT PRIMARY KEY, xml TEXT NOT NULL)')

        # Create qgis_resources table
        cursor.execute('CREATE TABLE IF NOT EXISTS qgis_resources (name TEXT PRIMARY KEY, mime_type TEXT NOT NULL, content BLOB NOT NULL)')

    def write_project(self, cursor, project_xml):
        """ Write or update qgis project """
        project_name = "qgpkg"
        cursor.execute('SELECT count(1) FROM qgis_projects WHERE name=?', (project_name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO qgis_projects VALUES (?,?)', (project_name, project_xml))
        else:
            cursor.execute('UPDATE qgis_projects SET xml=? WHERE name=?', (project_xml, project_name))

    def add_resource(self, cursor, gpkg_path, abspath):
        """ Add a resource file to qgis_resources """
        with open(abspath, 'rb') as fh:
            blob = fh.read()
            mime_type = mimetypes.MimeTypes().guess_type(abspath)[0]
            cursor.execute('SELECT count(1) FROM qgis_resources WHERE name=?', (gpkg_path,))
            if cursor.fetchone()[0] == 0:
                cursor.execute('INSERT INTO qgis_resources VALUES(?, ?, ?)', (gpkg_path, mime_type, sqlite3.Binary(blob)))
            else:
                cursor.execute('UPDATE qgis_resources SET mime_type=?, content=? WHERE name=?', (gpkg_path, mime_type, sqlite3.Binary(blob)))

    def ensure_absolute(self, base, path):
        if not os.path.isabs(path):
            return os.path.normpath(os.path.join(base, path))
        else:
            return path
