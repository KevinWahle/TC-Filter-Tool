import scipy.signal as ss
import scipy.special as sp
import numpy as np
import math as mt

def bessel_(wrg, retGroup, tol=0.1, N=[0,15]):
    tau= retGroup*1e-6
    success=0
    nOK=0
    for n in range(max(N[0],1), N[1]+1):
        nOK=n
        bn,an = ss.bessel(n, 1/tau, btype="lowpass", analog=True, output='ba', norm='delay')
        w, h = ss.freqs(bn, an, worN=np.linspace(wrg*0.99, wrg*1.01, num=3))
        retGroup_ = -np.diff(np.unwrap(np.angle(h)))/np.diff(w) # Calculo del retardo de grupo en wrg
        if retGroup_[1] >= tau*(1-tol):
            success=1
            break

    z,p,k = ss.tf2zpk(bn,an)
    # p=p[p.real<=0]  # Elimina polos del semiplano derecho

    return z,p,k, nOK 

def calcW(w,filter_type):
    if filter_type == 'highpass':
        # w = w[::-1]     # [ wa, wp ]
        w = [ 1/w[0], 1/w[1] ]
    elif filter_type == 'bandpass':
        w = [ w[0][1] - w[0][0], w[1][1] - w[1][0] ]   # [ (wp+ - wp-), (wa+ - wa-) ]
    elif filter_type == 'bandstop':
        w = [ w[1][1] - w[1][0], w[0][1] - w[0][0] ]   # [ (wa+ - wa-), (wp+ - wp-) ]
    return w

def legendre_(w, aten, desnorm, filter_type, N=[0,15]):
    w = calcW(w=w, filter_type=filter_type)

    print("Entro a Legendre.")
    print("w= ", w)
    print("aten= ", aten)

    #wx = w[0]*(w[1]/w[0])**desnorm                 # Calculamos la frecuencia deseada
    #Ax = aten[0]+(aten[1]-aten[0])*desnorm         # Calculamos al atenuación en la frecuencia deseada
    
    wx = w[0]
    Ax = aten[0]

    epsilon= np.sqrt(10**(Ax/10)-1)                # Calculamos el epsilon para la frec deseada
    
    print("wx = ", wx)
    print("Ax = ", Ax)
    print("E = ", epsilon)

    ord=0
    # CotaLp = (10**(aten[0]/10)-1)/(epsilon**2)
    # CotaLa = (10**(aten[1]/10)-1)/(epsilon**2)
        
    for n in range(max(N[0],1), N[1]+1):
        Lp= np.polyval(LegenPol2(n), (w[0]/wx))            # Pol de Legendre en wp
        La= np.polyval(LegenPol2(n), (w[1]/wx))            # Pol de Legendre en wa
        
        print("Pruebo n=", n)
        print("Ap= ", aten[0], "\t ALp=", -10*np.log10(1/(1+epsilon**2*Lp))) 
        print("Aa= ", aten[1], "\t ALa=", -10*np.log10(1/(1+epsilon**2*La)))
        print("Lp= ", Lp)
        print("La= ", La)

        #if Lp <= np.log10((10**(aten[0]/10)-1)/epsilon**2) and La >= np.log10((10**(aten[1]/10)-1)/epsilon**2):
        #if Lp <= CotaLp and La >= CotaLa:
        if -10*np.log10(1/(1+epsilon**2*Lp)) <= aten[0] and -10*np.log10(np.sqrt(1/(1+epsilon**2*La))) >= aten[1]:
            ord=n
            break

    a=[1]; b= np.polyadd(np.poly1d([1]), (epsilon**2)*LegenPol2(n))
    z,p,k=ss.tf2zpk(a,b)
    p=p[p.real<=0]  # Elimina polos del semiplano derecho 
    return transform(z,p,k, wx, w, filter_type), ord 


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
    num=den=[]
    nOK = 0
    # for n in range(max(N[0],1), N[1]+1):
    for n in range(max(N[0],1), 10):
        nOK = n
        num=[1]; den= np.polyadd(np.poly1d([1]), gaussPol(n))
        print(den)
        w,h = ss.freqs(num, den, worN=np.linspace(wrg*0.99, wrg*1.01, num=3))
        retGroup_ = -np.diff(np.unwrap(np.angle(h)))/np.diff(w) # Calculo del retardo de grupo en wrg
        if retGroup_[1]>= tau*(1-tol):
            break

    z,p,k = ss.tf2zpk(num,den)
    p=p[p.real<=0]  # Elimina polos del semiplano derecho
    return z, p, k, nOK

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

# Calcula el polinomio de legendre de orden n de w**2
def LegenPol(n):
  pol1=sp.legendre(n)
  pol2=np.zeros(2*n+1)

  for i in range(0,n+1,1):
    pol2[i*2]=pol1[i]
  pol2=pol2[::-1]

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
            b0 = 1 / np.sqrt((k + 1) * (k + 2))
            poly = np.poly1d([b0 if (k % 2) == 0 else 0])

            for i in range(1, k + 1):
                if ((k % 2) == 1 and (i % 2) == 0) or ((k % 2) == 0 and (i % 2) == 1):
                    continue
                bi = b0 * (2 * i + 1)
                new_poly = bi * sp.legendre(i)
                poly = np.polyadd(poly, new_poly)

            # poly = np.polymul(poly, poly)
            # poly = np.polymul(poly, np.poly1d([1, 1]))

            
            # k = (n - 2) // 2
            # if k % 2:                       # Si K es impar
            #     a1 = 3 / np.sqrt((k + 1) * (k + 2))
            #     poly = np.poly1d(0)         # Creo un np array

            #     for i in range(1, k + 1):   # Sumatoria
            #         if i % 2:               # i impar
            #             new_term = a1 * (2 * i + 1)/3 * sp.legendre(i)
            #             poly = np.polyadd(poly, new_term)

            # else:                           # Si K es impar
            #     a0 = 1 / np.sqrt((k + 1) * (k + 2))
            #     poly = np.poly1d(a0)        # Creamos un numpy poly

            #     for i in range(1, k + 1):   # Sumatoria
            #         if not i % 2:           # Terminos con i par
            #             new_term = a0 * (2 * i + 1) * sp.legendre(i)
            #             poly = np.polyadd(poly, new_term)

            poly = np.polymul(poly, poly)  # Elevo al cuadrado
            poly = np.polymul(poly, np.poly1d([1, 1]))  # Multiplico por (x + 1)

        poly = np.polyint(poly)     # Integro
        x1 = np.poly1d([-1])        # Límite inferior
        x2 = np.poly1d([2, 0, -1])  # Límite superior

        return np.polysub(np.polyval(poly, x2), np.polyval(poly, x1))

# def Wnorm(wa,wp,tipo):
#     print("TIPO:", tipo)
#     if tipo == 'lowpass':
#         return wa/wp
#     elif tipo == 'highpass':
#         return wp/wa
#     elif tipo == 'bandpass':
#         return(wa[1]-wa[0])/(wp[1]-wp[0])
#     elif tipo == "bandstop":
#         return (wp[1]-wp[0])/(wa[1]-wa[0])

# def Emin(approx, freqs, btype, A, N):
#     w = Wnorm(2*np.pi*freqs[0],2*np.pi*freqs[1], btype)

#     if approx == "butter" or approx=="ellip":
#         return np.sqrt(10 ** (A[1] / 10) - 1) / (w**N)
#     elif approx == "cheby1":
#         return np.sqrt(10 ** (A[1] / 10) - 1) / np.cosh(N*np.arcosh(w))
#     elif approx == "cheby2":
#         return 1 / (np.sqrt(10 ** (A[0] / 10) - 1))


# def Emax(approx, A):
#     if approx=="butter" or approx=="cheby1" or approx=="ellip":
#         return np.sqrt(10 ** (A[0] / 10) - 1)
#     elif approx=="cheby2":
#         return 1 / (np.sqrt(10 ** (A[1] / 10) - 1))

def gradNorm(approx, freqs, A, btype, wc, qmax, N, desnorm):
    w = calcW(w=2*np.pi*np.array(freqs), filter_type=btype)
    
    if approx == "butter":
        wc_min = w[0] * (10**(A[0]/10) -  1)**(-1/(2*N))
        wc_max = w[1] * (10**(A[1]/10) -  1)**(-1/(2*N))
        wc_ = wc_min + desnorm* (wc_max-wc_min)

    elif approx == "cheby1" or approx == "ellip":

        if approx == "cheby1": 
            a, b = ss.cheby1(N, A[0], Wn=1, analog = True, output='ba')
        if approx == "ellip": 
            a, b = ss.ellip(N, A[0], A[1], Wn=1, analog = True, output='ba')

        H_norm = ss.TransferFunction(a, b)
        wa=2*np.pi*freqs[1]
        w_values, mag_values, _ = ss.bode(H_norm, w=np.linspace(1, max(wa, 1/wa), num=100000))
        wx = [ w for w, mag in zip(w_values, mag_values) if mag <= (-A[1])]      # wa/wc

        print('wx: ', wx[0])

        wc_a = w[1] / wx[0]
        wc_ = wc + (wc_a - wc) * desnorm

    else:
        wc_ = wc


    if (btype == 'highpass'):
        wc_ = 1/wc_

    return wc_ 

def Qchecker(p, qmax):
    q_arr=[]; q_sys=0

    for pole in p:
        q = abs(abs(pole) / (2 * pole.real))    # Fórmula de Q
        q_arr.append(q)
        q_sys = np.max(q_arr)

    if qmax>0:
        if q_sys >= qmax :
            print("!Q EXCEDIDO! Qsistema = ", q_sys, "> Qmax")
            return False
        else:
            print("Q EN RANGO: Qsistema = ", q_sys, "< Qmax") 
            return True