None, # tbd# Build In
# Third Party
from scipy.stats import norm, lognorm

Gearbox_Params_Version = '0.5'

######## VIBRATION ELEMENTS ###########################################

VibTorque =   {'torq_method': None,                                   # Torque Influence Method for inner gear
               'torq_attributes': {'scale_min': 0,                    # Attributes regarding Torque Influence Method for gear signal
                                   'scale_max': 0.2,
                                   'value_min': 0,
                                   'value_max': 50,
                                   'norm_divisor': 1,
                                   'exponent': 4},
                 }

VibNoiseGear = {'noise_method': 'gaussian',
                'noise_attributes': {'mu': 0., 'sigma': 0.0005},           # Attributes regarding Noise Method for gear signal
                }

GearIn = {**{'no_teeth': 21,                                         # Number of teeth [2,3,4,5,6,7,9,10,11,12,14,16]
              'harmonics':     [  1,   2,   3,   4,   5,    6,   7,    9,  10,  11,  12],
              'harmonics_fac': [0.25, 0.75, 0.475, 0.225, 0.4, 0.525, 0.61, 0.59, 0.46, 0.44, 0.2],
              'signal': 'gausspulse',                                 # Signal type for gear
              'ampl_method': 'gaussian_repeat',                       # Amplitude Method for inner gear
              'ampl_attributes': {'mu': 1.8 ,'sigma':0.2},             # Attributes regarding Amplitude Method for gear signal
              },
          **VibNoiseGear,
          **VibTorque}

GearOut = {**{'no_teeth': 41,                                        # Number of teeth
              'harmonics':     [  1,   2,   3,   4,   5,   6,   7,   9,  10,  11,  12],
              'harmonics_fac': [0.1, 0.8, 0.3, 0.1, 0.1, 0.1, 0.45, 0.15, 0.05, 0.3, 0.1],
              'signal': 'gausspulse',                                 # Signal type for gear
               'ampl_method': 'gaussian_repeat',                      # Amplitude Method for inner gear
               'ampl_attributes': {'mu':1.8 , 'sigma':0.2},            # Attributes regarding Amplitude Method for gear signal
              },
          **VibNoiseGear,
          **VibTorque}

# General Definition of Amplitudes etc. (can be also defined seperatedly for each Bearing)
VibNoiseBearing = {'noise_method_iring': None,                     # Noise Method for inner gear
                   'noise_attributes_iring': {'mu': 0, 'sigma': 0.005},   # Attributes regarding Noise Method for gear signal
                   'noise_method_relement': None,                  # Noise Method for rolling element
                   'noise_attributes_relement': {'mu': 0, 'sigma': 0.01},# Attributes regarding Noise Method for gear signal
                   'noise_method_oring': None,                     # Noise Method for inner gear
                   'noise_attributes_oring': {'mu': 0, 'sigma': 0.0025},   # Attributes regarding Noise Method for gear signal
                   }

Bearing1 =   {**{
                 'no_elements': 11,
                 # Inner Ring Rollover
                 'harmonics_iring':[10],
                 'harmonics_fac_iring':[1],
                 'signal_iring': 'sine',                               # Signal type for inner cage
                 'ampl_method_iring': 'const', # tbd                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
                 'ampl_attributes_iring': {'constant': 0.16},           # Attributes regarding Amplitude Method for inner cage signal
                 'torq_method_iring': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_iring': VibTorque['torq_attributes'],

                 # Rolling Element:
                 'harmonics_relement':[85],
                 'signal_relement': 'sine',                            # Signal type for rolling element
                 'ampl_method_relement': 'const',                      # Amplitude Method for rolling element signal (Repeat methods are not working for bearings)
                 'ampl_attributes_relement': {'constant': 0.11},        # Attributes regarding Amplitude Method for rolling element signal
                 'torq_method_relement': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_relement': VibTorque['torq_attributes'],
                 # Outer Ring Rollover
                 #'harmonics_oring':[30,71],
                 'signal_oring': 'sine',                               # Signal type for inner cage
                 'ampl_method_oring': None, # tbd                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
                 'ampl_attributes_oring': {'constant':0},           # Attributes regarding Amplitude Method for inner cage signal
                 'torq_method_oring': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_oring': VibTorque['torq_attributes'],
                 },
            **VibNoiseBearing,
            }
Bearing2 =   {**{
                 'no_elements': 9,
                  # Inner Ring Rollover
                 'harmonics_iring':[8, 12, 16],
                 'harmonics_fac_iring':[1, 1, 0.35],
                 'signal_iring': 'sine',                               # Signal type for inner cage
                 'ampl_method_iring': 'const', # tbd                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
                 'ampl_attributes_iring': {'constant': 0.132},           # Attributes regarding Amplitude Method for inner cage signal
                 'torq_method_iring': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_iring': VibTorque['torq_attributes'],

                 # Rolling Element:
                 'harmonics_relement':[85],
                 'signal_relement': 'sine',                            # Signal type for rolling element
                 'ampl_method_relement': None, # tbd                      # Amplitude Method for rolling element signal (Repeat methods are not working for bearings)
                 'ampl_attributes_relement': {'constant': 0.105},        # Attributes regarding Amplitude Method for rolling element signal
                 'torq_method_relement': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_relement': VibTorque['torq_attributes'],
                 # Outer Ring Rollover
                 'harmonics_oring':[30],
                 'signal_oring': 'sine',                               # Signal type for inner cage
                 'ampl_method_oring': 'const', # tbd                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
                 'ampl_attributes_oring': {'constant':0.05},           # Attributes regarding Amplitude Method for inner cage signal
                 'torq_method_oring': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_oring': VibTorque['torq_attributes'],
                 },
            **VibNoiseBearing,
            }
Bearing3 =   {**{
                 'no_elements': 13,
                  # Inner Ring Rollover
                 #'harmonics_iring':[20],
                 'signal_iring': 'sine',                               # Signal type for inner cage
                 'ampl_method_iring': None, # tbd                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
                 'ampl_attributes_iring': {'constant': 0},           # Attributes regarding Amplitude Method for inner cage signal
                 'torq_method_iring': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_iring': VibTorque['torq_attributes'],

                 # Rolling Element:
                 'harmonics_relement':[772],
                 'signal_relement': 'sine',                            # Signal type for rolling element
                 'ampl_method_relement': 'const', # tbd                      # Amplitude Method for rolling element signal (Repeat methods are not working for bearings)
                 'ampl_attributes_relement': {'constant': 0.035},        # Attributes regarding Amplitude Method for rolling element signal
                 'torq_method_relement': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_relement': VibTorque['torq_attributes'],
                 # Outer Ring Rollover
                 'harmonics_oring':[16, 19, 30],
                 'harmonics_fac_oring': [1.1, 1, 1.4],
                 'signal_oring': 'sine',                               # Signal type for inner cage
                 'ampl_method_oring': 'const', # tbd                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
                 'ampl_attributes_oring': {'constant':0.07},           # Attributes regarding Amplitude Method for inner cage signal
                 'torq_method_oring': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_oring': VibTorque['torq_attributes'],
                 },
            **VibNoiseBearing,
            }
Bearing4 =   {**{
                 'no_elements': 12,
                  # Inner Ring Rollover
                 #'harmonics_iring':[47],
                 'signal_iring': 'sine',                               # Signal type for inner cage
                 'ampl_method_iring': None, # tbd                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
                 'ampl_attributes_iring': {'constant': 0},           # Attributes regarding Amplitude Method for inner cage signal
                 'torq_method_iring': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_iring': VibTorque['torq_attributes'],

                 # Rolling Element:
                 'harmonics_relement':[198],
                 'signal_relement': 'sine',                            # Signal type for rolling element
                 'ampl_method_relement': 'const', # tbd                      # Amplitude Method for rolling element signal (Repeat methods are not working for bearings)
                 'ampl_attributes_relement': {'constant': 0.425},        # Attributes regarding Amplitude Method for rolling element signal
                 'torq_method_relement': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_relement': VibTorque['torq_attributes'],
                 # Outer Ring Rollover
                 #'harmonics_oring':[126],                    #17,35,124,126
                 'signal_oring': 'sine',                               # Signal type for inner cage
                 'ampl_method_oring': None, # tbd                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
                 'ampl_attributes_oring': {'constant':0},           # Attributes regarding Amplitude Method for inner cage signal
                 'torq_method_oring': None,                         # Torque Influence Method for rolling element
                 'torq_attributes_oring': VibTorque['torq_attributes'],
                 },
            **VibNoiseBearing,
            }


######## DEGRADATION ELEMENTS ###########################################
# Reference Value for PDFs is given for load defined 'Whoeler' 'torqp'

Deg_GearIn = {'Failing_Teeth': 1,                                      # Number of Teeth falling at Gear
              'Chances': {'neighbouring': 10,                           # Chance that multiple falling teeth are neighbouring
                          'opposite': 10,                               # Chance that multiple falling teeth are opposite to each other
                          'keeporder': 1},                            # Chance that multiple falling teeth are keeping order from init to eol
              'PDF_Deg_Init': {'n': norm(loc=6.875e6, scale=1.053e6),  # P(n_0) n in Load Cycles (ref: input shaft)
                               'a': norm(loc=0.450, scale=0.205)},     # P(a_0) a in %
              'PDF_Deg_EOL': {'n': norm(loc=11390000, scale=1.053e6),  # P(n_eol) n in Load Cycles (ref: input shaft)
                              'a': norm(loc=4.0, scale=0.)},           # P(a_eol) a in %
              'Woehler': {'k': 10.5,                                   # Woehler Exponent
                          'np': 10390000,                              # Woehler Reference n in Load Cycles (ref: input shaft)
                          'torqp': 200},                               # Woehler Reference sigma in Nm
              'GridSearch': {'slice_theta1': (0.0001, 0.0902, 0.01),   # Grid for function a = theta1 * exp(theta2 * n) + theta3 defined in slices
                             'slice_theta2': (0.10/1e6, 1.51/1e6, 0.005/1e6), #tbd change step to 0.02/1e6
                             'slice_theta3':(-2.0, 0.5, 0.05)}
             }

Deg_GearOut = {'Failing_Teeth': None,                                      # Number of Teeth falling at Gear
               'Chances': {'neighbouring': 10,                           # Chance that multiple falling teeth are neighbouring
                           'opposite': 10,                               # Chance that multiple falling teeth are opposite to each other
                           'keeporder': 1},                            # Chance that multiple falling teeth are keeping order from init to eol
               'PDF_Deg_Init': {'n': norm(loc=6.875e6, scale=1.053e6),  # P(n_0) n in Load Cycles (ref: input shaft)
                                'a': norm(loc=0.450, scale=0.305)},     # P(a_0) a in %
               'PDF_Deg_EOL': {'n': norm(loc=10390000, scale=1.053e6),  # P(n_eol) n in Load Cycles (ref: input shaft)
                               'a': norm(loc=4.0, scale=0.)},           # P(a_eol) a in %
               'Woehler': {'k': 10.5,                                   # Woehler Exponent
                           'np': 10390000,                              # Woehler Reference n in Load Cycles (ref: input shaft)
                           'torqp': 200},                               # Woehler Reference sigma in Nm
               'GridSearch': {'slice_theta1': (0.0001, 0.0902, 0.01),   # Grid for function a = theta1 * exp(theta2 * n) + theta3 defined in slices
                              'slice_theta2': (0.10/1e6, 1.51/1e6, 0.005/1e6), #tbd change step to 0.02/1e6
                              'slice_theta3':(-2.0, 0.5, 0.05)}
              }
Deg_Bearing1 = 'tbd'
Deg_Bearing2 = 'tbd'
Deg_Bearing3 = 'tbd'
Deg_Bearing4 = 'tbd'


######## DEGRADATION VIBRATION ELEMENTS ###########################################

GearDegVibDictIn = {   'scale_method': 'linear',                            # Scale Method (See Torque Influence Method)
                       'scale_attributes': {'scale_min': 1,                 # Attributes regarding Scale Method for gear signal (see Torque Influence Method)
                                           'scale_max': 2,
                                           'value_min': 0,
                                           'value_max': 4,
                                           'exponent': 2},
                       'torq_influence': False,                              # If True Torque Influence will be taken into account in the same way as in vibration definition
                       'noise_method': 'gaussian',                          # Noise Method
                       'noise_attributes': {'mu': 0, 'sigma': 0.0005},       # Attributes regarding Noise Method for
                       }

GearDegVibDictOut = {  'scale_method': 'linear',                            # Scale Method (See Torque Influence Method)
                       'scale_attributes': {'scale_min': 1,                 # Attributes regarding Scale Method for gear signal (see Torque Influence Method)
                                           'scale_max': 2,
                                           'value_min': 0,
                                           'value_max': 4,
                                           'exponent': 2},
                       'torq_influence': False,                              # If True Torque Influence will be taken into account in the same way as in vibration definition
                       'noise_method': 'gaussian',                          # Noise Method
                       'noise_attributes': {'mu': 0, 'sigma': 0.0005},       # Attributes regarding Noise Method for
                       }
