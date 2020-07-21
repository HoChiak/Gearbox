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
#--------- Degradation Functions ----------------#
class Bearing_Degradation(Degradation_Helper,
                       Optimizer_Helper,
                       State0_Helper,
                       Woehler_Helper,
                       DamageAcc_Helper,
                       ):
    """
    Class Object to simulate teeth degradation.
    """

    def __init__(self,
                 degdict,
                 seed, # arguments given by parent class
                 verbose=0,
                 ):
        """
        Constructor method for Gear Degradation
        tbd include sanity checks for given geardict
        """
