import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
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

def plot_gear_polar(df, kind='order', no_teeth=None, **kwargs):
    """
    Function to plot different kinds of
    visualisation on the gear wheel
    """
    if no_teeth is not None:
        missing = pd.DataFrame([i for i in range(1, no_teeth, 1) if i not in df['tooth'].to_list()])
        missing.columns = ['tooth']
        df = df.append(missing, sort=False).fillna(0)
    tooth = df['tooth']
    if kind is 'order':
        """
        state0 dataframe must be given
        """
        order = pd.Series(df.index.values)
        order.rename('order', inplace=True)
        tooth_order = pd.concat([tooth, order], axis=1).sort_values('tooth')['order'].to_numpy()
        radii = tooth_order + 1
        no_teeth = df.shape[0]
        #rticks
        radii_max = max(radii)
        rticks = np.arange(2, radii_max+1, 2)
        colors = plt.cm.hot(radii / (radii_max * 1.35))

    elif kind is 'pitting':
        """
        last entry of df must be pitting size
        """
        try:
            assert kwargs['key'] in df.columns, 'Using kind="pitting" argument key="keyword" must be given specifying a column of df'
        except (KeyError): 'Using kind="pitting" argument key="keyword" must be given'
        pitting = df[kwargs['key']]
        pitting_order = pd.concat([tooth, pitting], axis=1).sort_values('tooth')[kwargs['key']].to_numpy()
        radii = pitting_order
        no_teeth = df.shape[0]
        #rticks
        radii_max = max(radii)
        if radii_max < 2:
            increment = 0.25
        elif radii_max < 5:
            increment = 0.5
        else:
            increment = 1
        rticks = np.arange(0, radii_max, increment)
        colors = plt.cm.hot_r(radii / (radii_max * 1.35))
    elif kind is 'pitting_growth':
        """
        last entry of df must be pitting size
        """
        try:
            assert kwargs['key1'] in df.columns, 'Using kind="pitting_growth" argument key1="keyword" must be given specifying a column of df'
            assert kwargs['key2'] in df.columns, 'Using kind="pitting_growth" argument key2="keyword" must be given specifying a column of df'
        except (KeyError): 'Using kind="pitting_growth" argument key1="keyword" and key2="keyword" must be given'
        pitting1 = df[kwargs['key1']]
        pitting2 = df[kwargs['key2']]
        pitting1_order = pd.concat([tooth, pitting1], axis=1).sort_values('tooth')[kwargs['key1']].to_numpy()
        pitting2_order = pd.concat([tooth, pitting2], axis=1).sort_values('tooth')[kwargs['key2']].to_numpy()
        radii = pitting1_order
        radii2 = pitting2_order
        no_teeth = df.shape[0]
        #rticks
        radii_max = max([max(radii), max(radii2)])
        if radii_max < 2:
            increment = 0.25
        elif radii_max < 5:
            increment = 0.5
        else:
            increment = 1
        rticks = np.arange(0, radii_max, increment)
        colors = plt.cm.hot_r(radii / (radii_max * 1.35))

    else:
        raise KeyError('given "kind" doesnt exist')

    # Compute pie slices
    thetas = np.linspace(0.0, 2 * np.pi, no_teeth, endpoint=False)
    width = 2 * np.pi / no_teeth * np.ones(no_teeth) - (2 * np.pi / no_teeth / 10)

    if kind is 'pitting_growth':
        ax = plt.subplot(111, projection='polar');
        colors2 = plt.cm.hot_r(radii2 / (radii_max * 1.35))
        ax.bar(thetas, radii2, width=width, bottom=0.0, color=colors2, alpha=0.5, edgecolor='black');
    else:
        ax = plt.subplot(111, projection='polar');

    ax.bar(thetas, radii, width=width, bottom=0.0, color=colors, alpha=0.5, edgecolor='black');


    # change radius ticks
    ax.set_xticks(thetas)
    xtick_pos = plt.xticks()[0]
    xtick_lab = ['T %i' % (i+1) for i in range(no_teeth)]
    plt.xticks(xtick_pos, xtick_lab)
    #ax.set_xlabel_position(+90)

    ax.set_rticks(rticks)
    ax.set_rlabel_position(+90)  # Move radial labels away from plotted line

    plt.show()
