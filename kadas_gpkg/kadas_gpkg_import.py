# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *
from qgis.gui import *

import logging
import glob
import os
import mimetypes
import sqlite3
import shutil
import tempfile


class KadasGpkgImport(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface

    def run(self, gpkg_filename=None):

        if QgsProject.instance().isDirty():
            ret = QMessageBox.question(self.iface.mainWindow(), self.tr("Save project?"), self.tr("The project has unsaved changes. Do you want to save them before proceeding?"), QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel, QMessageBox.Cancel)
            if ret == QMessageBox.Cancel:
                return
            elif ret == QMessageBox.Yes and not self.iface.fileSave():
                return

        if not gpkg_filename:
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

        # Create temporary folder
        tmpdir = tempfile.mkdtemp()

        # Write project to temporary dir
        xml = self.read_project(cursor)
        output = os.path.join(tmpdir, "gpkg_project.qgs")
        with open(output, "wb") as fh:
            if isinstance(xml, str):
                fh.write(xml.encode('utf-8'))
            else:
                fh.write(xml)

        # Read project, adjust paths and extract resources as necessary
        extracted_resources = {}
        preprocessorId = QgsPathResolver.setPathPreprocessor(lambda path: self.readProjectPaths(path, cursor, gpkg_filename, tmpdir, extracted_resources))

        self.iface.addProject(output)
        QgsProject.instance().setFileName(None)
        QgsProject.instance().setDirty(True)

        QgsPathResolver.removePathPreprocessor(preprocessorId)

        self.iface.messageBar().pushMessage(
            self.tr("GPKG import completed"), "", Qgis.Info, 5)

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

    def readProjectPaths(self, path, cursor, gpkg_filename, tmpdir, extracted_resources):
        if not path:
            return path
        path = path.replace("@gpkg_file@", gpkg_filename)
        if path.startswith("@qgis_resources@"):
            resource_id = path.replace("@qgis_resources@/", "")
            if resource_id in extracted_resources:
                path = extracted_resources[resource_id]
            else:
                path = self.extract_resource(cursor, tmpdir, resource_id)
                extracted_resources[resource_id] = path
        return path

    def extract_resource(self, cursor, outputdir, resource_id):
        """ Extract a resource file from qgis_resources """
        try:
            cursor.execute('SELECT content FROM qgis_resources WHERE name=?', (resource_id,))
        except:
            return None
        output = os.path.join(outputdir, resource_id)
        with open(output, 'wb') as fh:
            fh.write(cursor.fetchone()[0])
        return output
