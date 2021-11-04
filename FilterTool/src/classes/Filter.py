import scipy.signal as ss
import numpy as np
import Filteraux as aux

class Filter:
    def __init__(self, name, filter_type, approx, gain, freqs, aten=[0,0], N=None, qmax=None, 
                retardo=0, desnorm=0.5, tol = 0.1):
        self.name = name
        self.filter_type = filter_type      # ‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’
        self.approx = approx                # "butter", "bessel", "cheby1", "cheby2", "ellip", "legendre", "gauss"
        self.gain = gain                    # NO se usa
        self.A = aten                       # [Ap , Aa]
        self.freqs = freqs                  # [[fp-, fp+], [fa-, fa+] ] o [fp, fa]
        self.N = N                          # [Nmin, Nmax]
        self.qmax = qmax                    # TODO: ¿Como hacemo?
        self.ret = retardo                  # Se carga en us 
        self.desnorm = desnorm
        self.tol= tol       # Para Bessel
        self.z = []
        self.p = []
        self.k = 0


        if (self.approx == 'butter'):
            ord, wn = ss.buttord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.z, self.p, self.k = ss.butter(ord, wn, btype=self.filter_type, analog=True, output='zpk')
            else:
                pass 

        elif (self.approx == 'cheby1'):
            ord, wn = ss.cheb1ord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.z, self.p, self.k = ss.cheby1(ord, self.A[0], wn, btype=self.filter_type, analog=True, output='zpk')
            else:
                pass

        elif (self.approx == 'cheby2'):
            ord, wn = ss.cheb2ord(2*np.pi*self.freqs[1], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.z, self.p, self.k = ss.cheby2(ord, self.A[1], wn, btype=self.filter_type, analog=True, output='zpk')
            else:
                pass

        elif (self.approx == 'ellip'):
            ord, wn = ss.ellipord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.z, self.p, self.k = ss.ellip(ord, self.A[0], self.A[1], wn, btype=self.filter_type, analog=True, output='zpk')
            else:
                pass

        elif (self.approx == 'bessel'):
            self.z, self.p, self.k = aux.bessel_(self.freqs, self.filter_type, self.ret, self.tol, self.N[1])
            
        elif (self.approx == 'legendre'):
            self.z, self.p, self.k = aux.legendre_(self.w, aten=self.A, desnorm=self.desnorm, filter_type=self.filter_type, Nmax=N[1])

        elif (self.approx == 'gauss'):
            self.z, self.p, self.k = aux.gauss_(self.w, aten=self.A, desnorm=self.desnorm, filter_type=self.filter_type, Nmax=N[1])
        else:
            raise ValueError("Error en el ingreso de la aproximación")
        
        print(ord, wn)
        print(ss.sos2tf(self.sos))
        print(self.sos)