from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
from src.Drawings import drawTemplate, drawingFilter
from src.classes.Filter import Filter

from src.ui.widgets.Main_Window import FilterTool_MainWindow


class FilterToolApp(QMainWindow, FilterTool_MainWindow):
    def __init__(self, *args, **kwargs):

        # Inicializacion
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # Seteo de visivilidad de widgets

        self.onFilterTypeChanged(self.Filtro_B.currentIndex())

        # Conexiones

        self.Plus_Btn.clicked.connect(self.addFilter)
        self.Minus_Btn.clicked.connect(self.removeFilter)
        self.Edit_Btn.clicked.connect(self.editFilter)
        self.Filtro_B.currentIndexChanged.connect(self.onFilterTypeChanged)
        self.Plantilla_Box.stateChanged.connect(self.onTemplateBtnClick)


        # variables y arreglos

        self.filter = []
        self.template = []


    def onFilterTypeChanged(self, index):

        # Visibilidad de textboxes
        
        self.Normal_L.setVisible(index in [0, 1])
        self.Pass_Band_L.setVisible(index in [2, 3])

        # Cambio de imagenes
        filterImg = [ "res/lowpasstemplate.png", "res/highpasstemplate.png",
                    "res/bandpasstemplate.png", "res/bandstoptemplate.png", "res/groupdelaytemplate.png" ]
        self.Filter_Img.setPixmap(QPixmap(filterImg[self.Filtro_B.currentIndex()]))

    def addFilter(self):
        
        # Guardado de valores

        name = self.Nombre_T.text()

        if not name:
            print("Invalid name")
            return
        
        filterName = [ "lowpass", "highpass", "bandpass", "bandstop", "groupdelay" ]
        filterIndex = self.Filtro_B.currentIndex()    # Se maneja por indice
        filterType = filterName[filterIndex]

        approxName = [ "butter", "bessel", "cheby1", "cheby2", "ellip", "legendre", "gauss"  ]
        aproxIndex = self.Aproximacion_B.currentIndex()         # Se maneja por indice
        approx = approxName[aproxIndex]

        gain = self.Ganancia_T.value()
        aten = [ self.Ap_T.value(), self.Aa_T.value() ]     # [Ap, Aa]
        n = [int(self.Nmin_T.value()), int(self.Nmax_T.value())]      # [Nmin, Nmax]
        
        
        if filterType in ["lowpass", "highpass"]:
            freqs = [ self.Fp_T_2.value(), self.Fa_T_2.value() ]    # [Fp, Fa]
        else:
            freqs = [ [ self.Fpm_T.value(), self.Fpp_T.value() ], [self.Fam_T.value(), self.Fap_T.value()] ]    # [ [Fp-, Fp+], [Fa-, Fa+] ]
        
        qmax = self.Qmax_T.value()
        deonrm = self.Slider.value()

        # DEBUG
        print("Nombre: " + name)
        print("Tipo: " + str(filterType))
        print("Aproximación: " + str(approx))
        print("Ganancia: " + str(gain))
        print("Atenuación P: " + str(aten[0]))
        print("Atenuación A: " + str(aten[1]))
        # print("Fpm: " + str(freqs[0][0]))
        # print("Fpp: " + str(freqs[0][1]))
        # print("Fam: " + str(freqs[1][0]))
        # print("Fap: " + str(freqs[1][1]))
        print("Fp: " + str(freqs[0]))
        print("Fa: " + str(freqs[1]))
        print("Nmin: " + str(n[0]))
        print("Nmax: " + str(n[1]))
        print("Qmax: " + str(qmax))
        print("Deonrm: " + str(deonrm))

        # Agregar filtro a la lista
        self.filter.append(Filter(name=name, filter_type=filterType, approx=approx, gain=gain, aten=aten,
                                    freqs=freqs, N=n, qmax=qmax, desnorm=deonrm/100))
        self.updateFilterList()

        self.drawFilters()


    def updateFilterList(self):
        self.Filter_List.clear()

        for f in self.filter:
            item = QtWidgets.QListWidgetItem(f.name, self.Filter_List)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)


    def removeFilter(self):
        self.filter.pop(self.Filter_List.currentRow())
        self.updateFilterList()

    def editFilter(self):
        pass

    def drawFilters(self):

        axes = [ self.Atenuacion_Plot.axes, self.Fase_Plot.axes, self.Retardo_Plot.axes, self.Q_Plot.axes ]
        
        for i in range(len(self.filter)):
            filter = self.filter[i]
            drawingFilter(filter=filter, axes=axes, index=i)

        self.Atenuacion_Plot.draw()
        self.Fase_Plot.draw()
        self.Retardo_Plot.draw()
        self.Q_Plot.draw()

    def onFilterItemChanged(self, index):
        pass

    def onTemplateBtnClick(self, state):
        index = self.Filter_List.currentRow()
        if (state == Qt.Checked and len(self.filter) > 0 and index >= 0):
            self.template = drawTemplate(self.Atenuacion_Plot.axes, self.filter[index], index=index)
            self.Atenuacion_Plot.draw()
        elif len(self.template) > 0:
            [ tmp.remove() for tmp in self.template ]
            self.template = []
            
        self.drawFilters()