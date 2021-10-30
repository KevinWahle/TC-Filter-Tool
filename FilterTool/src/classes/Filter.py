class Filter:
    def __init__(self, name, filter_type, approx, gain, Aa, Ap, Fa, Fp, nmin, nmax, qmax):
        self.name = name
        self.filter_type = filter_type
        self.approx = approx
        self.gain = gain
        self.Aa = Aa
        self.Ap = Ap
        self.Fa = Fa
        self.Fp = Fp
        self.nmin = nmin
        self.nmax = nmax
        self.qmax = qmax
        self.nmin = nmin
        self.nmax = nmax
        self.qmax = qmax

        if (approx == 0):
            pass
        elif (approx == 1):
            pass
        elif (approx == 2):
            pass