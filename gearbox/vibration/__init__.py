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
from matplotlib import pyplot as plt
# from scipy.signal import gausspulse
# from sklearn.preprocessing import MinMaxScaler
# from scipy.stats import norm
from numpy.random import uniform
# from scipy.optimize import brute
# from sklearn.metrics import mean_squared_error

# import local libarys
from gearbox.vibration.bearing import Bearing
from gearbox.vibration.gear import Gear
from gearbox.vibration.helper import BasicHelper

####################################################
#------------------- Vibration Model ---------------------#

class Gearbox_Vibration(Gear, Bearing, BasicHelper):
    """
    Add new element:
    1. Load in Class (if not already exists)
    2. Add to __init__
    3. Add to init_vibration
    4. Add to raw_signal and create plots
    """

    def __init__(self,
                 rotational_frequency_in,
                 sample_interval, sample_rate,
                 GearIn, GearOut,
                 Bearing1, Bearing2, Bearing3, Bearing4,
                 seed=None,
                 fixed_start=False,
                 GearDegVibDictIn=None,
                 GearDegVibDictOut=None
                 ):
        """
        """
        BasicHelper.__init__(self)
        self.rotational_frequency_in = rotational_frequency_in
        self.angular_frequency_in = rotational_frequency_in * 2 * np.pi
        self.sample_interval = sample_interval
        self.sample_rate = sample_rate
        self.GearPropIn = GearIn
        self.GearPropOut = GearOut
        self.Bearing1Prop = Bearing1
        self.Bearing2Prop = Bearing2
        self.Bearing3Prop = Bearing3
        self.Bearing4Prop = Bearing4
        self.seed = seed
        self.fixed_start = fixed_start
        self.GearDegVibDictIn = GearDegVibDictIn
        self.GearDegVibDictOut = GearDegVibDictOut
        self.signal_degr = None
        self.init_missing()


    def get_minimum_sample_time(self):
        """
        Method to generate a minimum time-array as
        long as is needed to be to garantie every
        tooth mesh combination has been considered.
        """
        # Get meshing time between two tooth
        time2tooth = (1 / self.rotational_frequency_in) / self.GearPropIn['no_teeth']
        # Get lowest common multiple
        toothmeshlcm = np.lcm(self.GearPropIn['no_teeth'],
                                    self.GearPropOut['no_teeth'])
        min_time = time2tooth * toothmeshlcm
        return(min_time)

    def get_torque_sample_time(self):
        """
        Method to generate a time-array as long as is
        needed to be to garantie every tooth mesh
        combination has been considered.
        """
        # Get meshing time between two tooth
        full_sample_interval_min = self.get_minimum_sample_time()
        # Double Minimum (safety margin)
        # full_sample_interval = 2 * full_sample_interval
        # Ensure that full sample interval is greater than the specified one
        full_sample_interval = full_sample_interval_min
        while full_sample_interval <= self.sample_interval:
            full_sample_interval += full_sample_interval_min
        # Get sample time
        # must start with zero!!!!
        sample_time = np.arange(0, full_sample_interval,
                                  1/self.sample_rate)
        sample_time = sample_time.reshape(-1, 1)
        self.torque_sample_time = sample_time


    def get_real_sample_time(self):
        """
        Method to generate a time-array as long as the
        given sample interval.
        """
        sample_time = np.arange(0, self.sample_interval,
                                1/self.sample_rate)
        sample_time = sample_time.reshape(-1, 1)
        self.real_sample_time = sample_time

    def trim2realsampletime(self, signal):
        """
        Method to generate a time-array for given
        length (0 -> sample_interval) [sec] and number
        of samples per second.
        """
        if self.fixed_start is True:
            self.start_id = 0
            self.stop_id = self.real_sample_time.size
        else:
            # Get length of real sample vs full sample
            real_no_samples = self.real_sample_time.size
            full_no_samples = self.torque_sample_time.size
            # Diff
            diff_no_samples = full_no_samples - real_no_samples
            # Get random start id and consecutive end
            start_id = uniform(low=0.0, high=diff_no_samples, size=1)
            start_id = int(start_id)
            stop_id = start_id + real_no_samples
            # IDs to instance arguments
            self.start_id = start_id
            self.stop_id = stop_id
        return(signal[self.start_id:self.stop_id, :])

    def init_missing(self):
        """
        Method to calculate missing entitys
        """
        self.get_real_sample_time()
        self.get_torque_sample_time()
        if self.fixed_start is True:
            self.temp_sample_time = self.real_sample_time
        else:
            self.temp_sample_time = self.torque_sample_time
        self.check_declaration(self.GearPropIn, key='no_teeth', message='')
        self.check_declaration(self.GearPropOut, key='no_teeth', message='')
        self.gear_ratio =  self.GearPropOut['no_teeth']/self.GearPropIn['no_teeth']
        self.rotational_frequency_out = self.rotational_frequency_in / self.gear_ratio
        self.angular_frequency_out =  self.angular_frequency_in / self.gear_ratio


    def init_torque_attributes(self, torque):
        """
        Method to check and init torque_in
        and torque_out
        """
        # Sanity check
        #assert torque.size == self.get_minimum_sample_time(), 'Error: the given torque vector must have a size of %i values, see the instructions for further explanation' % (self.get_minimum_sample_time())
        # Extend torque array to same length as sample length
        torque = torque.reshape(-1)
        self.torque_in = self.repeat2no_values(torque, self.torque_sample_time.size)
        self.torque_out = self.torque_in * self.gear_ratio


    def get_loads(self, torque):
        """
        Method to get the load collectives corresponding to
        the gearbox elements. This method is in vibration
        because here factors as time of tooth meshing
        are known, which are needed to accumulate the loads
        """
        # Init torque_in and torque_out new!
        self.init_torque_attributes(torque)
        # Get loads
        loads = {}
        loads['GearIn'] = self.GearIn.load_per_tooth(self.torque_in)
        loads['GearOut'] = self.GearOut.load_per_tooth(self.torque_in) #!!!!!!!!!!!!!!!!!!!!! (Code1234)
        loads['Bearing1'] = 'tbd'
        loads['Bearing2'] = 'tbd'
        loads['Bearing3'] = 'tbd'
        loads['Bearing4'] = 'tbd'
        return(loads)

    def get_degr_signal(self, nolc, statei):
        """
        Method to get the load collectives corresponding to
        the gearbox elements. This method is in vibration
        because here factors as time of tooth meshing
        are known, which are needed to accumulate the loads
        """
        # Gears
        self.degr_gin, self.degr_labels_gin = self.GearIn.tooth_degr_signal(nolc, statei['GearIn'])
        self.degr_labels_gin = ['GearIn %s' % label for label in self.degr_labels_gin]
        self.degr_gout, self.degr_labels_gout = self.GearOut.tooth_degr_signal(nolc, statei['GearOut'])
        self.degr_labels_gout = ['GearOut %s' % label for label in self.degr_labels_gout]
        # Bearings
        self.degr_b1, self.degr_labels_b1 = np.zeros((self.temp_sample_time.shape[0], 1)), ['Bearing 1 None'] # tbd'
        self.degr_b2, self.degr_labels_b2 = np.zeros((self.temp_sample_time.shape[0], 1)), ['Bearing 2 None'] # tbd'
        self.degr_b3, self.degr_labels_b3 = np.zeros((self.temp_sample_time.shape[0], 1)), ['Bearing 3 None'] # tbd'
        self.degr_b4, self.degr_labels_b4 = np.zeros((self.temp_sample_time.shape[0], 1)), ['Bearing 4 None'] # tbd'
        # Concatenate all signals
        self.signal_degr = np.concatenate([self.degr_gin, self.degr_gout,
                                     self.degr_b1, self.degr_b2,
                                     self.degr_b3, self.degr_b4],
                                     axis=1)
        self.parts_degr = self.degr_labels_gin + self.degr_labels_gout + self.degr_labels_b1 +self.degr_labels_b2 + self.degr_labels_b3 + self.degr_labels_b4

    def init_vibration(self, torque):
        """
        Method to initialize the gearbox elements
        """
        # start = time.time()
        self.init_torque_attributes(torque)
        # print('--- Execution Time "Init Torque Attributes": %.3f' % (time.time() - start))
        # start = time.time()

        self.GearIn = Gear(self.rotational_frequency_in,
                           self.GearPropIn,
                           self.sample_rate, self.temp_sample_time,
                           self.torque_sample_time,
                           self.torque_in,
                           GearDegVibDict=self.GearDegVibDictIn,
                           seed=self.seed)
        self.GearOut = Gear(self.rotational_frequency_out,
                           self.GearPropOut,
                           self.sample_rate, self.temp_sample_time,
                           self.torque_sample_time,
                           self.torque_in, #!!!!!!!!!!!!!!!!!!!!! (Code1234)
                           GearDegVibDict=self.GearDegVibDictOut,
                           seed=self.seed)
        # print('--- Execution Time "Gears Init": %.3f' % (time.time() - start))
        # start = time.time()
        self.Bearing1 = Bearing(self.rotational_frequency_in,
                                self.Bearing1Prop,
                                self.sample_rate, self.temp_sample_time,
                                self.torque_in)
        self.Bearing2 = Bearing(self.rotational_frequency_in,
                                self.Bearing2Prop,
                                self.sample_rate, self.temp_sample_time,
                                self.torque_in)
        self.Bearing3 = Bearing(self.rotational_frequency_out,
                                self.Bearing3Prop,
                                self.sample_rate, self.temp_sample_time,
                                self.torque_out)
        self.Bearing4 = Bearing(self.rotational_frequency_out,
                                self.Bearing4Prop,
                                self.sample_rate, self.temp_sample_time,
                                self.torque_out)
        # print('--- Execution Time "Bearings Init": %.3f' % (time.time() - start))


    def run_vibration(self, nolc, torque, statei=None, output=True):
        """
        Method to get the raw_signals of all elements, as well as
        the sum.
        """
        # init torque attributes removed because already in init_vibration
        # self.init_torque_attributes(torque)
        # seed dependencie on number of load cycles
        if self.seed is not None:
            seed = np.random.randint(1, high=2**16, size=1, dtype=np.int32)[0]
            np.random.seed(seed)
        else:
            seed = self.seed
        # Gear Signals
        # start = time.time()
        self.signal_gin, self.teeth_signal_gin, self.teeth_no_gin, self.teeth_cid_gin = self.GearIn.raw_signal(seed)
        self.signal_gout, self.teeth_signal_gout, self.teeth_no_gout, self.teeth_cid_gout = self.GearOut.raw_signal(seed)
        # print('--- Execution Time "Gears Vibration Signal": %.3f' % (time.time() - start))
        # start = time.time()
        # Bearing Signals
        self.signal_b1, self.ids_b1, self.parts_b1 = self.Bearing1.raw_signal()
        self.signal_b2, self.ids_b2, self.parts_b2 = self.Bearing2.raw_signal()
        self.signal_b3, self.ids_b3, self.parts_b3 = self.Bearing3.raw_signal()
        self.signal_b4, self.ids_b4, self.parts_b4 = self.Bearing4.raw_signal()
        # print('--- Execution Time "Bearings Vibration Signal": %.3f' % (time.time() - start))
        # start = time.time()
        # Concatenate all signals
        signal_raw = np.concatenate([self.signal_gin, self.signal_gout,
                                     self.signal_b1, self.signal_b2,
                                     self.signal_b3, self.signal_b4],
                                    axis=1)
        # print('--- Execution Time "Concat Vibration Signals": %.3f' % (time.time() - start))
        # start = time.time()
        # start_2 = start
        # Degradation signals
        if statei is not None:
            self.get_degr_signal(nolc, statei)
            # Concatenate degr signals
            # print('------ Execution Time "Get Degr Signal": %.3f' % (time.time() - start_2))
            # start_2 = time.time()
            signal_raw = np.concatenate([signal_raw, self.signal_degr],
                                         axis=1)
        # Pick random window to fit real sample time
        signal_raw = self.trim2realsampletime(signal_raw)
        # print('------ Execution Time "Trim 2 Real Sample Time": %.3f' % (time.time() - start_2))
        # Accumulate
        self.signal_raw = np.sum(signal_raw, axis=1).reshape(-1, 1)
        # seed dependencie on number of load cycles
        if self.seed is not None:
            np.random.seed(self.seed)
        # print('--- Execution Time "Degradation Vibration Signal": %.3f' % (time.time() - start))
        if output is True:
            return(self.signal_raw)


    def plot_signal(self, signal, legend, title):
        """
        Method to plot a bearing signal
        """
        fig = plt.figure(figsize=[15, 5])
        plt.title(title)
        plt.plot(self.temp_sample_time, signal);
        if self.fixed_start is not True:
            plt.axvspan(self.temp_sample_time[self.start_id],
                        self.temp_sample_time[self.stop_id],
                        facecolor='r',
                        alpha=0.25,
                        );
        plt.ylabel('$Acceleration\ a\ in\ m/s²$')
        plt.xlabel('$Time\ t\ in\ s$')
        plt.legend(legend)
        plt.show()

    def plot_acc_signal(self, signal, legend, title):
        """
        Method to plot accumulated signal
        """
        fig = plt.figure(figsize=[15, 5])
        plt.title(title)
        plt.plot(self.real_sample_time, signal);
        plt.ylabel('$Acceleration\ a\ in\ m/s²$')
        plt.xlabel('$Time\ t\ in\ s$')
        #plt.legend(legend)
        plt.show()

    def plot_gears(self):
        """
        Method to plot a gear signal
        """
        # Min length of sample, max length of bigger gear
        supplots = max(self.GearPropOut['no_teeth'], self.GearPropIn['no_teeth'])
        supplots = min(self.teeth_signal_gin.shape[1], supplots)

        plt.figure(figsize=[15, 2*supplots*1.1])
        # Get max for fixed ylim
        a_max = max(np.max(self.signal_gin), np.max(self.signal_gout))
        a_max = np.round(a_max, 1)
        for i in range(0, supplots):
            plt.subplot(supplots, 1, i+1)
            plt.plot(self.temp_sample_time, self.teeth_signal_gin[:, i]);
            plt.plot(self.temp_sample_time, self.teeth_signal_gout[:, i]);
            plt.legend(['Input Gear - Tooth Nr.: %i' % (self.teeth_no_gin[i]),
                        'Output Gear - Tooth Nr.: %i' % (self.teeth_no_gout[i])],
                        loc='upper right')
            plt.ylim([-a_max, a_max])
            plt.ylabel('$a\ in\ m/s²$')

        # plt.suptitle('Gear Signal')
        plt.xlabel('$Time\ t\ in\ s$')
        plt.show()

    def plot_controls(self):
        """
        Method to plot rotational frequency, torque etc
        """
        fig = plt.figure(figsize=[15, 5])
        plt.plot(self.torque_sample_time, np.ones(self.torque_sample_time.shape)*self.rotational_frequency_in, ls='--');
        plt.plot(self.torque_sample_time, np.ones(self.torque_sample_time.shape)*self.rotational_frequency_out, ls='--');
        plt.legend(['Input Rotational Frequency', 'Output Rotational Frequency'], loc='center left')
        plt.ylabel('$Rotational Frequency\ in\ r/s$')
        plt.xlabel('$Time\ t\ in\ sec$')
        plt.twinx()
        plt.plot(self.torque_sample_time, self.torque_in);
        plt.plot(self.torque_sample_time, self.torque_out);
        plt.ylabel('$Torque\ M \ in\ N/m$')
        plt.legend(['Input Torque', 'Output Torque'], loc='center right')
        plt.axvspan(self.torque_sample_time[self.start_id],
                    self.torque_sample_time[self.stop_id],
                    facecolor='r',
                    alpha=0.25,
                    );
        plt.show()

    def summary_vibration(self):
        """
        Method to plot all element signals
        """
        # Plot Accumulation
        display(HTML('<h3>Controls</h3>'))
        self.plot_controls()
        display(HTML('<h3>Accumulated Signal</h3>'))
        self.plot_acc_signal(self.signal_raw, [''], 'Accumulated Signal')
        # Plot Bearings
        for signal, ids, parts, title in zip([self.signal_b1, self.signal_b2, self.signal_b3, self.signal_b4], [self.ids_b1, self.ids_b2, self.ids_b3, self.ids_b4], [self.parts_b1, self.parts_b2, self.parts_b3, self.parts_b4], ['Bearing 1', 'Bearing 2', 'Bearing 3', 'Bearing 4']):
            display(HTML('<h3>%s Signal</h3>' % (title)))
            self.plot_signal(signal[:, ids], parts, title)
        # Plot Degradation
        display(HTML('<h3>Degradation Signal</h3>'))
        if self.signal_degr is not None:
            self.plot_signal(self.signal_degr, self.parts_degr, 'Degradation Signal')
        else:
            display(HTML('<p>Degradation not available (probably no statei argument given)</p>'))
        # Plot Gears
        display(HTML('<h3>Gear Signals</h3>'))
        self.plot_gears()
