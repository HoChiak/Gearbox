# -*- coding: utf-8 -*-

# import built in libarys
import os
from copy import deepcopy as dc
# import sys
from IPython.display import display, HTML
from itertools import product as cart_prod
from math import log

# import 3rd party libarys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
# import time
# from scipy.signal import gausspulse
# from sklearn.preprocessing import MinMaxScaler
# from scipy.stats import norm
from numpy.random import uniform
# from scipy.optimize import brute
from sklearn.metrics import mean_squared_error

# import local libarys


####################################################
# --------- Degradation Helper Functions ------#

class Degradation_Helper():
    """
    Class for signal specific helper methods
    """

    def __init__(self):
        """
        Class constructor for signal specific helper methods
        """

    def repeat2no_values(self, vector, no_values):
        """
        Repeat the given vector as many times needed,
        to create a repeat_vector of given number of
        values (no_values)
        """
        # Calculate number of repetitions
        no_values_vector = vector.shape[0]
        repetitions = np.ceil((no_values / no_values_vector))
        repetitions = int(repetitions) #dtype decl. not working
        # Repeat Vetor
        repeat_vector = np.tile(vector, repetitions)
        # Trim to final length
        repeat_vector = np.delete(repeat_vector,
                                  np.s_[no_values:], axis=0)
        return(repeat_vector)

    def non_uniform_cdf(self, array):
        """
        Method to get a non uniform cdf from a given array
        containing absolute or relative values.
        """
        array = array.reshape(-1, 1)
        # Norm to sum=1
        array = array / np.sum(array, axis=0)
        # Cumulative Sum along axis 0
        cdf = np.cumsum(array, axis=0)
        return(cdf)

    def draw_sample_given_chances(self, samples, chances):
        """
        Method to draw a random sample, by given changes.
        Returns an booelean array -> sample = samples[booelean array]
        """
        chances_cdf = self.non_uniform_cdf(chances).reshape(-1, 1)
        # Workaround "while" to cover probabilitys of exact 0 and 1
        condition, i = [False], 1
        while any(condition) is False:
            # Get random uniform number
            if self.seed is not None:
                np.random.seed(self.seed_counter)
                if self.seed_counter < 2**16: # pretend exceeding seed limit
                    self.seed_counter += int(uniform(low=1, high=10, size=1))
                else:
                    self.seed_counter = int(uniform(low=1, high=10, size=1))
            random_nr = uniform(low=0.0, high=1.0, size=1)
            # Calculate lower condition (Insert a 0 at index 0)
            cond1 = (np.insert(chances_cdf, 0, 0) < random_nr)
            # Calculate upper condition (Append a 1 as last entry)
            cond2 = (random_nr <= np.append(chances_cdf, 1))
            # Get combined condition
            condition = np.logical_and(cond1, cond2)
            condition = np.delete(condition, -1, axis=0)
            # Workaround "while" to cover probabilitys of exact 0 and 1
            # Set new seed for drawing random_nr
        if self.seed is not None:
            np.random.seed(self.seed)
        return(condition)

    def reorder_list_given_indexes(self, indexes, lst):
        """
        Method to reorder a list by its given indexes.
        Example: lst = [15, 20, 12] indexes = [1, 0, 2]
        Return: [20, 15, 12]
        """
        assert max(indexes) < len(lst), "Max Index is out of list range"
        lst_reorderd = np.zeros((len(lst)))
        for i, index in enumerate(indexes):
            lst_reorderd[index] = lst[i]
        return(lst_reorderd)

    def get_opposite_teeth(self, tooth_i):
        """
        Method to return the teeth on the opposite
        of tooth_i.
        Returns List containing 1 (no_teeth=even) or
        2 (no_teeth=odd) values
        """
        teeth_list = np.arange(0, self.no_teeth, 1).tolist()
        teeth_diff = self.no_teeth/2
        oppo_tooth_1 = int(tooth_i - np.floor(teeth_diff))
        oppo_tooth_2 = int(tooth_i - np.ceil(teeth_diff))
        if oppo_tooth_1 == oppo_tooth_2:
            oppo_teeth = [teeth_list[oppo_tooth_1]]
        else:
            oppo_teeth = [teeth_list[oppo_tooth_1]]
            oppo_teeth.append(teeth_list[oppo_tooth_2])
        return(oppo_teeth)

    def slice2array(self, slicetype):
        """
        Method to input slice Definition and return an
        numpy array.
        """
        array = np.arange(slicetype[0],
                          slicetype[1],
                          slicetype[2])
        return(array)


####################################################
# --------- Optimizer Helper Functions ------------#

class Optimizer_Helper():
    """
    Class for signal specific helper methods
    """

    def __init__(self):
        """
        Class constructor for signal specific helper methods
        """
        self.curr_state = 1


    def prgr_bar(self, curr_state, no_states, txt=''):
        """
        Method to plot a prgr bar. => from pip whypy
        """
        # Standard width of bar
        bar_width = 80
        # One state equals one increment
        prgr_increment = bar_width / float(no_states)
        # Add prgr done
        prgr_done = int(round(prgr_increment * curr_state))
        prgr_bar = '=' * prgr_done
        # Add devider
        if curr_state < (no_states-1):
            prgr_bar += '>'
        # Add prgr to be done
        prgr_tbd = int(round(prgr_increment * (no_states - curr_state)))
        prgr_bar += ' ' * prgr_tbd
        # Write Output
        print('[%s] %s/%s %s\r' % (prgr_bar, curr_state,
                                   no_states, txt), end="\r")

        #sys.stdout.write()
        #sys.stdout.flush()

    def exp_function(self, x, theta1, theta2, theta3):
        """
        s = theta1 * exp(theta2 * x) + theta3
        """
        x = np.array(x).reshape(-1, 1)
        y = theta1 * np.exp(theta2 * x) + theta3
        return(y)

    def inv_exp_function(self, y, theta1, theta2, theta3):
        """
        s = theta1 * exp(theta2 * x) + theta3
        """
        y = np.array(y).reshape(-1, 1)
        try:
            x = log((y - theta3) / theta1) / theta2
        except ValueError:
            x = -999
        x = float(x)
        return(x)

    def inner_loop(self, x, y, theta1, theta2, theta3, no_states):
        """
        Method representanting inner loop for opt_exp_function_brute
        """
        fval = dict()
        fval['theta1'], fval['theta2'], fval['theta3'] = theta1, theta2, theta3
        fval['x_train'], fval['y_train'] = x, y
        try:
            y_pred = self.exp_function(x, theta1, theta2, theta3)
            y_pred = y_pred.flatten()
            fval['y_pred'] = y_pred
            if self.exp_function(np.array(0), theta1, theta2, theta3) <= 0:
                fval['rmse'] = np.nan
            else:
                fval['rmse'] = mean_squared_error(y, y_pred)
        except:
            fval['y_pred'] = np.nan
            fval['rmse'] = np.nan
        # Out Progress --> Costs an enourmous amount of speed
        if self.verbose == 1:
            if self.curr_state % 1000 == 0:
                self.prgr_bar(self.curr_state, no_states, txt='')
        #self.curr_state += 1
        return(fval)

    def opt_exp_function_brute(self, x, y, theta1s,
                               theta2s, theta3s):
        """
        """
        # Parameters to display progress
        no_states = theta1s.size * theta2s.size * theta3s.size
        theta_combs = list(cart_prod(theta1s, theta2s, theta3s))
        # Init Pool for Multiprocessing
        df_val = [self.inner_loop(x, y, theta1, theta2, theta3, no_states) for theta1, theta2, theta3 in theta_combs]
        # Check if all combinations are done
        assert len(df_val) == no_states, 'Internal Failure of Brute Force GridSearch'
        df_val = pd.DataFrame(df_val)
        # To tackle display mistakes
        if self.verbose == 1:
            self.prgr_bar(no_states, no_states, txt=u'\u2713')
        # Reset curr_state
        self.curr_state = 1
        return(df_val)

    def run_optimizer4state0(self, failure_range):
        """
        Method to get the parameters of the exponetial
        initial pitting growth, for a given numer of failing
        tooth (failure_range).
        """
        # Add placeholder
        # self.state0['fval'] = np.full(self.no_teeth, np.nan) if to be stored -> transform to json first
        self.state0['theta1'] = np.full(self.no_teeth, np.nan)
        self.state0['theta2'] = np.full(self.no_teeth, np.nan)
        self.state0['theta3'] = np.full(self.no_teeth, np.nan)

        for idx in failure_range:
            x = np.array((self.state0.loc[idx, 'n0'],
                         self.state0.loc[idx, 'neol']))
            y = np.array((self.state0.loc[idx, 'a0'],
                         self.state0.loc[idx, 'aeol']))
            if self.verbose == 1:
                display(HTML('<p>Running for tooth %i failure</p>' % (self.state0.loc[idx, 'tooth'])))
            fval = self.opt_exp_function_brute(x, y, self.theta1s,
                                               self.theta2s, self.theta3s)
            # self.state0['fval'][idx] = fval
            rmse_min = (fval[fval['rmse'] == fval['rmse'].min()])
            self.state0.loc[idx, 'theta1'] = rmse_min['theta1'].values
            self.state0.loc[idx, 'theta2'] = rmse_min['theta2'].values
            self.state0.loc[idx, 'theta3'] = rmse_min['theta3'].values
            del fval


####################################################
# --------- State0 Helper Functions ---------------#

class State0_Helper():
    """
    Class for signal specific helper methods
    """

    def __init__(self):
        """
        Class constructor for signal specific helper methods
        """

    def init_n0s(self):
        """
        """
        return(self.p_n0.rvs(size=self.no_teeth))

    def init_a0s(self):
        """
        """
        return(self.p_a0.rvs(size=self.no_teeth))

    def init_neols(self):
        """
        """
        return(self.p_neol.rvs(size=self.no_teeth))

    def init_aeols(self):
        """
        """
        return(self.p_aeol.rvs(size=self.no_teeth))

    def get_teeth_init_chances(self, drawn_teeth):
        """
        Method to return the chance to draw a teeth out
        of given teeth list, with respect to already
        drawn teeth (without putting back) the
        chance ratio for neighbouring teeth and
        the chance ratio for opposite teeth
        """
        chances = np.ones((self.no_teeth))
        # If no tooth drawn yet
        if len(drawn_teeth) == 0:
            pass
        # If tooth/teeth already drawn
        else:
            list_neighbouring = []
            list_opposite = []
            for tooth_i, chance_v in enumerate(chances):
                if tooth_i not in drawn_teeth:
                    tooth_i_lower = tooth_i - 1
                    tooth_i_upper = tooth_i + 1
                    teeth_opposite = self.get_opposite_teeth(tooth_i)
                    # Adjust for upper index bound
                    if tooth_i_upper == self.no_teeth:
                        tooth_i_upper = 0
                    # Taking neighbouring effects into account
                    if ((tooth_i_lower in drawn_teeth) or (tooth_i_upper in drawn_teeth)):
                        chances[tooth_i] = chance_v * self.neigh_chance
                        list_neighbouring.append(1)
                    else:
                        list_neighbouring.append(0)
                    # Taking opposite effects into account
                    opposite_considered = False
                    for tooth_opposite in teeth_opposite:
                        if ((tooth_opposite in drawn_teeth) and not(opposite_considered)):
                            chances[tooth_i] = chance_v * self.oppo_chance
                            list_opposite.append(1)
                            opposite_considered = True
                    if not(opposite_considered):
                        list_opposite.append(0)
                else:
                    chances[tooth_i] = 0
        return(np.array(chances))

    def get_teeth_neol_chances(self, drawn_teeth):
        """
        Method to return the chance to keep the teeth
        failing order from initialisation to neol
        """
        chances = np.ones((self.no_teeth))
        # Get initial Order of teeth
        teeth_init_order = dc(self.state0['tooth'].to_list())
        teeth_init_order = pd.Series(teeth_init_order)
        # Check if tooth already drawn
        for i, tooth_i in enumerate(teeth_init_order):
            if tooth_i in drawn_teeth:
                chances[i] = 0
        # Get current number of teeth remaining
        tooth_i = len(drawn_teeth)
        chances[tooth_i] = chances[tooth_i] * self.keeporder_chance
        return(np.array(chances))

    def draw_inital_teeth_order(self):
        """
        Method to draw the pitting initialisation
        order of teeth
        """
        teeth = np.arange(0, self.no_teeth, 1)
        # Iterate over all teeth
        drawn_teeth = []
        for tooth_i in teeth:
            chances = self.get_teeth_init_chances(drawn_teeth)
            condition = self.draw_sample_given_chances(teeth, chances)
            drawn_teeth.append(teeth[condition][0])
        return(drawn_teeth)

    def draw_neol_teeth_order(self):
        """
        Method to draw the pitting order of teeth
        for neol values
        """
        teeth = dc(self.state0['tooth'].to_numpy())
        # Iterate over all teeth
        drawn_teeth = []
        for tooth_i in teeth:
            chances = self.get_teeth_neol_chances(drawn_teeth)
            condition = self.draw_sample_given_chances(teeth, chances)
            drawn_teeth.append(teeth[condition][0])
        return(drawn_teeth)

    def get_initial_values(self, seed=None):
        """
        Method to get a0, n0, aeol, neol, tooth
        """
        np.random.seed(seed)
        self.state0 = pd.DataFrame()
        # Add a0 and n0
        self.state0['a0'] = self.init_a0s().reshape(-1)
        self.state0['n0'] = self.init_n0s().reshape(-1)
        # Sort values by 'n'
        self.state0.sort_values(by=['n0'], axis=0,
                                ascending=True, inplace=True,
                                kind='mergesort')
        self.state0.reset_index(drop=True, inplace=True)
        # Add tooth no
        self.state0['tooth'] = self.draw_inital_teeth_order()
        self.state0['tooth'] = self.state0['tooth'] + 1
        # Add a- and n-EOL
        temp_df = pd.DataFrame()
        temp_df['neol'] = self.init_neols().reshape(-1)
        # Sort values by 'n'
        temp_df.sort_values(by=['neol'], axis=0,
                            ascending=True, inplace=True,
                            kind='mergesort')
        temp_df.reset_index(drop=True, inplace=True)
        # Add neol
        temp_df['tooth'] = self.draw_neol_teeth_order()
        # Sort values by tooth numbering at n0
        neol = [temp_df.loc[temp_df['tooth'] == tooth, 'neol'].iloc[0] for tooth in self.state0['tooth']]
        # Add neol to state0
        self.state0['neol'] = neol
        self.state0['aeol'] = self.init_aeols().reshape(-1)
        # Sort values by 'neol' to sort them in number of fallen teeth
        self.state0.sort_values(by=['neol'], axis=0,
                                ascending=True, inplace=True,
                                kind='mergesort')
        self.state0.reset_index(drop=True, inplace=True)

    def match_a2function(self):
        """
        Method to match a0 and aeol to the exp
        function defined by estimated theta1, theta2,
        theta3
        """
        # Iterate over all failing tooth
        new_df = dc(self.state0)
        new_df['n0_old'] = self.state0['n0']
        new_df['neol_old'] = self.state0['neol']

        for index, row in self.state0.iterrows():
            new_df.loc[index, 'n0'] = self.inv_exp_function(row['a0'],
                                                            row['theta1'],
                                                            row['theta2'],
                                                            row['theta3'])
            new_df.loc[index, 'neol'] = self.inv_exp_function(row['aeol'],
                                                              row['theta1'],
                                                              row['theta2'],
                                                              row['theta3'])
        self.state0 = new_df

    def check_valid_state0(self):
        """
        Method to check if state0 is valid
        """
        # all a0 > 0
        valid_a0 = all(list(self.state0['a0'] > 0))
        # all n0 > 0
        valid_n0 = all(list(self.state0['n0'] > 0))
        # all a0 < aeol
        valid_a0_aeol = all(list(self.state0['a0'] < self.state0['aeol']))
        # all n0 < neol
        valid_n0_neol = all(list(self.state0['n0'] < self.state0['neol']))
        # all theta are not nan
        valid_thetas = not(any(list(self.state0[['theta1', 'theta2', 'theta3']].isna().to_numpy().reshape(-1))))
        # all before are true
        valid = all([valid_a0, valid_n0, valid_a0_aeol, valid_n0_neol, valid_thetas])
        return(valid)

    def get_initial_state0(self):
        """
        Method to initialise the uninfluenced degradation behaviour.
        """
        valid = False
        while not(valid):
            # Get random uniform number
            if self.seed is not None:
                np.random.seed(self.seed_counter)
                if self.seed_counter < 2**16: # pretend exceeding seed limit
                    self.seed_counter += int(uniform(low=1, high=10, size=1))
                else:
                    self.seed_counter = int(uniform(low=1, high=10, size=1))
            # Get a0, n0, aeol, neol, tooth
            self.get_initial_values(seed=self.seed_counter)
            # Get exp parameter theta1, theta2, theta3
            self.run_optimizer4state0(np.arange(0, self.no_failing, 1))
            # Get an Backup of state0
            self.backup_state0 = dc(self.state0)
            # only keep first n failing components (arg: no_failing)
            self.state0.dropna(axis=0, how='any', inplace=True)
            # Check validity of state0 here-> only failing teeth are listed
            valid = self.check_valid_state0()
            if valid:
                # Check a second time, because match_a2f.. could lead to heavy
                # adjustments so that before invalid values are now valid.
                # Adjust a0, aeol to match exp function
                self.match_a2function()
                # Check again if adjustment leads to still valid values
                valid = self.check_valid_state0()
        # Reset Seed
        if self.seed is not None:
            np.random.seed(self.seed)

    def plot_state0(self):

        """
        Method to get the parameters of the exponetial
        initial pitting growth, for a given numer of failing
        tooth (failure_range).
        """
        label1 = []
        label2 = []
        plt.figure()
        for index, row in self.state0.iterrows():
            plt.scatter([row['n0'], row['neol']],
                        [row['a0'], row['aeol']])
            label2.append('Point Estimates for tooth %i' % (row['tooth']))
            x_mod = np.linspace(min(self.state0['n0'])*0.95,
                                max(self.state0['neol'])*1.05,
                                100).reshape(-1, 1)
            y_mod = self.exp_function(x_mod,
                                      row['theta1'],
                                      row['theta2'],
                                      row['theta3'])
            y_mod = y_mod.reshape(-1, 1)
            plt.plot(x_mod, y_mod)
            label1.append('Degradation Curve for tooth %i' % (row['tooth']))
        label1.extend(label2)
        plt.ylim([min(self.state0['a0'])*0.95,
                  max(self.state0['aeol'])*1.05])
        plt.xlim([0,
                  max(self.state0['neol'])*1.05])
        plt.ylabel('$Pitting\ Size\ a\ in\ \%$')
        plt.xlabel('$Load\ Cycles\ N\ (reference:\ input/output\ shaft)$')
        plt.legend(label1)
        plt.show()

####################################################
# --------- Degradation Helper Functions ----------#


class Woehler_Helper():
    """
    Class for signal specific helper methods
    """

    def __init__(self):
        """
        Class constructor for signal specific helper methods
        """

    def woehler_torq_of_n(self, n):
        """
        torq = torq_p * (n/n_p)
        """
        return(self.woehler_torqp * np.power((n / self.woehler_np),
                                             -1*(1/self.woehler_k)))

    def woehler_n_of_torq(self, torq):
        """
        """
        return(self.woehler_np * np.power((torq / self.woehler_torqp),
                                          -1*self.woehler_k))

####################################################
# --------- Damage Accumulation Functions ---------#


class DamageAcc_Helper():
    """
    Class for Damage Accumulation methods
    """

    def __init__(self):
        """
        Class constructor for signal specific helper methods
        """

    def get_initial_damage_values(self):
        """
        Method to get damage at nolc=0
        """
        damage = []
        for index, row in self.state0.iterrows():
            dnorm = row['neol'] - row['n0']
            ddiff = 0 - row['neol']
            damage.append((ddiff / dnorm) + 1)
        self.damage.append(damage)

    def get_corresponding_pitting_size(self):
        """
        Method to get the corresponding pitting
        size a for a given self.nolc and level of
        damage.
        """
        # Get df containing state0 and damage
        pitting_size = []
        for index, row in self.state0.iterrows():
            damage = self.damage[-1][index]
            # If damage is a negative number
            if damage < 0:
                pitting_size.append(np.nan)
            elif damage >= 0:
                dnorm = row['neol'] - row['n0']
                ref_nolc = damage * dnorm + row['n0']
                pitting = self.exp_function(ref_nolc,
                                            row['theta1'],
                                            row['theta2'],
                                            row['theta3'])
                # Reduce pitting to type scaler
                while isinstance(pitting, (list, tuple, np.ndarray)):
                    pitting = pitting[0]
                pitting_size.append(pitting)
            # If damage is for example nan
            else:
                pitting_size.append(np.nan)
        self.pitting_size.append(pitting_size)

    def get_initial_damage(self):
        """
        Method to get the initial Damage at state0
        and initialises self.nolc (number_of_load_cycle)
        at 0
        """
        # Get initial damage values and corresponding pitting
        self.get_initial_damage_values()
        self.get_corresponding_pitting_size()

    def get_damage_growth(self, loads):
        """
        Method to get the Damage fraction for the load cycle
        fraction between given nolc and previous nolc. While
        the given loads is applied in this nolc fraction
        (loads must be dict, with key tooth number (starting
        with 1) and a list of loads as values)
        """
        # Define number of load cycles
        # Get initial damage values and corresponding pitting
        damage_frac = []
        # Iterate over failing tooth
        for index, row in self.state0.iterrows():
            # print('Failing tooth %s' % (str(int(row['tooth']))))
            # Iterate over loads list
            damage_equivalent = []
            # iterrows transforms tooth int to float -> backtransform:
            for load in loads[str(int(row['tooth']))]:
                # print('Load i at tooth: %.3f' % (load))
                # Get Woehler Reference Values at D=1
                N1 = row['neol'] - row['n0']
                T1 = self.woehler_torqp
                k = self.woehler_k
                # Get values of interest at D=1
                N2 = N1 * np.power((load / T1), -1*k)
                T2 = load
                # Add to damage aquivalent
                # list of damages for one load cycle
                # print('Damage equivalent: %.3f' % (1/N2))
                damage_equivalent.append(1/N2)
            # print('List of damage equiv.: %s' % (str(damage_equivalent)))
            # Change dtype to numpy array
            damage_equivalent = np.array(damage_equivalent)
            # Get Fraction
            n_frac = self.nolc[-1] - self.nolc[-2]
            # Fraction as integer (incase of e.g outer gear and )
            n_frac = int(np.floor(n_frac))
            # print('Number of load cycles: %i' % (n_frac))
            # Repeat damage_equivalent
            damage_equivalent = self.repeat2no_values(damage_equivalent, n_frac)
            # print('Shape of damage equivalent: %s' % (damage_equivalent.shape))
            damage_frac.append(np.sum(damage_equivalent))
            # print('Damage Fraction: %s' % (str(damage_frac)))

        # Change type
        damage_frac = np.array(damage_frac)
        # print('Damage Fraction all teeth: %s' % (str(damage_frac)))
        # Accumulate new damage
        damage = dc(np.array(self.damage[-1]) + damage_frac)
        # Add new state
        self.damage.append(damage.tolist())
        self.get_corresponding_pitting_size()

    def plot_helper(self, y, string):
        """
        Method to plot the pitting growth
        """
        if self.nolc_ref[-1] is None:
            x = np.array(self.nolc)
        else:
            x = np.array(self.nolc_ref)
        x = x.reshape(-1, 1)
        y = y.reshape(x.shape[0], -1)
        plt.figure()
        plt.plot(x, y)
        labels = ['%s for tooth %i' % (string, self.state0.loc[idx, 'tooth']) for idx in range(y.shape[1])]
        plt.legend(labels)
        if 'Pitting' in string:
            plt.ylabel('$Pitting\ Size\ a\ in\ \%$')
        elif 'Damage' in string:
            plt.ylabel('$Damage\ D$')
        plt.xlim([0,
                  max([max(self.state0['neol'])*1.05, max(x)])])
        # Workaround if all entrys in y are np.nan
        if y[~np.isnan(y)].size == 0:
            y_max = 0
        else:
            y_max = max(y[~np.isnan(y)])
        if 'Pitting' in string:
            plt.ylim([min(self.state0['a0'])*0.95,
                      max([max(self.state0['aeol'])*1.05, y_max * 1.05])])
        elif 'Damage' in string:
            plt.ylim([min(self.damage[0])*0.95,
                      max([1.25, y_max * 1.05])])
        plt.xlabel('$Load\ Cycles\ N\ (reference:\ input\ shaft)$')
        plt.show()

    def plot_pitting_size(self):
        """
        Method to plot the pitting growth
        """
        self.plot_helper(np.array(self.pitting_size), 'Pitting Growth')

    def plot_damage(self):
        """
        Method to plot the damge
        """
        self.plot_helper(np.array(self.damage), 'Damage')

    def get_current_statei(self):
        """
        Method to return a list of all teeth and the corresponding pitting size
        """
        # Array of allt tooth
        all_tooth = np.arange(1, self.no_teeth+1, 1)
        # List of failed tooth, damage and pitting
        failed_tooth = self.state0['tooth'].to_numpy()
        failed_tooth = failed_tooth.reshape(1, -1)
        failed_pitting = np.array(self.pitting_size[-1])
        failed_pitting = failed_pitting.reshape(1, -1)
        failed_damage = np.array(self.damage[-1])
        failed_damage = failed_damage.reshape(1, -1)
        failed = np.concatenate([failed_tooth, failed_pitting, failed_damage], axis=0)
        # Remaining tooth, damage and pitting
        rem_tooth = [tooth for tooth in all_tooth if tooth not in failed_tooth]
        rem_tooth = np.array(rem_tooth).reshape(1, -1)
        rem_pitting = np.full(rem_tooth.shape, np.nan)
        rem_damage = np.full(rem_tooth.shape, np.nan)
        rem = np.concatenate([rem_tooth, rem_pitting, rem_damage], axis=0)
        # Concat remaining and failed
        alle = np.concatenate([failed, rem], axis=1)
        df = pd.DataFrame(alle[1:, :])
        # If gear is output gear than nolc=nolc_in/gear_ratio so for a
        # uniform description nolc_ref is given as the value of nolc_in
        df.columns = alle[0, :]
        if self.nolc_ref[-1] is None:
            df.index = ['$a_{%i}$' % (self.nolc[-1]), '$d_{%i}$' % (self.nolc[-1])]
        else:
            df.index = ['$a_{%i}$' % (self.nolc_ref[-1]), '$d_{%i}$' % (self.nolc_ref[-1])]
        df = df.reindex(sorted(df.columns), axis=1)
        self.statei = pd.concat([self.statei, df], axis=0)
        return(df)
