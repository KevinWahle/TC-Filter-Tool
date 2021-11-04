import matplotlib.pyplot as plt
import scipy.signal as ss
import numpy as np

# Given the axes, and the filter, plot the templates of the filter
def drawTemplate(ax, filter, index=0, alpha=0.5):
    ftype = filter.filter_type
    color = 'C' + str(index)

    # print("Drawing filter: " + ftype)
    # print("Color: " + color)

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
        w, mag, fase = ss.bode(H, w=np.logspace(-10, 6, num=12000))
        aten = -mag
        freq = w/(2*np.pi)
        # Atenuacion
        print("Dibujo Ateniacion")
        axes[0].plot(freq, aten, color=color, label=filter.name)
        axes[0].legend()
        axes[0].set_xscale('log')
        axes[0].grid(which='both', zorder=0)

        # Fase
        print("Dibujo fase")
        axes[1].plot(freq, fase, color=color, label=filter.name)
        axes[1].legend()
        axes[1].set_xscale('log')
        axes[1].grid(which='both', zorder=0)

        # Retardo de grupo
        print("Dibujo retardo")
        delay = -np.diff(np.unwrap(fase))/np.diff(w)     # Calculo del retardo de grupo, en funcion de w
        freqDelay = freq[:-1]   # Tiene un valor menos
        axes[2].plot(freqDelay, delay, color=color, label=filter.name)    # Pero lo gafico en funcoin de freq
        axes[2].legend()
        # axes[2].set_xscale('log')
        axes[2].grid(which='both', zorder=0)

        #TODO: Polos y ceros
        zeros, poles = H.zeros, H.poles

        axes[3].scatter(np.real(zeros), np.imag(zeros), c=color, marker="o", label=filter.name)
        axes[3].scatter(np.real(poles), np.imag(poles), c=color, marker="x")
        axes[3].set_xlabel(r'$\sigma$', fontsize=15)
        axes[3].set_ylabel(r'$jw$', fontsize=15)
        axes[3].set_title('Gráfico Polos y Ceros')
        axes[3].grid(True)
        axes[3].legend()

        return 0

    except Exception as e:
        print("Error drawing filter: " + str(e))
        return -1

# Grafica arreglo de filtros en todos los ejes
def drawFilters(filters, ax):
    for i in range(len(filters)):
        drawingFilter(filters[i], ax, i)