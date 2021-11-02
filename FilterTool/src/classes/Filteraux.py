import scipy.signal as ss
import numpy as np

def nearIndex(w, woNorm):       
    # Averiguo cual es el índice de la frecuencia dentro de w  
    # más cercano a la normalizada
    diff = []
    for frec in w:
        diff.append(abs(w-woNorm))
    return diff.index(min(frec)) 

def besselord(wo, btype, retGroup, tol=0.1,Nmax=25):
    #TODO: retGroup viene en us
    woNorm = wo*retGroup*1e-6 
    for n in range(0,Nmax):
        bn,an = ss.bessel(n, 1, btype=btype, analog=True, output='ba', norm='delay')
        w,h = ss.freqs(bn,an,worN=np.logspace(-1, np.log10(woNorm)+1, num=20*np.log10(woNorm)))
        #retGroup_f = -np.diff(np.unwrap(np.angle(h)))/np.diff(w)   #el retardo de grupo es la derivada de la fase respecto de w
        retGroupN = ss.group_delay((bn,an), w=w) 
        if retGroupN[nearIndex(w, woNorm)] >= (1-tol):
            break
    return n, 1/(retGroup*1e-6)