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

def drawingFilter(filter, axes, index):    # axes = [ Aten, Fase, Retardo de Grupo, Polos y ceros, ¿Q? ]
    
    color = 'C' + str(index)
    H = filter.getTF()
    w,mag,fase = ss.bode(H, w=np.logspace(0, 6, n=1200))
    aten = -mag
    freq = w/(2*np.pi)
    axes[0].plot(freq, aten, color=color, label=filter.name)
    axes[0].legend()
    axes[0].grid(which='both', zorder=0)

    return 0
