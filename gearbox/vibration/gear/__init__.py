# -*- coding: utf-8 -*-

# import built in libarys
import os
from copy import deepcopy as dc
# import sys
from IPython.display import display, HTML
# import time

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
                 sample_rate, sample_time, torque_sample_time,
                 torque, GearDegVibDict=None,
                 seed=None):
        """
        Class constructor.
        """
        BasicHelper.__init__(self)
        SignalHelper.__init__(self)
        NonstationarySignals.__init__(self)
        self.rotational_frequency = rotational_frequency
        self.geardict = geardict
        self.sample_rate = sample_rate
        self.sample_time = sample_time
        self.torque_sample_time = torque_sample_time
        self.torque = torque
        self.GearDegVibDict = GearDegVibDict
        self.teeth_no_list = None
        self.teeth_cid_list = None
        self.seed = seed
        self.interpret_dict()
        self.interpret_deg_dict()
        self.get_plus_minus_harmonics_oddeven()
        self.init_gear()
#         self.get_ids2tooth()
        self.init_degr_signal()

    def interpret_dict(self):
        """
        Method to interpret and check the given Gear-Dictionary
        Input.
        """
        # Key 'no_teeth'
        self.check_declaration(self.geardict, key='no_teeth', message='')
        assert isinstance(self.geardict['no_teeth'], int), 'no_teeth must be integer'
        self.no_teeth = self.geardict['no_teeth']
        # # Key 'harmonics'
        if 'harmonics' in self.geardict:
            assert isinstance(self.geardict['harmonics'], (list, tuple)), 'harmonics must be given as list'
            assert all([isinstance(harmonic, (int)) for harmonic in self.geardict['harmonics']]), 'every given harmonic in list must be type integer'
            self.harmonics = np.abs(self.geardict['harmonics']).tolist()
        else:
            self.harmonics = [1]
        # # Key 'harmonics_fac'
        if 'harmonics_fac' in self.geardict:
            assert isinstance(self.geardict['harmonics_fac'], (list, tuple)), 'harmonics_fac must be given as list'
            assert len(self.geardict['harmonics_fac'])==len(self.harmonics), 'length of harmonics_fac must equal number of given harmonics'
            self.harmonics_fac = self.geardict['harmonics_fac']
        else:
            self.harmonics_fac = np.ones(len(self.harmonics)).tolist()
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
            # self.GearDegVibDict['signal'] = 'gausspulse'
            # self.GearDegVibDict['fc_factor'] = 2 * self.rotational_frequency
            # self.GearDegVibDict['bw_factor'] = 0.5
            # self.GearDegVibDict['bwr_factor'] = -6
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
#             self.GearDegVibDict['t2t_factor'] = 1

        else:
            # Key 'signal'
            # self.check_declaration(self.GearDegVibDict, key='signal', message='')
            # assert self.GearDegVibDict['signal'] in self.signal_list, 'signal must be one of the following: %s' % (str(self.signal_list))
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
#             self.check_declaration(self.GearDegVibDict, key='t2t_factor', message='')

    def get_plus_minus_harmonics_random(self):
        """
        Method to create a ones vector which assigns each
        harmonic a positive or negative sign. (Fixed over all iterations)
        """
        plus_minus_harmonics = []
        for i, harmonic in enumerate(self.harmonics):
            if self.seed is not None:
                np.random.seed(np.random.randint(1, high=2**16, size=1, dtype=np.int32)[0])
            if np.random.randn(1)>0:
                plus_minus_harmonics.append(-1)
            else:
                plus_minus_harmonics.append(1)
        # seed dependencie on number of load cycles
        if self.seed is not None:
            np.random.seed(self.seed)
        self.plus_minus_harmonics = plus_minus_harmonics

    def get_plus_minus_harmonics_oddeven(self):
        """
        Method to create a ones vector which assigns each
        harmonic a positive or negative sign. (Fixed over all iterations)
        """
        plus_minus_harmonics = []
        for i, harmonic in enumerate(self.harmonics):
            if (harmonic % 2) == 0:
                plus_minus_harmonics.append(-1)
            else:
                plus_minus_harmonics.append(1)
        self.plus_minus_harmonics = plus_minus_harmonics

    def init_gear(self):
        """
        Method to initialize the raw signal simulated by the given gear.
        """
        # Get Gear relevant parameters
        time2tooth = (1 / self.rotational_frequency) / self.no_teeth
        center_frequency = self.rotational_frequency * self.no_teeth # TBD check this formula
        # Mirror time to keep negative half of non stationary signal
        mirrored_time = self.mirror_at_0(self.sample_time)
        # Get single tooth signal with amplitude=1
        tooth_signal, tooth_center = self.signal_model.run(mirrored_time,
                                                           center_frequency)
        # Remove all values on the left where tooth_signal == 0 (save computational ressources)
        tooth_signal, tooth_center = self.remove_left_0s(tooth_signal, tooth_center)
        # Extend array to avoide "index out a range"
        tooth_signal = self.extend_array(tooth_signal, 0, self.sample_time.shape[0])
        tooth_center += self.sample_time.shape[0]
        # save values to pase them to get_ids_bounds
        self.tooth_center = tooth_center
        self.time2tooth = time2tooth
        # Get ids bounds
        # self.ids_bounds = self.get_ids_bounds(self.sample_time)
        self.ids_bounds_torque = self.get_ids_bounds(self.torque_sample_time)
        # Shift signal for each tooth
        teeth_signal, teeth_cid_list = self.shift_signal(signal=tooth_signal,
                                                         signal_center=tooth_center,
                                                         time=self.sample_time, time_shift=time2tooth,
                                                         time_start=0, id_start=0)
        self.ids_bounds = self.ids_bounds_torque[:teeth_signal.shape[1], :]
        # Get teeth list
        teeth_numbering = np.arange(1, self.no_teeth+0.1, 1, dtype=np.int32)
        teeth_no_list = self.repeat2no_values(teeth_numbering,
                                              no_values=teeth_signal.shape[1])
        teeth_no_list_torque = self.repeat2no_values(teeth_numbering,
                                                     no_values=np.shape(self.ids_bounds_torque)[0])
        signal = np.zeros(teeth_signal.shape)
        for i, harmonic in enumerate(self.harmonics):
            signal_harmonic_i = np.tile(teeth_signal, [harmonic, 1])
            #signal_harmonic_i = signal_harmonic_i / len(self.harmonics)
            signal_harmonic_i = signal_harmonic_i[::harmonic, :]
            # Assign pos or neg sign to harmonic_i based on plus_minus_harmoncis
            signal_harmonic_i = signal_harmonic_i * self.plus_minus_harmonics[i]
            signal_harmonic_i = signal_harmonic_i * self.harmonics_fac[i]
            signal += signal_harmonic_i
        # Norm by number of harmonics
        signal = signal / len(self.harmonics)
        self.base_signal = signal
        self.teeth_signal = teeth_signal
        self.teeth_no_list = teeth_no_list
        self.teeth_no_list_torque = teeth_no_list_torque
        self.teeth_cid_list = teeth_cid_list

    # def get_ids2tooth(self):
    #     """
    #     Get smallest number of ids assigned to one tooth
    #     Method init_gear() must have been run
    #     """
    #     # Get Tooth Center IDs
    #     ids_array = np.array(dc(self.teeth_cid_list))
    #     ids_array = ids_array.reshape(-1, 1)
    #     # Get distance between 2 tooth in no ids
    #     dist_ids = np.abs(np.subtract(ids_array[1:-1], ids_array[0:-2]))
    #     self.ids2tooth = dist_ids


    def raw_signal(self, seed=None):
        """
        Method to return the raw signal simulated by the given gear.
        """
        self.seed = seed
        base_signal = self.base_signal
        # Add Amplitude
        amplitude_vector = self.create_amplitude_vector(method=self.ampl_method,
                                                        mu=self.mu, sigma=self.sigma,
                                                        constant=self.constant,
                                                        no_values=self.no_teeth,
                                                        repeat2no_values=base_signal.shape[1])
        base_signal = base_signal * amplitude_vector
        # Add Torque Influence
        scale_vector = self.create_scale_vector(array=self.torque, method=self.torq_method,
                                                scale_min=self.scale_min, scale_max=self.scale_max,
                                                value_min=self.value_min, value_max=self.value_max,
                                                exponent=self.exponent,
                                                norm_divisor=self.norm_divisor)
        # Resize for Case: If scale_vector.size is greater than signal.size (due to larger torque)
        scale_vector = scale_vector[0:base_signal.shape[0], :]
        base_signal = base_signal * scale_vector
        # Add noise
        noise_vector = self.create_amplitude_vector(method=self.noise_method,
                                                    mu=self.noise_mu,
                                                    sigma=self.noise_sigma,
                                                    no_values=self.sample_time.shape[0])
        base_signal = base_signal + noise_vector.reshape(-1, 1)
        return(base_signal, self.teeth_signal, self.teeth_no_list, self.teeth_cid_list)

    def get_ids_bounds(self, time):
        """
        Method to get neccessary values for method load_per_tooth() at
        initialization
        """
        # Get Tooth Center IDs
        cids = self.shift_cid(signal_center=self.tooth_center,
                                   time=time, time_shift=self.time2tooth,
                                   time_start=0, id_start=0)
        ids_array = np.array(cids).reshape(-1, 1)
        # Get distance between 2 tooth in no ids
        dist_ids = np.abs(np.subtract(ids_array[1:-1], ids_array[0:-2])).reshape(-1)
        dist_ids = np.concatenate([[min(dist_ids)], dist_ids, [max(dist_ids)]]).reshape(-1, 1)
        #dist_ids = ids_array[1] - ids_array[0]
        # # Scale distance length
        # dist_ids = dist_ids * self.GearDegVibDict['t2t_factor']
        # Take half
        dist_ids = dist_ids / 2
        # Get upper and lower bound
        ids_low = np.floor(ids_array - dist_ids)
        ids_up = np.floor(ids_array + dist_ids)
        # Add to one array
        ids_bounds = np.concatenate([ids_low, ids_up], axis=1).astype(dtype=np.int32)
        # Sanity check that there are no deviations in lower and upper bound
        for idx, id_low_up in enumerate(ids_bounds):
            # Get current number of ids assigned to one tooth
            if idx==0:
                pass
            else:
                if (id_low_up[0]-prev)!=0:
                    if abs(id_low_up[0]-prev)>1:
                        print(idx)
                        print(prev)
                        print(id_low_up)
                        raise ValueError('Deviation in IDS bounds larger than one: contact hochiak')
                    else:
                        new_value = int(id_low_up[0]+prev)/2
                        ids_bounds[idx, 0] = new_value
                        ids_bounds[idx-1, 1] = new_value
            prev = id_low_up[1]
        # Add arguments
        return(ids_bounds)

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
        # Dict tooth no
        load_dict = {str(idx+1): [] for idx in range(self.no_teeth)}
        # Iterate over torque and get mean value of load per tooth and load cycle
        for idx, id_low_up in enumerate(self.ids_bounds_torque):
            low_id = max([0, id_low_up[0]])
            up_id = min([self.torque_sample_time.shape[0], id_low_up[1]])
            load_dict[str(self.teeth_no_list_torque[idx])].append(np.mean(torque[low_id:up_id]))
        return(load_dict)


    def init_degr_signal(self):
        """
        Method to initialize the degradation raw signal simulated
        by the given gear.
        """
        #---------------------
        # Get single tooth signal with amplitude=1
        # Placeholer
        teeth_signal = {'%i' % (tooth_i): [] for tooth_i in range(1, self.no_teeth+1, 1)}
        # Start to loop over id bounds all teeth
        tooth_curr = 1
        for idx, id_low_up in enumerate(self.ids_bounds):
            # Get current number of ids assigned to one tooth
            diff = id_low_up[1] - id_low_up[0]
            # Get weights by normal distribution
            # weights: Get absolute sorted normal random numbers --> eg. [0.1, 0.3, 0.8, 0.5, 0.2]
            randn_weights = 1/np.abs(np.sort(np.random.randn(diff)))
            # weights: Norm to one
            randn_weights = randn_weights / sum(randn_weights)
            # Create zero array
            tooth_signal_i = np.zeros(diff)
            # Choose one value as one, regarding given weights
            tooth_signal_i[np.random.choice(np.arange(0, diff), p=randn_weights)] = 1
            # Iterate over all tooth and add current fraction to eachs tooth
            # dictionary: 0s if tooth_i is not current tooth
            for tooth_i in range(1, self.no_teeth+1, 1):
                if tooth_i==tooth_curr:
                    teeth_signal['%i' % (tooth_i)].extend(tooth_signal_i)
                else:
                    teeth_signal['%i' % (tooth_i)].extend(np.zeros(diff))
            # Set current tooth for next loop
            if tooth_curr==self.no_teeth+1:
                tooth_curr = 1
            else:
                tooth_curr += 1
        # Change to numpy
        #teeth_signal = np.array(teeth_signal).reshape(-1, 1)
        # Crop if given id exceeds bounds
        lower_crop = np.abs(self.ids_bounds[0, 0])
        upper_crop = min(self.sample_time.shape[0] - np.abs(self.ids_bounds[-1, 1]), -1)
        for tooth_i in range(1, self.no_teeth+1, 1):
            del(teeth_signal['%i' % (tooth_i)][:lower_crop])
            del(teeth_signal['%i' % (tooth_i)][upper_crop:])
        self.teeth_degr_signal = teeth_signal


    def tooth_degr_signal(self, nolc, statei):
        """
        Method to get a degradation signal based on
        given tooth state i.
        Method raw_signal must been run before.
        """
        if statei is not None:
            #---------------------
            # Iterate over pitting (ordered by tooth number)
            pittings = []
            labels = []
            signal = np.zeros((self.sample_time.shape[0], 1))
            for tooth, pitting in enumerate(statei.loc['$a_{%i}$' % (nolc)]):
                # if no pitting @ tooth
                if np.isnan(pitting):
                    pass
                # else pitting @ tooth
                else:
                    # Condition on tooth to filter for itself tooth mesh
                    tooth_signal = self.teeth_degr_signal['%i' % (tooth+1)]
                    # Formatting
                    tooth_signal = np.array(tooth_signal).reshape(-1,1)
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
                    # Resize for Case: If scale_vector.size is greater than signal.size (due to larger torque)
                    scale_vector = scale_vector[0:degr_signal.shape[0], :]
                    degr_signal = degr_signal * (scale_vector / 2)
                # Add noise
                noise_vector = self.create_amplitude_vector(method=self.GearDegVibDict['noise_method'],
                                                            mu=self.GearDegVibDict['noise_attributes']['mu'],
                                                            sigma=self.GearDegVibDict['noise_attributes']['sigma'],
                                                            no_values=self.sample_time.shape[0])
                degr_signal = degr_signal + noise_vector.reshape(-1, 1)
            return(degr_signal, labels)
        else:
            degr_signal = np.zeros(self.sample_time.shape)
            labels = ['None']
            return(degr_signal, labels)
