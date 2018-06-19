# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'kadas_gpkg_export_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.10.2.dev1805251538
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GPKGExportDialog(object):
    def setupUi(self, GPKGExportDialog):
        GPKGExportDialog.setObjectName("GPKGExportDialog")
        GPKGExportDialog.resize(468, 235)
        self.gridLayout = QtWidgets.QGridLayout(GPKGExportDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.labelNote = QtWidgets.QLabel(GPKGExportDialog)
        self.labelNote.setWordWrap(True)
        self.labelNote.setObjectName("labelNote")
        self.gridLayout.addWidget(self.labelNote, 8, 1, 1, 1)
        self.labelWarnIcon = QtWidgets.QLabel(GPKGExportDialog)
        self.labelWarnIcon.setMinimumSize(QtCore.QSize(16, 16))
        self.labelWarnIcon.setMaximumSize(QtCore.QSize(16, 16))
        self.labelWarnIcon.setPixmap(QtGui.QPixmap(":/images/themes/default/mIconWarn.png"))
        self.labelWarnIcon.setScaledContents(True)
        self.labelWarnIcon.setObjectName("labelWarnIcon")
        self.gridLayout.addWidget(self.labelWarnIcon, 8, 0, 1, 1)
        self.labelCheckIcon = QtWidgets.QLabel(GPKGExportDialog)
        self.labelCheckIcon.setMinimumSize(QtCore.QSize(16, 16))
        self.labelCheckIcon.setMaximumSize(QtCore.QSize(2, 16))
        self.labelCheckIcon.setPixmap(QtGui.QPixmap(":/images/themes/default/mIconSuccess.png"))
        self.labelCheckIcon.setScaledContents(True)
        self.labelCheckIcon.setObjectName("labelCheckIcon")
        self.gridLayout.addWidget(self.labelCheckIcon, 7, 0, 1, 1)
        self.label = QtWidgets.QLabel(GPKGExportDialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 7, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(GPKGExportDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 2)
        self.listWidgetLayers = QtWidgets.QListWidget(GPKGExportDialog)
        self.listWidgetLayers.setIconSize(QtCore.QSize(16, 16))
        self.listWidgetLayers.setObjectName("listWidgetLayers")
        self.gridLayout.addWidget(self.listWidgetLayers, 5, 0, 1, 2)
        self.labelExport = QtWidgets.QLabel(GPKGExportDialog)
        self.labelExport.setWordWrap(True)
        self.labelExport.setObjectName("labelExport")
        self.gridLayout.addWidget(self.labelExport, 4, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelOutputFile = QtWidgets.QLabel(GPKGExportDialog)
        self.labelOutputFile.setObjectName("labelOutputFile")
        self.horizontalLayout.addWidget(self.labelOutputFile)
        self.lineEditOutputFile = QtWidgets.QLineEdit(GPKGExportDialog)
        self.lineEditOutputFile.setReadOnly(True)
        self.lineEditOutputFile.setObjectName("lineEditOutputFile")
        self.horizontalLayout.addWidget(self.lineEditOutputFile)
        self.buttonSelectFile = QtWidgets.QToolButton(GPKGExportDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonSelectFile.sizePolicy().hasHeightForWidth())
        self.buttonSelectFile.setSizePolicy(sizePolicy)
        self.buttonSelectFile.setObjectName("buttonSelectFile")
        self.horizontalLayout.addWidget(self.buttonSelectFile)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(GPKGExportDialog)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 2)

        self.retranslateUi(GPKGExportDialog)
        self.buttonBox.accepted.connect(GPKGExportDialog.accept)
        self.buttonBox.rejected.connect(GPKGExportDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GPKGExportDialog)

    def retranslateUi(self, GPKGExportDialog):
        _translate = QtCore.QCoreApplication.translate
        GPKGExportDialog.setWindowTitle(_translate("GPKGExportDialog", "GPKG Export"))
        self.labelNote.setText(_translate("GPKGExportDialog", "<html><head/><body><p><span style=\" font-size:small; font-style:italic;\">Layers larger than 50 MB are deselected by default.</span></p></body></html>"))
        self.label.setText(_translate("GPKGExportDialog", "<small><i>Layers already part of the output GeoPackage are disabled.</i></small>"))
        self.labelExport.setText(_translate("GPKGExportDialog", "Additionally, the following local layers will be added to the GeoPackage:"))
        self.labelOutputFile.setText(_translate("GPKGExportDialog", "Output file:"))
        self.buttonSelectFile.setText(_translate("GPKGExportDialog", "Browse"))
        self.label_2.setText(_translate("GPKGExportDialog", "The project, including embedded layers (annotations, redlining, ...), will be written to the Geopackage."))

