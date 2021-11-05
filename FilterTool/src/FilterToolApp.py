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


        ############
        self.Nombre_T.setText("Filtro")
        self.Filtro_B.setCurrentIndex(0)
        self.Aproximacion_B.setCurrentIndex(0)
        self.Ap_T.setValue(0.5)
        self.Aa_T.setValue(20)
        self.Fp_T.setValue(500)
        self.Fa_T.setValue(2000)
        self.Fa_T.setValue(2000)
        self.Nmax_T.setValue(100)



    def onFilterTypeChanged(self, index):

        # Visibilidad de textboxes
        
        self.Normal_L.setVisible(index in [0, 1])
        self.Pass_Band_L.setVisible(index in [2, 3])
        self.Attenuation_L.setVisible(index in [0, 1, 2, 3])
        self.Group_Delay_L.setVisible(index == 4)

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
            freqs = [ self.Fp_T.value(), self.Fa_T.value() ]    # [Fp, Fa]
        elif filterType == 'groupdelay':
            freqs = self.ft_T.value()       # fgd
        else:
            freqs = [ [ self.Fpm_T.value(), self.Fpp_T.value() ], [self.Fam_T.value(), self.Fap_T.value()] ]    # [ [Fp-, Fp+], [Fa-, Fa+] ]
        
        qmax = self.Qmax_T.value()
        denorm = self.Slider.value()/100

        gd = self.Gd_T.value()  # En us
        ft = self.ft_T.value()
        tol = self.Tol_T.value()/100

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
        # print("Fp: " + str(freqs[0]))
        # print("Fa: " + str(freqs[1]))
        print("Freqs: ", str(freqs))
        print("Nmin: " + str(n[0]))
        print("Nmax: " + str(n[1]))
        print("Qmax: " + str(qmax))
        print("Deonrm: " + str(denorm))
        print("Gd: " + str(gd))
        print("Ft: " + str(ft))
        print("Tol: " + str(tol))

        # Agregar filtro a la lista
        self.filter.append(Filter(name=name, filter_type=filterType, approx=approx, gain=gain, aten=aten,
                                    freqs=freqs, N=n, qmax=qmax, desnorm=denorm, retardo=gd, tol=tol))
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

        axes = [ self.Atenuacion_Plot.axes, self.Fase_Plot.axes, self.Retardo_Plot.axes, self.PZ_Plot.axes, self.Q_Plot.axes ]
        
        # [ax.clear() for ax in axes]

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