from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QTableWidgetItem, QAbstractItemView

from .resources import *
from qgis.core import QgsProject
from qgis.utils import iface
from PyQt5.QtWidgets import QAction, QFileDialog, QTableWidgetItem

from .band_stacker_dialog import BandStackerDialog
from osgeo import gdal
import numpy as np
import os
import re

class BandStacker:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BandStacker_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Band Stacker')
        self.first_start = None
        self.select_all_state = True  # Added to keep track of the select all/unselect all state

    def tr(self, message):
        return QCoreApplication.translate('BandStacker', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        self.actions.append(action)
        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = ':/icon.png'
        self.toolbar = self.iface.addToolBar(u'Band Stacker')
        self.toolbar.setObjectName("Band Stacker")

        self.action_BandStack = QAction(QIcon(icon_path), u"Band Stacker", self.iface.mainWindow())
        self.action_BandStack.triggered.connect(self.run)
        self.iface.addPluginToRasterMenu(u"&Band Stacker", self.action_BandStack)
        
        self.toolbar.addActions([self.action_BandStack])

    def select_output_file(self):
        filename, _filter = QFileDialog.getSaveFileName(
            self.dlg, "Select output file", "", '*.tif')
        if filename:
            self.dlg.outputFileName.setText(filename)

    def move_items_up(self):
        selected_rows = sorted([index.row() for index in self.dlg.layerTableWidget.selectionModel().selectedRows()])
        if not selected_rows:
            return
        if selected_rows[0] == 0:
            return  # Cannot move the topmost item up
        for row in selected_rows:
            self.swap_rows(row, row - 1)
        self.dlg.layerTableWidget.clearSelection()
        for row in selected_rows:
            self.dlg.layerTableWidget.selectRow(row - 1)

    def move_items_down(self):
        selected_rows = sorted([index.row() for index in self.dlg.layerTableWidget.selectionModel().selectedRows()], reverse=True)
        if not selected_rows:
            return
        if selected_rows[0] == self.dlg.layerTableWidget.rowCount() - 1:
            return  # Cannot move the bottommost item down
        for row in selected_rows:
            self.swap_rows(row, row + 1)
        self.dlg.layerTableWidget.clearSelection()
        for row in selected_rows:
            self.dlg.layerTableWidget.selectRow(row + 1)

    def remove_items(self):
        selected_rows = sorted([index.row() for index in self.dlg.layerTableWidget.selectionModel().selectedRows()], reverse=True)
        for row in selected_rows:
            self.dlg.layerTableWidget.removeRow(row)
        self.update_band_names()

    def select_all_items(self):
        if self.select_all_state:
            for row in range(self.dlg.layerTableWidget.rowCount()):
                item = self.dlg.layerTableWidget.item(row, 0)
                item.setCheckState(Qt.Checked)
            self.dlg.selectAllButton.setText("Unselect All")
        else:
            for row in range(self.dlg.layerTableWidget.rowCount()):
                item = self.dlg.layerTableWidget.item(row, 0)
                item.setCheckState(Qt.Unchecked)
            self.dlg.selectAllButton.setText("Select All")
        self.select_all_state = not self.select_all_state

    def open_bands(self):
        filenames, _ = QFileDialog.getOpenFileNames(
            self.dlg, "Select band files", "", 'GeoTiff Files (*.tif);;All Files (*)')
        if filenames:
            for filename in filenames:
                row_position = self.dlg.layerTableWidget.rowCount()
                self.dlg.layerTableWidget.insertRow(row_position)

                # Checkbox
                check_item = QTableWidgetItem()
                check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                check_item.setCheckState(Qt.Unchecked)
                self.dlg.layerTableWidget.setItem(row_position, 0, check_item)

                band_name = os.path.basename(filename)
                item = QTableWidgetItem(band_name)
                item.setData(Qt.UserRole, filename)  # Store the file path in the item
                self.dlg.layerTableWidget.setItem(row_position, 1, item)
                self.dlg.layerTableWidget.setItem(row_position, 2, QTableWidgetItem(f"Band {row_position + 1}"))

            self.dlg.layerTableWidget.resizeColumnsToContents()

    def swap_rows(self, row1, row2):
        for col in range(self.dlg.layerTableWidget.columnCount()):
            item1 = self.dlg.layerTableWidget.takeItem(row1, col)
            item2 = self.dlg.layerTableWidget.takeItem(row2, col)
            self.dlg.layerTableWidget.setItem(row1, col, item2)
            self.dlg.layerTableWidget.setItem(row2, col, item1)

        # Update default band names
        self.update_band_names()

    def update_band_names(self):
        for row in range(self.dlg.layerTableWidget.rowCount()):
            output_band_item = self.dlg.layerTableWidget.item(row, 2)
            if re.match(r'^Band \d+$', output_band_item.text()):
                output_band_item.setText(f"Band {row + 1}")

    def unload(self):
        for action in self.actions:
            self.iface.removePluginRasterMenu(self.tr(u'&Band Stacker'), action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        self.dlg = BandStackerDialog()
        self.dlg.browseButton.clicked.connect(self.select_output_file)
        self.dlg.stackBandsButton.clicked.connect(self.stack_bands)
        self.dlg.moveUpButton.clicked.connect(self.move_items_up)
        self.dlg.moveDownButton.clicked.connect(self.move_items_down)
        self.dlg.removeButton.clicked.connect(self.remove_items)
        self.dlg.selectAllButton.clicked.connect(self.select_all_items)
        self.dlg.openBandsButton.clicked.connect(self.open_bands)

        self.dlg.layerTableWidget.setColumnCount(3)
        self.dlg.layerTableWidget.setHorizontalHeaderLabels(['Select', 'Input Band Name', 'Output Band Name'])
        self.dlg.layerTableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dlg.outputFileName.clear()
        self.dlg.layerTableWidget.setRowCount(0)

        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == layer.RasterLayer:
                row_position = self.dlg.layerTableWidget.rowCount()
                self.dlg.layerTableWidget.insertRow(row_position)
                
                # Checkbox
                check_item = QTableWidgetItem()
                check_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                check_item.setCheckState(Qt.Unchecked)
                self.dlg.layerTableWidget.setItem(row_position, 0, check_item)
                
                self.dlg.layerTableWidget.setItem(row_position, 1, QTableWidgetItem(layer.name()))
                self.dlg.layerTableWidget.setItem(row_position, 2, QTableWidgetItem(f"Band {row_position + 1}"))

        self.dlg.layerTableWidget.resizeColumnsToContents()
        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            self.stack_bands()

    def stack_bands(self):
        selected_layers = []
        output_band_names = []
        for row in range(self.dlg.layerTableWidget.rowCount()):
            check_item = self.dlg.layerTableWidget.item(row, 0)
            input_band_item = self.dlg.layerTableWidget.item(row, 1)
            output_band_item = self.dlg.layerTableWidget.item(row, 2)
            if check_item and check_item.checkState() == Qt.Checked and input_band_item and output_band_item:
                file_path = input_band_item.data(Qt.UserRole)  # Get the file path from the item's data
                selected_layers.append(file_path)
                output_band_names.append(output_band_item.text())

        if len(selected_layers) < 2:
            self.iface.messageBar().pushMessage("Error", "Please select at least two raster layers.", level=3)
            return

        output_file_name = self.dlg.outputFileName.text()
        if not output_file_name:
            self.iface.messageBar().pushMessage("Error", "Please specify an output file name.", level=3)
            return

        bands_arrays = []
        geotransform = None
        projection = None

        for file_path in selected_layers:
            ds = gdal.Open(file_path)
            if ds is None:
                self.iface.messageBar().pushMessage("Error", f"Could not open {file_path}", level=3)
                return
            band_array = ds.GetRasterBand(1).ReadAsArray()
            bands_arrays.append(band_array)
            if geotransform is None:
                geotransform = ds.GetGeoTransform()
                projection = ds.GetProjection()

        ref_shape = bands_arrays[0].shape
        for band_array in bands_arrays:
            if band_array.shape != ref_shape:
                self.iface.messageBar().pushMessage("Error", "All selected bands must have the same dimensions.", level=3)
                return

        stacked_array = np.stack(bands_arrays, axis=0)

        driver = gdal.GetDriverByName('GTiff')
        out_ds = driver.Create(output_file_name, ref_shape[1], ref_shape[0], len(bands_arrays), gdal.GDT_Float32)
        out_ds.SetGeoTransform(geotransform)
        out_ds.SetProjection(projection)

        for i in range(len(bands_arrays)):
            out_ds.GetRasterBand(i+1).WriteArray(stacked_array[i])
            out_ds.GetRasterBand(i+1).SetDescription(output_band_names[i])  # Set the band name

        out_ds = None

        if self.dlg.openInQGISCheckBox.isChecked():
            output_layer = iface.addRasterLayer(output_file_name, os.path.basename(output_file_name))
            if not output_layer:
                self.iface.messageBar().pushMessage("Error", "Failed to load the output raster layer into QGIS.", level=3)
            else:
                self.iface.messageBar().pushMessage("Success", "Stacking completed successfully and layer added to QGIS!", level=1)
        else:
            self.iface.messageBar().pushMessage("Success", "Stacking completed successfully!", level=1)
