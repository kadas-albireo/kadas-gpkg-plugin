from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import re

from qgis.core import *

from ui_kadas_gpkg_export_dialog import Ui_GPKGExportDialog


class KadasGpkgExportDialog(QDialog):

    LayerIdRole = Qt.UserRole + 1
    LayerTypeRole = Qt.UserRole + 2
    LayerSizeRole = Qt.UserRole + 3
    WARN_SIZE = 50 * 1024 * 1024

    def __init__(self, layers, parent):
        QDialog.__init__(self, parent)
        self.layers = layers
        self.outputGpkg = None
        self.ui = Ui_GPKGExportDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.ui.buttonSelectFile.clicked.connect(self.__selectOutputFile)

        # Populate layer selection list
        reg = QgsMapLayerRegistry.instance()
        for layerid in self.layers:
            layer = reg.mapLayer(layerid)
            if not layer:
                continue
            filename = layer.source()
            # Strip options from <filename>|options
            pos = filename.find("|")
            if pos >= 0:
                filename = filename[:pos]
            # Remove vsi prefix
            if filename.startswith("/vsi"):
                filename = re.sub(r"/vsi\w+/", "", filename)
                while not os.path.isfile(filename):
                    newfilename = os.path.dirname(filename)
                    if newfilename == filename:
                        filename = None
                        break
                    filename = newfilename
                if not filename:
                    continue

            filesize = os.path.getsize(filename)
            item = QListWidgetItem(layer.name())
            item.setData(KadasGpkgExportDialog.LayerIdRole, layerid)
            item.setData(KadasGpkgExportDialog.LayerTypeRole, self.layers[layerid])
            item.setData(KadasGpkgExportDialog.LayerSizeRole, filesize)
            if filesize < KadasGpkgExportDialog.WARN_SIZE:
                item.setCheckState(Qt.Checked)
                item.setIcon(QIcon())
            else:
                item.setCheckState(Qt.Unchecked)
                item.setIcon(QIcon(":/images/themes/default/mIconWarn.png"))

            self.ui.listWidgetLayers.addItem(item)

    def __selectOutputFile(self):
        lastDir = QSettings().value("/UI/lastImportExportDir", ".")
        filename = QFileDialog.getSaveFileName(self, self.tr("Select GPKG Databse..."), lastDir, self.tr("GPKG Database (*.gpkg)"))[0]

        if not filename:
            return

        QSettings().setValue("/UI/lastImportExportDir", os.path.dirname(filename))
        self.outputGpkg = filename
        self.ui.lineEditOutputFile.setText(self.outputGpkg)

        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(self.outputGpkg is not None)

        # Update layer list
        reg = QgsMapLayerRegistry.instance()
        for i in range(0, self.ui.listWidgetLayers.count()):
            item = self.ui.listWidgetLayers.item(i)
            layerid = item.data(KadasGpkgExportDialog.LayerIdRole)
            layer = reg.mapLayer(layerid)
            # Disable layers already in GPKG
            if layer.source().startswith(self.outputGpkg):
                item.setFlags(item.flags() & ~(Qt.ItemIsSelectable | Qt.ItemIsEnabled))
                item.setIcon(QIcon(":/images/themes/default/mIconSuccess.png"))
            else:
                size = int(item.data(KadasGpkgExportDialog.LayerSizeRole))
                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                if size < KadasGpkgExportDialog.WARN_SIZE:
                    item.setIcon(QIcon())
                else:
                    item.setIcon(QIcon(":/images/themes/default/mIconWarn.png"))

    def getOutputFile(self):
        return self.outputGpkg

    def clearOutputFile(self):
        return self.ui.checkBoxClear.isChecked()

    def getSelectedLayers(self):
        layers = {}
        for i in range(0, self.ui.listWidgetLayers.count()):
            item = self.ui.listWidgetLayers.item(i)
            if item.flags() & Qt.ItemIsEnabled and item.checkState() == Qt.Checked:
                layerid = item.data(KadasGpkgExportDialog.LayerIdRole)
                layers[layerid] = item.data(KadasGpkgExportDialog.LayerTypeRole)
        return layers
