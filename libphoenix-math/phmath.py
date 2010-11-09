#------------------------------- phmath library----------------------
from numpy import *
from scipy import *
from scipy.optimize import leastsq
from scipy import fft as sfft       

#-------------------------- Least square fitting routines--------------

def find_frequency(x,y):   # estimate frequency, x y are numpy arrays
  mid = (max(y)+min(y))/2
  zc = []
  for k in range(1,len(y)):
    if (y[k-1] < mid) and (y[k]>mid):	# crossing middle level
      zc.append(x[k])
  if len(zc) < 2:
      return 1.0/(x[-1]-x[0])
  sum = 0.0
  np = len(zc)
  for k in range(1,np):
    sum = sum + (zc[k] - zc[k-1])
  per = sum / (np-1)
  return 1.0/per

#--Damped sinusoid -------
def dsine_erf(p,y,x):
	return y - p[0] * sin(2*pi*p[1]*x+p[2]) * exp(-p[4]*x) + p[3]

def dsine_eval(x,p):
	return     p[0] * sin(2*pi*p[1]*x+p[2]) * exp(-p[4]*x) - p[3]

def fit_dsine(data):
    size = len(data)
    x = zeros(size, float)
    y = zeros(size, float)
    for k in range(size):
        x[k] = data[k][0]
        y[k] = data[k][1]

    amp = (max(y)-min(y))/2
    freq = find_frequency(x,y)
    par = [amp, freq, 0.0, 0.0, 1.0] # Amp, freq, phase , offset, damping
    plsq = leastsq(dsine_erf, par,args=(y,x))
#    print 'Fit result = ', plsq
    y2 = dsine_eval(x, plsq[0])
    ep = [ plsq[0][0], -plsq[0][4], plsq[0][3] ]
    y3 = exp_eval(x,ep)
    for k in range(size):
        data[k].append(y2[k])
        data[k].append(y3[k])
    return data,plsq[0]

#--------------------------------------------------------------------
def sine_erf(p,y,x):
	return y - p[0] * sin(2*pi*p[1]*x+p[2])+p[3]

def sine_eval(x,p):
	return p[0] * sin(2*pi*p[1]*x+p[2])-p[3]

def fit_sine(data):
    size = len(data)
    x = zeros(size, float)
    y = zeros(size, float)
    for k in range(size):
        x[k] = data[k][0]
        y[k] = data[k][1]

    amp = (max(y)-min(y))/2
    freq = find_frequency(x,y)
    par = [amp, freq, 0.0, 0.0] # Amp, freq, phase , offset
    plsq = leastsq(sine_erf, par,args=(y,x))
    y2 = sine_eval(x, plsq[0])
    for k in range(size):
        data[k].append(y2[k])
    return data,plsq[0]

#-----------------Exponential decay fit------------------------------------
def exp_erf(p,y,x):
	return y - p[0] * exp(p[1]*x) + p[2]

def exp_eval(x,p):
	return p[0] * exp(p[1]*x)  -p[2]

def fit_exp(data):
    size = len(data)
    x = zeros(size, float)
    y = zeros(size, float)
    for k in range(size):
        x[k] = data[k][0]
        y[k] = data[k][1]
    
    maxy = max(y)
    halfmaxy = maxy / 2.0
    halftime = 1.0
    for k in range(size):
        if abs(y[k] - halfmaxy) < halfmaxy/100:
            halftime = x[k]
            break 
    par = [maxy, -halftime,0] # Amp, decay, offset
    plsq = leastsq(exp_erf, par,args=(y,x))
    y2 = exp_eval(x, plsq[0])
    for k in range(size):
        data[k].append(y2[k])
    return data,plsq[0]

#--------------------------------------------------------------------
def gauss_erf(p,y,x):#height, mean, sigma
	return y - p[0] * exp(-(x-p[1])**2 /(2.0 * p[2]**2))

def gauss_eval(x,p):
	return p[0] * exp(-(x-p[1])**2 /(2.0 * p[2]**2))

def fit_gauss(data):
    size = len(data)
    x = zeros(size, float)
    y = zeros(size, float)
    for k in range(size):
        x[k] = data[k][0]
        y[k] = data[k][1]
    
    maxy = max(y)
    halfmaxy = maxy / 2.0
    for k in range(size):
        if abs(y[k] - maxy) < maxy/100:
            mean = x[k]
            break
    for k in range(size):
        if abs(y[k] - halfmaxy) < halfmaxy/10:
            halfmaxima = x[k]
            break
                        
    sigma = mean - halfmaxima
    par = [maxy, halfmaxima, sigma] # Amplitude, mean, sigma
    plsq = leastsq(gauss_erf, par,args=(y,x))
    y2 = gauss_eval(x, plsq[0])
    for k in range(size):
        data[k].append(y2[k])
    return data,plsq[0]


#-------------Fast Fourier Transform Routines ---by Kishore A.------
def fft(data):
        """
        Returns the Fourier transform of the signal represented by the samples 
        in 'data' which is obtained by a read_block() call.
        Usage example:
        x = p.read_block(200,10,1)
        y = p.fft(x) 
        """
        np = len(data)
        delay = data[1][0] - data[0][0]  # in microseconds
        
        v = []
        for i in range(np):
            v.append(data[i][1])
        
        ft = sfft(v)
        
        #corrections in the frequency axis
        fmax = 1/(delay*1.0e-6)
        incf = fmax/np
        freq = []
        for i in range(np/2):
            freq.append(i*incf - fmax/2)
        for i in range(np/2,np):
            freq.append((i-np/2)*incf)
        
        ft_freq = []
        
        for i in range(np/2):
            x = [freq[i], abs(ft[i+np/2])/np]
            ft_freq.append(x)    
        
        for i in range(np/2,np):
            x = [freq[i], abs(ft[i-np/2])/np]
            ft_freq.append(x)
        return ft_freq                
    
def plot_fft(data):               
        """
        Plots the Fourier transform of the signal represented by the samples in
        'data'. Calls self.fft() for obtaining the Fourier Transform
        Usage example:
        x = p.read_block(200,10,1)
        p.plot_fft(x)
        """
        ft_freq = self.fft(data)
        np = len(data)
        delay = data[1][0] - data[0][0]
        fmax = 1/(delay*1.0e-6)
        
        y = 0.0
        for i in range(np):
            if data[i][1] > y:
                y = data[i][1]
                
        if self.root == None:
            self.window(400,300,None)
        self.remove_lines()
        self.set_scale(-fmax/2, 0, fmax/2, y*1.1)
        self.line(ft_freq)
    
def freq_comp(data):
        """
        Displays the frequency components with the greatest
        spectral density. Calls self.fft() for obtaining the Fourier transform
        Usage example:
        x = p.read_block(200,10,1)
        p.freq_comp(x)	# Only prints the components
              
        """
        ft_freq = self.fft(data)
        np = len(data)
        delay = data[1][0] - data[0][0]
        
        peaks = []
        for n in range(1,np-1):
            a = ft_freq[n-1][1]
            b = ft_freq[n][1]
            c = ft_freq[n+1][1]            
            if (b>50) & (b>a) & (b>c):
                peaks.append([ft_freq[n][1],ft_freq[n][0]])
                
        peaks.sort()
        peaks.reverse()
        print 'Dominant frequency components are:'
        for i in range(len(peaks)):
            print '%6.3f Hz, %5.3f mV'%(peaks[i][1],peaks[i][0])
