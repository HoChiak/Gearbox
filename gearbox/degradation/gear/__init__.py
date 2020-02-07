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
from gearbox.degradation.helper import Degradation_Helper
from gearbox.degradation.helper import Optimizer_Helper
from gearbox.degradation.helper import State0_Helper
from gearbox.degradation.helper import Woehler_Helper
from gearbox.degradation.helper import DamageAcc_Helper

####################################################
#--------- Gear Degradation Functions ----------------#
class Gear_Degradation(Degradation_Helper,
                       Optimizer_Helper,
                       State0_Helper,
                       Woehler_Helper,
                       DamageAcc_Helper,
                       ):
    """
    Class Object to simulate teeth degradation.
    """

    def __init__(self, no_teeth,
                 degdict,
                 seed, # arguments given by parent class
                 ):
        """
        Constructor method for Gear Degradation
        tbd include sanity checks for given geardict
        """
        #BasicHelper.__init__(self)
        self.no_teeth = no_teeth
        self.no_failing = degdict['Failing_Teeth']
        self.p_n0 = degdict['PDF_Deg_Init']['n']
        self.p_a0 = degdict['PDF_Deg_Init']['a']
        self.p_neol = degdict['PDF_Deg_EOL']['n']
        self.p_aeol = degdict['PDF_Deg_EOL']['a']
        self.woehler_k = degdict['Woehler']['k']
        self.woehler_np = degdict['Woehler']['np']
        self.woehler_torqp = degdict['Woehler']['torqp']
        self.theta1s = self.slice2array(degdict['GridSearch']['slice_theta1'])
        self.theta2s = self.slice2array(degdict['GridSearch']['slice_theta2'])
        self.theta3s = self.slice2array(degdict['GridSearch']['slice_theta3'])
        self.neigh_chance = degdict['Chances']['neighbouring']
        self.oppo_chance = degdict['Chances']['opposite']
        self.keeporder_chance = degdict['Chances']['keeporder']
        self.seed = seed
        # States:
        self.state0 = None

    def init_gear_degradation(self):
        """
        Method to initialise the Degradation Behaviour.
        This inludes a degradation model for the given
        number of failing tooth (no_failing). The degra.
        model includes values for a0/n0, aeol/neol, the
        degradation path parameters (theta1, theta2,
        theta3) and a caculation of the reference damage
        at nolc = 0
        """
        # Initialise state0
        self.get_initial_state0()
        self.get_initial_damage()
        state_i = self.get_current_statei(None)
        return(state_i)

    def run_gear_degradation(self, nolc, loads):
        """
        Method to get the current degradation for a given
        nolc and torque (torque must be list, length equal
        to no_failure)
        """
        self.get_damage_growth(nolc, loads)
        state_i = self.get_current_statei(nolc)
        return(state_i)

    def summary_gear_degradation(self):
        """
        Method to ouput a summary of the degradation states
        """
        # Get legend
        legend = ['Row: %i <=> Tooth: %i' % (idx, tooth) for idx, tooth in enumerate(self.state0['tooth'])]
        # Display
        display(HTML('<h3>State 0 Parameter (Ref. Torque: %.3f Nm)</h3>' % (self.woehler_torqp)))
        display(self.state0)
        display(HTML('<h3>State 0 Degradation Model Plot (Ref. Torque: %.3f Nm)</h3>' % (self.woehler_torqp)))
        self.plot_state0()
        display(HTML('<h3>Damage Accumulation (until load cycle %i)</h3>' % (self.nolc[-1])))
        display(pd.DataFrame(self.damage, index=self.nolc).T)
        display(HTML('<p>Legend: %s)</p>' % (' | '.join(legend))))
        self.plot_damage()
        display(HTML('<h3>Pitting Growth (until load cycle %i)</h3>' % (self.nolc[-1])))
        display(pd.DataFrame(self.pitting_growth, index=self.nolc).T)
        display(HTML('<p>Legend: %s)</p>' % (' | '.join(legend))))
        self.plot_pitting_growth()
