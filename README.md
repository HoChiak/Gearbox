[![DOI](https://zenodo.org/badge/238858131.svg)](https://zenodo.org/badge/latestdoi/238858131)


# Gearbox Simulation Model

<p><b>Simulation of the vibration behaviour of a gearbox under degradation</b></p>
<img src="https://github.com/HoChiak/Gearbox/blob/master/__pictures/Gearbox.png" width="60%">



<p><b>Comparison of the vibration signals between simulation and test bench based on the frequency spectrum: </b></p>
<img src="https://github.com/HoChiak/Gearbox/blob/master/__pictures/FTT_SimVsTestbench.png" width="60%">


### Version History
<p><b>Version 0.6.2</b><u> (current)</u></p>
<li>DOI added </li>


<p><b>Version 0.6.1</b></p>
<li>Optional key {'harmonics_fac': []} (list) added to element dictionary for explicit specifying the relativ amplitude of each harmonic frequencies</li>
<li>Method for choosing 'number of fallen teeth' changed. Previous: Take the n first teeth where pitting occurs. Now: Take the n first teeth that reach the EOL criterion.</li>
<li>Degradation-Vibration modeling changed. Previous: Pitting is modeld by Gaus-Pulse. Now: Pitting is modeled by one peak [0, 0, ..., 1, ..., 0, 0] </li>
<li>Changes in Layout and Description</li>
<li>Realistic Gearbox Parameters are provided by external file (GearboxPArams.py)</li>
<li>Minor performance increase</li>
<li>Minor bug fixes</li>
<br>
<br>
<p><b>Version 0.6.0</b></p>
<li>Optional key {'harmonics': []} (list) added to element dictionary for explicit modelling of the harmonic frequencies</li>
<li>Massive performance increase</li>
<li>Further warnings and checks added</li>
<li>model.reinitialize() method added (can be used if Element Dictionarys stay the same, performance increase)</li>
<li>"verbose" argument added (verbose=1: outputs information)</li>
<li>Minor bug fixes</li>
<br>
<br>
# Brief Introduction

<br>
<li>Toolbox to simulate gearbox vibration</li>
<li>Virtual copy of an existing testbench</li>
  <ul>
    <li>Match on Vibration Spectra</li>
    <li>Match on Gear Degradation</li>
  </ul>
<li>No consideration of:</li>
  <ul>
    <li>Transmission paths formulation (Structure Borne Acoustics)</li>
    <li>Bearing Degradation (not seen in testbench)</li>
  </ul>


### Preliminary

<p> Load Modules </p>


```python
# Build In
import os
from copy import deepcopy as dc
import sys
from IPython.display import display, HTML
# Third Party
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import norm
# from gearbox_functions import gearbox_functions as gf
import gearbox_functions as gf
```

### Module Structure

<br>
<img src="https://github.com/HoChiak/Gearbox/blob/master/__pictures/Modules.png" width="80%">


<li>GearBox Simulation Toolbox is structured in Modules</li>
<li>Top Modules are accessing lower Modules</li>
<li>Helper-Module is used by Modules on the same level</li>
<li>Modules consisting of several Module Methods</li>

### State Model

<br>

<li>Acts as a state model:</li>
<li>Executes for a given load cycle (must be greater than the previous)</li>
<li>Optional: Setting a new torque signal at the given load cycle (effecting the following load cycles)</li>
<br>

<img src="https://github.com/HoChiak/Gearbox/blob/master/__pictures/State_Definition.png" width="80%">

### Inputs and main Methods

<br>
<p>General Input Arguments:</p>
<li>f<sub>i</sub>: Rotational Frequency input shaft - in revolutions per second (float)</li>
<li>t<sub>i</sub>: Sample Interval - in seconds (float)</li>
<li>f<sub>s</sub>: Sample Rate - in Hz (float)</li>
<li>seed: Random Generator Seed (integer)</li>

<p>Input Arguments <b>vibrations = model.run()</b>:</p>
<li>n<sub>lc</sub>: Current number of load cycle - in revolutions (float)</li>

<p>Input Arguments <b>model.set()</b>:</p>
<li>n<sub>lc</sub>: Current number of load cycle - in revolutions (float)</li>
<li><a href="torque">torque</a>: Input Torque - in Nm</li>



### Torque Definition

<br>

<p><b>Vibration/Degradation Output is calculated for previous given torque<sub>p-1</sub> argument.</b></p>
<p>Given Input Torque will be relevant for the next time steps n<sub>lc</sub></p>

<p>Definition:</p>
<li>Must be defined as array</li>
<li>Each value corresponds to a given time</li>
<li>Function <u>'get_sample_time_torque()'</u> returns the time vector for torque</li>
<li>Length of the torque vector must be at least as long as it takes for running once every possible meshing</li>



<p>Which Torque Applies on which Gear Element</p>
<p>Input Torque applies on:</p>
    <li>Vibration Influence of Gear In, Bearing 1 and Bearing 2</li>
    <li>Load Spectre Calculation of Gear In, Bearing 1,  Bearing 2 and <u>Gear Out</u></li>
<p>Output Torque applies on:</p>
    <li>Vibration Influence of Gear Out, Bearing 3 and Bearing 4</li>
    <li>Load Spectre Calculation of Bearing 3 and Bearing 4</li>

<p><b>Gear Degradation strongly depends on the Gearbox Design &#8594; Both Input and Output Gear Degradation are defined for input torque!!!</b></p>

# Brief Running Example

<p>Complete High Level Example. Details and Theory will follow.</p>
<p>Detailed Element Dictionary Explanation will follow</p>
<br>
<p>Load Gearbox Simulation Toolbox:</p>


```python
from gearbox import Gearbox

```

<p>Define General Input Arguments:</p>


```python
rotational_frequency_in = 42.301587301587304 # U/s | float
sample_interval = 0.25 # s | float
sample_rate = 12800 # Hz | float
seed = 8
```

<p><b>Load Gearbox Parameters: Specifying Vibration and Degradation Elements (see below for explanation)</b></p>


```python
from GearboxParams import *
```

### Torque Definition (Workaround)


```python
sample_time = gf.get_sample_time_torque(rotational_frequency_in, sample_rate, GearIn['no_teeth'], GearOut['no_teeth'])
initial_torque = np.ones(sample_time.shape) * 200 # Nm | array
```

### Instance Initialization
</div>
<br>
<p>Initialize a new Instance:</p>




```python
model = Gearbox(rotational_frequency_in,
                  sample_interval, sample_rate,
                  # Vibration Arguments
                  GearIn, GearOut,
                  Bearing1, Bearing2, Bearing3, Bearing4,
                  # Degradation Arguments
                  Deg_GearIn, Deg_GearOut,
                  Deg_Bearing1, Deg_Bearing2, Deg_Bearing3, Deg_Bearing4,
                  # Shared Arguments
                  seed=seed,
                  verbose=1, # 0: no output of "load cycle #### done"
                  fixed_start=True,
                  GearDegVibDictIn=GearDegVibDictIn,
                  GearDegVibDictOut=GearDegVibDictOut)
```

### Initialize <u>All</u> Vibration and Degradation

<br>
<p>Initialize Degradation Module: <b>initialize(torque)</b></p>
<p>Input Arguments:</p>
<li>torque: input torque</li>
<p>Returns:</p>
<li>-</li>



```python
model.initialize(initial_torque)
```


<div style="background-color:rgb(62, 68, 76);color:white;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Initialize Degradation</b></p></div>



<p><u>Gear in:</u></p>



<p>Running for tooth 4 failure</p>


    


<p><u>Gear out:</u></p>



<div style="background-color:rgb(62, 68, 76);color:white;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Initialize Vibration</b></p></div>



<p>Done</p>


### Run and Set <u>All</u> Vibration and Degradation

<br>
<p>Run Vibration and Degradation: <b>run(nolc, output=True)</b></p>
<p>Input Arguments:</p>
<li>nolc: current number of load cycle (must be greater than the previous given nolc)</li>
<li>output: if true returns vibration signal</li>
<p>Returns:</p>
<li>vibration (if output is True)</li>

<p>Set Torque for upcoming cycles: <b>set(nolc, torque)</b></p>
<p>Input Arguments:</p>
<li>nolc: current number of load cycle (must be <b>equal</b> to the previous nolc in run())</li>
<li>torque: input torque</li>
<p>Returns:</p>



```python
vibrations = []
for nolc in np.linspace(0, 12e6, 12):
    vibrations.append(model.run(nolc, output=True))
    model.set(nolc, initial_torque)
    
```

    Load Cycle 12000000 done

### Summary <u>All</u> Vibration and Degradation

<br>
<p>Initialize Degradation Module: <b>initialize(torque)</b></p>
<p>Input Arguments:</p>
<li>torque: input torque</li>
<p>Returns:</p>
<li>-</li>


```python
model.summary()

```


<div style="background-color:rgb(62, 68, 76);color:white;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Summary Degradation</b></p></div>



<h1>Degradation Gear In</h1>



<h3>State 0 Parameter (Ref. Torque: 200.000 Nm)</h3>



<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>n0</th>
      <th>tooth</th>
      <th>neol</th>
      <th>aeol</th>
      <th>theta1</th>
      <th>theta2</th>
      <th>theta3</th>
      <th>n0_old</th>
      <th>neol_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.241921</td>
      <td>6.602707e+06</td>
      <td>4</td>
      <td>8.980199e+06</td>
      <td>4.0</td>
      <td>0.0001</td>
      <td>0.000001</td>
      <td>1.776357e-15</td>
      <td>7.557768e+06</td>
      <td>8.971794e+06</td>
    </tr>
  </tbody>
</table>
</div>



<h3>State 0 Degradation Model Plot (Ref. Torque: 200.000 Nm)</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_5.png)



<h3>Damage Accumulation (until load cycle 12000000)</h3>



<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0.000000e+00</th>
      <th>0.000000e+00</th>
      <th>1.090909e+06</th>
      <th>2.181818e+06</th>
      <th>3.272727e+06</th>
      <th>4.363636e+06</th>
      <th>5.454545e+06</th>
      <th>6.545455e+06</th>
      <th>7.636364e+06</th>
      <th>8.727273e+06</th>
      <th>9.818182e+06</th>
      <th>1.090909e+07</th>
      <th>1.200000e+07</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-2.777173</td>
      <td>-2.777173</td>
      <td>-2.318325</td>
      <td>-1.859476</td>
      <td>-1.400627</td>
      <td>-0.941779</td>
      <td>-0.48293</td>
      <td>-0.024081</td>
      <td>0.434767</td>
      <td>0.893616</td>
      <td>1.352465</td>
      <td>1.811313</td>
      <td>2.270162</td>
    </tr>
  </tbody>
</table>
</div>



<p>Legend: Row: 0 <=> Tooth: 4</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_9.png)



<h3>Pitting Growth (until load cycle 12000000)</h3>



<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0.000000e+00</th>
      <th>0.000000e+00</th>
      <th>1.090909e+06</th>
      <th>2.181818e+06</th>
      <th>3.272727e+06</th>
      <th>4.363636e+06</th>
      <th>5.454545e+06</th>
      <th>6.545455e+06</th>
      <th>7.636364e+06</th>
      <th>8.727273e+06</th>
      <th>9.818182e+06</th>
      <th>1.090909e+07</th>
      <th>1.200000e+07</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>0.819196</td>
      <td>2.967858</td>
      <td>10.75223</td>
      <td>38.95417</td>
      <td>141.126754</td>
    </tr>
  </tbody>
</table>
</div>



<p>Legend: Row: 0 <=> Tooth: 4)</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_13.png)



<h1>Degradation Gear Out</h1>



<p>No teeth are failing</p>



<div style="background-color:rgb(62, 68, 76);color:white;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Summary Vibration</b></p></div>



<h3>Controls</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_18.png)



<h3>Accumulated Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_20.png)



<h3>Bearing 1 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_22.png)



<h3>Bearing 2 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_24.png)



<h3>Bearing 3 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_26.png)



<h3>Bearing 4 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_28.png)



<h3>Degradation Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_30.png)



<h3>Gear Signals</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_27_32.png)



```python
model.reinitialize(initial_torque)
```


<div style="background-color:rgb(62, 68, 76);color:white;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Initialize Degradation</b></p></div>



<p><u>Gear in:</u></p>



<p>Running for tooth 4 failure</p>


    


<p><u>Gear out:</u></p>



<p>Done</p>



```python
nolc = 4.4e6
vibration = model.run(nolc, output=True)
model.summary()   
```

    Load Cycle 4400000 done


<div style="background-color:rgb(62, 68, 76);color:white;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Summary Degradation</b></p></div>



<h1>Degradation Gear In</h1>



<h3>State 0 Parameter (Ref. Torque: 200.000 Nm)</h3>



<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>n0</th>
      <th>tooth</th>
      <th>neol</th>
      <th>aeol</th>
      <th>theta1</th>
      <th>theta2</th>
      <th>theta3</th>
      <th>n0_old</th>
      <th>neol_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.241921</td>
      <td>6.602707e+06</td>
      <td>4</td>
      <td>8.980199e+06</td>
      <td>4.0</td>
      <td>0.0001</td>
      <td>0.000001</td>
      <td>1.776357e-15</td>
      <td>7.557768e+06</td>
      <td>8.971794e+06</td>
    </tr>
  </tbody>
</table>
</div>



<h3>State 0 Degradation Model Plot (Ref. Torque: 200.000 Nm)</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_6.png)



<h3>Damage Accumulation (until load cycle 4400000)</h3>



<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0.0</th>
      <th>4400000.0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-2.777173</td>
      <td>-0.926484</td>
    </tr>
  </tbody>
</table>
</div>



<p>Legend: Row: 0 <=> Tooth: 4</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_10.png)



<h3>Pitting Growth (until load cycle 4400000)</h3>



<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0.0</th>
      <th>4400000.0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



<p>Legend: Row: 0 <=> Tooth: 4)</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_14.png)



<h1>Degradation Gear Out</h1>



<p>No teeth are failing</p>



<div style="background-color:rgb(62, 68, 76);color:white;padding:0.5em;letter-spacing:0.1em;font-size:1.5em;align=center"><p><b>Summary Vibration</b></p></div>



<h3>Controls</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_19.png)



<h3>Accumulated Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_21.png)



<h3>Bearing 1 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_23.png)



<h3>Bearing 2 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_25.png)



<h3>Bearing 3 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_27.png)



<h3>Bearing 4 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_29.png)



<h3>Degradation Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_31.png)



<h3>Gear Signals</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_29_33.png)


# Running Example - Only Vibration or Only Degradation

### Run <u>only</u> Vibration

<br>
<p>Initialize Vibration Module: <b>init_vibration(torque)</b></p>
<p>Input Arguments:</p>
<li>Input Torque</li>
<p>Returns:</p>
<li>-</li>



```python
model.Vibration.init_vibration(initial_torque)
```

<p>Get Loads from Torque: <b>get_loads(torque)</b></p>
<p>Input Arguments:</p>
<li>Input Torque</li>
<p>Returns:</p>
<li>Loads Dictionary</li>


```python
torque_in = np.sin((2 * np.pi * rotational_frequency_in * sample_time)) * 5 + 200 # Nm | array
loads = model.Vibration.get_loads(torque_in)

df_loads = pd.DataFrame(loads)
df_loads.index = df_loads.index.astype(dtype='int32')
df_loads = df_loads.sort_index()

```


```python
df_loads

```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>GearIn</th>
      <th>GearOut</th>
      <th>Bearing1</th>
      <th>Bearing2</th>
      <th>Bearing3</th>
      <th>Bearing4</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>[200.31100138240075, 199.93908292760395, 199.9...</td>
      <td>[200.31100138240075, 198.4563289064186, 197.14...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[201.37849406072755, 201.4192940350947, 201.40...</td>
      <td>[201.37849406072755, 199.9298317308874, 198.48...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[202.7349881835852, 202.72870576316683, 202.76...</td>
      <td>[202.7349881835852, 201.40971762544459, 199.91...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[203.84813737331055, 203.84026957478707, 203.8...</td>
      <td>[203.84813737331055, 202.76417422441713, 201.3...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>5</th>
      <td>[204.61122903882642, 204.61014630033674, 204.6...</td>
      <td>[204.61122903882642, 203.8363973116237, 202.74...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>6</th>
      <td>[204.96403768050845, 204.9606470412003, 204.96...</td>
      <td>[204.96403768050845, 204.60423795922097, 203.8...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>7</th>
      <td>[204.87858936868102, 204.86977537329844, 204.8...</td>
      <td>[204.87858936868102, 204.96241761265512, 204.6...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>8</th>
      <td>[204.35664921035902, 204.36338187624236, 204.3...</td>
      <td>[204.35664921035902, 204.86917584968458, 204.9...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>9</th>
      <td>[203.44707720882153, 203.45192712783563, 203.4...</td>
      <td>[203.44707720882153, 204.34270030579225, 204.8...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>10</th>
      <td>[202.223931341172, 202.23333797163062, 202.240...</td>
      <td>[202.223931341172, 203.4603685387051, 204.3517...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>11</th>
      <td>[200.8029117032604, 200.81158643185418, 200.82...</td>
      <td>[200.8029117032604, 202.24040688851608, 203.43...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>12</th>
      <td>[199.35975793060157, 199.31762417936753, 199.3...</td>
      <td>[199.35975793060157, 200.82110556009835, 202.2...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>13</th>
      <td>[197.92428127158098, 197.93158251191218, 197.8...</td>
      <td>[197.92428127158098, 199.32710986617377, 200.8...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>14</th>
      <td>[196.67349120031244, 196.6820929122891, 196.68...</td>
      <td>[196.67349120031244, 197.8929844143234, 199.34...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>15</th>
      <td>[195.72530712298695, 195.72781331878016, 195.7...</td>
      <td>[195.72530712298695, 196.68724257100942, 197.9...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>16</th>
      <td>[195.1574628433107, 195.16216618495451, 195.16...</td>
      <td>[195.1574628433107, 195.73479136295404, 196.66...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>17</th>
      <td>[195.03013468962317, 195.02696418185843, 195.0...</td>
      <td>[195.03013468962317, 195.16183609451795, 195.7...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>18</th>
      <td>[195.3449991380422, 195.34414951253532, 195.33...</td>
      <td>[195.3449991380422, 195.02899912596882, 195.16...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>19</th>
      <td>[196.04953921860147, 196.0755880499888, 196.07...</td>
      <td>[196.04953921860147, 195.33845579603647, 195.0...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>20</th>
      <td>[197.1292012366517, 197.1201738559916, 197.154...</td>
      <td>[197.1292012366517, 196.0719640174729, 195.331...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>21</th>
      <td>[198.4642919023635, 198.4563289064186, 198.446...</td>
      <td>[198.4642919023635, 197.1549683205547, 196.060...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>22</th>
      <td>NaN</td>
      <td>[199.93908292760395, 198.44675982727605, 197.1...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>23</th>
      <td>NaN</td>
      <td>[201.4192940350947, 199.92065398177144, 198.47...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>24</th>
      <td>NaN</td>
      <td>[202.72870576316683, 201.40160792965676, 199.9...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>25</th>
      <td>NaN</td>
      <td>[203.84026957478707, 202.75506034779656, 201.3...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>26</th>
      <td>NaN</td>
      <td>[204.61014630033674, 203.86338191669398, 202.7...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>27</th>
      <td>NaN</td>
      <td>[204.9606470412003, 204.603120009825, 203.8517...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>28</th>
      <td>NaN</td>
      <td>[204.86977537329844, 204.95899384668485, 204.6...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>29</th>
      <td>NaN</td>
      <td>[204.36338187624236, 204.87364236737417, 204.9...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>30</th>
      <td>NaN</td>
      <td>[203.45192712783563, 204.34494518194649, 204.8...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>31</th>
      <td>NaN</td>
      <td>[202.23333797163062, 203.4296575164903, 204.35...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>32</th>
      <td>NaN</td>
      <td>[200.81158643185418, 202.24980679409109, 203.4...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>33</th>
      <td>NaN</td>
      <td>[199.31762417936753, 200.82976520821128, 202.2...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>34</th>
      <td>NaN</td>
      <td>[197.93158251191218, 199.33589545725212, 200.7...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>35</th>
      <td>NaN</td>
      <td>[196.6820929122891, 197.9024379965773, 199.354...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>36</th>
      <td>NaN</td>
      <td>[195.72781331878016, 196.65561062393266, 197.9...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>37</th>
      <td>NaN</td>
      <td>[195.16216618495451, 195.7373317520114, 196.66...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>38</th>
      <td>NaN</td>
      <td>[195.02696418185843, 195.1665702807718, 195.72...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>39</th>
      <td>NaN</td>
      <td>[195.34414951253532, 195.02586208686793, 195.1...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>40</th>
      <td>NaN</td>
      <td>[196.0755880499888, 195.33764148216096, 195.02...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
    <tr>
      <th>41</th>
      <td>NaN</td>
      <td>[197.1201738559916, 196.06425313470905, 195.33...</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
      <td>tbd</td>
    </tr>
  </tbody>
</table>
</div>



<p>Get Vibration Signal: <b>run_vibration(nolc, torque, statei=None, output=True)</b></p>
<p>Input Arguments:</p>
<li>nolc: current number of load cycle</li>
<li>torque: Input Torque</li>
<li>statei: current degradation state</li>
<li>output: if true method returns vibration signal</li>
<p>Returns:</p>
<li>vibration signal</li>


```python
nolc = 2e6
vibration = model.Vibration.run_vibration(nolc, initial_torque, statei=None, output=True)
```


```python
plt.plot(np.arange(0, sample_interval, 1/sample_rate), vibration)
plt.xlabel('Time in seconds'), plt.ylabel('Acceleration in g'), plt.legend(['Vibration Signal'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_37_0.png)


<p>Summarize Vibration: <b>summary_vibration()</b></p>


```python
model.Vibration.summary_vibration()
```


<h3>Controls</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_39_1.png)



<h3>Accumulated Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_39_3.png)



<h3>Bearing 1 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_39_5.png)



<h3>Bearing 2 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_39_7.png)



<h3>Bearing 3 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_39_9.png)



<h3>Bearing 4 Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_39_11.png)



<h3>Degradation Signal</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_39_13.png)



<h3>Gear Signals</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_39_15.png)


### Run <u>only</u> Degradation

<br>
<p>Initialize Degradation Module: <b>init_degradation()</b></p>
<p>Input Arguments:</p>
<p>Returns:</p>
<li>statei: DataFrame containing the degradation states</li>


```python
statei = model.Degradation.init_degradation()

```


<p><u>Gear in:</u></p>



<p>Running for tooth 4 failure</p>


    


<p><u>Gear out:</u></p>



```python
pd.DataFrame(statei['GearIn'])

```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>1.0</th>
      <th>2.0</th>
      <th>3.0</th>
      <th>4.0</th>
      <th>5.0</th>
      <th>6.0</th>
      <th>7.0</th>
      <th>8.0</th>
      <th>9.0</th>
      <th>10.0</th>
      <th>...</th>
      <th>12.0</th>
      <th>13.0</th>
      <th>14.0</th>
      <th>15.0</th>
      <th>16.0</th>
      <th>17.0</th>
      <th>18.0</th>
      <th>19.0</th>
      <th>20.0</th>
      <th>21.0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>$a_{0}$</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>$d_{0}$</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-2.777173</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>2 rows × 21 columns</p>
</div>




```python
pd.DataFrame(statei['GearOut'])

```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



<p>Summarize Vibration: <b>summary_vibration()</b></p>


```python
model.Degradation.summary_degradation()
```


<h1>Degradation Gear In</h1>



<h3>State 0 Parameter (Ref. Torque: 200.000 Nm)</h3>



<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>n0</th>
      <th>tooth</th>
      <th>neol</th>
      <th>aeol</th>
      <th>theta1</th>
      <th>theta2</th>
      <th>theta3</th>
      <th>n0_old</th>
      <th>neol_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.241921</td>
      <td>6.602707e+06</td>
      <td>4</td>
      <td>8.980199e+06</td>
      <td>4.0</td>
      <td>0.0001</td>
      <td>0.000001</td>
      <td>1.776357e-15</td>
      <td>7.557768e+06</td>
      <td>8.971794e+06</td>
    </tr>
  </tbody>
</table>
</div>



<h3>State 0 Degradation Model Plot (Ref. Torque: 200.000 Nm)</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_45_4.png)



<h3>Damage Accumulation (until load cycle 0)</h3>



<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-2.777173</td>
    </tr>
  </tbody>
</table>
</div>



<p>Legend: Row: 0 <=> Tooth: 4</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_45_8.png)



<h3>Pitting Growth (until load cycle 0)</h3>



<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



<p>Legend: Row: 0 <=> Tooth: 4)</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_45_12.png)



<h1>Degradation Gear Out</h1>



<p>No teeth are failing</p>


<p>Get Degradation Growth: <b>run_degradation(nolc, loads)</b></p>
<p>Input Arguments:</p>
<li>nolc: current number of load cycle (must be greater than the previous given nolc)</li>
<li>loads: Dictionary regarding get_loads(torque) return</li>
<p>Returns:</p>
<li>statei </li>


```python
loads = {'GearIn': {'%i' %(int(i)): [200] for i in range(1, GearIn['no_teeth']+1, 1)},
         'GearOut': {'%i' %(int(i)): [200] for i in range(1, GearOut['no_teeth']+1, 1)}}

for nolc in np.linspace(1e6, 6e6, 50):
    statei = model.Degradation.run_degradation(nolc, loads)
    
```


```python
pd.DataFrame(statei['GearIn'])

```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>1.0</th>
      <th>2.0</th>
      <th>3.0</th>
      <th>4.0</th>
      <th>5.0</th>
      <th>6.0</th>
      <th>7.0</th>
      <th>8.0</th>
      <th>9.0</th>
      <th>10.0</th>
      <th>...</th>
      <th>12.0</th>
      <th>13.0</th>
      <th>14.0</th>
      <th>15.0</th>
      <th>16.0</th>
      <th>17.0</th>
      <th>18.0</th>
      <th>19.0</th>
      <th>20.0</th>
      <th>21.0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>$a_{6000000}$</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>$d_{6000000}$</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>-0.253522</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>2 rows × 21 columns</p>
</div>




```python
pd.DataFrame(statei['GearOut'])

```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>




```python
model.Degradation.summary_degradation()

```


<h1>Degradation Gear In</h1>



<h3>State 0 Parameter (Ref. Torque: 200.000 Nm)</h3>



<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>n0</th>
      <th>tooth</th>
      <th>neol</th>
      <th>aeol</th>
      <th>theta1</th>
      <th>theta2</th>
      <th>theta3</th>
      <th>n0_old</th>
      <th>neol_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.241921</td>
      <td>6.602707e+06</td>
      <td>4</td>
      <td>8.980199e+06</td>
      <td>4.0</td>
      <td>0.0001</td>
      <td>0.000001</td>
      <td>1.776357e-15</td>
      <td>7.557768e+06</td>
      <td>8.971794e+06</td>
    </tr>
  </tbody>
</table>
</div>



<h3>State 0 Degradation Model Plot (Ref. Torque: 200.000 Nm)</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_50_4.png)



<h3>Damage Accumulation (until load cycle 6000000)</h3>



<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0.000000e+00</th>
      <th>1.000000e+06</th>
      <th>1.102041e+06</th>
      <th>1.204082e+06</th>
      <th>1.306122e+06</th>
      <th>1.408163e+06</th>
      <th>1.510204e+06</th>
      <th>1.612245e+06</th>
      <th>1.714286e+06</th>
      <th>1.816327e+06</th>
      <th>...</th>
      <th>5.081633e+06</th>
      <th>5.183673e+06</th>
      <th>5.285714e+06</th>
      <th>5.387755e+06</th>
      <th>5.489796e+06</th>
      <th>5.591837e+06</th>
      <th>5.693878e+06</th>
      <th>5.795918e+06</th>
      <th>5.897959e+06</th>
      <th>6.000000e+06</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-2.777173</td>
      <td>-2.356562</td>
      <td>-2.313643</td>
      <td>-2.270724</td>
      <td>-2.227804</td>
      <td>-2.184885</td>
      <td>-2.141966</td>
      <td>-2.099047</td>
      <td>-2.056128</td>
      <td>-2.013209</td>
      <td>...</td>
      <td>-0.639795</td>
      <td>-0.596876</td>
      <td>-0.553956</td>
      <td>-0.511037</td>
      <td>-0.468118</td>
      <td>-0.425199</td>
      <td>-0.38228</td>
      <td>-0.339361</td>
      <td>-0.296441</td>
      <td>-0.253522</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 51 columns</p>
</div>



<p>Legend: Row: 0 <=> Tooth: 4</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_50_8.png)



<h3>Pitting Growth (until load cycle 6000000)</h3>



<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0.000000e+00</th>
      <th>1.000000e+06</th>
      <th>1.102041e+06</th>
      <th>1.204082e+06</th>
      <th>1.306122e+06</th>
      <th>1.408163e+06</th>
      <th>1.510204e+06</th>
      <th>1.612245e+06</th>
      <th>1.714286e+06</th>
      <th>1.816327e+06</th>
      <th>...</th>
      <th>5.081633e+06</th>
      <th>5.183673e+06</th>
      <th>5.285714e+06</th>
      <th>5.387755e+06</th>
      <th>5.489796e+06</th>
      <th>5.591837e+06</th>
      <th>5.693878e+06</th>
      <th>5.795918e+06</th>
      <th>5.897959e+06</th>
      <th>6.000000e+06</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 51 columns</p>
</div>



<p>Legend: Row: 0 <=> Tooth: 4)</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_50_12.png)



<h1>Degradation Gear Out</h1>



<p>No teeth are failing</p>



```python
loads = {'GearIn': {'%i' %(int(i)): [200] for i in range(1, GearIn['no_teeth']+1, 1)},
         'GearOut': {'%i' %(int(i)): [200] for i in range(1, GearOut['no_teeth']+1, 1)}}

for nolc in np.linspace(6.1e6, 10e6, 40):
    statei = model.Degradation.run_degradation(nolc, loads)
    
```


```python
pd.DataFrame(statei['GearIn'])
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>1.0</th>
      <th>2.0</th>
      <th>3.0</th>
      <th>4.0</th>
      <th>5.0</th>
      <th>6.0</th>
      <th>7.0</th>
      <th>8.0</th>
      <th>9.0</th>
      <th>10.0</th>
      <th>...</th>
      <th>12.0</th>
      <th>13.0</th>
      <th>14.0</th>
      <th>15.0</th>
      <th>16.0</th>
      <th>17.0</th>
      <th>18.0</th>
      <th>19.0</th>
      <th>20.0</th>
      <th>21.0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>$a_{10000000}$</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>13.324606</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>$d_{10000000}$</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1.428923</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>2 rows × 21 columns</p>
</div>




```python
pd.DataFrame(statei['GearOut'])
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>




```python
model.Degradation.summary_degradation()

```


<h1>Degradation Gear In</h1>



<h3>State 0 Parameter (Ref. Torque: 200.000 Nm)</h3>



<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>n0</th>
      <th>tooth</th>
      <th>neol</th>
      <th>aeol</th>
      <th>theta1</th>
      <th>theta2</th>
      <th>theta3</th>
      <th>n0_old</th>
      <th>neol_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.241921</td>
      <td>6.602707e+06</td>
      <td>4</td>
      <td>8.980199e+06</td>
      <td>4.0</td>
      <td>0.0001</td>
      <td>0.000001</td>
      <td>1.776357e-15</td>
      <td>7.557768e+06</td>
      <td>8.971794e+06</td>
    </tr>
  </tbody>
</table>
</div>



<h3>State 0 Degradation Model Plot (Ref. Torque: 200.000 Nm)</h3>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_54_4.png)



<h3>Damage Accumulation (until load cycle 10000000)</h3>



<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0.000000e+00</th>
      <th>1.000000e+06</th>
      <th>1.102041e+06</th>
      <th>1.204082e+06</th>
      <th>1.306122e+06</th>
      <th>1.408163e+06</th>
      <th>1.510204e+06</th>
      <th>1.612245e+06</th>
      <th>1.714286e+06</th>
      <th>1.816327e+06</th>
      <th>...</th>
      <th>9.100000e+06</th>
      <th>9.200000e+06</th>
      <th>9.300000e+06</th>
      <th>9.400000e+06</th>
      <th>9.500000e+06</th>
      <th>9.600000e+06</th>
      <th>9.700000e+06</th>
      <th>9.800000e+06</th>
      <th>9.900000e+06</th>
      <th>1.000000e+07</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-2.777173</td>
      <td>-2.356562</td>
      <td>-2.313643</td>
      <td>-2.270724</td>
      <td>-2.227804</td>
      <td>-2.184885</td>
      <td>-2.141966</td>
      <td>-2.099047</td>
      <td>-2.056128</td>
      <td>-2.013209</td>
      <td>...</td>
      <td>1.050373</td>
      <td>1.092434</td>
      <td>1.134495</td>
      <td>1.176556</td>
      <td>1.218617</td>
      <td>1.260679</td>
      <td>1.30274</td>
      <td>1.344801</td>
      <td>1.386862</td>
      <td>1.428923</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 91 columns</p>
</div>



<p>Legend: Row: 0 <=> Tooth: 4</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_54_8.png)



<h3>Pitting Growth (until load cycle 10000000)</h3>



<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0.000000e+00</th>
      <th>1.000000e+06</th>
      <th>1.102041e+06</th>
      <th>1.204082e+06</th>
      <th>1.306122e+06</th>
      <th>1.408163e+06</th>
      <th>1.510204e+06</th>
      <th>1.612245e+06</th>
      <th>1.714286e+06</th>
      <th>1.816327e+06</th>
      <th>...</th>
      <th>9.100000e+06</th>
      <th>9.200000e+06</th>
      <th>9.300000e+06</th>
      <th>9.400000e+06</th>
      <th>9.500000e+06</th>
      <th>9.600000e+06</th>
      <th>9.700000e+06</th>
      <th>9.800000e+06</th>
      <th>9.900000e+06</th>
      <th>1.000000e+07</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>...</td>
      <td>4.607164</td>
      <td>5.184184</td>
      <td>5.833472</td>
      <td>6.56408</td>
      <td>7.386193</td>
      <td>8.31127</td>
      <td>9.352208</td>
      <td>10.523517</td>
      <td>11.841525</td>
      <td>13.324606</td>
    </tr>
  </tbody>
</table>
<p>1 rows × 91 columns</p>
</div>



<p>Legend: Row: 0 <=> Tooth: 4)</p>



![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_54_12.png)



<h1>Degradation Gear Out</h1>



<p>No teeth are failing</p>


# Details and Theory

### Vibration Element Definition

<br>
<h3>Gear Element</h3>
<p>Keyword Attributes: <br>
<ol>
    <li><b>no_teeth: Number of teeth</b> <br></li>
    <li>signal: <a href="NonstationarySignals">Nonstationary Signals</a><br></li>
    <li>ampl_method: <a href="AmplitudeMethod">Method to create Signal Amplitude</a><br></li>
    <li>ampl_attributes: <a href="AmplitudeMethod">Attributes regarding the Method to create Signal Amplitude</a><br></li>
    <li>noise_method:  <a href="AmplitudeMethod">Method to create Signal Noise (repeat methods are not working)</a><br></li>
    <li>noise_attributes: <a href="AmplitudeMethod">Attributes regarding the Method to create Signal Noise</a><br></li>
    <li>torq_method:  <a href="TorqueMethod">Method to create Signal Noise (repeat methods are not working)</a><br></li>
    <li>torq_attributes: <a href="TorqueAmplitudeMethod">Attributes regarding the Method to create Signal Noise</a><br></li>
</ol>
</p>

<p>Gear Element:</p>


```python
Gear = {'no_teeth': 10,                                         # Number of teeth
        'signal': 'gausspulse',                                 # Signal type for gear
        'ampl_method': 'gaussian_repeat',                       # Amplitude Method for inner gear
        'ampl_attributes': {'mu': 4, 'sigma': 0.5},             # Attributes regarding Amplitude Method for gear signal
        'noise_method': None,                                   # Noise Method for inner gear
        'noise_attributes': {'mu': 0, 'sigma': 0.25},           # Attributes regarding Noise Method for gear signal
        'torq_method': None,                                    # Torque Influence Method for inner gear
        'torq_attributes': {'scale_min': 0,
                            'scale_max': 0.2,
                            'value_min': 0,
                            'value_max': 50,
                            'norm_divisor': 200,
                            'exponent': 2},
        }
```

<p>Modelling:</p>

<li>The chosen Non-Stationary Signal is repeated every tooth mesh</li>
<li>Repeat Methods are modeling the same amplitude at tooth i</li>
<li>Using const_repeat argument constant must be a list of length no_teeth</li>

<h3>Bearing Element</h3>
<p>Keyword Attributes: <br>

<ol>
    <li><b>no_elements: Number of rolling elements</b> <br></li>
    <li>signal_*: <a href="NonstationarySignals">Nonstationary Signals</a><br></li>
    <li>ampl_method_*: <a href="AmplitudeMethod">Method to create Signal Amplitude</a><br></li>
    <li>ampl_attributes_*: <a href="AmplitudeMethod">Attributes regarding the Method to create Signal Amplitude</a><br></li>
    <li>noise_method_*:  <a href="AmplitudeMethod">Method to create Signal Noise (repeat methods are not working)</a><br></li>
    <li>noise_attributes_*: <a href="AmplitudeMethod">Attributes regarding the Method to create Signal Noise</a><br></li>
    <li>torq_method_*:  <a href="TorqueMethod">Method to create Signal Noise (repeat methods are not working)</a><br></li>
    <li>torq_attributes_*: <a href="TorqueAmplitudeMethod">Attributes regarding the Method to create Signal Noise</a><br></li>
</ol>
</p>

<p>*: Can be 'iring' (inner ring), 'relement' (rolling element) or 'oring' (outer ring)</p>




```python
Bearing =   {'no_elements': 11,                                    # Number of Rolling Elements
             # Inner Ring Rollover
             'signal_iring': 'sine',                               # Signal type for inner cage
             'ampl_method_iring': 'const',                         # Amplitude Method for inner cage signal (Repeat methods are not working for bearings)
             'ampl_attributes_iring': {'constant': 2.5},           # Attributes regarding Amplitude Method for inner cage signal
             'noise_method_iring': 'gaussian',                     # Noise Method for inner gear
             'noise_attributes_iring': {'mu': 0, 'sigma': 0.05},   # Attributes regarding Noise Method for gear signal
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
             'ampl_attributes_relement': {'constant': 1.2},        # Attributes regarding Amplitude Method for rolling element signal
             'noise_method_relement': 'gaussian',                  # Noise Method for rolling element
             'noise_attributes_relement': {'mu': 0, 'sigma': 0.05},# Attributes regarding Noise Method for gear signal
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
             'ampl_attributes_oring': {'constant': 2.5},           # Attributes regarding Amplitude Method for inner cage signal
             'noise_method_oring': 'gaussian',                     # Noise Method for inner gear
             'noise_attributes_oring': {'mu': 0, 'sigma': 0.05},   # Attributes regarding Noise Method for gear signal
             'torq_method_oring': None,                         # Torque Influence Method for rolling element
             'torq_attributes_oring': {'scale_min': 0,          # Attributes regarding Torque Influence Method for rolling element signal
                                       'scale_max': 0.1,
                                       'value_min': 0,
                                       'value_max': 50,
                                       'norm_divisor': 1,
                                       'exponent': 4},          
            }
```

<p>Modelling:</p>

<li>The frequencies for the chosen Stationary Signal are estimated by VDI 3832 (Estimation without geometrical dimensions)</li>
<li>Repeat Methods are not working</li>
<li>Formula:</li>
<ul>
    <li>f<sub>K</sub> &cong; (0.4....0.45) &sdot; f<sub>n</sub>  (As approximation factor 0.425 is chosen)</li>
    <li>f<sub>I</sub> &cong; (f<sub>n</sub> &minus; f<sub>K</sub>) &sdot; Z</li>
    <li>f<sub>A</sub> &cong; Z &sdot; f<sub>K</sub></li>
</ul>

<li>Legend:</li>
<ul>
    <li>f<sub>n</sub>: rotational frequency of the rotor</li>
    <li>Z: number of rolling elements</li>
    <li>f<sub>K</sub>: rotational frequency of the rolling element</li>
    <li>f<sub>I</sub>: inner ring rollover frequency</li>
    <li>f<sub>A</sub>: outer ring rollover frequency</li>
</ul>

### Vibration Methods and Theory

<br>

<p>Module Methods Structure:</p>

<img src="https://github.com/HoChiak/Gearbox/blob/master/__pictures/Vibration_Method.png" width="100%">




<p>Required Inputs:</p>
<li>General Input Arguments (previous slides)</li>
<li>Vibration Method Definition for each Element (see following slides)</li>
<li>State of Degradation (given by degradation model)</li>

<p>Methods and Returns:</p>
<li>run(): Vibration Signal (for state s<sub>p</sub> = n<sub>lc</sub> based on previous torque<sub>p-1</sub>)</li>
<li>set(): Loads per tooth/bearing (based on current torque<sub>p</sub>)</li>


<h3>Element Method</h3>
<br>

<li>Creating Base Signals for Bearing and Gear Elements</li>
<li>Amplitude of +-1</li>
<li>For Bearing choose any stationary signal: 'sine'</li>
<li>For Gear choose any non-stationary signal: <a href="https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.gausspulse.html">'gausspulse'</a> <br>
</li>


<p>Example Non-Stationary Sine Signal</p>


```python
from scipy.signal import gausspulse
fi, fs = 5, 100
time_vector = gf.get_sample_time_torque(fi, fs, 21, 41)
element_signal = gausspulse(np.linspace(-max(time_vector)/2, max(time_vector)/2, time_vector.size), fc=fi, bw=0.5, bwr=-6, tpr=-60, retquad=False, retenv=False) # Nm | array

plt.plot(time_vector, element_signal)
plt.xlabel('Time in seconds'), plt.ylabel('Acceleration in g'), plt.legend(['Example Element Signal'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_66_0.png)


<p>Example Stationary Sine Signal</p>


```python
fi, fs = 5, 100
time_vector = gf.get_sample_time_torque(fi, fs, 21, 41)
element_signal = np.sin((2 * np.pi * fi * time_vector)) # Nm | array

plt.plot(time_vector, element_signal)
plt.xlabel('Time in seconds'), plt.ylabel('Acceleration in g'), plt.legend(['Example Element Signal'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_68_0.png)


<h3>Amplitude Method</h3>
<br>

<li>Scaling the Base Signals</li>
<li>Various methods can be chosen (depending on Element)</li>
<li>Depending on the chosen Method, different Attributes must be given</li>
<li>'repeat' Methods create a pattern which will be repeated</li>

<p>Methods:</p>
<li>None: Method not used</li>
<li>'const': Constant Amplitude for all teeth and all tooth mesh repetitions (<u>attributes:</u> 'constant' (scalar))</li>
<li>'const_repeat': Constant Amplitude for each tooth (list), and unchanging over all tooth mesh repetitions (<u>attributes:</u> 'constant' (list, tuple))</li>
<li>'gaussian': Gaussian Random Amplitude for all teeth and all tooth mesh repetitions (<u>attributes:</u> 'mu' (scalar), 'sigma' (scalar)) </li>
<li>'gaussian_repeat': Gaussian Random Amplitude for each tooth, and unchanging over all tooth mesh repetitions (<u>attributes:</u> 'mu' (scalar), 'sigma' (scalar)) </li>


<p>Example Stationary Sine Signal * const Amplitude</p>


```python
const = 5
amplitude_signal = element_signal * const

plt.plot(time_vector, element_signal, time_vector, amplitude_signal)
plt.xlabel('Time in seconds'), plt.ylabel('Acceleration in g'), plt.legend(['Example Element Signal', 'Amplitude Signal'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_72_0.png)


<h3>Noise Method</h3>
<br>

<li>Adds noise to the signal</li>
<li>Based on the Amplitude Methods Toolbox (repeat methods are not working)</li>
<li>General use: Adding Gaussian Noise</li>

<p>Methods:</p>

<li>None: Method not used</li>
<li>'const': Constant Amplitude for all teeth and all tooth mesh repetitions (<u>attributes:</u> 'constant' (scalar))</li>
<li><strike>'const_repeat': Constant Amplitude for each tooth (list), and unchanging over all tooth mesh repetitions (<u>attributes:</u> 'constant' (list, tuple))</strike></li>
<li>'gaussian': Gaussian Random Amplitude for all teeth and all tooth mesh repetitions (<u>attributes:</u> 'mu' (scalar), 'sigma' (scalar)) </li>
<li><strike>'gaussian_repeat': Gaussian Random Amplitude for each tooth, and unchanging over all tooth mesh repetitions (<u>attributes:</u> 'mu' (scalar), 'sigma' (scalar))</strike></li>

<p>Example Stationary Sine Signal * const Amplitude + noise</p>


```python
noise = np.random.randn(time_vector.size)*0.5
noised_signal = amplitude_signal + noise

plt.plot(time_vector, element_signal, time_vector, amplitude_signal, time_vector, noised_signal)
plt.xlabel('Time in seconds'), plt.ylabel('Acceleration in g'), plt.legend(['Example Element Signal', 'Amplitude Signal', 'Noised Signal'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_76_0.png)


<h3>Torque Method</h3>
<br>

<li>Scales Signal s regarding the torque s<sub>t</sub></li>
<li>1. s<sub>t</sub> = s<sub>t</sub>/s<sub>norm</sub>, norm signal by s<sub>norm</sub></li>
<li>2. s<sub>t</sub> = f(s<sub>t</sub>), while f can be linear, polynomial and exponential</li>
<li>3. s<sub>t</sub> = scale(s<sub>t</sub>), scale into range scale_min-scale_max while scale_min corresponds to value_min and scale_max to value_max</li>
<li>4. s<sub>t</sub> = s<sub>t</sub> + 1, add one to retain original signal and add torque on top</li>
<li>5. s = s * s<sub>t</sub></li>

<p>Methods:</p>

<li>None: Method not used</li>
<li>'linear': f in step 2 is a linear transformation (no transformation)</li>
<li>'polynomial': f in step 2 is polynomial with given exponent argument</li>
<li>'exponential': f in step 2 is exponential</li>

<p>Example Torque Signal 200 Nm +- 5 Nm</p>


```python
torque = np.sin((2 * np.pi * fi /10 * time_vector))*5 + 200 # Nm | array

plt.plot(time_vector, torque)
plt.xlabel('Time in seconds'), plt.ylabel('Torque in Nm'), plt.legend(['Torque'])
plt.show()

```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_80_0.png)


<p>Define Scale Arguments</p>


```python
scale_min = 0                   
scale_max = 0.2
value_min = 1-0.01
value_max = 1.01
norm_divisor = 200
exponent = 2

```

<p>1. s<sub>t</sub> = s<sub>t</sub>/s<sub>norm</sub>, norm signal by s<sub>norm</sub></p>


```python
torque_1 = torque / norm_divisor

plt.plot(time_vector, torque_1)
plt.xlabel('Time in seconds'), plt.ylabel('Torque'), plt.legend(['Normed Torque'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_84_0.png)


<p>2. s<sub>t</sub> = f(s<sub>t</sub>), while f can be linear, polynomial and exponential</p>


```python
torque_2 = np.power(torque_1, exponent) 

plt.plot(time_vector, torque_1, time_vector, torque_2)
plt.xlabel('Time in seconds'), plt.ylabel('Torque'), plt.legend(['Normed Torque', 'f(Torque)'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_86_0.png)


<p>3. s<sub>t</sub> = scale(s<sub>t</sub>), scale into range scale_min-scale_max while scale_min corresponds to value_min and scale_max to value_max</p>


```python
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(scale_min, scale_max))
scaler.fit(np.array([value_min, value_max]).reshape(-1, 1))
torque_3 = scaler.transform(torque_2.reshape(-1, 1)) 

plt.plot(time_vector, torque_1, time_vector, torque_2, time_vector, torque_3)
plt.xlabel('Time in seconds'), plt.ylabel('Torque'), plt.legend(['Normed Torque', 'f(Torque)', 'scale(f(Torque))'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_88_0.png)


<p>4. s<sub>t</sub> = s<sub>t</sub> + 1, add one to retain origninal signal and add torque on top</p>


```python
torque_4 = torque_3 + 1 

plt.plot(time_vector, torque_1, time_vector, torque_2, time_vector, torque_3, time_vector, torque_4)
plt.xlabel('Time in seconds'), plt.ylabel('Torque'), plt.legend(['Normed Torque', 'f(Torque)', 'scale(f(Torque))', '+1'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_90_0.png)


<p>5. s = s * s<sub>t</sub></p>
<p>(Example Stationary Sine Signal * const Amplitude + noise) * Torque</p>


```python
final_signal = noised_signal * torque_4.reshape(-1)

plt.plot(time_vector, element_signal, time_vector, amplitude_signal, time_vector, noised_signal, time_vector, final_signal)
plt.xlabel('Time in seconds'), plt.ylabel('Acceleration in g'), plt.legend(['Example Element Signal', 'Amplitude Signal', 'Noised Signal', 'Final Signal'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_92_0.png)


### Degradation Element Definition

<br>
<h3>Gear Element</h3>
<p>Keyword Attributes: <br>
<ol>
    <li>Failing Teeth: Number of teeth failing at given Gear</li>
    <li>Chances: Various chances influencing the teeth failing order</li>
    <li>PDF_Deg_Init: PDF for pitting_size and load_cycles @ pitting initialization</li>
    <li>PDF_Deg_EOL: PDF for pitting_size and load_cycles @ pitting end of life</li>
    <li>Woehler: Woehler Definition</li>
    <li>GridSearch: Slices for exp.-function Parameters to be determined in Gridsearch</li>
</ol>
</p>



```python
Deg_Gear = {'Failing_Teeth': 2,                                      # Number of Teeth falling at Gear
            'Chances': {'neighbouring': 1,                           # Chance that multiple falling teeth are neighbouring 
                        'opposite': 1,                               # Chance that multiple falling teeth are opposite to each other 
                        'keeporder': 10},                            # Chance that multiple falling teeth are keeping order from init to eol
            'PDF_Deg_Init': {'n': norm(loc=6.875e6, scale=1.053e6),  # P(n_0)
                             'a': norm(loc=0.450, scale=0.305)},     # P(a_0)
            'PDF_Deg_EOL': {'n': norm(loc=10390000, scale=1.053e6),  # P(n_eol)
                            'a': norm(loc=4.0, scale=0.)},           # P(a_eol)
            'Woehler': {'k': 10.5,                                   # Woehler Exponent 
                        'np': 10390000,                              # Woehler Reference n
                        'torqp': 200},                               # Woehler Reference sigma in Nm
            'GridSearch': {'slice_theta1': (0.0001, 0.0902, 0.01),   # Grid for function a = theta1 * exp(theta2 * n) + theta3 defined in slices
                           'slice_theta2': (0.10/1e6, 1.51/1e6, 0.2/1e6), #tbd change step to 0.02/1e6
                           'slice_theta3':(-2.0, 0.5, 0.1)}
           }
```


<h3>Bearing Element</h3>
<p>Keyword Attributes: <br>
<ol>
    <li>TBD</li>
</ol>
</p>


### Degradation Methods

<br>


<p>Module Methods Structure:</p>

<img src="https://github.com/HoChiak/Gearbox/blob/master/__pictures/Degradation_Method.png" width="100%">




<p>Load the Gear Degradation Module for demonstration purposes</p>


```python
from gearbox.degradation.gear import Gear_Degradation
```

<h3>Chances</h3>
<br>

<p>Chances are describing <u>how many times more likely</u> it is that an event occurs compared to the event does not occur</p>
<p>Events:</p>
<li>neighbouring: The next failing tooth is a neighbour of an already fallen one</li>
<li>opposite: The next failing tooth is opposite of an already fallen one</li>
<li>keeporder: The teeth are keeping the same order in initialization and end of life (first tooth with initialization is also the first reaching end of life</li>


<p>Random Pitting Initialization</p>


```python
Deg_Gear['Chances'] = {'neighbouring': 1, 'opposite': 1, 'keeporder': 1}  
deg_model = Gear_Degradation(17, Deg_Gear, 1)
deg_model.get_initial_values()

deg_model.state0.head()
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>n0</th>
      <th>tooth</th>
      <th>neol</th>
      <th>aeol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.680316</td>
      <td>7.053553e+06</td>
      <td>5</td>
      <td>7.966480e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.292661</td>
      <td>6.782824e+06</td>
      <td>6</td>
      <td>8.220672e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>-0.128040</td>
      <td>6.748063e+06</td>
      <td>11</td>
      <td>9.231814e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.467624</td>
      <td>7.369779e+06</td>
      <td>9</td>
      <td>9.260164e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.311195</td>
      <td>6.280401e+06</td>
      <td>7</td>
      <td>9.588449e+06</td>
      <td>4.0</td>
    </tr>
  </tbody>
</table>
</div>



<p>Visualization of Pitting Size at Initialization</p>


```python
gf.plot_gear_polar(deg_model.state0, kind='pitting', key='a0')

```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_103_0.png)


<p>Pitting Order Visualization</p>


```python
gf.plot_gear_polar(deg_model.state0, kind='order')

```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_105_0.png)


<p>Neighbouring favoured Pitting Initialization</p>


```python
Deg_Gear['Chances'] = {'neighbouring': 100, 'opposite': 1, 'keeporder': 1}  
deg_model = Gear_Degradation(17, Deg_Gear, 1)
deg_model.get_initial_values()
gf.plot_gear_polar(deg_model.state0, kind='order')
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_107_0.png)


<p>Opposite favoured Pitting Initialization</p>


```python
Deg_Gear['Chances'] = {'neighbouring': 1, 'opposite': 100, 'keeporder': 1}  
deg_model = Gear_Degradation(17, Deg_Gear, 1)
deg_model.get_initial_values()
gf.plot_gear_polar(deg_model.state0, kind='order')
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_109_0.png)


<p>Neighbouring and Opposite favoured Pitting Initialization</p>


```python
Deg_Gear['Chances'] = {'neighbouring': 100, 'opposite': 100, 'keeporder': 1}  
deg_model = Gear_Degradation(17, Deg_Gear, 1)
deg_model.get_initial_values()
gf.plot_gear_polar(deg_model.state0, kind='order')
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_111_0.png)


<p>Keeporder favoured Initialization</p>


```python
Deg_Gear['Chances'] = {'neighbouring': 1, 'opposite': 1, 'keeporder': 100}  
deg_model = Gear_Degradation(17, Deg_Gear, 1)
deg_model.get_initial_values()

deg_model.state0.head()
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>n0</th>
      <th>tooth</th>
      <th>neol</th>
      <th>aeol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>-0.049329</td>
      <td>5.990150e+06</td>
      <td>13</td>
      <td>7.966480e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.073635</td>
      <td>6.016130e+06</td>
      <td>15</td>
      <td>8.220672e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>-0.001042</td>
      <td>6.174741e+06</td>
      <td>12</td>
      <td>9.231814e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.683793</td>
      <td>6.316424e+06</td>
      <td>17</td>
      <td>9.260164e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.446157</td>
      <td>6.345976e+06</td>
      <td>7</td>
      <td>9.588449e+06</td>
      <td>4.0</td>
    </tr>
  </tbody>
</table>
</div>



<h3>PDF Degradation</h3>
<br>

<p>Probability Density Function for Degradation <u>Initialization</u></p>
<li>n: Initialization Load Cycle PDF - P(n<sub>0</sub>)</li>
<li>a: Initialization Pitting Size PDF - P(a<sub>0</sub>)</li>

<p>Probability Density Function for Degradation <u>End of Life</u></p>
<li>n: EOL Load Cycle PDF - P(n<sub>eol</sub>)</li>
<li>a: EOL Pitting Size PDF - P(a<sub>eol</sub>)</li>

<p> PDF can be defined as any continuous distribution function available on <a href="https://docs.scipy.org/doc/scipy/reference/stats.html">'Scipy Stats'</a></p>
<p><b>PDFs are valid for a reference torque, defined by woehler</b></p>


<p>P(n<sub>0</sub>) and P(n<sub>eol</sub>)</p>


```python
P_n0, P_neol= norm(loc=6.875e6, scale=1.053e6), norm(loc=10390000, scale=1.053e6)
n0, neol = np.linspace(P_n0.ppf(0.01), P_n0.ppf(0.99), 100), np.linspace(P_neol.ppf(0.01), P_neol.ppf(0.99), 100)

plt.plot(n0, P_n0.pdf(n0), neol, P_neol.pdf(neol))
plt.xlabel('Load Cycles N'), plt.ylabel('p(N)'), plt.legend(['PDF Initialization Load Cycle', 'PDF EOL Load Cycle'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_116_0.png)


<p>P(a<sub>0</sub>) and P(a<sub>eol</sub>)</p>


```python
P_a0, P_aeol= norm(loc=0.450, scale=0.305), norm(loc=4.0, scale=0.1)
a0, aeol = np.linspace(P_a0.ppf(0.01), P_a0.ppf(0.99), 100), np.linspace(P_aeol.ppf(0.01), P_aeol.ppf(0.99), 100)

plt.plot(a0, P_a0.pdf(a0), aeol, P_aeol.pdf(aeol))
plt.xlabel('Pitting Size a'), plt.ylabel('p(a)'), plt.legend(['PDF Initialization Pitting Size', 'PDF EOL Pitting Size'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_118_0.png)


<h3>Woehler Curve</h3>
<br>

<p>Definition of Woehler Curve for EOL</p>
<li>k: Woehler exponent (measure for gradien)</li>
<li>np: Reference Load Cycle on Woehler Curve - pair (np, torquep)</li>
<li>torquep: Reference Torque on Woehler Curve - pair (np, torquep)</li>


<p>The definition of the reference points (np, torquep) also determines the probability of failure Px for which the Woehler line applies.</p>




<p>Woehler Curve Plot</p>


```python
k, n_p, torq_p = 10.5, 10390000., 200.
torq = np.linspace(torq_p*0.5, torq_p*1.5, 10)
N = n_p * np.power((torq / torq_p), -1*k)

plt.plot(N, torq), plt.scatter(n_p, torq_p, c='r')
plt.xscale('log'), plt.yscale('log'), plt.xlabel('Load Cyvles log(N)'), plt.ylabel('Torque log(T)'), plt.legend(['Woehler Curve', 'Reference'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_121_0.png)


<h3>GridSearch</h3>
<br>

<p>Definition of <u>Slices</u> for Exponential Function Parameters &theta;</p>
<li>Function: a = &theta;<sub>1</sub> * exp(&theta;<sub>2</sub> * n) + &theta;<sub>3</sub></li>
<li>Two points Given: (a<sub>0</sub>, n<sub>0</sub>) and (a<sub>eol</sub>, n<sub>eol</sub>)</li>
<li>GridSearch for best fit</li>
<li>Only failing teeth</li>

<p>The definition of the reference points (np, torquep) also determines the probability of failure Px for which the Woehler line applies.</p>




```python
Deg_Gear['GridSearch'] = {'slice_theta1': (0.0001, 0.0902, 0.01),
                          'slice_theta2': (0.10/1e6, 1.51/1e6, 0.2/1e6),
                          'slice_theta3':(-2.0, 0.5, 0.1)}

```

### Degradation Theory
</div>
<br>

<li>How Degradation Simulation Works</li>
<li>Running Example for one tooth</li>


<h3>1. Define Degradation Dictionary</h3>



```python
Deg_Gear = {'Failing_Teeth': 2,                                      # Number of Teeth falling at Gear
            'Chances': {'neighbouring': 1,                           # Chance that multiple falling teeth are neighbouring 
                        'opposite': 10,                               # Chance that multiple falling teeth are opposite to each other 
                        'keeporder': 1},                            # Chance that multiple falling teeth are keeping order from init to eol
            'PDF_Deg_Init': {'n': norm(loc=6.875e6, scale=1.053e6),  # P(n_0)
                             'a': norm(loc=0.450, scale=0.305)},     # P(a_0)
            'PDF_Deg_EOL': {'n': norm(loc=10390000, scale=1.053e6),  # P(n_eol)
                            'a': norm(loc=4.0, scale=0.)},           # P(a_eol)
            'Woehler': {'k': 10.5,                                   # Woehler Exponent 
                        'np': 10390000,                              # Woehler Reference n
                        'torqp': 200},                               # Woehler Reference sigma in Nm
            'GridSearch': {'slice_theta1': (0.00, 0.09, 0.01),   # Grid for function a = theta1 * exp(theta2 * n) + theta3 defined in slices
                           'slice_theta2': (0.30/1e6, 0.61/1e6, 0.005/1e6), #tbd change step to 0.02/1e6
                           'slice_theta3':(-.1, 0.4, 0.01)}
           }
no_teeth = 10
seed = 4
```

<h3>2. Draw (tooth, a<sub>0</sub>, n<sub>0</sub>, a<sub>eol</sub>, n<sub>eol</sub>) Pairs for all teeth considering chances</h3>


```python
deg_model = Gear_Degradation(no_teeth, Deg_Gear, seed)
deg_model.get_initial_values()

deg_model.state0.head()
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>n0</th>
      <th>tooth</th>
      <th>neol</th>
      <th>aeol</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.688419</td>
      <td>6.529432e+06</td>
      <td>5</td>
      <td>8.721440e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.339692</td>
      <td>6.159135e+06</td>
      <td>6</td>
      <td>9.181707e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.534619</td>
      <td>6.894539e+06</td>
      <td>8</td>
      <td>9.341308e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.112874</td>
      <td>7.342072e+06</td>
      <td>7</td>
      <td>9.707965e+06</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.157939</td>
      <td>6.867023e+06</td>
      <td>3</td>
      <td>9.949528e+06</td>
      <td>4.0</td>
    </tr>
  </tbody>
</table>
</div>



<h3>3. GridSearch for all failing teeth to get individual degradation function</h3>
<br>
<li>If Failing_Teeth is n --> First n teeth are considered</li>
<li>!! Value Pairs will be adjusted to fit on Degradation Function !!</li>


```python
deg_model = Gear_Degradation(no_teeth, Deg_Gear, seed)
deg_model.init_gear_degradation()
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>1.0</th>
      <th>2.0</th>
      <th>3.0</th>
      <th>4.0</th>
      <th>5.0</th>
      <th>6.0</th>
      <th>7.0</th>
      <th>8.0</th>
      <th>9.0</th>
      <th>10.0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>$a_{0}$</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>$d_{0}$</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>-1.766703</td>
      <td>NaN</td>
      <td>-2.473716</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



<p>Results:</p>


```python
deg_model.state0
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>n0</th>
      <th>tooth</th>
      <th>neol</th>
      <th>aeol</th>
      <th>theta1</th>
      <th>theta2</th>
      <th>theta3</th>
      <th>n0_old</th>
      <th>neol_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.679899</td>
      <td>5.565490e+06</td>
      <td>3</td>
      <td>8.715702e+06</td>
      <td>4.0</td>
      <td>0.02</td>
      <td>6.050000e-07</td>
      <td>0.10</td>
      <td>5.546529e+06</td>
      <td>8.721440e+06</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.861807</td>
      <td>6.564932e+06</td>
      <td>5</td>
      <td>9.218807e+06</td>
      <td>4.0</td>
      <td>0.02</td>
      <td>5.750000e-07</td>
      <td>-0.01</td>
      <td>7.009050e+06</td>
      <td>9.181707e+06</td>
    </tr>
  </tbody>
</table>
</div>



<p>Gear Visualization:</p>


```python
gf.plot_gear_polar(deg_model.state0, kind='pitting_growth', no_teeth=no_teeth, key1='a0', key2='aeol')
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_134_0.png)


<p>Degradation Function Visualization:</p>


```python
deg_model.plot_state0()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_136_0.png)


<h3>4. Transform Degradation to Damage D</h3>
<br>
<li>Under constant torque load degradation starts at n<sub>0</sub> and ends at n<sub>eol</sub> </li>
<li>D(n<sub>0</sub>) = 0</li>
<li>D(n<sub>eol</sub>) = 1</li>
<li>Assumption: Linear Damage Accumulation</li>

<p>Draw D(n<sub>0</sub>) = 0 and D(n<sub>eol</sub>) = 1</p>


```python
fig = plt.figure()
legend = []
for i, row in deg_model.state0.iterrows():
    plt.scatter([row['n0'], row['neol']], [0, 1])
    legend.append('Tooth %i' % (row['tooth']))
plt.xlabel('Load Cyvles N'), plt.ylabel('Damage (D)'), plt.legend(legend)
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_139_0.png)


<p>Get Linear Damage over Load Cycle Dependency</p>


```python
N = np.linspace(0, 1.5e7, 10)
for i, row in deg_model.state0.iterrows():
    m = (1)/(row['neol'] - row['n0'])
    b = 0 - m * row['n0']
    plt.scatter([row['n0'], row['neol']], [0, 1])
    plt.plot(N, (m * N + b))
plt.xlabel('Load Cyvles N'), plt.ylabel('Damage (D)'), plt.legend(legend)
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_141_0.png)


<h3>5. Pitting Size and Damage Dependency</h3>
<br>
<li>Both Pitting Size a and Damage D are a function of Load Cycles N, so it follows:</li>
<li>D(a<sub>0</sub>) = 0</li>
<li>D(a<sub>eol</sub>) = 1</li>
<li>In General: a(D(N)) = a<sub>d</sub></li>

<h3>6. Defining State0</h3>
<br>
<li>Assumption: Linear Damage Accumulation</li>
<li>All values are valid for the reference load (torque) given in woehler curve definition</li>
<li>At State0 (Initialization) the following is known:</li>
<ul>
    <li>Degradation Function: a(N) = a<sub>N</sub></li>
    <li>Damage Function: D(N) = d<sub>N</sub></li>
    <li>Damage Pitting Dependency: a(D(N)) = a<sub>d</sub></li>
</ul>

<p>Values @ State0</p>


```python
print('Load Cycle:                 %i' % (deg_model.nolc[0]))
print('Failing teeth:              %s' % ('|'.join(['   %i   ' % (tooth) for tooth in deg_model.state0['tooth']])))
print('Corresponding Damage:       %s' % ('|'.join(['%.4f' % (damage) for damage in deg_model.damage[-1]])))
print('Corresponding Pitting Size: %s' % ('|'.join(['  %.4f  ' % (ps) if np.isnan(ps) else '%.4f' % (ps) for ps in deg_model.pitting_size[-1]])))
```

    Load Cycle:                 0
    Failing teeth:                 3   |   5   
    Corresponding Damage:       -1.7667|-2.4737
    Corresponding Pitting Size:   nan  |  nan  
    

<h3>7. Calculating &Delta;D </h3>
<br>
<li>Given:</li>
<ul>
    <li>List of loads applied on tooth i</li>
    <li>Load Cycles n<sub>p</sub> and n<sub>p-1</sub></li>
    <li>Previous Damage D<sub>p-1, i</sub> </li>
</ul>
<li>Searched:</li>
<ul>
    <li>&Delta;D = D(n<sub>p</sub> - n<sub>p-1</sub>)</li>
    <li>Current Damage D<sub>p, i</sub> </li>
</ul>
<p><b>&Delta;D will be computed for all full Load Cycles (e.g. considering gear_ratio for output gear -> 10,5 Load Cycles will be considered as 10 Load Cycles)</b></p>

<p>Definition of Given</p>


```python
loads = [195, 200, 205]
curr_cycle = 73
```

<p>From State0</p>


```python
idx = 0 # Tooth ID
prev_cycle = deg_model.nolc[-1]
tooth_i = deg_model.state0['tooth'].to_list()[idx]
prev_damage = deg_model.damage[-1][idx]
prev_pitting = deg_model.pitting_size[-1][idx]
n0, neol = deg_model.state0['n0'][idx], deg_model.state0['neol'][idx]
T1, k = Deg_Gear['Woehler']['torqp'], Deg_Gear['Woehler']['k']
```

<p>Define Woehler for Damage tooth_i</p>


```python
N1 = neol - n0
torq = np.linspace(T1*0.5, T1*1.5, 10)
N = N1 * np.power((torq / T1), -1*k)

plt.plot(N, torq), plt.scatter(N1, T1, c='r')
plt.xscale('log'), plt.yscale('log'), plt.xlabel('$Load Cyvles log(N_{EOL}-N_0)$'), plt.ylabel('Torque log(T)'), plt.legend(['Woehler Curve', '$N_{EOL} - N_{0}$'])
plt.show()
```


![png](https://github.com/HoChiak/Gearbox/blob/master/__pictures/output_152_0.png)


<p>Get Damage Equivalent D* for all loads</p>


```python
damage_equivalents = []
for load in loads:
    N2 = N1 * np.power((load / T1), -1*k)
    damage = 1/N2
    damage_equivalents.append(damage)
print('Loads:  %s' % ('|'.join(['  %.3f  ' % (load) for load in loads])))
print('D\'s:    %s' % ('|'.join([' %.3e ' % (de) for de in damage_equivalents])))
```

    Loads:    195.000  |  200.000  |  205.000  
    D's:     2.433e-07 | 3.174e-07 | 4.114e-07 
    

<p>Repeat Damage Equivalent D* for &Delta;N load cycle</p>


```python
delta_n = int(np.floor(curr_cycle - prev_cycle))
repeated_damage_equivalent = gf.repeat2no_values(np.array(damage_equivalents), delta_n)

print('\u0394N = %i' % (delta_n))
print('D* Shape: %s' % (str(repeated_damage_equivalent.shape)))
```

    ΔN = 73
    D* Shape: (73,)
    

<p>Calculate &Delta;D = &Sum;D*</p>


```python
delta_d = np.sum(repeated_damage_equivalent)
print('\u0394D = \u2211 D* = %.3e for \u0394N = %i load cycles' % (delta_d, delta_n))
```

    ΔD = ∑ D* = 2.358e-05 for ΔN = 73 load cycles
    

<h3>8. Calculating current D </h3>
<br>
<p>D<sub>p</sub> = D<sub>p-1</sub> + &Delta;D</p>


```python
curr_damage = prev_damage + delta_d
print('D(p) = D(p-1) + \u0394D = %.3e' % (curr_damage))
```

    D(p) = D(p-1) + ΔD = -1.767e+00
    

<h3>9. Calculating a<sub>p</sub> </h3>
<br>
<p>Using: Damage Pitting Dependency: a(D(N))</p>
<ul>
    <li>a(D(N)) is given for each tooth</li>
</ul>


### Degradation-Vibration Dependency Element Definition
</div>
<br>
<p>Module Methods Connection Vibration and Degradtion:</p>
<li>Getting Loads from Torque Signal for Gear Degradation</li>
<li>Translating Pitting Size into Vibration</li>


<h3>Gear Element</h3>
<p>Keyword Attributes: <br>
<ol>
    <li>scale_method: <a href="AmplitudeMethod">Scale Method to scale Amplitude based on pitting size(see Torque Influence Method as reference)</a><br></li>
    <li>scale_attributes: <a href="AmplitudeMethod">Attributes regarding Scale Method to (see Torque Influence Attributes as reference)</a><br></li>
    <li>torq_influence:  <a href="TorqueMethod">If True Torque Influence will be taken into account in the same way as in vibration definition</a><br></li>
    <li>noise_method:  <a href="AmplitudeMethod">Method to create Signal Noise (repeat methods are not working)</a><br></li>
    <li>noise_attributes: <a href="AmplitudeMethod">Attributes regarding the Method to create Signal Noise</a><br></li>
    <li>t2t_factor: <a href="">If 1 loads are calculated without any overlap between two tooh and all loads are considered. If t2t_factor > 1 there is a overlap of loads considered for each tooth </a><br></li>
</ol>
</p>


```python
GearDegVibDict = {'scale_method': 'linear',                            # Scale Method (See Torque Influence Method)
                   'scale_attributes': {'scale_min': 0,                 # Attributes regarding Scale Method for gear signal (see Torque Influence Method)
                                       'scale_max': 1,
                                       'value_min': 0,
                                       'value_max': 4,
                                       'exponent': 2},
                   'torq_influence': True,                              # If True Torque Influence will be taken into account in the same way as in vibration definition
                   'noise_method': 'gaussian',                          # Noise Method
                   'noise_attributes': {'mu': 0, 'sigma': 0.005},       # Attributes regarding Noise Method for
                   }
```

<p>Construction of Degradation Signal: <br>
<ol>
    <li>Degradation Signal is constructed as a single peak when tooth is meshing tooth_mesh_i = [0, 0, 0, 1, 0, 0]</li>
    <li>The array tooth_mesh_i = [0, 0, 0, 1, 0, 0] contains as many values as tooth i meshes in this period</li>
    <li>During the sample interval there are prably more than one periods like tooth_mesh_i = [0, 0, 0, 1, 0, 0]</li>
    <li>For all other teeth during this period: tooth_mesh_i = [0, 0, 0, 0, 0, 0] (Zero Array)</li>
    <li>The position of the peak inside the array is given by the following code:</li>
</ol>
</p>


```python
period = 1
tooth = 12
start_mesh_12_1 = 162
end_mesh_12_1 = 168
diff = end_mesh_12_1 - start_mesh_12_1
# Get weights by normal distribution
# weights: Get absolute sorted normal random numbers --> eg. [0.1, 0.3, 0.8, 0.5, 0.2]
print('Diff = %i' % (diff))

print('Normal Random Numbers: \t %s' % (str(np.random.randn(diff))))
print('--> Sorted: \t \t %s' % (str(np.sort(np.random.randn(diff)))))
print('--> Absolut: \t \t %s' % (str(np.abs(np.sort(np.random.randn(diff))))))
print('--> Inverse: \t \t %s' % (str(1/np.abs(np.sort(np.random.randn(diff))))))
randn_weights = 1/np.abs(np.sort(np.random.randn(diff)))
# weights: Norm to one
randn_weights = randn_weights / sum(randn_weights)
print('--> Sum(array)=1: \t %s ==> Probabilitys\n' % (str(randn_weights)))
# Create zero array
tooth_signal_i = np.zeros(diff)
print('Create Zero Vector: \t \t \t %s' % (str(tooth_signal_i)))
# Choose one value as one, regarding given weights
tooth_signal_i[np.random.choice(np.arange(0, diff), p=randn_weights)] = 1
print('Given Probabiliy assign value to one:\t %s' % (str(tooth_signal_i)))

```

    Diff = 6
    Normal Random Numbers: 	 [ 1.37459323 -0.45104291  0.61353263 -0.21015656  0.40805817  1.73239851]
    --> Sorted: 	 	 [-1.23313682 -0.34944796  0.51655963  0.67380149  0.71827439  1.02645497]
    --> Absolut: 	 	 [1.96601472 1.20740046 1.16829028 0.68114843 0.40865031 1.04090637]
    --> Inverse: 	 	 [0.88879836 1.47732103 5.52995453 3.30139743 1.17593537 0.88623151]
    --> Sum(array)=1: 	 [0.02616688 0.03244002 0.03388619 0.06010881 0.09929126 0.74810686] ==> Probabilitys
    
    Create Zero Vector: 	 	 	 [0. 0. 0. 0. 0. 0.]
    Given Probabiliy assign value to one:	 [0. 0. 0. 0. 0. 1.]
    
