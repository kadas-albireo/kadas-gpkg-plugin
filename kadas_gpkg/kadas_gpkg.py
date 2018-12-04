# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import sys

import resources
from kadas_gpkg_export import KadasGpkgExport
from kadas_gpkg_import import KadasGpkgImport


class KadasGpkg(QObject):

    def __init__(self, iface):
        QObject.__init__(self)

        self.iface = iface
        self.offlineService = None

        # initialize locale
        self.locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            os.path.dirname(__file__),
            'i18n',
            'kadas_gpkg_{}.qm'.format(self.locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)


    def initGui(self):

        self.menu = QMenu()

        self.exportShortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_E, Qt.CTRL + Qt.Key_G), self.iface.mainWindow())
        self.exportShortcut.activated.connect(self.__exportGpkg)
        self.exportAction = QAction(self.tr("Export GPKG"))
        self.exportAction.triggered.connect(self.__exportGpkg)
        self.menu.addAction(self.exportAction)

        self.importShortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_I, Qt.CTRL + Qt.Key_G), self.iface.mainWindow())
        self.importShortcut.activated.connect(self.__importGpkg)
        self.importAction = QAction(self.tr("Import GPKG"))
        self.importAction.triggered.connect(self.__importGpkg)
        self.menu.addAction(self.importAction)

        self.iface.addActionMenu(self.tr("GPKG"), QIcon(":/plugins/KADASGpkg/icons/gpkg.png"), self.menu, self.iface.PLUGIN_MENU, self.iface.NO_TOOLBAR, self.iface.MAPS_TAB)

    def unload(self):
        pass

    def __importGpkg(self):
        KadasGpkgImport(self.iface).run()

    def __exportGpkg(self):
        KadasGpkgExport(self.iface).run()
