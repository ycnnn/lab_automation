**Python script to automate semiconductor parameter analysis with Keithley 2450 SMUs**

Prerequisites:
- Two Kiethley 2450 series source-measure-units (SMUs). 
- A RJ45 LAN crossover cable.
- Two USB-B to USB-A cables.

How to setup Keithely SMUs and the computer:

- Connect each of the Keithley SMU to the computer with USB cable.
- Connet two Keithley SMUs to each other by plugging the RJ45 cable to the TSP-Link portal on the back of Keithley 2450 SMU.
- Make sure all two Keithleys are using TSP command set, not SCPI. To change, press MENU, go to Settings, check Command set tab.
- Install NI-VISA to the computer.
- Install Python and the dependencies (NumPy, Pandas, Matplotlib, PyVISA).
- Initialize TSP-Link. For each Keithley,press MENU, click Communication, go to the TSP-Link tab, select node number as follows, and click Initialize.
  - For the SMU used as the gate, set the node number as 1.
  - For the SMU used as the drain, set the node number as 2.

How to use this script:
- As a quick start, see `scriptGenerator.ipynb` as an example.
- For transfer measurement, call `transfer()` function. The arguments are:
  - `gate_start`: gate sweeping start value.
  - `gate_end`: gate sweep eend value.
  - `drain_voltage`: constant drain-source bias.
  - `sweep_steps`: the number of sweep steps for a single scan. Note you will get `2*sweep_steps` readings if you choose to test hysteresis.
  - `test_hysteresis`: whether to test hysteresis.
  - `test_leakage`: whether to measure gate leakage current during sweping. If `True`, the whole sweep speed will be 3x slower.
    
- For output measurement, call `output()` function. The arguments are:
  - `drain_start`: drain sweeping start value.
  - `drain_end`: drain sweep eend value.
  - `gate_voltage`: constant gate bias.
  - `sweep_steps`: the number of sweep steps for a single scan. Note you will get `2*sweep_steps` readings if you choose to test hysteresis.
  - `test_hysteresis`: whether to test hysteresis.
- Both the `transfer()` and `output()` fucntion call return two arrays, `gate_readings` and `drain_readings`. Each of them are numpy array of shape `(2, # of readings)`. For each array, the first column is the output voltage, and the second column is the measuremnt result.
- Simple repeateadly call the `transfer()` and `output()` fucntion if multiple scans are needed by using a `for` loop.
