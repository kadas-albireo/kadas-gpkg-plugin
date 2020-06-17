# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'kadas_gpkg_export_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_KadasGpkgExportDialog(object):
    def setupUi(self, KadasGpkgExportDialog):
        KadasGpkgExportDialog.setObjectName("KadasGpkgExportDialog")
        KadasGpkgExportDialog.resize(468, 262)
        self.gridLayout = QtWidgets.QGridLayout(KadasGpkgExportDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.labelNote = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.labelNote.setWordWrap(True)
        self.labelNote.setObjectName("labelNote")
        self.gridLayout.addWidget(self.labelNote, 8, 1, 1, 1)
        self.labelWarnIcon = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.labelWarnIcon.setMinimumSize(QtCore.QSize(16, 16))
        self.labelWarnIcon.setMaximumSize(QtCore.QSize(16, 16))
        self.labelWarnIcon.setPixmap(QtGui.QPixmap(":/images/themes/default/mIconWarning.svg"))
        self.labelWarnIcon.setScaledContents(True)
        self.labelWarnIcon.setObjectName("labelWarnIcon")
        self.gridLayout.addWidget(self.labelWarnIcon, 8, 0, 1, 1)
        self.labelCheckIcon = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.labelCheckIcon.setMinimumSize(QtCore.QSize(16, 16))
        self.labelCheckIcon.setMaximumSize(QtCore.QSize(2, 16))
        self.labelCheckIcon.setPixmap(QtGui.QPixmap(":/images/themes/default/mIconSuccess.svg"))
        self.labelCheckIcon.setScaledContents(True)
        self.labelCheckIcon.setObjectName("labelCheckIcon")
        self.gridLayout.addWidget(self.labelCheckIcon, 7, 0, 1, 1)
        self.label = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 7, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(KadasGpkgExportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 2)
        self.listWidgetLayers = KadasGpkgLocalLayersList(KadasGpkgExportDialog)
        self.listWidgetLayers.setIconSize(QtCore.QSize(16, 16))
        self.listWidgetLayers.setObjectName("listWidgetLayers")
        self.gridLayout.addWidget(self.listWidgetLayers, 5, 0, 1, 2)
        self.labelExport = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.labelExport.setWordWrap(True)
        self.labelExport.setObjectName("labelExport")
        self.gridLayout.addWidget(self.labelExport, 4, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelOutputFile = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.labelOutputFile.setObjectName("labelOutputFile")
        self.horizontalLayout.addWidget(self.labelOutputFile)
        self.lineEditOutputFile = QtWidgets.QLineEdit(KadasGpkgExportDialog)
        self.lineEditOutputFile.setReadOnly(True)
        self.lineEditOutputFile.setObjectName("lineEditOutputFile")
        self.horizontalLayout.addWidget(self.lineEditOutputFile)
        self.buttonSelectFile = QtWidgets.QToolButton(KadasGpkgExportDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonSelectFile.sizePolicy().hasHeightForWidth())
        self.buttonSelectFile.setSizePolicy(sizePolicy)
        self.buttonSelectFile.setObjectName("buttonSelectFile")
        self.horizontalLayout.addWidget(self.buttonSelectFile)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.checkBoxClear = QtWidgets.QCheckBox(KadasGpkgExportDialog)
        self.checkBoxClear.setObjectName("checkBoxClear")
        self.gridLayout.addWidget(self.checkBoxClear, 2, 0, 1, 2)
        self.checkBoxPyramids = QtWidgets.QCheckBox(KadasGpkgExportDialog)
        self.checkBoxPyramids.setObjectName("checkBoxPyramids")
        self.gridLayout.addWidget(self.checkBoxPyramids, 9, 0, 1, 2)

        self.retranslateUi(KadasGpkgExportDialog)
        self.buttonBox.accepted.connect(KadasGpkgExportDialog.accept)
        self.buttonBox.rejected.connect(KadasGpkgExportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(KadasGpkgExportDialog)

    def retranslateUi(self, KadasGpkgExportDialog):
        _translate = QtCore.QCoreApplication.translate
        KadasGpkgExportDialog.setWindowTitle(_translate("KadasGpkgExportDialog", "GPKG Project Export"))
        self.labelNote.setText(_translate("KadasGpkgExportDialog", "<html><head/><body><p><span style=\" font-size:small; font-style:italic;\">Layers larger than 50 MB are deselected by default.</span></p></body></html>"))
        self.label.setText(_translate("KadasGpkgExportDialog", "<small><i>Layers already part of the output GeoPackage are disabled.</i></small>"))
        self.labelExport.setText(_translate("KadasGpkgExportDialog", "Additionally, the following local layers will be added to the GeoPackage:"))
        self.label_2.setText(_translate("KadasGpkgExportDialog", "The project, including embedded layers (redlining, symbols, pictures, ...), will be written to the GeoPackage."))
        self.labelOutputFile.setText(_translate("KadasGpkgExportDialog", "Output file:"))
        self.buttonSelectFile.setText(_translate("KadasGpkgExportDialog", "Browse"))
        self.checkBoxClear.setText(_translate("KadasGpkgExportDialog", "Clear existing GeoPackage before exporting"))
        self.checkBoxPyramids.setText(_translate("KadasGpkgExportDialog", "Generate pyramids (slow)"))
from .kadas_gpkg_local_layers_list import KadasGpkgLocalLayersList
