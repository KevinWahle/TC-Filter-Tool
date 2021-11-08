from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
import numpy as np
import scipy.signal as ss
from scipy.signal.filter_design import zpk2tf
from src.Drawings import drawingFilters, drawTemplate, tf2Tex
from src.classes.Filter import Filter

from src.ui.widgets.Main_Window import FilterTool_MainWindow
from src.ui.widgets.TeXLabel import TeXLabel


class FilterToolApp(QMainWindow, FilterTool_MainWindow):
    def __init__(self, *args, **kwargs):

        # Inicializacion
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        # Constantes
        self.filterName = [ "lowpass", "highpass", "bandpass", "bandstop", "groupdelay" ]
        self.approxDisplayName = [ "Butterworth", "Chebycheff I", "Chebycheff II", "Cauer", "Legendre", "Bessel", "Gauss" ]
        self.approxName =        [ "butter",        "cheby1",       "cheby2",      "ellip", "legendre", "bessel", "gauss" ]
        self.approxNameLP = self.approxName[:-2]
        self.approxDisplayNameLP = self.approxDisplayName[:-2]
        self.approxNameGD = self.approxName[-2:]
        self.approxDisplayNameGD = self.approxDisplayName[-2:]
        self.filterImg = [ "res/lowpasstemplate.png", "res/highpasstemplate.png",
                    "res/bandpasstemplate.png", "res/bandstoptemplate.png", "res/groupdelaytemplate.png" ]


        # Seteo de visivilidad de widgets

        self.onFilterTypeChanged(self.Filtro_B.currentIndex())

        # Conexiones

        #Diseño
        self.Plus_Btn.clicked.connect(self.addFilter)
        self.Minus_Btn.clicked.connect(self.removeFilter)
        self.Edit_Btn.clicked.connect(self.editFilter)
        self.Filtro_B.currentIndexChanged.connect(self.onFilterTypeChanged)
        self.Plantilla_Box.stateChanged.connect(self.onTemplateBtnClick)

        # Etapas
        self.Seleccionado_B.currentIndexChanged.connect(self.onStageFilterChanged)
        self.Plus_Btn_5.clicked.connect(self.onStageCreated)

        # variables y arreglos

        self.filter = []
        self.template = []

        self.stageZeros = []
        self.stagePoles = []


        ############ EJEMPLO PARA DEBUG
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
        self.Filter_Img.setPixmap(QPixmap(self.filterImg[self.Filtro_B.currentIndex()]))

        # Cambio de aproximaciones
        self.Aproximacion_B.clear()
        if self.filterName[index] == 'groupdelay':
            self.Aproximacion_B.addItems(self.approxDisplayNameGD)  # Se muestran aproximaciones de GD
            self.horizontalWidget_3.setVisible(False)      # Oculto textbox de ganancia
            self.widget.setVisible(False)      # Oculto Slider de denormaliazcion
        else:
            self.Aproximacion_B.addItems(self.approxDisplayNameLP)  # Se muestran aproximaciones de LP
            self.horizontalWidget_3.setVisible(True)        # Muestro textbox de ganancia
            self.widget.setVisible(True)       # Muestro slider de denormalizacion

    def addFilter(self):
        
        # Guardado de valores

        name = self.Nombre_T.text()

        if not name:
            print("Invalid name")
            return
        
        filterIndex = self.Filtro_B.currentIndex()    # Se maneja por indice
        filterType = self.filterName[filterIndex]

        aproxIndex = self.Aproximacion_B.currentIndex()         # Se maneja por indice
        approx = self.approxNameLP[aproxIndex]      # Si es aproximacion de modulo

        gain = self.Ganancia_T.value()
        aten = [ self.Ap_T.value(), self.Aa_T.value() ]     # [Ap, Aa]
        n = [int(self.Nmin_T.value()), int(self.Nmax_T.value())]      # [Nmin, Nmax]
        
        
        if filterType in ["lowpass", "highpass"]:
            freqs = [ self.Fp_T.value(), self.Fa_T.value() ]    # [Fp, Fa]
        elif filterType == 'groupdelay':
            freqs = self.ft_T.value()       # fgd
            approx = self.approxNameGD[aproxIndex]      # Es aproximacion de fase
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
        self.Filter_List.clear()    # Listview en diseño
        self.Seleccionado_B.clear() # ComboBox en etapas

        for f in self.filter:
            item = QtWidgets.QListWidgetItem(f.name, self.Filter_List)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)
            
            self.Seleccionado_B.addItem(f.name)


    def removeFilter(self):
        if self.filter:
            self.filter.pop(self.Filter_List.currentRow())
            self.updateFilterList()
            self.drawFilters()

    def editFilter(self):
        pass

    def drawFilters(self):

        if self.filter:

            axes = [ self.Atenuacion_Plot.axes, self.Fase_Plot.axes, self.Retardo_Plot.axes, self.PZ_Plot.axes, self.Q_Plot.axes ]
            
            [ax.clear() for ax in axes]

            if len(self.template):
                [axes[0].add_patch(patch) for patch in self.template]

            drawingFilters(filters=self.filter, ax=axes)

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
            # [ tmp.remove() for tmp in self.template ]
            self.template = []
            
        self.drawFilters()



    # Pestaña de etapas

    def onStageFilterChanged(self, index):
        
        filter = self.filter[index]

        self.Polos_B.clear()
        self.Ceros_B.clear()

        self.stageZeros = filter.z
        self.stagePoles = filter.p

        self.Polos_B.addItems([self.displayPZ(p) for p in filter.p if p.imag >= 0])     # Muestro polos y ceros, una sola vez si es conjugado
        self.Ceros_B.addItems([self.displayPZ(z) for z in filter.z if z.imag >= 0])

    def displayPZ(self, complex) -> str:

        real = complex.real
        imag = complex.imag
        f = np.sqrt(real**2 + imag**2)/(2*np.pi)
        
        if (imag == 0):
            return "n = 1\tf0 = " + str(f)
        elif (real == 0):
            return "n = 2\tf0 = " + str(f) + "\tQ = ∞"
        
        xi = -np.cos(np.angle(complex))
        Q = 1/(2*xi)
        return "n = 2\tf0 = " + str(f) +"\tQ = " + str(Q)


    def onStageCreated(self):

        z = []  # Ceros seleccionados
        p = []  # Polos seleccionados


        # TODO: CAMBIAR ESTO, ESTA TOMANDO SOLO UNO Y NO TIENE EN CUENTA LOS CONJUGADOS
        if len(self.stageZeros):
            z.append(self.stageZeros[self.Ceros_B.currentIndex()])
        if len(self.stagePoles):
            p.append(self.stagePoles[self.Polos_B.currentIndex()])
        
        print("z: ", z)
        print("p: ", p)

        num, den = zpk2tf(z, p, 1)
        
        print("num: ", num)
        print("den: ", den)

        latexH = tf2Tex(num, den)
        # print(latexH)
        tfPlot = TeXLabel(text=latexH)
        self.verticalLayout_20.addWidget(tfPlot)    # Agrega el widget al scroll

        self.Stage_List.addItem("Etapa i")