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
        BandStackerDialogBase.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(BandStackerDialogBase)
        self.verticalLayout.setObjectName("verticalLayout")
        self.layerListWidget = QtWidgets.QListWidget(BandStackerDialogBase)
        self.layerListWidget.setObjectName("layerListWidget")
        self.verticalLayout.addWidget(self.layerListWidget)
        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.hboxlayout.setObjectName("hboxlayout")
        self.outputFileName = QtWidgets.QLineEdit(BandStackerDialogBase)
        self.outputFileName.setObjectName("outputFileName")
        self.hboxlayout.addWidget(self.outputFileName)
        self.browseButton = QtWidgets.QPushButton(BandStackerDialogBase)
        self.browseButton.setObjectName("browseButton")
        self.hboxlayout.addWidget(self.browseButton)
        self.verticalLayout.addLayout(self.hboxlayout)
        self.stackBandsButton = QtWidgets.QPushButton(BandStackerDialogBase)
        self.stackBandsButton.setObjectName("stackBandsButton")
        self.verticalLayout.addWidget(self.stackBandsButton)

        self.retranslateUi(BandStackerDialogBase)
        QtCore.QMetaObject.connectSlotsByName(BandStackerDialogBase)

    def retranslateUi(self, BandStackerDialogBase):
        _translate = QtCore.QCoreApplication.translate
        BandStackerDialogBase.setWindowTitle(_translate("BandStackerDialogBase", "Band Stacker"))
        self.browseButton.setText(_translate("BandStackerDialogBase", "Browse"))
        self.stackBandsButton.setText(_translate("BandStackerDialogBase", "Stack Bands"))

