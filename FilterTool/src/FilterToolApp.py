from PyQt5 import QtCore
from PyQt5.QtWidgets import QListWidgetItem, QMainWindow

from FilterTool.src.ui.widgets.Main_Window import FilterTool_MainWindow


class FilterToolApp(QMainWindow, FilterTool_MainWindow):
    def __init__(self, *args, **kwargs):
        # Inicializacion
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # Seteo de visivilidad de widgets


        # Conexiones


        # variables y arreglos


    def removeCurrentCurve(self):
        index = self.listWidget.currentRow()
        if index >= 0:
            self.listWidget.removeItemWidget(self.listWidget.takeItem(index))
            self.curves.pop(index)
            self.updateGraphs()

    def removeCurrentExcit(self):
        index = self.listWidget2.currentRow()
        if index >= 0:
            self.listWidget2.removeItemWidget(self.listWidget2.takeItem(index))
            self.excits.pop(index)
            self.updateGraphs()

    def clearAll(self):
        self.curves = []
        self.excits = []
        self.clearFigs()

    def clearFigs(self):
        self.listWidget.clear()
        self.listWidget2.clear()

        self.widgetModulo.clear()
        self.widgetFase.clear()
        self.widgetRespuesta.clear()