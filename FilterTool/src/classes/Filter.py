import scipy.signal as ss
import numpy as np
import Filteraux

class Filter:
    def __init__(self, name, filter_type, approx, gain, freqs, aten=[0,0], N=None, qmax=None, 
                retardo=0, desnorm=0.5, tol = 0.1):
        self.name = name
        self.filter_type = filter_type # ‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’
        self.approx = approx        # "butter", "bessel", "cheby1", "cheby2", "ellip", "legendre", "gauss"
        self.gain = gain    # NO se usa
        self.A = aten       # [Ap , Aa]
        self.freqs = freqs  # [[fp-, fp+], [fa-, fa+] ] o [fp, fa]
        self.N = N          # [Nmin, Nmax]
        self.qmax = qmax
        self.ret = retardo  # Se carga en us 
        self.desnorm = desnorm
        self.tol= tol       # Para Bessel
        self.num = []       #no se usa
        self.den = []       #no se usa
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
            ord, wn = ss.ellipord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
            
            if ord in range(self.N[0], self.N[1]):
                self.z, self.p, self.k = ss.ellip(ord, self.A[0], self.A[1], wn, btype=self.filter_type, analog=True, output='zpk')
            else:
                pass

        elif (approx == 'bessel'):
            self.z, self.p, self.k = bessel_(self.freqs, self.filter_type, self.ret, self.tol, self.N[1])
            
        elif (approx == 'legendre'):
            n=legenord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[1], self.filter_type)
            a=[1]; b= np.polyadd(np.poly1d([1]), (epsilon**2)*ss.legendre(n))
            # Aplicar transformación

        elif (approx == 'gauss'):
            pass
        else:
            raise ValueError("Error en el ingreso de la aproximación")
        
        print(ord, wn)
        print(ss.sos2tf(self.sos))
        print(self.sos)
        print(a,b)

def legendre_(w, aten, desnorm, filter_type, Nmax=25):
    Ax = aten[0]+(aten[1]-aten[0])*desnorm  # Calculamos al atenuación en la frecuencia deseada
    wx = 10**(w[0]+desnorm*(w[1]-w[0]))     # Calculamos la frecuencia deseada
    epsilon= np.sqrt(10**(Ax/10)-1)         # Calculamos el epsilon para la frec deseada
    ord=0
    for n in range(Nmax):
        Lp= np.polyval(ss.legendre(n), w[0]**2) # Pol de Legendre en wp
        La= np.polyval(ss.legendre(n), w[1]**2) # Pol de Legendre en wa
        if Lp <= np.log10((10**(aten[0]/10)-1)/epsilon**2) and La >= np.log10((10**(aten[1]/10)-1)/epsilon**2):
            ord=n
            break

    if ord != 0:
        a=[1]; b= np.polyadd(np.poly1d([1]), (epsilon**2)*ss.legendre(n))
        z,p,k=ss.tf2zpk(a,b)
        p=p[p.imag<=0]  # Elimina polos del semiplano derecho 
        return transform(z,p,k,filter_type)
    else:
        return 0



def transform(z, p, k, wx, filter_type):
    if filter_type == 'lowpass':
        z,p,k=ss.lp2lp_zpk(z,p,k,wx)
    elif filter_type == 'highpass':
        z,p,k=ss.lp2hp_zpk(z,p,k,wx)
    elif filter_type == 'bandpass':
        z,p,k=ss.lp2bp_zpk(z,p,k,wx)    # TODO: Ancho de banda?
    elif filter_type == 'bandstop': 
        z,p,k=ss.lp2bs_zpk(z,p,k,wx)    # TODO: Ancho de banda?
    return z,p,k