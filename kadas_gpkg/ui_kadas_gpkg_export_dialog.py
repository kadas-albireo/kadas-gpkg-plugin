# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'kadas_gpkg_export_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_KadasGpkgExportDialog(object):
    def setupUi(self, KadasGpkgExportDialog):
        KadasGpkgExportDialog.setObjectName("KadasGpkgExportDialog")
        KadasGpkgExportDialog.resize(557, 491)
        self.gridLayout = QtWidgets.QGridLayout(KadasGpkgExportDialog)
        self.gridLayout.setObjectName("gridLayout")
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
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
        self.checkBoxClear = QtWidgets.QCheckBox(KadasGpkgExportDialog)
        self.checkBoxClear.setObjectName("checkBoxClear")
        self.gridLayout.addWidget(self.checkBoxClear, 1, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 2)
        self.labelExport = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.labelExport.setWordWrap(True)
        self.labelExport.setObjectName("labelExport")
        self.gridLayout.addWidget(self.labelExport, 3, 0, 1, 2)
        self.listWidgetLayers = KadasGpkgLayersList(KadasGpkgExportDialog)
        self.listWidgetLayers.setIconSize(QtCore.QSize(16, 16))
        self.listWidgetLayers.setObjectName("listWidgetLayers")
        self.gridLayout.addWidget(self.listWidgetLayers, 4, 0, 1, 2)
        self.labelCheckIcon = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.labelCheckIcon.setMinimumSize(QtCore.QSize(16, 16))
        self.labelCheckIcon.setMaximumSize(QtCore.QSize(2, 16))
        self.labelCheckIcon.setPixmap(QtGui.QPixmap(":/images/themes/default/mIconSuccess.svg"))
        self.labelCheckIcon.setScaledContents(True)
        self.labelCheckIcon.setObjectName("labelCheckIcon")
        self.gridLayout.addWidget(self.labelCheckIcon, 5, 0, 1, 1)
        self.label = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 5, 1, 1, 1)
        self.labelWarnIcon = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.labelWarnIcon.setMinimumSize(QtCore.QSize(16, 16))
        self.labelWarnIcon.setMaximumSize(QtCore.QSize(16, 16))
        self.labelWarnIcon.setPixmap(QtGui.QPixmap(":/images/themes/default/mIconWarning.svg"))
        self.labelWarnIcon.setScaledContents(True)
        self.labelWarnIcon.setObjectName("labelWarnIcon")
        self.gridLayout.addWidget(self.labelWarnIcon, 6, 0, 1, 1)
        self.labelNote = QtWidgets.QLabel(KadasGpkgExportDialog)
        self.labelNote.setWordWrap(True)
        self.labelNote.setObjectName("labelNote")
        self.gridLayout.addWidget(self.labelNote, 6, 1, 1, 1)
        self.checkBoxPyramids = QtWidgets.QCheckBox(KadasGpkgExportDialog)
        self.checkBoxPyramids.setObjectName("checkBoxPyramids")
        self.gridLayout.addWidget(self.checkBoxPyramids, 7, 0, 1, 2)
        self.layoutExportScale = QtWidgets.QHBoxLayout()
        self.layoutExportScale.setObjectName("layoutExportScale")
        self.checkBoxExportScale = QtWidgets.QCheckBox(KadasGpkgExportDialog)
        self.checkBoxExportScale.setObjectName("checkBoxExportScale")
        self.layoutExportScale.addWidget(self.checkBoxExportScale)
        self.spinBoxExportScale = QtWidgets.QSpinBox(KadasGpkgExportDialog)
        self.spinBoxExportScale.setEnabled(False)
        self.spinBoxExportScale.setSuffix("")
        self.spinBoxExportScale.setPrefix("1:")
        self.spinBoxExportScale.setMinimum(1)
        self.spinBoxExportScale.setMaximum(999999999)
        self.spinBoxExportScale.setObjectName("spinBoxExportScale")
        self.layoutExportScale.addWidget(self.spinBoxExportScale)
        self.gridLayout.addLayout(self.layoutExportScale, 8, 0, 1, 2)
        self.buttonBox = QtWidgets.QDialogButtonBox(KadasGpkgExportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)

        self.retranslateUi(KadasGpkgExportDialog)
        self.buttonBox.accepted.connect(KadasGpkgExportDialog.accept) # type: ignore
        self.buttonBox.rejected.connect(KadasGpkgExportDialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(KadasGpkgExportDialog)

    def retranslateUi(self, KadasGpkgExportDialog):
        _translate = QtCore.QCoreApplication.translate
        KadasGpkgExportDialog.setWindowTitle(_translate("KadasGpkgExportDialog", "GPKG Project Export"))
        self.labelOutputFile.setText(_translate("KadasGpkgExportDialog", "Output file:"))
        self.buttonSelectFile.setText(_translate("KadasGpkgExportDialog", "Browse"))
        self.checkBoxClear.setText(_translate("KadasGpkgExportDialog", "Clear existing GeoPackage before exporting"))
        self.label_2.setText(_translate("KadasGpkgExportDialog", "The project, including embedded layers (redlining, symbols, pictures, ...), will be written to the GeoPackage."))
        self.labelExport.setText(_translate("KadasGpkgExportDialog", "Additionally, the following layers will be added to the GeoPackage:"))
        self.label.setText(_translate("KadasGpkgExportDialog", "<small><i>Layers already part of the output GeoPackage are disabled.</i></small>"))
        self.labelNote.setText(_translate("KadasGpkgExportDialog", "<small><i>Layers with unknown size or larger than 50 MB are deselected by default.</i></span>"))
        self.checkBoxPyramids.setText(_translate("KadasGpkgExportDialog", "Generate pyramids (slow)"))
        self.checkBoxExportScale.setText(_translate("KadasGpkgExportDialog", "Specify raster export scale:"))
from .kadas_gpkg_layer_list import KadasGpkgLayersList
