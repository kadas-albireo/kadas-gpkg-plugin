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
import tempfile
from xml.etree import ElementTree as ET


class KadasGpkgImport(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface

    def run(self):

        if QgsProject.instance().isDirty():
            ret = QMessageBox.question(self.iface.mainWindow(), self.tr("Save project?"), self.tr("The project has unsaved changes. Do you want to save them before proceeding?"), QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel, QMessageBox.Cancel)
            if ret == QMessageBox.Cancel:
                return
            elif ret == QMessageBox.Yes and not self.iface.fileSave():
                return

        lastDir = QSettings().value("/UI/lastImportExportDir", ".")
        gpkg_filename = QFileDialog.getOpenFileName(self.iface.mainWindow(), self.tr("GPKG Import"), lastDir, self.tr("GPKG Database (*.gpkg)"))[0]

        if not gpkg_filename:
            return

        QSettings().setValue("/UI/lastImportExportDir", os.path.dirname(gpkg_filename))

        self.iface.newProject(False)
        # Open database
        try:
            conn = sqlite3.connect(gpkg_filename)
        except:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("Error"), self.tr("Unable to open %s") % gpkg_filename)
            return

        cursor = conn.cursor()

        # Extract project and resources to temporary dir
        xml = self.read_project(cursor)
        try:
            doc = ET.fromstring(xml)
        except:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("Error"), self.tr("No valid project was found in %s") % gpkg_filename)
            return

        ### Create temporary folder
        tmpdir = tempfile.mkdtemp()

        ### Extract project resources
        ### Composer images
        for composer in doc.findall("Composer"):
            for composition in composer:
                for composer_picture in composition.findall("ComposerPicture"):
                    img = composer_picture.attrib['file']
                    if img.startswith("@qgis_resources@"):
                        tmppath = self.extract_resource(cursor, tmpdir, img)
                        composer_picture.set('file', tmppath)

        ### Image annotation items
        for annotation in doc.findall("GeoImageAnnotationItem"):
            img = annotation.attrib['file']
            if img.startswith("@qgis_resources@"):
                tmppath = self.extract_resource(cursor, tmpdir, img)
                annotation.set('file', tmppath)

        ### SVG annotation items
        for annotation in doc.findall("SVGAnnotationItem"):
            img = annotation.attrib['file']
            if img.startswith("@qgis_resources@"):
                tmppath = self.extract_resource(cursor, tmpdir, img)
                annotation.set('file', tmppath)

        ### Fixup layer paths
        for maplayerEl in doc.find("projectlayers").findall("maplayer"):
            datasource = maplayerEl.find("datasource")
            try:
                datasource.text = datasource.text.replace("@gpkg_file@", gpkg_filename)
            except:
                pass


        ### Write project
        xml = ET.tostring(doc)
        output = os.path.join(tmpdir, self.tr("Imported GPKG Project") + ".qgs")
        with open(output, "w") as fh:
            fh.write(xml)

        # Set project
        self.iface.addProject(output)
        QgsProject.instance().setFileName(None)
        QgsProject.instance().setDirty(True)

        self.iface.messageBar().pushMessage( self.tr( "GPKG Import Completed" ), "", QgsMessageBar.INFO, 5 );

    def read_project(self, cursor):
        """ Read qgis project """
        project_name = "qgpkg"
        try:
            cursor.execute('SELECT xml FROM qgis_projects WHERE name=?', (project_name,))
        except sqlite3.OperationalError:
            return None
        qgis_projects = cursor.fetchone()
        if qgis_projects is None:
            return None
        else:
            return qgis_projects[0]

    def extract_resource(self, cursor, outputdir, gpkg_path):
        """ Extract a resource file from qgis_resources """
        try:
            cursor.execute('SELECT content FROM qgis_resources WHERE name=?', (gpkg_path,))
        except:
            return None
        output = os.path.join(outputdir, os.path.basename(gpkg_path))
        with open(output, 'wb') as fh:
            fh.write(cursor.fetchone()[0])
        return output
