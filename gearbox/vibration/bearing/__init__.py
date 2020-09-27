# -*- coding: utf-8 -*-

# import built in libarys
import os
from copy import deepcopy as dc
# import sys
from IPython.display import display, HTML

# import 3rd party libarys
import numpy as np
import pandas as pd
# from matplotlib import pyplot as plt
# from scipy.signal import gausspulse
# from sklearn.preprocessing import MinMaxScaler
# from scipy.stats import norm
# from numpy.random import uniform
# from scipy.optimize import brute
# from sklearn.metrics import mean_squared_error

# import local libarys
from gearbox.vibration.helper import StationarySignals
from gearbox.vibration.helper import SignalHelper
from gearbox.vibration.helper import BasicHelper

####################################################

class Bearing(BasicHelper, SignalHelper, StationarySignals):

    def __init__(self, rotational_frequency, bearingdict,
                 sample_rate, time, torque):
        """
        Class constructor.
        """
        BasicHelper.__init__(self)
        SignalHelper.__init__(self)
        StationarySignals.__init__(self)
        self.fn = rotational_frequency
        self.bearingdict = bearingdict
        self.sample_rate = sample_rate
        self.time = time
        self.torque = torque
        self.interpret_dict()


    def interpret_dict(self):
        """
        Method to interpret and check the given Gear-Dictionary
        Input.
        """
        # # Key 'no_elements'
        self.check_declaration(self.bearingdict, key='no_elements', message='')
        assert isinstance(self.bearingdict['no_elements'], (int)), 'no_elements must be integer'
        # Set Rotational Frequencies
        self.approx_factor = 0.425 # Must be in range [0.4, 0,45] (VDI 3832)
        self.rotational_frequency = {'rotor': self.fn}
        self.rotational_frequency['relement'] = self.approx_factor * self.fn
        self.rotational_frequency['iring'] = (1 - self.approx_factor) * self.fn * self.bearingdict['no_elements']
        self.rotational_frequency['oring'] = self.bearingdict['no_elements'] * self.approx_factor * self.fn
        # Key 'signal_%s'
        self.harmonics = {}
        self.harmonics_fac = {}
        self.signal_model = {}
        self.ampl_method = {}
        self.mu = {}
        self.sigma = {}
        self.constant = {}
        self.noise_method = {}
        self.noise_mu = {}
        self.noise_sigma = {}
        self.torq_method = {}
        self.scale_min = {}
        self.scale_max = {}
        self.value_min = {}
        self.value_max = {}
        self.norm_divisor = {}
        self.exponent = {}
        for part in ['iring', 'relement', 'oring']:
            # Key 'harmonics'
            if 'harmonics_%s' % (part) in self.bearingdict:
                assert isinstance(self.bearingdict['harmonics_%s' % (part)], (list, tuple)), 'harmonics must be given as list'
                assert all([isinstance(harmonic, (int)) for harmonic in self.bearingdict['harmonics_%s' % (part)]]), 'every given harmonic in list must be type integer'
                self.harmonics['%s' % (part)] = self.bearingdict['harmonics_%s' % (part)]
            else:
                self.harmonics['%s' % (part)] = [1]
            # Key 'harmonics_fac'
            if 'harmonics_fac_%s' % (part) in self.bearingdict:
                assert isinstance(self.bearingdict['harmonics_fac_%s' % (part)], (list, tuple)), 'harmonics_fac must be given as list'
                assert len(self.bearingdict['harmonics_fac_%s' % (part)])==len(self.harmonics['%s' % (part)]), 'length of harmonics_fac for given part must equal number of given harmonics'
                self.harmonics_fac['%s' % (part)] = self.bearingdict['harmonics_fac_%s' % (part)]
            else:
                self.harmonics_fac['%s' % (part)] = np.ones(len(self.harmonics['%s' % (part)])).tolist()
            # Key 'signal'
            self.check_declaration(self.bearingdict, key='signal_%s' % (part), message='')
            assert self.bearingdict['signal_%s' % (part)] in self.signal_list, 'signal_%s must be one of the following: %s' % (part, str(self.signal_list))
            self.signal_model['%s' % (part)] = self.choose_signal_model(self.bearingdict['signal_%s' % (part)])
            # Key 'ampl_method'
            self.check_declaration(self.bearingdict, key='ampl_method_%s' % (part), message='')
            assert self.bearingdict['ampl_method_%s' % (part)] in self.amplitude_method_list, 'ampl_method_%s must be one of the following: %s' % (part, str(self.amplitude_method_list))
            self.ampl_method['%s' % (part)] = self.bearingdict['ampl_method_%s' % (part)]
            # Key 'ampl_attributes'
            self.check_declaration(self.bearingdict, key='ampl_attributes_%s' % (part), message='')
            if 'mu' in self.bearingdict['ampl_attributes_%s' % (part)]:
                self.mu['%s' % (part)] = self.bearingdict['ampl_attributes_%s' % (part)]['mu']
            else:
                self.mu['%s' % (part)] = None
            if 'sigma' in self.bearingdict['ampl_attributes_%s' % (part)]:
                self.sigma['%s' % (part)] = self.bearingdict['ampl_attributes_%s' % (part)]['sigma']
            else:
                self.sigma['%s' % (part)] = None
            if 'constant' in self.bearingdict['ampl_attributes_%s' % (part)]:
                self.constant['%s' % (part)] = self.bearingdict['ampl_attributes_%s' % (part)]['constant']
            else:
                self.constant['%s' % (part)] = None
            # Key 'noise_method'
            self.check_declaration(self.bearingdict, key='noise_method_%s' % (part), message='')
            assert self.bearingdict['noise_method_%s' % (part)] in self.amplitude_method_list, 'noise_method_%s must be one of the following: %s' % (part, str(self.amplitude_method_list))
            self.noise_method['%s' % (part)] = self.bearingdict['noise_method_%s' % (part)]
            # Key 'noise_attributes'
            self.check_declaration(self.bearingdict, key='noise_attributes_%s' % (part), message='')
            if 'mu' in self.bearingdict['noise_attributes_%s' % (part)]:
                self.noise_mu['%s' % (part)] = self.bearingdict['noise_attributes_%s' % (part)]['mu']
            else:
                self.noise_mu['%s' % (part)] = None
            if 'sigma' in self.bearingdict['noise_attributes_%s' % (part)]:
                self.noise_sigma['%s' % (part)] = self.bearingdict['noise_attributes_%s' % (part)]['sigma']
            else:
                self.noise_sigma['%s' % (part)] = None
            # Key 'noise_method'
            self.check_declaration(self.bearingdict, key='torq_method_%s' % (part), message='')
            assert self.bearingdict['torq_method_%s' % (part)] in self.scale_method_list, 'torq_method must be one of the following: %s' % (str(self.scale_method_list))
            self.torq_method['%s' % (part)] = self.bearingdict['torq_method_%s' % (part)]
            # Key 'torq_attributes'
            self.check_declaration(self.bearingdict, key='torq_attributes_%s' % (part), message='')
            if 'scale_min' in self.bearingdict['torq_attributes_%s' % (part)]:
                self.scale_min['%s' % (part)] = self.bearingdict['torq_attributes_%s' % (part)]['scale_min']
            else:
                self.scale_min['%s' % (part)] = None
            if 'scale_max' in self.bearingdict['torq_attributes_%s' % (part)]:
                self.scale_max['%s' % (part)] = self.bearingdict['torq_attributes_%s' % (part)]['scale_max']
            else:
                self.scale_max['%s' % (part)] = None
            if 'value_min' in self.bearingdict['torq_attributes_%s' % (part)]:
                self.value_min['%s' % (part)] = self.bearingdict['torq_attributes_%s' % (part)]['value_min']
            else:
                self.value_min['%s' % (part)] = None
            if 'value_max' in self.bearingdict['torq_attributes_%s' % (part)]:
                self.value_max['%s' % (part)] = self.bearingdict['torq_attributes_%s' % (part)]['value_max']
            else:
                self.value_max['%s' % (part)] = None

            if 'norm_divisor' in self.bearingdict['torq_attributes_%s' % (part)]:
                self.norm_divisor['%s' % (part)] = self.bearingdict['torq_attributes_%s' % (part)]['norm_divisor']
            else:
                self.norm_divisor['%s' % (part)] = None
            if 'exponent' in self.bearingdict['torq_attributes_%s' % (part)]:
                self.exponent['%s' % (part)] = self.bearingdict['torq_attributes_%s' % (part)]['exponent']
            else:
                self.exponent['%s' % (part)] = None


    def raw_signal(self):
        """
        Method to return the raw signal simulated by the given gear.
        """
        # Get Gear relevant parameters
        signal = np.zeros((self.time.shape[0], 1))
        # i and ids are used to save the id of the first signal of each element
        i = 0
        ids = []
        labels = ['Inner Ring Rollover', 'Rolling Element', 'Outer Ring Rollover']
        for idp, part in enumerate(['iring', 'relement', 'oring']):
            for idh, harmonic in enumerate(self.harmonics['%s' % (part)]):
                if idh == 0:
                    labels[idp] = labels[idp] + ': Harmonic no %i' % (harmonic)
                    ids.append(i)
                    i += 1
                # Get signal for part i
                signal_i = self.signal_model['%s' % (part)].run(self.time,
                                                                self.rotational_frequency['%s' % (part)] * harmonic,
                                                                ampl=1)
                # Scale by given harmonic factor
                signal_i = signal_i * self.harmonics_fac['%s' % (part)][idh]
                # Add Amplitude
                amplitude_vector = self.create_amplitude_vector(method=self.ampl_method['%s' % (part)],
                                                                mu=self.mu['%s' % (part)],
                                                                sigma=self.sigma['%s' % (part)],
                                                                constant=self.constant['%s' % (part)],
                                                                no_values=self.time.shape[0],
                                                                repeat2no_values=self.time.shape[0])
                signal_i = signal_i * amplitude_vector.reshape(-1, 1)
                # Add Torque Influence
                scale_vector = self.create_scale_vector(array=self.torque, method=self.torq_method['%s' % (part)],
                                                        scale_min=self.scale_min['%s' % (part)], scale_max=self.scale_max['%s' % (part)],
                                                        value_min=self.value_min['%s' % (part)], value_max=self.value_max['%s' % (part)],
                                                        exponent=self.exponent['%s' % (part)],
                                                        norm_divisor=self.norm_divisor['%s' % (part)])
                # Resize for Case: If scale_vector.size is greater than signal.size (due to larger torque)
                scale_vector = scale_vector[0:signal_i.size]
                signal_i = signal_i * scale_vector.reshape(-1, 1)
                # Add noise
                noise_vector = self.create_amplitude_vector(method=self.noise_method['%s' % (part)],
                                                            mu=self.noise_mu['%s' % (part)],
                                                            sigma=self.noise_sigma['%s' % (part)],
                                                            no_values=self.time.shape[0])
                signal_i = signal_i + noise_vector.reshape(-1, 1)
                signal = np.concatenate([signal, signal_i], axis=1)
                # Get new shift arguments
        # Remove first zero axis
        signal = np.delete(signal, 0, 1)
        return(signal, ids, labels)
