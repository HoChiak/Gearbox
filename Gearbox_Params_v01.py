# Build In
# Third Party
from scipy.stats import norm, lognorm

Gearbox_Params_Version = '0.1'

######## VIBRATION ELEMENTS ###########################################

GearI =   {'torq_method': None,                                   # Torque Influence Method for inner gear
           'torq_attributes': {'scale_min': 0,                    # Attributes regarding Torque Influence Method for gear signal
                               'scale_max': 0.2,
                               'value_min': 0,
                               'value_max': 50,
                               'norm_divisor': 1,
                               'exponent': 4},
             }

GearIn = {**{'no_teeth': 21,                                         # Number of teeth
              'harmonics': [1, 2, 3, 4, 5], #, 6, 7, 8, 9],
              'signal': 'gausspulse',                                 # Signal type for gear
              'ampl_method': 'gaussian_repeat',                      # Amplitude Method for inner gear
              'ampl_attributes': {'mu': 1, 'sigma': 0.0},            # Attributes regarding Amplitude Method for gear signal
              'noise_method': None,                             # Noise Method for inner gear
              'noise_attributes': {'mu': 0, 'sigma': 0.001},           # Attributes regarding Noise Method for gear signal
              },
          **GearI}

GearOut = {**{'no_teeth': 41,                                        # Number of teeth
               'harmonics': [1], #, 2, 3, 4, 5], #, 6, 7, 8, 9],
               'signal': 'gausspulse',                                # Signal type for gear
               'ampl_method': 'gaussian_repeat',                      # Amplitude Method for inner gear
               'ampl_attributes': {'mu': 1, 'sigma': 0.},            # Attributes regarding Amplitude Method for gear signal
               'noise_method': None,                            # Noise Method for inner gear
               'noise_attributes': {'mu': 0, 'sigma': 0.001},          # Attributes regarding Noise Method for gear signal
              },
          **GearI}

# General Definition of Amplitudes etc. (can be also defined seperatedly for each Bearing)
BearingI =   {# Inner Ring Rollover
#             'harmonics': [1, 2, 4, 8],                            # Harmonics to be calculated
             'signal_iring': 'sine',                               # Signal type for inner cage
             'ampl_method_iring': 'const',                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
             'ampl_attributes_iring': {'constant': 0.25},           # Attributes regarding Amplitude Method for inner cage signal
             'noise_method_iring': None,                     # Noise Method for inner gear
             'noise_attributes_iring': {'mu': 0, 'sigma': 0.005},   # Attributes regarding Noise Method for gear signal
             'torq_method_iring': None,                         # Torque Influence Method for rolling element
             'torq_attributes_iring': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                       'scale_max': 0.1,
                                       'value_min': 0,
                                       'value_max': 50,
                                       'norm_divisor': 1,
                                       'exponent': 4},

             # Rolling Element:
             'signal_relement': 'sine',                            # Signal type for rolling element
             'ampl_method_relement': 'const',                      # Amplitude Method for rolling element signal (Repeat methods are not working for bearings)
             'ampl_attributes_relement': {'constant': 0.25},        # Attributes regarding Amplitude Method for rolling element signal
             'noise_method_relement': None,                  # Noise Method for rolling element
             'noise_attributes_relement': {'mu': 0, 'sigma': 0.01},# Attributes regarding Noise Method for gear signal
             'torq_method_relement': None,                         # Torque Influence Method for rolling element
             'torq_attributes_relement': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                          'scale_max': 0.1,
                                          'value_min': 0,
                                          'value_max': 50,
                                          'norm_divisor': 1,
                                          'exponent': 4},
             # Outer Ring Rollover
             'signal_oring': 'sine',                               # Signal type for inner cage
             'ampl_method_oring': 'const',                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
             'ampl_attributes_oring': {'constant': 0.},           # Attributes regarding Amplitude Method for inner cage signal
             'noise_method_oring': None,                     # Noise Method for inner gear
             'noise_attributes_oring': {'mu': 0, 'sigma': 0.0025},   # Attributes regarding Noise Method for gear signal
             'torq_method_oring': None,                         # Torque Influence Method for rolling element
             'torq_attributes_oring': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                       'scale_max': 0.1,
                                       'value_min': 0,
                                       'value_max': 50,
                                       'norm_divisor': 1,
                                       'exponent': 4},
            }

BearingII =   {# Inner Ring Rollover
             'harmonics_iring': [3, 10, 223],                    # Harmonics to be calculated
             'signal_iring': 'sine',                               # Signal type for inner cage
             'ampl_method_iring': 'const',                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
             'ampl_attributes_iring': {'constant': 0.25},           # Attributes regarding Amplitude Method for inner cage signal
             'noise_method_iring': None,                     # Noise Method for inner gear
             'noise_attributes_iring': {'mu': 0, 'sigma': 0.005},   # Attributes regarding Noise Method for gear signal
             'torq_method_iring': None,                         # Torque Influence Method for rolling element
             'torq_attributes_iring': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                       'scale_max': 0.1,
                                       'value_min': 0,
                                       'value_max': 50,
                                       'norm_divisor': 1,
                                       'exponent': 4},

             # Rolling Element:
             'harmonics_relement': [18, 85, 525],                    # Harmonics to be calculated
             'signal_relement': 'sine',                            # Signal type for rolling element
             'ampl_method_relement': 'const',                      # Amplitude Method for rolling element signal (Repeat methods are not working for bearings)
             'ampl_attributes_relement': {'constant': 1.},        # Attributes regarding Amplitude Method for rolling element signal
             'noise_method_relement': None,                  # Noise Method for rolling element
             'noise_attributes_relement': {'mu': 0, 'sigma': 0.01},# Attributes regarding Noise Method for gear signal
             'torq_method_relement': None,                         # Torque Influence Method for rolling element
             'torq_attributes_relement': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                          'scale_max': 0.1,
                                          'value_min': 0,
                                          'value_max': 50,
                                          'norm_divisor': 1,
                                          'exponent': 4},
             # Outer Ring Rollover
             'harmonics_oring': [1],                    # Harmonics to be calculated
             'signal_oring': 'sine',                               # Signal type for inner cage
             'ampl_method_oring': 'const',                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
             'ampl_attributes_oring': {'constant': 0.},           # Attributes regarding Amplitude Method for inner cage signal
             'noise_method_oring': None,                     # Noise Method for inner gear
             'noise_attributes_oring': {'mu': 0, 'sigma': 0.0025},   # Attributes regarding Noise Method for gear signal
             'torq_method_oring': None,                         # Torque Influence Method for rolling element
             'torq_attributes_oring': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                       'scale_max': 0.1,
                                       'value_min': 0,
                                       'value_max': 50,
                                       'norm_divisor': 1,
                                       'exponent': 4},
            }

BearingIII =   {# Inner Ring Rollover
             'harmonics_iring': [10, 299],                    # Harmonics to be calculated
             'signal_iring': 'sine',                               # Signal type for inner cage
             'ampl_method_iring': 'const',                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
             'ampl_attributes_iring': {'constant': 1},           # Attributes regarding Amplitude Method for inner cage signal
             'noise_method_iring': None,                     # Noise Method for inner gear
             'noise_attributes_iring': {'mu': 0, 'sigma': 0.005},   # Attributes regarding Noise Method for gear signal
             'torq_method_iring': None,                         # Torque Influence Method for rolling element
             'torq_attributes_iring': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                       'scale_max': 0.1,
                                       'value_min': 0,
                                       'value_max': 50,
                                       'norm_divisor': 1,
                                       'exponent': 4},

             # Rolling Element:
             'harmonics_relement': [9, 1050],                    # Harmonics to be calculated
             'signal_relement': 'sine',                            # Signal type for rolling element
             'ampl_method_relement': 'const',                      # Amplitude Method for rolling element signal (Repeat methods are not working for bearings)
             'ampl_attributes_relement': {'constant': 1},        # Attributes regarding Amplitude Method for rolling element signal
             'noise_method_relement': None,                  # Noise Method for rolling element
             'noise_attributes_relement': {'mu': 0, 'sigma': 0.01},# Attributes regarding Noise Method for gear signal
             'torq_method_relement': None,                         # Torque Influence Method for rolling element
             'torq_attributes_relement': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                          'scale_max': 0.1,
                                          'value_min': 0,
                                          'value_max': 50,
                                          'norm_divisor': 1,
                                          'exponent': 4},
             # Outer Ring Rollover
             'harmonics_oring': [1],                    # Harmonics to be calculated
             'signal_oring': 'sine',                               # Signal type for inner cage
             'ampl_method_oring': 'const',                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
             'ampl_attributes_oring': {'constant': 0.},           # Attributes regarding Amplitude Method for inner cage signal
             'noise_method_oring': None,                     # Noise Method for inner gear
             'noise_attributes_oring': {'mu': 0, 'sigma': 0.0025},   # Attributes regarding Noise Method for gear signal
             'torq_method_oring': None,                         # Torque Influence Method for rolling element
             'torq_attributes_oring': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                       'scale_max': 0.1,
                                       'value_min': 0,
                                       'value_max': 50,
                                       'norm_divisor': 1,
                                       'exponent': 4},
            }

Bearing1 = {**{'no_elements': 11}, **BearingII}                     # Number of rolling elements
Bearing2 = {**{'no_elements': 9}, **BearingI}                     # Number of rolling elements
Bearing3 = {**{'no_elements': 13}, **BearingIII}                     # Number of rolling elements
Bearing4 = {**{'no_elements': 12}, **BearingI}                     # Number of rolling elements




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

GearDegVibDictIn = {'signal': 'gausspulse',                                 # Signal type for gear
                       'fc_factor': 128*1300/60*41/21,                                      # fc = frequency * fc_factor (see gauspulse defintion)
                       'bw_factor': 0.01,                                    # see gauspulse defintion
                       'bwr_factor': -10,                                    # see gauspulse defintion
                       'scale_method': 'linear',                            # Scale Method (See Torque Influence Method)
                       'scale_attributes': {'scale_min': 0,                 # Attributes regarding Scale Method for gear signal (see Torque Influence Method)
                                           'scale_max': 8,
                                           'value_min': 0,
                                           'value_max': 4,
                                           'exponent': 2},
                       'torq_influence': False,                              # If True Torque Influence will be taken into account in the same way as in vibration definition
                       'noise_method': 'gaussian',                          # Noise Method
                       'noise_attributes': {'mu': 0, 'sigma': 0.0005},       # Attributes regarding Noise Method for
                       't2t_factor': 1,
                       }

GearDegVibDictOut = {'signal': 'gausspulse',                                # Signal type for gear
                       'fc_factor': 128*1300/60,                                      # fc = frequency * fc_factor (see gauspulse defintion)
                       'bw_factor': 0.01,                                    # see gauspulse defintion
                       'bwr_factor': -10,                                    # see gauspulse defintion
                       'scale_method': 'linear',                            # Scale Method (See Torque Influence Method)
                       'scale_attributes': {'scale_min': 0,                 # Attributes regarding Scale Method for gear signal (see Torque Influence Method)
                                           'scale_max': 8,
                                           'value_min': 0,
                                           'value_max': 4,
                                           'exponent': 2},
                       'torq_influence': False,                              # If True Torque Influence will be taken into account in the same way as in vibration definition
                       'noise_method': 'gaussian',                          # Noise Method
                       'noise_attributes': {'mu': 0, 'sigma': 0.0005},       # Attributes regarding Noise Method for
                       't2t_factor': 1,
                       }
