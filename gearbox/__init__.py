# -*- coding: utf-8 -*-

# import built in libarys
import os
from copy import deepcopy as dc
import sys
## import time
from IPython.display import display, HTML

# import 3rd party libarys
import numpy as np
# import pandas as pd
# from matplotlib import pyplot as plt
# from scipy.signal import gausspulse
# from sklearn.preprocessing import MinMaxScaler
# from scipy.stats import norm
# from numpy.random import uniform
# from scipy.optimize import brute
# from sklearn.metrics import mean_squared_error

# import local libarys
from gearbox.vibration import Gearbox_Vibration as Vibration
from gearbox.degradation import Gearbox_Degradation as Degradation


####################################################

class Gearbox(Vibration,
              Degradation):
    """
    Overall parent class object combining
    Gearbox Vibration Model and Gear Degradation
    Model
    """

    def __init__(self,
                 # Vibration Arguments
                 rotational_frequency_in,
                 sample_interval, sample_rate,
                 GearIn, GearOut,
                 Bearing1, Bearing2, Bearing3, Bearing4,
                 # Degradation Arguments
                 Deg_GearIn, Deg_GearOut,
                 Deg_Bearing1, Deg_Bearing2, Deg_Bearing3, Deg_Bearing4,
                 # Arguments for both
                 seed=None,
                 fixed_start=True,
                 GearDegVibDictIn=None,
                 GearDegVibDictOut=None
                 ):
        """
        Parent Class Constructor
        """
        # Vibration Arguments
        self.ga_rotational_frequency_in = rotational_frequency_in
        self.ga_sample_interval = sample_interval
        self.ga_sample_rate = sample_rate
        self.ga_GearIn = GearIn
        self.ga_GearOut = GearOut
        self.ga_Bearing1 = Bearing1
        self.ga_Bearing2 = Bearing2
        self.ga_Bearing3 = Bearing3
        self.ga_Bearing4 = Bearing4
        self.fixed_start = fixed_start
        # Degradation Arguments
        self.ga_Deg_GearIn = Deg_GearIn
        self.ga_Deg_GearOut = Deg_GearOut
        self.ga_Deg_Bearing1 = Deg_Bearing1
        self.ga_Deg_Bearing2 = Deg_Bearing2
        self.ga_Deg_Bearing3 = Deg_Bearing3
        self.ga_Deg_Bearing4 = Deg_Bearing4
        # Shared Arguments
        self.ga_seed  = seed
        # Degradation Vibration
        self.GearDegVibDictIn = GearDegVibDictIn
        self.GearDegVibDictOut = GearDegVibDictOut
        self.Vibration = Vibration(self.ga_rotational_frequency_in,
                                    self.ga_sample_interval,
                                    self.ga_sample_rate,
                                    self.ga_GearIn,
                                    self.ga_GearOut,
                                    self.ga_Bearing1,
                                    self.ga_Bearing2,
                                    self.ga_Bearing3,
                                    self.ga_Bearing4,
                                    seed=self.ga_seed,
                                    fixed_start=self.fixed_start,
                                    GearDegVibDictIn=self.GearDegVibDictIn,
                                    GearDegVibDictOut=self.GearDegVibDictOut)
        # Init Gearbox Degradation
        self.Degradation = Degradation(self.ga_GearIn['no_teeth'],
                                       self.ga_GearOut['no_teeth'],
                                       self.ga_Deg_GearIn,
                                       self.ga_Deg_GearOut,
                                       self.ga_Deg_Bearing1,
                                       self.ga_Deg_Bearing2,
                                       self.ga_Deg_Bearing3,
                                       self.ga_Deg_Bearing4,
                                       self.ga_seed)

    def initialize(self, torque):
        """
        Method to initialize the model.
        """
        display(HTML('<div style="background-color:rgb(0, 190, 255);color:black;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Initialize Degradation</b></p></div>'))
        statei = self.Degradation.init_degradation()
        display(HTML('<div style="background-color:rgb(0, 190, 255);color:black;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Initialize Vibration</b></p></div>'))
        self.Vibration.init_vibration(torque)
        # Get loads
        loads = self.Vibration.get_loads(torque)
        # Init global Attributes
        self.ga_torque = [torque]
        self.ga_load_cycle_torquechange = [np.nan]
        self.ga_load_cycle = [np.nan]
        self.ga_loads = [loads]
        self.ga_statei = [statei]
        display(HTML('<p>Done</p>'))


    def run(self, nolc, output=True):
        """
        Method to initialize the model.
        """
        ## run_start = time.time()
        # Get Degradation based on previous selected torque
        statei = self.Degradation.run_degradation(nolc, self.ga_loads[-1])
        ## print('Elapsed Time Run Degradation: %.3e' % (time.time()-run_start))
        ## run_start = time.time()
        # Get Vibration based on previous selected torque
        vibration = self.Vibration.run_vibration(nolc, self.ga_torque[-1], statei, output=True)
        ## print('Elapsed Time Run Vibration: %.3e' % (time.time()-run_start))
        # Append global Attributes
        self.ga_load_cycle.append(nolc)
        self.ga_statei.append(statei)
        display(HTML('<p>Load Cycle %i done</p>' % (nolc)))
        if output is True:
            return(vibration)

    def set(self, nolc, torque):
        """
        """
        ## run_start = time.time()
        assert ((self.ga_load_cycle[-1] == nolc) or (np.isnan(self.ga_load_cycle[-1]))), 'Given nolc must equal last given nolc for method "run()"'
        self.ga_torque.append(torque)
        self.ga_load_cycle_torquechange.append(nolc)
        # Get Vibration based loads
        loads = self.Vibration.get_loads(torque)
        ## print('Elapsed Time Set Torque: %.3e' % (time.time()-run_start))
        self.ga_loads.append(loads)


    def summary(self):
        """
        Method to summary until the current State.
        """
        display(HTML('<div style="background-color:rgb(0, 190, 255);color:black;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Summary Degradation</b></p></div>'))
        self.Degradation.summary_degradation()
        display(HTML('<div style="background-color:rgb(0, 190, 255);color:black;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Summary Vibration</b></p></div>'))
        self.Vibration.summary_vibration()
