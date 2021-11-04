import scipy.signal as ss
import numpy as np
import math as mt

def nearIndex(w, woNorm):       
    # Averiguo cual es el índice de la frecuencia dentro de w  
    # más cercano a la normalizada
    diff = []
    for frec in w:
        diff.append(abs(w-woNorm))
    return diff.index(min(frec)) 

def bessel_(wrg, btype, retGroup, tol=0.1,Nmax=25):
    tau=retGroup*1e-6 
    success=0
    for n in range(0,Nmax):
        bn,an = ss.bessel(n, 1/tau, btype=btype, analog=True, output='ba', norm='delay')
        w,h = ss.freqs(bn, an, worN=np.linspace(wrg*0.99, wrg*1.01, n=3))
        retGroup_ = -np.diff(np.unwrap(np.angle(h)))/np.diff(w) # Calculo del retardo de grupo en wrg
        if retGroup_[1]>= tau*(1-tol):
            success=1
            break
        
    if success==1:
        z,p,k = ss.tf2zpk(bn,an)
    else: 
        z=p=k=0
    return z,p,k 

def legendre_(w, aten, desnorm, filter_type, Nmax=15):
    Ax = aten[0]+(aten[1]-aten[0])*desnorm  # Calculamos al atenuación en la frecuencia deseada
    wx = 10**(w[0]+desnorm*(w[1]-w[0]))     # TODO: Calculamos la frecuencia deseada
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


def gauss_(w, aten, desnorm, filter_type, Nmax=15):
    Ax = aten[0]+(aten[1]-aten[0])*desnorm  # Calculamos al atenuación en la frecuencia deseada
    wx = 10**(w[0]+desnorm*(w[1]-w[0]))     # TODO: Calculamos la frecuencia deseada
    ord=0
    epsilon= np.sqrt(10**(Ax/10)-1)         # Calculamos el epsilon para la frec deseada
    for n in range(Nmax):
        Gp= np.polyval(gaussPol(n), w[0]**2) # Pol de Legendre en wp
        Ga= np.polyval(gaussPol(n), w[1]**2) # Pol de Legendre en wa
        if Gp <= np.log10((10**(aten[0]/10)-1)/epsilon**2) and Ga >= np.log10((10**(aten[1]/10)-1)/epsilon**2):
            ord=n
            break

    if ord != 0:
        a=[1]; b= np.polyadd(np.poly1d([1]), (epsilon**2)*gaussPol(n))
        z,p,k=ss.tf2zpk(a,b)
        p=p[p.imag<=0]  # Elimina polos del semiplano derecho 
        return transform(z,p,k,filter_type)
    else:
        return 0

def gaussPol(n):    
    # Genera un arreglo con los coeficientes del Pol de Gauss.
    # implementar en w1^2 
    pol=[]
    for i in range(n):
        pol.append(1/mt.factorial(i))
    return pol

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