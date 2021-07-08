from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.core import *

import os
import re

class KadasGpkgLocalLayersList(QListWidget):

    LayerIdRole = Qt.UserRole + 1
    LayerTypeRole = Qt.UserRole + 2
    LayerSizeRole = Qt.UserRole + 3
    WARN_SIZE = 50 * 1024 * 1024

    def __init__(self, parent):
        QListWidget.__init__(self, parent)

        self.layers = {}
        local_providers = ["delimitedtext", "gdal", "gpx", "mssql", "ogr", "postgres", "spatialite", "wcs", "WFS"]

        for layer in QgsProject.instance().mapLayers().values():
            provider = "unknown"
            if layer.type() == QgsMapLayer.VectorLayer or layer.type() == QgsMapLayer.RasterLayer:
                provider = layer.dataProvider().name()
            elif layer.type() == QgsMapLayer.PluginLayer:
                provider = "plugin"

            if provider in local_providers:
                self.layers[layer.id()] = layer.type()

        for layerid in sorted(self.layers.keys()):
            layer = QgsProject.instance().mapLayer(layerid)
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

            try:
                filesize = os.path.getsize(filename)
            except:
                filesize = None
            item = QListWidgetItem(layer.name())
            item.setData(KadasGpkgLocalLayersList.LayerIdRole, layerid)
            item.setData(KadasGpkgLocalLayersList.LayerTypeRole, self.layers[layerid])
            item.setData(KadasGpkgLocalLayersList.LayerSizeRole, filesize)
            if filesize is not None and filesize < KadasGpkgLocalLayersList.WARN_SIZE:
                item.setCheckState(Qt.Checked)
                item.setIcon(QIcon())
            else:
                item.setCheckState(Qt.Unchecked)
                item.setIcon(QIcon(":/images/themes/default/mIconWarning.svg"))

            self.addItem(item)

    def updateLayerList(self, existingOutputGpkg):
        # Update layer list
        for i in range(0, self.count()):
            item = self.item(i)
            layerid = item.data(KadasGpkgLocalLayersList.LayerIdRole)
            layer = QgsProject.instance().mapLayer(layerid)
            # Disable layers already in GPKG
            gpkgLayer = existingOutputGpkg and (layer.source().startswith(existingOutputGpkg) or layer.source().startswith("GPKG:" + existingOutputGpkg))
            if gpkgLayer:
                item.setFlags(item.flags() & ~(Qt.ItemIsSelectable | Qt.ItemIsEnabled))
                item.setIcon(QIcon(":/images/themes/default/mIconSuccess.svg"))
            else:
                size = item.data(KadasGpkgLocalLayersList.LayerSizeRole)
                item.setFlags(item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                if size is None or int(size) < KadasGpkgLocalLayersList.WARN_SIZE:
                    item.setIcon(QIcon())
                else:
                    item.setIcon(QIcon(":/images/themes/default/mIconWarning.svg"))

    def getSelectedLayers(self):
        layers = {}
        for i in range(0, self.count()):
            item = self.item(i)
            if item.flags() & Qt.ItemIsEnabled and item.checkState() == Qt.Checked:
                layerid = item.data(KadasGpkgLocalLayersList.LayerIdRole)
                layers[layerid] = item.data(KadasGpkgLocalLayersList.LayerTypeRole)
        return layers
