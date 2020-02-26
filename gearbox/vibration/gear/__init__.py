# -*- coding: utf-8 -*-

# import built in libarys
import os
from copy import deepcopy as dc
import sys
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
from gearbox.vibration.helper import NonstationarySignals
from gearbox.vibration.helper import SignalHelper
from gearbox.vibration.helper import BasicHelper

####################################################
#------------------- ELEMENTS ---------------------#

class Gear(BasicHelper, SignalHelper, NonstationarySignals):

    def __init__(self, rotational_frequency, geardict,
                 sample_rate, time, torque, GearDegVibDict=None):
        """
        Class constructor.
        """
        BasicHelper.__init__(self)
        SignalHelper.__init__(self)
        NonstationarySignals.__init__(self)
        self.rotational_frequency = rotational_frequency
        self.geardict = geardict
        self.sample_rate = sample_rate
        self.time = time
        self.torque = torque
        self.GearDegVibDict = GearDegVibDict
        self.teeth_no_list = None
        self.teeth_cid_list = None
        self.interpret_dict()
        self.interpret_deg_dict()

    def interpret_dict(self):
        """
        Method to interpret and check the given Gear-Dictionary
        Input.
        """
        # Key 'no_teeth'
        self.check_declaration(self.geardict, key='no_teeth', message='')
        assert isinstance(self.geardict['no_teeth'], int), 'no_teeth must be integer'
        self.no_teeth = self.geardict['no_teeth']
        # Key 'signal'
        self.check_declaration(self.geardict, key='signal', message='')
        assert self.geardict['signal'] in self.signal_list, 'signal must be one of the following: %s' % (str(self.signal_list))
        self.signal_model = self.choose_signal_model(self.geardict['signal'])
        # Key 'ampl_method'
        self.check_declaration(self.geardict, key='ampl_method', message='')
        assert self.geardict['ampl_method'] in self.amplitude_method_list, 'ampl_method must be one of the following: %s' % (str(self.amplitude_method_list))
        self.ampl_method = self.geardict['ampl_method']
        # Key 'ampl_attributes'
        self.check_declaration(self.geardict, key='ampl_attributes', message='')
        if 'mu' in self.geardict['ampl_attributes']:
            self.mu = self.geardict['ampl_attributes']['mu']
        else:
            self.mu = None
        if 'sigma' in self.geardict['ampl_attributes']:
            self.sigma = self.geardict['ampl_attributes']['sigma']
        else:
            self.sigma = None
        if 'constant' in self.geardict['ampl_attributes']:
            self.constant = self.geardict['ampl_attributes']['constant']
        else:
            self.constant = None
        # Key 'noise_method'
        self.check_declaration(self.geardict, key='noise_method', message='')
        assert self.geardict['noise_method'] in self.amplitude_method_list, 'noise_method must be one of the following: %s' % (str(self.amplitude_method_list))
        self.noise_method = self.geardict['noise_method']
        # Key 'noise_attributes'
        self.check_declaration(self.geardict, key='noise_attributes', message='')
        if 'mu' in self.geardict['noise_attributes']:
            self.noise_mu = self.geardict['noise_attributes']['mu']
        else:
            self.noise_mu = None
        if 'sigma' in self.geardict['noise_attributes']:
            self.noise_sigma = self.geardict['noise_attributes']['sigma']
        else:
            self.noise_sigma = None
        # Key 'torq_method'
        self.check_declaration(self.geardict, key='torq_method', message='')
        assert self.geardict['torq_method'] in self.scale_method_list, 'torq_method must be one of the following: %s' % (str(self.scale_method_list))
        self.torq_method = self.geardict['torq_method']
        # Key 'torq_attributes'
        self.check_declaration(self.geardict, key='torq_attributes', message='')
        if 'scale_min' in self.geardict['torq_attributes']:
            self.scale_min = self.geardict['torq_attributes']['scale_min']
        else:
            self.scale_min = None
        if 'scale_max' in self.geardict['torq_attributes']:
            self.scale_max = self.geardict['torq_attributes']['scale_max']
        else:
            self.scale_max = None
        if 'value_min' in self.geardict['torq_attributes']:
            self.value_min = self.geardict['torq_attributes']['value_min']
        else:
            self.value_min = None
        if 'value_max' in self.geardict['torq_attributes']:
            self.value_max = self.geardict['torq_attributes']['value_max']
        else:
            self.value_max = None
        if 'norm_divisor' in self.geardict['torq_attributes']:
            self.norm_divisor = self.geardict['torq_attributes']['norm_divisor']
        else:
            self.norm_divisor = None
        if 'exponent' in self.geardict['torq_attributes']:
            self.exponent = self.geardict['torq_attributes']['exponent']
        else:
            self.exponent = None

    def interpret_deg_dict(self):
        """
        Method to interpret and check the given Gear-Dictionary
        Input.
        """
        if self.GearDegVibDict is None:
            self.GearDegVibDict = {}
            self.GearDegVibDict['signal'] = 'gausspulse'
            self.GearDegVibDict['fc_factor'] = 2 * self.rotational_frequency
            self.GearDegVibDict['bw_factor'] = 0.5
            self.GearDegVibDict['bwr_factor'] = -6
            self.GearDegVibDict['scale_method'] = 'linear'
            self.GearDegVibDict['scale_attributes'] = {}
            self.GearDegVibDict['scale_attributes']['scale_min'] = 0
            self.GearDegVibDict['scale_attributes']['scale_max'] = 1
            self.GearDegVibDict['scale_attributes']['value_min'] = 0
            self.GearDegVibDict['scale_attributes']['value_max'] = 4
            self.GearDegVibDict['scale_attributes']['exponent'] = 2
            self.GearDegVibDict['torq_influence'] = True
            self.GearDegVibDict['noise_method'] = 'gaussian'
            self.GearDegVibDict['noise_attributes'] = {}
            self.GearDegVibDict['noise_attributes']['mu'] = 0
            self.GearDegVibDict['noise_attributes']['sigma'] = 0.005
            self.GearDegVibDict['t2t_factor'] = 1

        else:
            # Key 'signal'
            self.check_declaration(self.GearDegVibDict, key='signal', message='')
            assert self.GearDegVibDict['signal'] in self.signal_list, 'signal must be one of the following: %s' % (str(self.signal_list))
            # Key 'ampl_method'
            self.check_declaration(self.GearDegVibDict, key='scale_method', message='')
            assert self.GearDegVibDict['scale_method'] in self.scale_method_list, 'ampl_method must be one of the following: %s' % (str(self.scale_method_list))
            # Key 'ampl_attributes'
            self.check_declaration(self.GearDegVibDict, key='scale_attributes', message='')
            # Key 'noise_method'
            self.check_declaration(self.GearDegVibDict, key='noise_method', message='')
            assert self.GearDegVibDict['noise_method'] in self.amplitude_method_list, 'noise_method must be one of the following: %s' % (str(self.amplitude_method_list))
            # Key 'noise_attributes'
            self.check_declaration(self.GearDegVibDict, key='noise_attributes', message='')
            # Key 'torq_method'
            self.check_declaration(self.GearDegVibDict, key='torq_influence', message='')
            # Key 't2t_factor'
            self.check_declaration(self.GearDegVibDict, key='t2t_factor', message='')


    def raw_signal(self):
        """
        Method to return the raw signal simulated by the given gear.
        """
        # Get Gear relevant parameters
        time2tooth = (1 / self.rotational_frequency) / self.no_teeth
        center_frequency = self.rotational_frequency * self.no_teeth # TBD check this formula
        # Mirror time to keep negative half of non stationary signal
        mirrored_time = self.mirror_at_0(self.time)
        # Get single tooth signal with amplitude=1
        tooth_signal, tooth_center = self.signal_model.run(mirrored_time,
                                                           center_frequency)
        # Extend array to avoide "index out a range"
        tooth_signal = self.extend_array(tooth_signal, 0, self.time.shape[0])
        tooth_center += self.time.shape[0]
        # Shift signal for each tooth
        teeth_signal, teeth_cid_list = self.shift_signal(signal=tooth_signal,
                                                         signal_center=tooth_center,
                                                         time=self.time, time_shift=time2tooth,
                                                         time_start=0, id_start=0)
        # Get teeth list
        teeth_numbering = np.arange(1, self.no_teeth+0.1, 1, dtype=np.int32)
        teeth_no_list = self.repeat2no_values(teeth_numbering,
                                              no_values=teeth_signal.shape[1])
        # Add Amplitude
        amplitude_vector = self.create_amplitude_vector(method=self.ampl_method,
                                                        mu=self.mu, sigma=self.sigma,
                                                        constant=self.constant,
                                                        no_values=self.no_teeth,
                                                        repeat2no_values=teeth_signal.shape[1])
        gear_signal = teeth_signal * amplitude_vector
        # Add Torque Influence
        scale_vector = self.create_scale_vector(array=self.torque, method=self.torq_method,
                                                scale_min=self.scale_min, scale_max=self.scale_max,
                                                value_min=self.value_min, value_max=self.value_max,
                                                exponent=self.exponent,
                                                norm_divisor=self.norm_divisor)
        gear_signal = gear_signal * scale_vector
        # Add noise
        noise_vector = self.create_amplitude_vector(method=self.noise_method,
                                                    mu=self.noise_mu,
                                                    sigma=self.noise_sigma,
                                                    no_values=self.time.shape[0])
        gear_signal = gear_signal + noise_vector.reshape(-1, 1)
        # Store Variables
        self.teeth_no_list = teeth_no_list
        self.teeth_cid_list = teeth_cid_list
        return(gear_signal, teeth_no_list, teeth_cid_list)

    def load_per_tooth(self, torque):
        """
        Method to determine an aquivalent load for each tooth.
        Returns a dictionary containing a list of mean loads
        per tooth. E.g.
        '1': [155, 177, 169,....]
        '2': [196, 155, 169,....]
        '3' ...
        ....
        """
        # Cover initialization
        if self.teeth_no_list is None:
            _, _, _ = self.raw_signal()
        # Get Tooth Center IDs
        ids_array = np.array(dc(self.teeth_cid_list))
        ids_array = ids_array.reshape(-1, 1)
        # Get distance between 2 tooth in no ids
        dist_ids = ids_array[1] - ids_array[0]
        # Scale distance length
        dist_ids = dist_ids * self.GearDegVibDict['t2t_factor']
        # Take half
        dist_ids = dist_ids / 2
        # Get upper and lower bound
        ids_low = np.floor(ids_array - dist_ids)
        ids_up = np.floor(ids_array + dist_ids)
        # Correct for highest and lowest possible id
        ids_low[ids_low < 0] = 0
        ids_up[ids_up > (torque.size -1)] = torque.size -1
        # Add to one array
        ids_bounds = np.concatenate([ids_low, ids_up], axis=1).astype(dtype=np.int32)
        # Dict tooth no
        load_dict = {str(idx+1): [] for idx in range(self.no_teeth)}
        # Iterate over torque and get mean value of load per tooth and load cycle
        mean_torque = []
        for idx, id_low_up in enumerate(ids_bounds):
            load_dict[str(self.teeth_no_list[idx])].append(np.mean(torque[id_low_up[0]:id_low_up[1]]))
        return(load_dict)

    def tooth_degr_signal(self, nolc, statei):
        """
        Method to get a degradation signal based on
        given tooth state i.
        Method raw_signal must been run before.
        """
        #---------------------
        # Get single tooth signal with amplitude=1
        degr_signal_model = self.choose_signal_model(self.GearDegVibDict['signal'])
        period = 1 / self.rotational_frequency
        time2tooth = period / self.no_teeth
        tooth_signal, tooth_center = degr_signal_model.run(self.time,
                                                           self.GearDegVibDict['fc_factor'],
                                                           bw=self.GearDegVibDict['bw_factor'],
                                                           bwr=self.GearDegVibDict['bwr_factor'])
        # Remove first half (let signal start with zero)
        tooth_signal = tooth_signal[tooth_center:]
        tooth_center = 0
        # Extend array to avoide "index out a range"
        ext_tooth_signal = self.extend_array(tooth_signal, 0, self.time.shape[0])
        tooth_center += self.time.shape[0]
        #---------------------
        # Shift signal for each tooth
        # Each row represents a tooth mesh
        teeth_signal, _ = self.shift_signal(signal=ext_tooth_signal,
                                            signal_center=tooth_center,
                                            time=self.time, time_shift=time2tooth,
                                            time_start=0, id_start=0)
        # Get teeth list (not starting at zero due to following enumerate)
        teeth_numbering = np.arange(0, self.no_teeth, 1, dtype=np.int32)
        teeth_no_list = self.repeat2no_values(teeth_numbering,
                                              no_values=teeth_signal.shape[1])
        #---------------------
        # Iterate over pitting (ordered by tooth number)
        pittings = []
        labels = []
        signal = np.zeros((self.time.shape[0], 1))
        for tooth, pitting in enumerate(statei.loc['$a_{%i}$' % (nolc)]):
            # if no pitting @ tooth
            if np.isnan(pitting):
                pass
            # else pitting @ tooth
            else:
                # Condition on tooth to filter for itself tooth mesh
                condition = teeth_no_list == tooth
                tooth_signal = teeth_signal[:, condition]
                # Sum up all tooth mesh of tooth
                tooth_signal = np.sum(tooth_signal, axis=1).reshape(-1,1)
                pittings.append(pitting)
                labels.append('Tooth %i (a = %.3f)' % (tooth+1, pitting))
                # Add signal_i to signal
                signal = np.concatenate([signal, tooth_signal], axis=1)
        #---------------------
        # Set degradation signal to zero signal if no pitting occurs
        if signal.shape[1] == 1:
            labels = ['None']
            degr_signal = signal
        else:
            # Delete dummy entry
            signal = np.delete(signal, 0, 1)
            # Scale Pitting
            scaled_pittings = self.create_scale_vector(array=np.array(pittings),
                                                       method=self.GearDegVibDict['scale_method'],
                                                       ones_base=False,
                                                       scale_min=self.GearDegVibDict['scale_attributes']['scale_min'],
                                                       scale_max=self.GearDegVibDict['scale_attributes']['scale_max'],
                                                       value_min=self.GearDegVibDict['scale_attributes']['value_min'],
                                                       value_max=self.GearDegVibDict['scale_attributes']['value_max'],
                                                       exponent=self.GearDegVibDict['scale_attributes']['exponent'],
                                                       norm_divisor=1)
            pittings = scaled_pittings.reshape(-1).tolist()
            # Add Amplitude
            amplitude_vector = self.create_amplitude_vector(method='const_repeat',
                                                            mu=None, sigma=None,
                                                            constant=pittings,
                                                            no_values=None,
                                                            repeat2no_values=signal.shape[1])
            degr_signal = signal * amplitude_vector
            # Add Torque Influence
            if self.GearDegVibDict['torq_influence']:
                scale_vector = self.create_scale_vector(array=self.torque, method=self.torq_method,
                                                        scale_min=self.scale_min, scale_max=self.scale_max,
                                                        value_min=self.value_min, value_max=self.value_max,
                                                        exponent=self.exponent,
                                                        norm_divisor=self.norm_divisor)
                degr_signal = degr_signal * (scale_vector / 2)
            # Add noise
            noise_vector = self.create_amplitude_vector(method=self.GearDegVibDict['noise_method'],
                                                        mu=self.GearDegVibDict['noise_attributes']['mu'],
                                                        sigma=self.GearDegVibDict['noise_attributes']['sigma'],
                                                        no_values=self.time.shape[0])
            degr_signal = degr_signal + noise_vector.reshape(-1, 1)
        return(degr_signal, labels)
