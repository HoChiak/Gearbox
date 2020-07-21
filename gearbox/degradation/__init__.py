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
from gearbox.degradation.bearing import Bearing_Degradation
from gearbox.degradation.gear import Gear_Degradation

####################################################
#--------- Degradation Functions ----------------#
class Gearbox_Degradation(Gear_Degradation,
                          Bearing_Degradation):
    """
    Class Object to simulate Gearbox degradation.
    """

    def __init__(self,
                 no_teeth_GearIn,
                 no_teeth_GearOut,
                 Deg_GearIn,
                 Deg_GearOut,
                 Deg_Bearing1,
                 Deg_Bearing2,
                 Deg_Bearing3,
                 Deg_Bearing4,
                 seed, # arguments given by parent class
                 verbose=0,
                 ):
        """
        Constructor method for Gearbox Degradation
        """
        self.no_teeth_GearIn = no_teeth_GearIn
        self.no_teeth_GearOut = no_teeth_GearOut
        self.Deg_GearPropIn = Deg_GearIn
        self.Deg_GearPropOut = Deg_GearOut
        self.Deg_Bearing1Prop = Deg_Bearing1
        self.Deg_Bearing2Prop = Deg_Bearing2
        self.Deg_Bearing3Prop = Deg_Bearing3
        self.Deg_Bearing4Prop = Deg_Bearing4
        self.seed = seed
        self.verbose = verbose
        self.gear_ratio =  self.no_teeth_GearOut/self.no_teeth_GearIn
        self.nolc = [None]

    def init_degradation(self):
        """
        Method to initialise the Degradation Behaviour.
        This inludes a degradation model for the given
        number of failing tooth (no_failing). The degra.
        model includes values for a0/n0, aeol/neol, the
        degradation path parameters (theta1, theta2,
        theta3) and a caculation of the reference damage
        at nolc = 0
        """
        # Init Gear In Degradation
        self.GearIn_Degradation = Gear_Degradation(self.no_teeth_GearIn,
                                                    self.Deg_GearPropIn,
                                                    self.seed, self.verbose)
        # Init Gear Out Degradation
        self.GearOut_Degradation = Gear_Degradation(self.no_teeth_GearOut,
                                                    self.Deg_GearPropOut,
                                                    self.seed, self.verbose)
        # Init Bearing1 Degradation
        self.Bearing1_Degradation = Bearing_Degradation(self.Deg_Bearing1Prop,
                                                        self.seed, self.verbose)
        # Init Bearing2 Degradation
        self.Bearing2_Degradation = Bearing_Degradation(self.Deg_Bearing2Prop,
                                                        self.seed, self.verbose)
        # Init Bearing3 Degradation
        self.Bearing3_Degradation = Bearing_Degradation(self.Deg_Bearing3Prop,
                                                        self.seed, self.verbose)
        # Init Bearing4 Degradation
        self.Bearing4_Degradation = Bearing_Degradation(self.Deg_Bearing4Prop,
                                                        self.seed, self.verbose)
        # Init Statei
        self.statei = {}
        if self.verbose == 1:
            display(HTML('<p><u>Gear in:</u></p>'))
        self.statei['GearIn'] = self.GearIn_Degradation.init_gear_degradation()
        if self.verbose == 1:
            display(HTML('<p><u>Gear out:</u></p>'))
        self.statei['GearOut'] = self.GearOut_Degradation.init_gear_degradation()
        #
        self.statei['Bearing1'] = None
        self.statei['Bearing2'] = None
        self.statei['Bearing3'] = None
        self.statei['Bearing4'] = None
        return(self.statei)


    def run_degradation(self, nolc, loads):
        """
        Method to get the current degradation for a given
        nolc and torque (torque must be list, length equal
        to no_failure)
        If gear is output gear than nolc=nolc_in/gear_ratio so for a
        uniform description nolc_ref is given as the value of nolc_in
        """
        if ((self.nolc[-1] == nolc) and (self.nolc[-1] is not None)):
            return(self.statei)
        else:
            self.statei['GearIn'] = self.GearIn_Degradation.run_gear_degradation(nolc, loads['GearIn'], nolc_ref=None)
            #
            self.statei['Bearing1'] = None
            self.statei['Bearing2'] = None
            nolc_out = round(nolc / self.gear_ratio, 3)
            self.statei['GearOut'] = self.GearOut_Degradation.run_gear_degradation(nolc_out, loads['GearOut'], nolc_ref=nolc)
            self.statei['Bearing3'] = None
            self.statei['Bearing4'] = None
            self.nolc.append(nolc)
            return(self.statei)


    def summary_degradation(self):
        """
        Method to ouput a summary of the degradation states
        """
        display(HTML('<h1>Degradation Gear In</h1>'))
        self.GearIn_Degradation.summary_gear_degradation()
        display(HTML('<h1>Degradation Gear Out</h1>'))
        self.GearOut_Degradation.summary_gear_degradation()
