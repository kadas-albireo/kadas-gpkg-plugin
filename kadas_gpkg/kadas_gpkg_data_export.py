# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from qgis.core import *
from qgis.gui import *

from kadas.kadasgui import *

import os
import sqlite3
import shutil

from .kadas_gpkg_export_base import KadasGpkgExportBase
from .ui_kadas_gpkg_data_export_dialog import Ui_KadasGpkgDataExportDialog


class KadasGpkgDataExportDialog(QDialog):

    def __init__(self, parent, tool, iface):
        QDialog.__init__(self, parent)
        self.tool = tool
        self.iface = iface

        self.ui = Ui_KadasGpkgDataExportDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.ui.lineEditXMin.setValidator(QDoubleValidator())
        self.ui.lineEditYMin.setValidator(QDoubleValidator())
        self.ui.lineEditXMax.setValidator(QDoubleValidator())
        self.ui.lineEditYMax.setValidator(QDoubleValidator())

        self.ui.buttonSelectFile.clicked.connect(self.__selectOutputFile)
        self.ui.checkBoxClear.toggled.connect(self.__updateLocalLayerList)
        self.ui.groupBoxExtent.toggled.connect(self.__extentToggled)
        self.tool.rectChanged.connect(self.__extentChanged)
        self.ui.lineEditXMin.textEdited.connect(self.__extentEdited)
        self.ui.lineEditYMin.textEdited.connect(self.__extentEdited)
        self.ui.lineEditXMax.textEdited.connect(self.__extentEdited)
        self.ui.lineEditYMax.textEdited.connect(self.__extentEdited)

    def __extentToggled(self, active):
        if active:
            self.tool.setRect(self.iface.mapCanvas().extent())
        else:
            self.tool.clear()

    def __extentChanged(self, extent):
        if not extent.isNull():
            fmt = "%.3f" if self.iface.mapCanvas().mapSettings().mapUnits() == QgsUnitTypes.DistanceDegrees else "%.0f"
            self.ui.lineEditXMin.setText(fmt % extent.xMinimum())
            self.ui.lineEditYMin.setText(fmt % extent.yMinimum())
            self.ui.lineEditXMax.setText(fmt % extent.xMaximum())
            self.ui.lineEditYMax.setText(fmt % extent.yMaximum())
        else:
            self.ui.lineEditXMin.setText("")
            self.ui.lineEditYMin.setText("")
            self.ui.lineEditXMax.setText("")
            self.ui.lineEditYMax.setText("")

    def __extentEdited(self):
        xmin = float(self.ui.lineEditXMin.text())
        ymin = float(self.ui.lineEditYMin.text())
        xmax = float(self.ui.lineEditXMax.text())
        ymax = float(self.ui.lineEditYMax.text())
        self.tool.setRect(QgsRectangle(xmin, ymin, xmax, ymax))

    def __selectOutputFile(self):
        lastDir = QSettings().value("/UI/lastImportExportDir", ".")
        filename = QFileDialog.getSaveFileName(self, self.tr("Select GPKG File..."), lastDir, self.tr("GPKG Database (*.gpkg)"), "", QFileDialog.DontConfirmOverwrite)[0]

        if not filename:
            return

        if not filename.lower().endswith(".gpkg"):
            filename += ".gpkg"

        QSettings().setValue("/UI/lastImportExportDir", os.path.dirname(filename))
        self.outputGpkg = filename
        self.ui.lineEditOutputFile.setText(filename)

        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(filename is not None)
        self.__updateLocalLayerList()

    def __updateLocalLayerList(self):
        self.ui.listWidgetLayers.updateLayerList(self.ui.lineEditOutputFile.text() if not self.ui.checkBoxClear.isChecked() else None)

    def outputFile(self):
        return self.ui.lineEditOutputFile.text()

    def clearOutputFile(self):
        return self.ui.checkBoxClear.isChecked()

    def selectedLayers(self):
        return self.ui.listWidgetLayers.getSelectedLayers()

    def buildPyramids(self):
        return self.ui.checkBoxPyramids.isChecked()


class KadasGpkgDataExport(KadasMapToolSelectRect, KadasGpkgExportBase):

    def __init__(self, iface):
        KadasMapToolSelectRect.__init__(self, iface.mapCanvas())
        self.iface = iface

        self.dialog = KadasGpkgDataExportDialog(iface.mainWindow(), self, iface)
        self.dialog.accepted.connect(self.export)
        self.dialog.rejected.connect(self.close)
        self.deactivated.connect(self.dialog.reject)

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

        gpkg_filename = self.dialog.outputFile()
        selected_layers = self.dialog.selectedLayers()
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
            self.close()
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
        messages = []
        if not self.write_local_layers(selected_layers, gpkg_writefile, pdialog, added_layer_ids, added_layers_by_source, messages, self.dialog.buildPyramids(), self.rect(), self.iface.mapCanvas().mapSettings().destinationCrs()):
            pdialog.hide()
            QMessageBox.warning(self.iface.mainWindow(), self.tr("GPKG Export"), self.tr("The operation was canceled."))
            return

        if not added_layer_ids:
            pdialog.hide()
            QMessageBox.warning(self.iface.mainWindow(), self.tr("GPKG Export"), self.tr("No data was exported."))
            self.close()
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
                self.close()
                return

        pdialog.hide()
        self.iface.messageBar().pushMessage(
            self.tr("GPKG export completed"), "", Qgis.Info, 5)

        if messages:
            QMessageBox.warning(
                self.iface.mainWindow(),
                self.tr("GPKG Export"),
                self.tr("The following layers were not exported to the GeoPackage:\n- %s") % "\n- ".join(messages))

        self.close()
