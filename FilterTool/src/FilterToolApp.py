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
        self.Filtro_B.currentIndexChanged.connect(self.onFilterChanged)

            # Cambio de imagenes
        filterImg = [ "res/lowpasstemplate.png", "res/highpasstemplate.png",
                    "res/bandpasstemplate.png", "res/bandstoptemplate.png", "res/groupdelaytemplate.png" ]
        self.Filtro_B.currentIndexChanged.connect(lambda: self.Filter_Img.setPixmap(QPixmap(filterImg[self.Filtro_B.currentIndex()])))


        # variables y arreglos

        self.filter = []


    def onFilterChanged(self, index):
        self.Normal_L.setVisible(index in [0, 1])
        self.Pass_Band_L.setVisible(index in [2, 3])

    def addFilter(self):
        
        # Guardado de valores

        name = self.Nombre_T.text()

        filterType = self.Filtro_B.currentIndex()    # Se maneja por indice
        aprox = self.Aproximacion_B.currentIndex()         # Se maneja por indice

        gain = self.Ganancia_T.value()
        aten_a = self.Aa_T.value()
        aten_p = self.Ap_T.value()
        fpp = self.Fpp_T.value()
        fpm = self.Fpm_T.value()
        fap = self.Fap_T.value()
        fam = self.Fam_T.value()
        nmin = self.Nmin_T.value()
        nmax = self.Nmax_T.value()
        qmax = self.Qmax_T.value()
        deonrm = self.Slider.value()

        filterName = [ "lowpass", "highpass", "bandpass", "bandstop", "groupdelay" ]

        # TODO: LLamar a función que cree el filtro

        # DEBUG
        print("Nombre: " + name)
        print("Tipo: " + str(filterType))
        print("Aproximación: " + str(aprox))
        print("Ganancia: " + str(gain))
        print("Atenuación A: " + str(aten_a))
        print("Atenuación P: " + str(aten_p))
        print("Fpp: " + str(fpp))
        print("Fpm: " + str(fpm))
        print("Fap: " + str(fap))
        print("Fam: " + str(fam))
        print("Nmin: " + str(nmin))
        print("Nmax: " + str(nmax))
        print("Qmax: " + str(qmax))
        print("Deonrm: " + str(deonrm))

        # Agregar filtro a la lista


    def removeFilter(self):
        pass

    def editFilter(self):
        pass