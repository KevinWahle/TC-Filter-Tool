import matplotlib.pyplot as plt
import scipy.signal as ss
import numpy as np

# Given the axes, and the filter, plot the templates of the filter
def drawTemplate(ax, filter, index=0, alpha=0.5):
    ftype = filter.filter_type
    color = 'C' + str(index)

    # print("Drawing filter: " + ftype)
    # print("Color: " + color)

    filter.A = np.array(filter.A) - filter.gain

    boxes = []

    if ftype == 'lowpass':
        boxes.append(ax.add_patch(plt.Rectangle((0, filter.A[0]), filter.freqs[0], 100, alpha=alpha, color=color)))
        boxes.append(ax.add_patch(plt.Rectangle((filter.freqs[1], 0), 1e6, filter.A[1], alpha=alpha, color=color)))
    elif ftype == 'highpass':
        boxes.append(ax.add_patch(plt.Rectangle((0, 0), filter.freqs[1], filter.A[1],  alpha=alpha, color=color)))
        boxes.append(ax.add_patch(plt.Rectangle((filter.freqs[0], filter.A[0]), 1e6, 100, alpha=alpha, color=color)))
    elif ftype == 'bandpass':
        boxes.append(ax.add_patch(plt.Rectangle((0, 0), filter.freqs[1][0], filter.A[1], alpha=alpha, color=color)))
        boxes.append(ax.add_patch(plt.Rectangle((filter.freqs[0][0], filter.A[0]), filter.freqs[0][1] - filter.freqs[0][0], 100, alpha=alpha, color=color)))
        boxes.append(ax.add_patch(plt.Rectangle((filter.freqs[1][1], 0), 1e6, filter.A[1], alpha=alpha, color=color)))
    elif ftype == 'bandstop':
        boxes.append(ax.add_patch(plt.Rectangle((0, filter.A[0]), filter.freqs[0][0], 100, alpha=alpha, color=color)))
        boxes.append(ax.add_patch(plt.Rectangle((filter.freqs[1][0], 0), filter.freqs[1][1] - filter.freqs[1][0], filter.A[1], alpha=alpha, color=color)))
        boxes.append(ax.add_patch(plt.Rectangle((filter.freqs[0][1], filter.A[0]), 1e6, 100, alpha=alpha, color=color)))
    elif ftype == 'groupdelay':
        boxes.append(ax.add_patch(plt.Rectangle((0, 0), filter.freqs, filter.ret*1e-6*(1-filter.tol), alpha=alpha, color=color)))

    return boxes

# Grafica un filtro en todos los ejes
def drawingFilter(filter, axes, index):    # axes = [ Aten, Fase, Retardo de Grupo, Polos y ceros, ¿Q? ]
    try:
        color = 'C' + str(index)
        H = filter.getTF()
        w, mag, fase = ss.bode(H, w=np.logspace(-1, 7, num=14000))
        aten = -mag
        freq = w/(2*np.pi)
        # Atenuacion
        # print("Dibujo Atenuacion")
        # axes[0].plot(w, aten, color=color, label=filter.name)            # OJO!!! DIBUJO EN RADIANES
        axes[0].plot(freq, aten, color=color, label=filter.name)
        

        # Fase
        # print("Dibujo fase")
        axes[1].plot(freq, fase, color=color, label=filter.name)
        

        # Retardo de grupo
        # print("Dibujo retardo")
        delay = -np.diff(np.unwrap(fase*np.pi/180))/np.diff(w)     # Calculo del retardo de grupo, en funcion de w
        freqDelay = freq[1:]   # Tiene un valor menos
        delay = delay*1e6
        axes[2].plot(freqDelay, delay, color=color, label=filter.name)    # Pero lo gafico en funcoin de freq
        

        #TODO: Polos y ceros
        zeros, poles = H.zeros, H.poles

        axes[3].scatter(np.real(zeros), np.imag(zeros), c=color, marker="o", label=filter.name)
        axes[3].scatter(np.real(poles), np.imag(poles), c=color, marker="x")

        return 0

    except Exception as e:
        print("Error drawing filter: " + str(e))
        return -1

# Grafica arreglo de filtros en todos los ejes
def drawingFilters(filters, ax):   # axes = [ Aten, Fase, Retardo de Grupo, Polos y ceros ]
    for i in range(len(filters)):
        if filters[i].visible == True:
            drawingFilter(filters[i], ax, i)
        else:
            pass

    ax[0].set_xlabel(r'$Frecuencia\ [Hz]$', fontsize=10)
    ax[0].set_ylabel(r'$Atenuación\ [dB]$', fontsize=10)
    ax[0].set_title('Atenuación', fontsize=15)
    ax[0].set_xscale('log')
    ax[0].grid(which='both', zorder=0)
    ax[0].legend()

    ax[1].set_xlabel(r'$Frecuencia\ [Hz]$', fontsize=10)
    ax[1].set_ylabel(r'$Fase\ [°]$', fontsize=10)
    ax[1].set_title('Fase', fontsize=15)
    ax[1].legend()
    ax[1].set_xscale('log')
    ax[1].grid(which='both', zorder=0)
    
    ax[2].set_xlabel(r'$Frecuencia\ [Hz]$', fontsize=10)
    ax[2].set_ylabel(r'$Retardo\ [\mu s]$', fontsize=10)
    ax[2].set_title('Retardo', fontsize=15)
    ax[2].set_xscale('log')
    ax[2].grid(which='both', zorder=0)
    ax[2].legend()
    
    ax[3].set_xlabel(r'$\sigma$', fontsize=15)
    ax[3].set_ylabel(r'$j \omega$', fontsize=15)
    ax[3].set_title('Gráfico Polos y Ceros')
    ax[3].grid(which='both', zorder=0)
    ax[3].legend()

def drawPZ(filter, ax):
    H = filter.getTF(); zeros, poles = H.zeros, H.poles

    ax.scatter(np.real(zeros), np.imag(zeros), c='b', marker="o", label=filter.name)
    ax.scatter(np.real(poles), np.imag(poles), c="r", marker="x")

    ax.set_xlabel(r'$\sigma$', fontsize=15)
    ax.set_ylabel(r'$j \omega$', fontsize=15)
    ax.set_title('Gráfico Polos y Ceros')
    ax.grid(which='both', zorder=0)
    ax.legend()



# Tex plotting de funcion transferencia

def tf2Tex(num, den) -> str:
    # print("tf: ", tf)
    # print("num: ", tf.num)
    # print("den: ", tf.den)
    return "$H(s) = \\frac{" + arrToPol(num) + "}{" + arrToPol(den) + "}$ "

def arrToPol(arr = [], var = 's'):

    # print('Entro a arrToPol. arr: ', arr)

    pol = ''
    for i in range(len(arr)):
        q = len(arr)-i-1
        if arr[i] != 0:
            if pol and arr[i] > 0:  # No es el primer elemento y es positivo
                pol += ' + '

            if abs(arr[i]) != 1 or q<1:
                base, exp = toBaseExp(arr[i])
                if (exp < -1 or exp > 3):      # Numeros muy grandes o muy chicos los muestro en notacion cienifica
                    pol += str(base) + '\\times10^{'+str(exp)+'}\ '
                else:
                    pol += "{:.2f}".format(arr[i]) + '\ '
            elif arr[i] == -1:
                pol += '-'

            if  q > 1:
                pol +=  var + '^{' + str(q) + '}'
            elif q==1:
                pol += var

    return pol if pol else '0'

def toBaseExp(num):
    str = "{:.2e}".format(num)
    return (float(str[:4]), int(str[-3:]))  # Tomo base y exponente del numero
