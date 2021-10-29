from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QListWidgetItem, QMainWindow

from src.ui.widgets.Main_Window import FilterTool_MainWindow


class FilterToolApp(QMainWindow, FilterTool_MainWindow):
    def __init__(self, *args, **kwargs):
        # Inicializacion
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # Seteo de visivilidad de widgets

        self.autoSetParamVisiility()

        # Conexiones

        self.Plus_Btn.clicked.connect(self.addFilter)
        self.Minus_Btn.clicked.connect(self.removeFilter)
        self.Edit_Btn.clicked.connect(self.editFilter)
        self.Filtro_B.currentIndexChanged.connect(self.autoSetParamVisiility)

            # Cambio de imagenes
        filterImg = [ "res/lowpasstemplate.png", "res/highpasstemplate.png",
                    "res/bandpasstemplate.png", "res/bandstoptemplate.png", "res/groupdelaytemplate.png" ]
        self.Filtro_B.currentIndexChanged.connect(lambda: self.Filter_Img.setPixmap(QPixmap(filterImg[self.Filtro_B.currentIndex()])))


        # variables y arreglos

        self.filter = []

    def autoSetParamVisiility(self):

        if (self.Filtro_B.currentIndex() == 0):
            #TODO: En lo posible nombrar mejor los horizontal_widgets
            self.horizontalWidget_4.setVisible(True)
            self.horizontalWidget_5.setVisible(True)
            self.horizontalWidget_6.setVisible(True)
            self.horizontalWidget_7.setVisible(True)
            self.horizontalWidget_8.setVisible(True)
            self.horizontalWidget_9.setVisible(True)
            self.horizontalWidget_10.setVisible(True)

        #TODO: Terminar

    def addFilter(self):
        
        # Guardado de valores

        name = self.Nombre_B.text()

        filterType = self.Filtro_B.currenIndex()    # Se maneja por indice
        aprox = self.Aprox_B.currentIndex()         # Se maneja por indice

        gain = self.Ganancia_T.value()
        aten_a = self.Aa_T.value()
        aten_p = self.Ap_T.value()
        fpp = self.Fpp_T.value()
        fpm = self.Fpm_T.value()
        fap = self.Fap_T.value()
        fam = self.Fam_T.value()
        nmin = self.Nmin_T.value()
        nmax = self.Nmax_T.value()

        # TODO: LLamar a función que cree el filtro

        # Agregar filtro a la lista


    def removeFilter(self):
        pass

    def editFilter(self):
        pass