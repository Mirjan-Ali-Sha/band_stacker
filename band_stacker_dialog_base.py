# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'band_stacker_dialog_base.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_BandStackerDialogBase(object):
    def setupUi(self, BandStackerDialogBase):
        BandStackerDialogBase.setObjectName("BandStackerDialogBase")
        BandStackerDialogBase.resize(600, 400)
        self.verticalLayout = QtWidgets.QVBoxLayout(BandStackerDialogBase)
        self.verticalLayout.setObjectName("verticalLayout")
        self.layerTableWidget = QtWidgets.QTableWidget(BandStackerDialogBase)
        self.layerTableWidget.setObjectName("layerTableWidget")
        self.layerTableWidget.setColumnCount(3)
        self.layerTableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.layerTableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.layerTableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.layerTableWidget.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.layerTableWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.moveUpButton = QtWidgets.QPushButton(BandStackerDialogBase)
        self.moveUpButton.setObjectName("moveUpButton")
        self.horizontalLayout.addWidget(self.moveUpButton)
        self.moveDownButton = QtWidgets.QPushButton(BandStackerDialogBase)
        self.moveDownButton.setObjectName("moveDownButton")
        self.horizontalLayout.addWidget(self.moveDownButton)
        self.removeButton = QtWidgets.QPushButton(BandStackerDialogBase)
        self.removeButton.setObjectName("removeButton")
        self.horizontalLayout.addWidget(self.removeButton)
        self.selectAllButton = QtWidgets.QPushButton(BandStackerDialogBase)
        self.selectAllButton.setObjectName("selectAllButton")
        self.horizontalLayout.addWidget(self.selectAllButton)
        self.openBandsButton = QtWidgets.QPushButton(BandStackerDialogBase)
        self.openBandsButton.setObjectName("openBandsButton")
        self.horizontalLayout.addWidget(self.openBandsButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.openInQGISCheckBox = QtWidgets.QCheckBox(BandStackerDialogBase)
        self.openInQGISCheckBox.setObjectName("openInQGISCheckBox")
        self.verticalLayout.addWidget(self.openInQGISCheckBox)
        self.outputFileNameLabel = QtWidgets.QLabel(BandStackerDialogBase)
        self.outputFileNameLabel.setObjectName("outputFileNameLabel")
        self.verticalLayout.addWidget(self.outputFileNameLabel)
        self.outputFile = QtWidgets.QHBoxLayout()
        self.outputFile.setObjectName("outputFile")
        self.outputFileName = QtWidgets.QLineEdit(BandStackerDialogBase)
        self.outputFileName.setObjectName("outputFileName")
        self.outputFile.addWidget(self.outputFileName)
        self.browseButton = QtWidgets.QPushButton(BandStackerDialogBase)
        self.browseButton.setObjectName("browseButton")
        self.outputFile.addWidget(self.browseButton)
        self.verticalLayout.addLayout(self.outputFile)
        self.stackBandsButton = QtWidgets.QPushButton(BandStackerDialogBase)
        self.stackBandsButton.setObjectName("stackBandsButton")
        self.verticalLayout.addWidget(self.stackBandsButton)

        self.retranslateUi(BandStackerDialogBase)
        QtCore.QMetaObject.connectSlotsByName(BandStackerDialogBase)

    def retranslateUi(self, BandStackerDialogBase):
        _translate = QtCore.QCoreApplication.translate
        BandStackerDialogBase.setWindowTitle(_translate("BandStackerDialogBase", "Band Stacker"))
        item = self.layerTableWidget.horizontalHeaderItem(0)
        item.setText(_translate("BandStackerDialogBase", "Select"))
        item = self.layerTableWidget.horizontalHeaderItem(1)
        item.setText(_translate("BandStackerDialogBase", "Input Band Name"))
        item = self.layerTableWidget.horizontalHeaderItem(2)
        item.setText(_translate("BandStackerDialogBase", "Output Band Name"))
        self.moveUpButton.setText(_translate("BandStackerDialogBase", "Move Up"))
        self.moveDownButton.setText(_translate("BandStackerDialogBase", "Move Down"))
        self.removeButton.setText(_translate("BandStackerDialogBase", "Remove"))
        self.selectAllButton.setText(_translate("BandStackerDialogBase", "Select All"))
        self.openBandsButton.setText(_translate("BandStackerDialogBase", "Open Bands"))
        self.openInQGISCheckBox.setText(_translate("BandStackerDialogBase", "Do you want to open the output image in QGIS Interface?"))
        self.outputFileNameLabel.setText(_translate("BandStackerDialogBase", "Output File Name:"))
        self.browseButton.setText(_translate("BandStackerDialogBase", "Browse"))
        self.stackBandsButton.setText(_translate("BandStackerDialogBase", "Stack Bands"))

