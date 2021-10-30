import numpy as np
from scipy.special import legendre
from scipy.signal import cheby1, cheb1ord

#Legendre Low pass filter approximation
def LegendreLP(fa, fp, Aa, Ap):
    n = min(fa,fp)      # Obvio que esto no es asi
    poly = legendre(n)


# Chebychev Low pass filter approximation
def ChebychevLP(fa, fp, Aa, Ap):
    n, wc = cheb1ord(wp = 2*np.pi*fp, ws = 2*np.pi*fa, gpass = Ap, gstop = Aa)
    poly = cheby1(n, Aa, 2*np.pi*fa)