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

    def __init__(self, iface):
        QObject.__init__(self)
        self.iface = iface

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

    def safe_name(self, name):
        return re.sub(r"\W", "", name)
