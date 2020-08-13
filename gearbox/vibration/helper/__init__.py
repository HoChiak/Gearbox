# -*- coding: utf-8 -*-

# import built in libarys
import os
# import sys
from IPython.display import display, HTML

# import 3rd party libarys
import numpy as np
import pandas as pd
# from matplotlib import pyplot as plt
from scipy.signal import gausspulse
from sklearn.preprocessing import MinMaxScaler
# from scipy.stats import norm
# from numpy.random import uniform
# from scipy.optimize import brute
# from sklearn.metrics import mean_squared_error

# import local libarys


####################################################
#---------- Basic Helper Functions ----------------#

class BasicHelper():
    """
    Class for basic helper functions
    """

    def __init__(self):
        """
        Class constructor for basic helper methods
        """

    def extend_array(self, array, value, length, left=True, right=True):
        """
        Method to fill up an array on the left and or the right side
        by a given value
        """
        extension = np.ones(length,) * value
        extension = extension.reshape(-1, 1)
        if left is True:
            array = np.concatenate([extension, array], axis=0)
        if right is True:
            array = np.concatenate([array, extension], axis=0)
        return(array)

    def repeat2no_values(self, vector, no_values):
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

    def check_declaration(self, objectdict, key, message=''):
        """
        Method to test wheter a keyword in kwargs exist. If not, set kwargs
        keyword to given default.
        """
        if key not in objectdict:
            raise NameError('%s Missing declaration of Key %s' % (message, key))

    def check_and_init_declaration(self, anchor, key, target):
        """
        Method to test wheter a keyword in anchor exist. If not, set target
        to given default.
        """
        if key in anchor:
            target = anchor[key]

    def get_gcd(self, a, b):
        """
        Method to compute the greatest common
        divisor of a and b
        """
        while b > 0:
            a, b = b, a % b
        return(a)

    def get_lcm(self, a, b):
        """
        Method to get the lowest common
        multiple of a and b
        """
        return(a * b / self.get_gcd(a, b))

    def mirror_at_0(self, array):
        """
        Method to mirror an given array at value 0.
        Adds the negative flipped array to the given array.
        Given Array must start with 0.
        """
        array = array.reshape(-1)
        assert array[0] == 0, 'Given Array must start with 0 (Method mirror_at_0())'
        flipped = np.flip(array, axis=0)
        negative = np.negative(flipped)
        # Delete redundant 0
        negative = np.delete(negative, -1, axis=0)
        mirrored = np.concatenate([negative, array], axis=0)
        return(mirrored)

    def remove_left_0s(self, array, center):
        """
        Method to remove zeros on the left of an given array. Only one
        Zero at the highest id will remain
        """
        # Set all values smaller 1e
        array[np.logical_and(-1e-5 <= array, array <= 1e-5)] = 0
        # Find first value not zero (inverse because zero values are at left and right)
        condition = array != 0
        condition_id = np.where(condition)[0]
        # Id of last zero value is id of first not zero value - 1
        cutoffid = condition_id[0] - 1
        # Adjust array and center
        cutoff_array = array[cutoffid:]
        cutoff_center = center - cutoffid
        return(cutoff_array, cutoff_center)

####################################################
#--------- Signal Helper Functions ----------------#

class SignalHelper():
    """
    Class for signal specific helper methods
    """

    amplitude_method_list = ['const', 'const_repeat', 'gaussian', 'gaussian_repeat', None]
    scale_method_list = ['linear', 'polynomial', 'exponential', None]


    def __init__(self):
        """
        Class constructor for signal specific helper methods
        """

    def shift_signal(self, signal, signal_center, time, time_shift,
                     time_start=0, id_start=0):
        """
        Shift a given signal by a given time shift.
        Signal:  [--|--]
        Signal_center: 2 (Id of | in the given array)
        time: time array
        time shift: how many time units a signal is
                    shifted each shift
        time_start = corresponding to id_start
        id_start = 2 (Places first center at id 2)
        Example:
        [[--|-------------------------------------]
         [----|-----------------------------------]
         [------|---------------------------------]
         [--------|-------------------------------]
         [----------|-----------------------------]
         [------------|---------------------------]]
        """
        # Shift signal for each gear
        ti, tv = id_start, time_start
        shifted_signal = np.zeros((time.shape[0], 1))
        cid_list = list()
        while tv < (max(time)+time_shift):
            # Add current center id to list
            cid_list.append(ti)
            # Get IDs for shift
            min_id, max_id = signal_center-ti, -(ti+1)
            # Shift on x-Axis -> truncated signal
            signal_i = signal[min_id:max_id]
            # Get truncated signal to right size
            signal_i = signal_i[0:time.shape[0]]
            # Add teeth signal to gear signal
            shifted_signal = np.concatenate([shifted_signal, signal_i], axis=1)
            # Get new shift arguments
            tv += time_shift
            ti = np.argmin(np.abs(time - tv))
        # Remove first zero axis
        shifted_signal = np.delete(shifted_signal, 0, 1)
        # Remove doubled last values (bug)
        if cid_list[-1]==cid_list[-2]:
            del(cid_list[-1])
            shifted_signal = np.delete(shifted_signal, -1, 1)
        return(shifted_signal, cid_list)

    def shift_cid(self, signal_center, time, time_shift,
                  time_start=0, id_start=0):
        """
        Shift a given signal by a given time shift.
        Signal_center: 2 (Id of | in the given array)
        time: time array
        time shift: how many time units a signal is
                    shifted each shift
        time_start = corresponding to id_start
        id_start = 2 (Places first center at id 2)
        Example:
        [[--|-------------------------------------]
         [----|-----------------------------------]
         [------|---------------------------------]
         [--------|-------------------------------]
         [----------|-----------------------------]
         [------------|---------------------------]]
        """
        # Shift signal for each gear
        ti, tv = id_start, time_start
        cid_list = list()
        while tv < (max(time)+time_shift):
            # Add current center id to list
            cid_list.append(ti)
            # Get IDs for shift
            min_id, max_id = signal_center-ti, -(ti+1)
            # Get new shift arguments
            tv += time_shift
            ti = np.argmin(np.abs(time - tv))
        # Remove first zero axis
        # Remove doubled last values (bug)
        if cid_list[-1]==cid_list[-2]:
            del(cid_list[-1])
        return(cid_list)

    def create_amplitude_vector(self, method='const', **kwargs):
        """
        """
        if method is None:
            amplitude_vector = np.zeros((1, kwargs['no_values']))
        else:
            if 'const' in method:
                if 'repeat' in method:
                    try:
                        assert isinstance(kwargs['constant'], (list, tuple)), "Using method 'const' and 'repeat', argument -constant- must be given (tuple, list)"
                        assert isinstance(kwargs['repeat2no_values'], (int)), "Using method 'repeat', argument -repeat2no_values- must be given (integer)"
                    except KeyError:
                        raise KeyError("Using method 'const' and 'repeat', argument -constant- and -repeat2no_values- must be given")
                    amplitude_vector = np.array(kwargs['constant']).reshape(-1,)
                    amplitude_vector = self.repeat2no_values(amplitude_vector, kwargs['repeat2no_values'])
                else:
                    try:
                        assert isinstance(kwargs['constant'], (int, float)), "Using method 'const', argument -constant- must be given (scalar)"
                        assert isinstance(kwargs['no_values'], int), "Using method 'const', argument -no_values- must be given (integer)"
                    except KeyError:
                        raise KeyError("Using method 'const', argument -constant- and -no_values- must be given")
                    amplitude_vector = np.ones((1, kwargs['no_values']))
                    amplitude_vector = amplitude_vector*kwargs['constant']
            if 'gaussian' in method:
                try:
                    assert isinstance(kwargs['mu'], (int, float)), "Using method 'gaussian', argument -mu- must be given (scalar)"
                    assert isinstance(kwargs['sigma'], (int, float)), "Using method 'gaussian', argument -sigma- must be given (scalar)"
                    assert isinstance(kwargs['no_values'], int), "Using method 'gaussian', argument -no_values- must be given (integer)"
                except KeyError:
                    raise KeyError("Using method 'gaussian', argument -mu-, -sigma- and -no_values- must be given")
                amplitude_vector = kwargs['sigma'] * np.random.randn(kwargs['no_values']) + kwargs['mu']
                if 'repeat' in method:
                    try:
                        assert isinstance(kwargs['repeat2no_values'], (int)), "Using method 'repeat', argument -repeat2no_values- must be given (integer)"
                    except KeyError:
                        raise KeyError("Using method 'repeat', argument -repeat2no_values- must be given")
                    amplitude_vector = amplitude_vector.reshape(-1,)
                    amplitude_vector = self.repeat2no_values(amplitude_vector, kwargs['repeat2no_values'])
        amplitude_vector = amplitude_vector.reshape(1, -1)
        return(amplitude_vector)


    def create_scale_vector(self, array, method='linear', ones_base=True, **kwargs):
        """
        """
        array = array.reshape(-1, 1)
        if ones_base is True:
            scale_base_vector = np.ones((array.shape[0], 1))
        else:
            scale_base_vector = np.zeros((array.shape[0], 1))
        if method is None:
            scale_vector = scale_base_vector
            pass
        else:
            # Define Min Max Scaler
            try:
                assert isinstance(kwargs['scale_min'], (int, float)), "Using a torque scaling method, argument -scale_min- must be given (scalar)"
                assert isinstance(kwargs['scale_max'], (int, float)), "Using a torque scaling method, argument -scale_max- must be given (scalar)"
                assert isinstance(kwargs['value_min'], (int, float)), "Using a torque scaling method, argument -value_min- must be given (scalar)"
                assert isinstance(kwargs['value_max'], (int, float)), "Using a torque scaling method, argument -value_max- must be given (scalar)"
                scaler = MinMaxScaler(feature_range=(kwargs['scale_min'], kwargs['scale_max']), copy=True)
            except KeyError:
                raise KeyError("Using a torque scaling method, argument -scale_min-, -value_min-, -value_max- and -scale_max- must be given")
            # Norm array by given value
            array = array / kwargs['norm_divisor']
            # Choose Method and transform
            if 'linear' in method:
                array = array # linear scaling
                scaler.fit(np.array([kwargs['value_min'], kwargs['value_max']], dtype=np.float64).reshape(-1, 1))
                array = scaler.transform(array)
                scale_vector = scale_base_vector + array
            if 'polynomial' in method:
                try:
                    assert isinstance(kwargs['exponent'], (int, float)), "Using method 'linear', argument -exponent- must be given (scalar)"
                except KeyError:
                    raise KeyError("Using method 'linear', argument -exponent- must be given (scalar)")
                array = np.power(array, kwargs['exponent']) # polynomial scaling
                scaler.fit(np.power(np.array([kwargs['value_min'], kwargs['value_max']]), kwargs['exponent']).reshape(-1, 1))
                array = scaler.transform(array)
                scale_vector = scale_base_vector + array
            if 'exponential' in method:
                array = np.exp(array) # exponential scaling
                scaler.fit(np.exp(np.array([kwargs['value_min'], kwargs['value_max']])).reshape(-1, 1))
                array = scaler.transform(array)
                scale_vector = scale_base_vector + array
        return(scale_vector)

####################################################
#----------------- RAW SIGNALS --------------------#
class StationarySignals():
    """
    Class for all stationary raw signals

    Adding a new Signal Model:
    1. Add name to attribute "signal_list"
    2. Create new Class with method __init__() and run()
    3. Add new Model to method choose_signal_model method
    """

    signal_list = ['sine',]


    def __init__(self):
        """
        Class constructor for stationary raw signal methods
        """

    class Sine():#StationarySignals):
        """
        Class for stationary raw signal method Sine
        """

        def __init__(self):
            """
            Class constructor for stationary raw signal methods
            """

        def run(self, time, frq, ampl):
            """
            Method to generate a sine signal for a given
            time array, a frequency and amplitude.
            """
            signal = np.sin((2 * np.pi * frq * time))
            signal = signal * ampl
            signal = signal.reshape(-1, 1)
            return(signal)

    def choose_signal_model(self, name):
        """
        Method to return
        """
        if 'sine' in name:
            return(self.Sine())


class NonstationarySignals():
    """
    Class for all non-stationary raw signals

    Adding a new Signal Model:
    1. Add name to attribute "signal_list"
    2. Create new Class with method __init__() and run()
    3. Add new Model to method choose_signal_model method

    """
    signal_list = ['gausspulse',]

    def __init__(self):
        """
        Class constructor for nobn-stationary raw signal methods
        """

    class GaussPulse():#NonstationarySignals):
        """
        Class for stationary raw signal method GaussPulse
        """

        def __init__(self):
            """
            Class constructor for non stationary raw signal methods
            """

        def run(self, time, frq, bw=0.5, bwr=-6, ampl=1, retquad=False):
            """
            Method to generate a sine signal for a given
            time array, a frequency and amplitude.
            """
            if retquad is False:
                signal = gausspulse(time, fc=frq, bw=bw, bwr=bwr, retquad=False, retenv=False)
            elif retquad is True:
                _, signal = gausspulse(time, fc=frq, bw=bw, bwr=bwr, retquad=True, retenv=False)
            signal = signal * ampl
            signal_center = np.argmin(np.abs(time))
            signal = signal.reshape(-1, 1)
            return(signal, signal_center)

    def choose_signal_model(self, name):
        """
        Method to return
        """
        if 'gausspulse' in name:
            return(self.GaussPulse())
