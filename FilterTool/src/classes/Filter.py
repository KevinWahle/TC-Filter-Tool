import scipy.signal as ss
import numpy as np
import Filteraux

class Filter:
    def __init__(self, name, filter_type, approx, gain, aten, freqs, N=None, qmax=None, desnorm=0.5, tol = 10):
        self.name = name
        self.filter_type = filter_type # ‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’
        self.approx = approx        # "butter", "bessel", "cheby1", "cheby2", "ellip", "legendre", "gauss"
        self.gain = gain
        self.A = aten       # [Ap , Aa]
        self.freqs = freqs  # [[fp-, fp+], [fa-, fa+] ] o [fp, fa]
        self.N = N          # [Nmin, Nmax]
        self.qmax = qmax
        self.desnorm = desnorm
        self.tol= tol       # Para Bessel
        self.num = []
        self.den = []
        self.z = []
        self.p = []
        self.k = 0

        # Calculo del epsilon ...
        epsilon = 0

        if (approx == 'butter'):
            ord, wn = ss.buttord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.sos = ss.butter(ord, wn, btype=self.filter_type, analog=True, output='sos')
                a, b = ss.butter(ord, wn, btype=self.filter_type, analog=True)
            else:
                pass 

        elif (approx == 'cheby1'):
            ord, wn = ss.cheb1ord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.z, self.p, self.k = ss.cheby1(ord, self.A[0], wn, btype=self.filter_type, analog=True, output='zpk')
            else:
                pass

        elif (approx == 'cheby2'):
            ord, wn = ss.cheb2ord(2*np.pi*self.freqs[1], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.z, self.p, self.k = ss.cheby2(ord, self.A[1], wn, btype=self.filter_type, analog=True, output='zpk')
            else:
                pass

        elif (approx == 'ellip'):
            ord, wn = ss.ellipord(2*np.pi*self.freqs[1], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.z, self.p, self.k = ss.ellip(ord, self.A[0], self.A[1], wn, btype=self.filter_type, analog=True, output='zpk')
            else:
                pass

        elif (approx == 'bessel'):
            ord, wn = ss.besselord(2*np.pi*self.freqs[0], btype=self.filter_type, tol= self.tol)

            if ord in range(self.N[0], self.N[1]):
                self.z, self.p, self.k = ss.bessel(ord, wn, btype=self.filter_type, analog=True, output='sos', output='zpk')            
                
            else:
                pass
            
        elif (approx == 'legendre'):
            n=legenord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], epsilon, self.A[1], self.filter_type)
            a=[1]; b= np.polyadd(np.poly1d([1]), (epsilon**2)*ss.legendre(n))

        elif (approx == 'gauss'):
            pass
        else:
            raise ValueError("Error en el ingreso de la aproximación")
        
        print(ord, wn)
        print(ss.sos2tf(self.sos))
        print(self.sos)
        print(a,b)

def legenord(wa, wp, epsilon, aten, filter_type, Nmax=25):
    for n in range(Nmax):
        L= np.polyval(ss.legendre(n), Wnorm(wa, wp, filter_type)**2)
        if L>= np.log10((10**(aten/10)-1)/epsilon**2):
            ord=n
            wn=?
    return ord, wn

            

def Wnorm(wa,wp,tipo):
    normalizaciones={
        "lowpass": wa/wp,
        "highpass": wp/wa,
        "bandpass": (wa[1]-wa[0])/(wp[1]-wp[0]),
        "bandstop": (wp[1]-wp[0])/(wa[1]-wa[0]),
    }
    return normalizaciones[tipo]











def nearIndex(w, woNorm):       
    # Averiguo cual es el índice de la frecuencia dentro de w  
    # más cercano a la normalizada
    diff = []
    for frec in w:
        diff.append(abs(w-woNorm))
    return diff.index(min(frec)) 

def besselord(wo, btype, retGroup, tol=0.1,Nmax=25):
    #retGroup viene en us
    woNorm = wo*retGroup*1e-6   # TODO: revisar en que viene el retardo
    for n in range(0,Nmax):
        bn,an = ss.bessel(n, 1, btype=btype, analog=True, output='ba', norm='delay')
        w,h = ss.freqs(bn,an,worN=np.logspace(-1, np.log10(woNorm)+1, num=20*np.log10(woNorm)))
        #retGroup_f = -np.diff(np.unwrap(np.angle(h)))/np.diff(w)   #el retardo de grupo es la derivada de la fase respecto de w
        retGroupN = ss.group_delay((bn,an), w=w) 
        if retGroupN[nearIndex(w, woNorm)] >= (1-tol):
            break
    return n, 1/(retGroup*1e-6)