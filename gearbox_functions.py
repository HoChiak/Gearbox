import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from scipy.io import wavfile
from scipy.fftpack import rfft,rfftfreq
from scipy.signal import tukey, find_peaks
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from scipy.stats import kurtosis


def get_sample_time_torque(rotational_frequency_in, sample_rate, no_teeth_in, no_teeth_out):
    """
    Method to get a sample time vector for
    the torque definition.
    """
    # Get meshing time between two tooth
    time2tooth = (1 / rotational_frequency_in) / no_teeth_in
    # Get lowest common multiple
    toothmeshlcm = np.lcm(no_teeth_in,
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

def repeat2no_values(vector, no_values):
    """
    Repeat the given vector as many times needed,
    to create a repeat_vector of given number of
    values (no_values)
    """
    # Calculate number of repetitions
    no_values_vector = vector.shape[0]
    repetitions = np.ceil((no_values / no_values_vector))
    repetitions = int(repetitions) #dtype decl. not working
    # Repeat Vetor
    repeat_vector = np.tile(vector, repetitions)
    # Trim to final length
    repeat_vector = np.delete(repeat_vector,
                              np.s_[no_values:], axis=0)
    return(repeat_vector)


def get_cids(time, time_shift, time_start=0, id_start=0):
    """
    Shift a given signal by a given time shift.
    """
    # Shift signal for each gear
    ti, tv = id_start, time_start
    #shifted_signal = np.zeros((time.shape[0], 1))
    cid_list = list()
    while tv < (max(time)+time_shift):
        # Add current center id to list
        cid_list.append(ti)
        # Get new shift arguments
        tv += time_shift
        ti = np.argmin(np.abs(time - tv))
    # Remove first zero axis
    #shifted_signal = np.delete(shifted_signal, 0, 1)
    return(cid_list)



def torque_from_dict(no_teeth, rotational_frequency, sample_time, load_dict):
    """
    Method to determine an aquivalent load for each tooth.
    Returns a dictionary containing a list of mean loads
    per tooth. E.g.
    '1': [155, 177, 169,....]
    '2': [196, 155, 169,....]
    '3' ...
    ....
    """
    time2tooth = (1 / rotational_frequency) / no_teeth
    teeth_cid_list = get_cids(time=sample_time, time_shift=time2tooth,
                                  time_start=0, id_start=0)
    teeth_numbering = np.arange(1, no_teeth+0.1, 1, dtype=np.int32)
    teeth_no_list = repeat2no_values(teeth_numbering, no_values=len(teeth_cid_list))
    # Get Tooth Center IDs
    ids_array = np.array(teeth_cid_list)
    ids_array = ids_array.reshape(-1, 1)
    # Get distance between 2 tooth in no ids
    dist_ids = ids_array[1] - ids_array[0]
    # Take half
    dist_ids = dist_ids / 2
    # Get upper and lower bound
    #ids_low = np.floor(ids_array - dist_ids)
    ids_up = np.floor(ids_array + dist_ids)
    # Correct for highest and lowest possible id
    #ids_low[ids_low < 0] = 0
    ids_up[ids_up > (sample_time.size -1)] = sample_time.size
    ids_up = ids_up.tolist()
    # Add to one array
    #ids_bounds = np.concatenate([ids_low, ids_up], axis=1).astype(dtype=np.int32)
    # Get empty array
    torque = np.zeros(sample_time.shape)
    # Iterate over torque and get mean value of load per tooth and load cycle
    id_low = int(0)
    for idx, id_up in enumerate(ids_up):
        torque[id_low:int(id_up[0])] = load_dict[str(teeth_no_list[idx])]
        id_low = int(id_up[0])
    return(torque)
