import scipy.signal as ss
import scipy.special as sp
import numpy as np
import math as mt

def bessel_(wrg, retGroup, tol=0.1, N=[0,15]):
    tau= retGroup*1e-6
    success=0
    for n in range(max(N[0],1), N[1]+1):
        bn,an = ss.bessel(n, 1/tau, btype="lowpass", analog=True, output='ba', norm='delay')
        w, h = ss.freqs(bn, an, worN=np.linspace(wrg*0.99, wrg*1.01, num=3))
        retGroup_ = -np.diff(np.unwrap(np.angle(h)))/np.diff(w) # Calculo del retardo de grupo en wrg
        if retGroup_[1] >= tau*(1-tol):
            success=1
            break

    if success==1:
        z,p,k = ss.tf2zpk(bn,an)
        # p=p[p.imag<=0]  # Elimina polos del semiplano derecho
    else: 
        z=p=k=0
    return z,p,k 

def legendre_(w, aten, desnorm, filter_type, N=[0,15]):
    if filter_type == 'highpass':
        w = w[::-1]     # [ wa, wp ]
    elif filter_type == 'bandpass':
        w = [ w[0][1] - w[0][0], w[1][1] - w[1][0] ]   # [ (wp+ - wp-), (wa+ - wa-) ]
    elif filter_type == 'bandstop':
        w = [ w[1][1] - w[1][0], w[0][1] - w[0][0] ]   # [ (wa+ - wa-), (wp+ - wp-) ]

    print("Entro a Legendre.")
    print("w= ", w)
    print("aten= ", aten)

    wx = w[0]*(w[1]/w[0])**desnorm                 # Calculamos la frecuencia deseada
    Ax = aten[0]+(aten[1]-aten[0])*desnorm         # Calculamos al atenuación en la frecuencia deseada
    epsilon= np.sqrt(10**(Ax/10)-1)                # Calculamos el epsilon para la frec deseada
    
    print("wx = ", wx)
    print("Ax = ", Ax)
    print("E = ", epsilon)

    ord=0
    for n in range(max(N[0],1), N[1]+1):
        Lp= np.polyval(LegenPol2(n), (w[0]/wx)**2)            # Pol de Legendre en wp
        La= np.polyval(LegenPol2(n), (w[1]/wx)**2)            # Pol de Legendre en wa
        
        print("Pruebo n=", n)
        print("Lp= ", Lp, " La= ", La)

        # if Lp <= np.log10((10**(aten[0]/10)-1)/epsilon**2) and La >= np.log10((10**(aten[1]/10)-1)/epsilon**2):
        if Lp <= (10**(aten[0]/10)-1)/(epsilon**2) and La >= (10**(aten[1]/10)-1)/(epsilon**2):
            ord=n
            break

    if ord != 0:
        a=[1]; b= np.polyadd(np.poly1d([1]), (epsilon**2)*LegenPol2(n))
        z,p,k=ss.tf2zpk(a,b)
        p=p[p.real<=0]  # Elimina polos del semiplano derecho 
        #return z,p,k
        return transform(z,p,k, wx, w, filter_type)
    else:
        print("Algo malio sal")
        return 0,0,0

#TODO: gauss Módulo
#def gauss_(w, aten, desnorm, filter_type, N=[0,15]):
    # Ax = aten[0]+(aten[1]-aten[0])*desnorm  # Calculamos al atenuación en la frecuencia deseada
    # wx = 10**(np.log10(w[0])-desnorm*np.log10(w[1]/w[0]))     # Calculamos la frecuencia deseada
    # epsilon= np.sqrt(10**(Ax/10)-1)         # Calculamos el epsilon para la frec deseada
    # ord=0
    
    # for n in range(max(N[0],1), N[1]+1):
    #     Gp= np.polyval(gaussPol(n), w[0]**2) # Pol de Legendre en wp
    #     Ga= np.polyval(gaussPol(n), w[1]**2) # Pol de Legendre en wa
    #     if Gp <= np.log10((10**(aten[0]/10)-1)/epsilon**2) and Ga >= np.log10((10**(aten[1]/10)-1)/epsilon**2):
    #         ord=n
    #         break

    # if ord != 0:
    #     a=[1]; b= np.polyadd(np.poly1d([1]), (epsilon**2)*gaussPol(n))
    #     z,p,k=ss.tf2zpk(a,b)
    #     p=p[p.imag<=0]  # Elimina polos del semiplano derecho 
    #     return transform(z, p, k, wx, w, filter_type)
    # else:
    #     return 0

def gauss_(wrg, retGroup, tol=0.1, N=[0,15]):
    tau= retGroup*1e-6
    success=0
    num=den=[]

    for n in range(max(N[0],1), N[1]+1):
        num=[1]; den= np.polyadd(np.poly1d([1]), gaussPol(n))
        w,h = ss.freqs(num, den, worN=np.linspace(wrg*0.99, wrg*1.01, num=3))
        retGroup_ = -np.diff(np.unwrap(np.angle(h)))/np.diff(w) # Calculo del retardo de grupo en wrg
        if retGroup_[1]>= tau*(1-tol):
            success=1
            break

    if success==1:
        z,p,k = ss.tf2zpk(num,den)
        p=p[p.imag<=0]  # Elimina polos del semiplano derecho
        return z,p,k
        
    else: 
        return 0,0,0


def gaussPol(n):    
    # Genera un arreglo con los coeficientes del Pol de Gauss.
    pol=np.zeros(n*2+1)
    for i in range(1,n+1):
        pol[int(i*2)]= 1/mt.factorial(i)
    return pol[::-1]

def transform(z, p, k, wx, w,filter_type):
    if filter_type == 'lowpass':
        z,p,k=ss.lp2lp_zpk(z,p,k,wx)
    elif filter_type == 'highpass':
        z,p,k=ss.lp2hp_zpk(z,p,k,wx)
    elif filter_type == 'bandpass':
        w0=mt.sqrt(w[0][1]*w[0][0])
        BW= (w[0][1]-w[0][0])/w0   
        z,p,k=ss.lp2bp_zpk(z,p,k,w0,BW)    
    elif filter_type == 'bandstop':
        w0=mt.sqrt(w[1]*w[0])
        BW= (w[1]-w[0])/w0 
        z,p,k=ss.lp2bs_zpk(z,p,k,w0,BW)   
    return z,p,k

def Wnorm(wa,wp,tipo):
    normalizaciones={
        "lowpass": wa/wp,
        "highpass": wp/wa,
        "bandpass": (wa[1]-wa[0])/(wp[1]-wp[0]),
        "bandstop": (wp[1]-wp[0])/(wa[1]-wa[0]),
    }
    return normalizaciones[tipo]

# Calcula el polinomio de legendre de orden n de w**2
def LegenPol(n):
#   n=5
  pol1=sp.legendre(n)
  pol2=np.zeros(2*n+1)

  for i in range(0,n+1,1):
    pol2[i*2]=pol1[i]
  pol2=pol2[::-1]
  
  print("Legendre(",n,"): ", np.array(pol1))
  print("LegenPol(",n,"): ", pol2)

  return pol2

# Calcula el polinomio de legendre de orden n
def LegenPol2(n):
        if n == 0:
            return [0]

        if n % 2:                           # Si n es impar 
            k = (n - 1) // 2
            a0 = 1 / (np.sqrt(2) * (k + 1))

            poly = np.poly1d([a0])
            for i in range(1, k + 1):       # Sumatoria
                new_term = a0 * (2 * i + 1) * sp.legendre(i)
                poly = np.polyadd(poly, new_term)
            poly = np.polymul(poly, poly)   # Elevo al cuadrado

        else:                               # Si n es par
            k = (n - 2) // 2
            if k % 2:                       # Si K es impar
                a1 = 3 / np.sqrt((k + 1) * (k + 2))
                poly = np.poly1d(0)         # Creo un np array

                for i in range(1, k + 1):   # Sumatoria
                    if i % 2:               # i impar
                        new_term = a1 * (2 * i + 1)/3 * sp.legendre(i)
                        poly = np.polyadd(poly, new_term)

            else:                           # Si K es par
                a0 = 1 / np.sqrt((k + 1) * (k + 2))
                poly = np.poly1d(a0)        # Creamos un numpy poly

                for i in range(1, k + 1):   # Sumatoria
                    if not i % 2:           # Terminos con i par
                        new_term = a0 * (2 * i + 1) * sp.legendre(i)
                        poly = np.polyadd(poly, new_term)

            poly = np.polymul(poly, poly)  # Elevo al cuadrado
            poly = np.polymul(poly, np.poly1d([1, 1]))  # Multiplico por (x + 1)

        poly = np.polyint(poly)     # Integro
        x1 = np.poly1d([-1])        # Límite inferior
        x2 = np.poly1d([2, 0, -1])  # Límite superior

        return np.polysub(np.polyval(poly, x2), np.polyval(poly, x1))
    