import scipy.signal as ss
import numpy as np

class Filter:
    def __init__(self, name, filter_type, approx, gain, aten, freqs, N=None, qmax=None, desnorm=0.5):
        self.name = name
        self.filter_type = filter_type
        self.approx = approx        # "butter", "bessel", "cheby1", "cheby2", "ellip", "legendre", "gauss"
        self.gain = gain
        self.A = aten       # [Ap , Aa]
        self.freqs = freqs  # [[fp-, fp+], [fa-, fa+] ] o [fp, fa]
        self.N = N          # [Nmin, Nmax]
        self.qmax = qmax
        self.desnorm = desnorm

        if (approx == 'butter'):
            ord, wn = ss.buttord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                print("the house is in order")
                self.sos = ss.butter(ord, wn, btype=self.filter_type, analog=True, output='sos')
                a, b = ss.butter(ord, wn, btype=self.filter_type, analog=True)
            else:
                pass 

        elif (approx == 'cheby1'):
            ord, wn = ss.cheb1ord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.sos = ss.cheby1(ord, self.A[0], wn, btype=self.filter_type, analog=True, output='sos')
            else:
                pass

        elif (approx == 'cheby2'):
            ord, wn = ss.cheb2ord(2*np.pi*self.freqs[1], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.sos = ss.cheby2(ord, self.A[1], wn, btype=self.filter_type, analog=True, output='sos')
            else:
                pass

        elif (approx == 'ellip'):
            ord, wn = ss.ellipord(2*np.pi*self.freqs[1], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                print("the house is in order")
                self.sos = ss.ellip(ord, self.A[0], self.A[1], wn, btype=self.filter_type, analog=True, output='sos')
            else:
                pass
        # elif (approx == 'bessel'):
        #     self.sos = ss.bessel(ord, wn, btype=self.filter_type, analog=True, output='sos')

        #     if ord in range(self.N[0], self.N[1]):
        #         self.sos = ss.bessel(ord, wn, btype=self.filter_type, analog=True, output='sos')

        #     else:
        #         pass
            
        elif (approx == 'legendre'):
            pass
        elif (approx == 'gauss'):
            pass
        else:
            raise ValueError("Error en el ingreso de la aproximación")
        
        print(ord, wn)
        print(ss.sos2tf(self.sos))
        print(self.sos)
        print(a,b)
