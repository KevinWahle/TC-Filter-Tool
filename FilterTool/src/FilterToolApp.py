from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
import numpy as np
from numpy.core.defchararray import find
import scipy.signal as ss
import scipy.special as sp
from scipy.signal.filter_design import zpk2tf
from src.Drawings import drawPZ, drawingFilters, drawTemplate, tf2Tex
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
        # self.Edit_Btn.clicked.connect(self.editFilter)
        self.Filtro_B.currentIndexChanged.connect(self.onFilterTypeChanged)
        self.Plantilla_Box.stateChanged.connect(self.onTemplateBtnClick)
        self.Filter_List.itemChanged.connect(self.onFilterItemChanged)

        # Etapas
        self.Seleccionado_B.currentIndexChanged.connect(self.onStageFilterChanged)
        self.Plus_Btn_5.clicked.connect(self.onStageCreated)
        self.Minus_Btn_5.clicked.connect(self.onStageRemoved)
        self.Stage_List.itemChanged.connect(self.onStageItemChanged)
        self.Seleccionadas_RB.toggled.connect(self.drawStages)
        # variables y arreglos

        self.filter = []
        self.template = []

        self.stageZeros = []
        self.stagePoles = []


        ############ EJEMPLO PARA DEBUG
        self.Nombre_T.setText("Filtro")
        self.Filtro_B.setCurrentIndex(0)
        self.Aproximacion_B.setCurrentIndex(0)
        self.Ap_T.setValue(2)
        self.Aa_T.setValue(20)
        self.Fp_T.setValue(500)
        self.Fa_T.setValue(2000)
        self.Fa_T.setValue(2000)

        self.Fam_T.setValue(20e3)
        self.Fpm_T.setValue(25e3)
        self.Fpp_T.setValue(30e3)
        self.Fap_T.setValue(50e3)

        self.Nmax_T.setValue(100)



    def onFilterTypeChanged(self, index):
        try:
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
        except Exception as e:
            print("Error al cambiar de filtro: ", e)

    def addFilter(self):
        try:
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
            # print("Nombre: " + name)
            # print("Tipo: " + str(filterType))
            # print("Aproximación: " + str(approx))
            # print("Ganancia: " + str(gain))
            # print("Atenuación P: " + str(aten[0]))
            # print("Atenuación A: " + str(aten[1]))
            # # print("Fpm: " + str(freqs[0][0]))
            # # print("Fpp: " + str(freqs[0][1]))
            # # print("Fam: " + str(freqs[1][0]))
            # # print("Fap: " + str(freqs[1][1]))
            # # print("Fp: " + str(freqs[0]))
            # # print("Fa: " + str(freqs[1]))
            # print("Freqs: ", str(freqs))
            # print("Nmin: " + str(n[0]))
            # print("Nmax: " + str(n[1]))
            # print("Qmax: " + str(qmax))
            # print("Deonrm: " + str(denorm))
            # print("Gd: " + str(gd))
            # print("Ft: " + str(ft))
            # print("Tol: " + str(tol))

            # Agregar filtro a la lista
            self.filter.append(Filter(name=name, filter_type=filterType, approx=approx, gain=gain, aten=aten,
                                        freqs=freqs, N=n, qmax=qmax, desnorm=denorm, retardo=gd, tol=tol))
            self.updateFilterList()
            self.drawFilters()
        except Exception as e:
            print("Error al agregar filtro: ", e)


    def updateFilterList(self):

        try:
            self.Filter_List.clear()    # Listview en diseño
            self.Seleccionado_B.clear() # ComboBox en etapas

            for f in self.filter:
                item = QtWidgets.QListWidgetItem(f.name, self.Filter_List)
                item.setCheckState(QtCore.Qt.Checked if f.visible else QtCore.Qt.Unchecked)
                item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
                
                self.Seleccionado_B.addItem(f.name)
        except Exception as e:
            print("Error al actualizar la lista de filtros: ",e)

    def removeFilter(self):
        try:
            if self.filter:
                self.filter.pop(self.Filter_List.currentRow())
                self.updateFilterList()
            self.drawFilters()
        except Exception as e:
            print("Error al eliminar filtro: ", e)
    # def editFilter(self):
    #     pass

    def drawFilters(self):

        try:
            axes = [ self.Atenuacion_Plot.axes, self.Fase_Plot.axes, self.Retardo_Plot.axes, self.PZ_Plot.axes ]
            
            [ax.clear() for ax in axes]
            if self.filter:

                if len(self.template):
                    [axes[0].add_patch(patch) for patch in self.template]

                drawingFilters(filters=self.filter, ax=axes)

            self.Atenuacion_Plot.draw()
            self.Fase_Plot.draw()
            self.Retardo_Plot.draw()
            self.PZ_Plot.draw()
                # self.Q_Plot.draw()
        except Exception as e:
            print("Error al dibujar filtros: ", e)


    def onFilterItemChanged(self, item):
        try:
            if (len(self.filter)):
                index = self.Filter_List.row(item)
                self.filter[index].visible = item.checkState() == QtCore.Qt.Checked
                self.filter[index].name = item.text()
                self.Seleccionado_B.setItemText(index, self.filter[index].name)     # Actualizo tambie en las etapas

            self.drawFilters()
        except Exception as e:
            print("Error al actualizar filtro: ", e)

    def onTemplateBtnClick(self, state):
        try:
            index = self.Filter_List.currentRow()
            if (state == Qt.Checked and len(self.filter) > 0 and index >= 0):
                self.template = drawTemplate(self.Atenuacion_Plot.axes, self.filter[index], index=index)
                self.Atenuacion_Plot.draw()
            elif len(self.template) > 0:
                # [ tmp.remove() for tmp in self.template ]
                self.template = []
                
            self.drawFilters()
        except Exception as e:
            print("Error al actualizar template: ", e)


    # Pestaña de etapas

    def onStageFilterChanged(self, index):
        try:
            self.Polos_B.clear()
            self.Ceros_B.clear()
            self.stages = []
            self.stageZeros = []
            self.stagepoles = []
            self.stageGain = None
            self.Stage_List.clear()
            self.PZ_Plot_2.axes.clear()
            self.TF_Modulo.clear()
            self.TF_FASE.clear()

            for i in reversed(range(self.verticalLayout_20.count())):   # Elimina las transferencias de la etapa
                self.verticalLayout_20.itemAt(i).widget().deleteLater()

            if (len(self.filter)):

                filter = self.filter[index]

                drawPZ(filter=filter, ax=self.PZ_Plot_2.axes)
                self.PZ_Plot_2.draw()

                self.stageZeros = []      # [ z1, z2, z3]
                self.stagePoles = []
                self.gain = filter.gain

                filterz = np.copy(filter.z)  # Para no modificar el original
                filterp = np.copy(filter.p)

                while len(filterz):
                    z = filterz[0]
                    if z.imag == 0:
                        self.stageZeros.append(filterz[0])
                        filterz = np.delete(filterz, 0)
                    else:
                        for i in range(1,len(filterz)):
                            if z.imag == -filterz[i].imag and z.real == filterz[i].real:
                                self.stageZeros.append(np.array([z, filterz[i]]))
                                filterz= np.delete(filterz, [0, i])

                                break

                while len(filterp):
                    p = filterp[0]
                    if p.imag == 0:
                        self.stagePoles.append(filterp[0])
                        filterp = np.delete(filterp, 0)

                    else:
                        for i in range(1,len(filterp)):
                            if self.isEqual(p.imag,-filterp[i].imag) and self.isEqual(p.real,filterp[i].real):
                                self.stagePoles.append(np.array([p, filterp[i]]))
                                filterp= np.delete(filterp, [0, i])
                                break
                
                # print(self.stageZeros)
                # print(self.stagePoles)

                # while len(filter.p):
                #     p = filter.p[0]
                #     if p.imag == 0:
                #         self.stagePoles.append(filter.p[0])
                #         filter.p.pop(0)
                #     else:
                #         indexes = np.where(filter.p == p or filter.p == np.conjugate(p))
                #         print (indexes)
                #         self.stagePoles.append( filter.p[indexes] )
                #         filter.p.pop(filter.p.real == p.real and abs(filter.p.imag) == abs(p.imag))



                # for i in range(len(filter.z)):
                #     if filter.z[i].imag != 0:
                #         for j in range(i+1,len(filter.z))
                #             if filter.z[j].imag == -filter.z[i].imag and filter.z[j].real == filter.z[i].real:
                                
                #         self.stageZeros.append([filter.z[i] ])


                self.Polos_B.addItems([self.displayPZ(p) for p in self.stagePoles ])     # Muestro polos y ceros, una sola vez si es conjugado
                self.Ceros_B.addItems([self.displayPZ(z) for z in self.stageZeros])
        except Exception as e:
            print("Error al actualizar etapas: ", e)

    def isEqual(self, n1, n2):
        offset = 0.0001
        return n1 >= n2-offset and n1 <= n2+offset

    def displayPZ(self, complex) -> str:
        try:
            complex = complex if not isinstance(complex, np.ndarray) else complex[0]

            # print(complex)

            real = complex.real
            imag = complex.imag
            w0 = abs(complex)
            # f = np.sqrt(real**2 + imag**2)/(2*np.pi)
            f = w0/(2*np.pi)
            
            if (imag == 0):
                return "n = 1\tf0 = " + self.formatedNum(f) + 'Hz'
            elif (real == 0):
                return "n = 2\tf0 = " + self.formatedNum(f) + "Hz\tQ = ∞"
            
            # xi = -np.cos(np.angle(complex))
            # Q = 1/(2*xi)
            Q = abs(w0/(2*real))
            
            return "n = 2\tf0 = " + self.formatedNum(f) +"Hz\tQ = " + self.formatedNum(Q)
        except Exception as e:
            print("Error al obtener expresion de polos y ceros: ", e)
            return ""

    def formatedNum(self, num) -> str:
        return "{0:.2f}".format(num)

    def onStageCreated(self):
        try:
            z = []  # Ceros seleccionados
            p = []  # Polos seleccionados


            if len(self.stageZeros):
                z = [ self.stageZeros[self.Ceros_B.currentIndex()] ]
            if len(self.stagePoles):
                p = self.stagePoles[self.Polos_B.currentIndex()]
            
            # print("z: ", z)
            # print("p: ", p)

            # num, den = zpk2tf(z, p, 1)
        
            # zpg = ss.ZerosPolesGain(z, p, self.findK(z, p))
            zpg = ss.ZerosPolesGain(z, p, 1)
            H = ss.TransferFunction(zpg)
            
            a, b = ss.normalize(H.num, H.den)

            # print("num_norm: ", a)
            # print("den_norm: ", b)

            H = ss.TransferFunction(a/a[-1], b/b[-1])       # H con ganancia 1

            self.stages.append([H, True])   # [ H, visibilidad]

            num = H.num
            den = H.den

            # print("num: ", num)
            # print("den: ", den)

            latexH = tf2Tex(num, den)
            # print(latexH)

            text = latexH + '\n$' + self.displayPZ(H.poles).replace('\t', '\quad').replace('f0', 'f_0') + '$'

            tfPlot = TeXLabel(text=text)
            self.verticalLayout_20.addWidget(tfPlot)    # Agrega el widget al scroll

            name = "Etapa " + str(len(self.stages))     # Etapa i

            item = QtWidgets.QListWidgetItem(name, self.Stage_List)
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)

            # self.Stage_List.addItem(item)

            self.drawStages()
        except Exception as e:
            print("Error al crear etapa: ", e)

    def onStageRemoved(self):
        try:
            if (len(self.stages)):
                index = self.Stage_List.currentRow()
                self.stages.pop(index)
                self.Stage_List.takeItem(index)
                self.verticalLayout_20.itemAt(index).widget().deleteLater()

            self.drawStages()
        except Exception as e:
            print("Error al eliminar etapa: ", e)

    def onStageItemChanged(self, item):
        try:
            if (len(self.stages)):
                index = self.Stage_List.row(item)
                self.stages[index][1] = item.checkState() == QtCore.Qt.Checked

            self.drawStages()
        except Exception as e:
            print("Error al actualizar etapa: ", e)

    def drawStages(self):

        try:
            self.TF_Modulo.axes.clear()
            self.TF_FASE.axes.clear()

            if (len(self.stages)):
                self.drawHs(axMod = self.TF_Modulo.axes, axFase = self.TF_FASE.axes, H = np.array(self.stages)[:,0],
                            visibilidad = np.array(self.stages)[:,1], mode = self.Seleccionadas_RB.isChecked())
                self.TF_Modulo.draw()
                self.TF_FASE.draw()
        except Exception as e:
            print("Error al dibujar etapas: ", e)

    def drawHs(self, axMod, axFase, H, visibilidad, mode=0):
        # 0 = "Total"; 1 = "Individual"
        try:
            if mode == 1:                           #Grafico todas por separado
                for i in range(len(H)):
                    if visibilidad[i] == True:
                        color = 'C' + str(i)
                        w, mag, fase = ss.bode(H[i], w=np.logspace(-1, 7, num=14000))
                        aten = -mag 
                        freq = w/(2*np.pi)

                        axMod.plot(freq, aten, color=color)
                        axFase.plot(freq, fase, color=color)
            
            if mode == 0:                           #Grafico la final
                num=[1]; den=[1]
                
                for i in range(len(H)):
                    num = np.polymul(num, H[i].num)
                    den = np.polymul(den, H[i].den)

                Hfinal= ss.TransferFunction(num,den)    
                w, mag, fase = ss.bode(Hfinal, w=np.logspace(-1, 7, num=14000))
                aten = -mag 
                freq = w/(2*np.pi)

                axMod.plot(freq, aten, color="b")
                axFase.plot(freq, fase, color="b")

            axMod.set_xlabel(r'$Frecuencia\ [Hz]$', fontsize=10)
            axMod.set_ylabel(r'$Atenuación\ [dB]$', fontsize=10)
            axMod.set_title('Atenuación', fontsize=15)
            axMod.set_xscale('log')
            axMod.grid(which='both', zorder=0)

            axFase.set_xlabel(r'$Frecuencia\ [Hz]$', fontsize=10)
            axFase.set_ylabel(r'$Fase\ [°]$', fontsize=10)
            axFase.set_title('Fase', fontsize=15)
            axFase.set_xscale('log')
            axFase.grid(which='both', zorder=0)
        except Exception as e:
            print("Error al graficar transferencias: ", e)

    # def findK(self, Zeros,Poles):
    #     den=num=1

    #     isArr = True if isinstance(z, list) else False

    #     for z in Zeros:
    #         if len(z)==2:
    #             num=num*z[1]
    #             num=num*z[0]
    #         elif len(z)==1:
    #             num=num*z

    #     for p in Poles:
    #         if len(p)==2:
    #             den=den*p[1]
    #             den=den*p[0]
    #         elif len(p)==1:
    #             den=den*p

    #     return num/den
