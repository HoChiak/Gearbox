import numpy as np
from scipy.io import wavfile
from scipy.fftpack import rfft,rfftfreq
from scipy.signal import tukey, find_peaks
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from scipy.stats import kurtosis

def get_gcd(a, b):
    """
    Method to compute the greatest common
    divisor of a and b
    """
    while b > 0:
        a, b = b, a % b
    return(a)

def get_lcm(a, b):
    """
    Method to get the lowest common
    multiple of a and b
    """
    return(a * b / get_gcd(a, b))

def get_sample_time_torque(rotational_frequency_in, sample_rate, no_teeth_in, no_teeth_out):
    """
    Method to get a sample time vector for
    the torque definition.
    """
    # Get meshing time between two tooth
    time2tooth = (1 / rotational_frequency_in) / no_teeth_in
    # Get lowest common multiple
    toothmeshlcm = get_lcm(no_teeth_in,
                           no_teeth_out)
    min_time = time2tooth * toothmeshlcm
    min_time

    sample_time = np.arange(0, min_time, 1/sample_rate)
    return(sample_time)

def rfft_y(array, alpha, sample_rate, pp, scale=False):
    #change file format
    array = np.array(array)
    yt = np.ravel(array)
    #tukey window
    yt = yt * (tukey(yt.shape[0], alpha, sym=True))
    #scale to max(abs())=1
    if scale is True:
        scaler = StandardScaler(copy=False, with_mean=False, with_std=True)
        yt = scaler.fit_transform(yt.reshape(-1, 1))
    #rfft
    yf = np.abs(rfft(yt, n=sample_rate, axis=0))
    xf = rfftfreq(sample_rate, d=1./sample_rate).reshape(-1, 1)
    #max pooling
    if yf.shape[0]%pp!=0:
        num_pad = (yf.shape[0]//pp) * pp + pp - yf.shape[0]
        yf_mp = np.pad(yf[:, 0], (0, num_pad), 'constant').reshape(-1, pp)
    else:
        yf_mp = yf.reshape(-1, pp)
    yf_mp = np.max(yf_mp, axis=1)
    fac_xf = (np.max(xf, axis=0) - np.min(xf, axis=0))/xf.shape[0] # stepsize xf
    xf_mp = np.arange((pp//2) * fac_xf,(yf_mp.shape[0]*pp) * fac_xf + 1, pp * fac_xf)
    return(yf_mp, xf_mp)
