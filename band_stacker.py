from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QListWidgetItem

from .resources import *
from qgis.core import QgsProject
from qgis.utils import iface
from PyQt5.QtWidgets import QAction, QFileDialog, QListWidgetItem

from .band_stacker_dialog import BandStackerDialog
from osgeo import gdal
import numpy as np
import os

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

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)
        return action

    def initGui(self):
        icon_path = ':/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Band Stacker'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.first_start = True

    def select_output_file(self):
        filename, _filter = QFileDialog.getSaveFileName(
            self.dlg, "Select output file ", "", '*.tif')
        if filename:
            self.dlg.outputFileName.setText(filename)

    def unload(self):
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&Band Stacker'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        if self.first_start:
            self.first_start = False
            self.dlg = BandStackerDialog()
            self.dlg.browseButton.clicked.connect(self.select_output_file)
            self.dlg.stackBandsButton.clicked.connect(self.stack_bands)

        self.dlg.outputFileName.clear()
        self.dlg.layerListWidget.clear()

        layers = QgsProject.instance().mapLayers().values()
        for layer in layers:
            if layer.type() == layer.RasterLayer:
                item = QListWidgetItem(layer.name())
                item.setCheckState(False)
                self.dlg.layerListWidget.addItem(item)

        self.dlg.show()
        result = self.dlg.exec_()
        if result:
            self.stack_bands()

    def stack_bands(self):
        selected_layers = []
        for index in range(self.dlg.layerListWidget.count()):
            item = self.dlg.layerListWidget.item(index)
            if item.checkState():
                layer_name = item.text()
                layer = QgsProject.instance().mapLayersByName(layer_name)[0]
                selected_layers.append(layer)

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

        for layer in selected_layers:
            path = layer.dataProvider().dataSourceUri()
            ds = gdal.Open(path)
            if ds is None:
                self.iface.messageBar().pushMessage("Error", f"Could not open {path}", level=3)
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

        out_ds = None
        self.iface.messageBar().pushMessage("Success", "Stacking completed successfully!", level=1)
