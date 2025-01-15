**Python script to automate semiconductor parameter analysis with Keithley 2450 SMUs**

⚠️ Before starting, always make sure all SMUs are using TSP command sets, and the TSPLink has been initialited. See below for how to set up TSP command sets and TSPLink.

⚠️ Important! Make sure you always restart all SMUs, and make sure TSP Link is not initiated if you want to use other scripts in this repository.

Prerequisites:
- Two Kiethley 2450 series source-measure-units (SMUs). 
- A RJ45 LAN crossover cable.
- A USB-B to USB-A cable.
- A python-ready computer.

How to setup Keithely SMUs and the computer:

- Connect two Keithley SMUs to the computer with USB cable.
- Connet two Keithley SMUs to each other by plugging the RJ45 cable to the TSP-Link portal on the back of Keithley 2450 SMU.
- Make sure all two Keithleys are using TSP command set, not SCPI. To change, press MENU, go to Settings, check Command set tab.
- Install NI-VISA, NI-MAX to the computer.
- Install Python and the dependencies (NumPy, Pandas, Matplotlib, PyVISA).
- Record the USB addresses of two Keithley SMUs, as `gate_address` and `drain_address`. They should look similar to `USB0::0x0XXX::0x2450::XXXXXXXX::INSTR`.
- Update the USB addresses in `script.py`.
- Initialize TSP-Link. For each Keithley, press the MENU button, click Communication, go to the TSP-Link tab, select node number as follows, and click Initialize. This needs to be done before running the script. 
  - For the SMU to be used as the gate, set the node number as 1.
  - For the SMU to be used as the drain, set the node number as 2.

How to use this script:
- Make electrical connections:
  
  - Prepare the device under test (DUT). Ground the source.
  - Connect the drain to the front terminal of SMU node 2 with a BNC cable.
  - Connect the gate to the front terminal of SMU nide 1 with a BNC cable.
  - It is strongly suggested to use common ground for all connections.
    
- As a quick start, see `scriptGenerator.ipynb` as an example.
- For transfer measurement, call `transfer()` function. The arguments are:
  - `gate_start`: a float number which is gate sweeping start value.
  - `gate_end`: a float number which is gate sweep eend value.
  - `drain_voltage`: a float number which is constant drain-source bias.
  - `sweep_steps`: an int number which is the number of sweep steps for a single scan. Note you will get `2*sweep_steps` readings if you choose to test hysteresis.
  - `test_hysteresis`: Boolean value representing whether to test hysteresis.
  - `test_leakage`: Boolean value representing whether to measure gate leakage current during sweping. If `True`, the whole sweep speed will be 3x slower.
    
- For output measurement, call `output()` function. The arguments are:
  - `drain_start`: a float number which is drain sweeping start value.
  - `drain_end`: a float number which is drain sweep eend value.
  - `gate_voltage`: a float number which is constant gate bias.
  - `sweep_steps`: an int number which is the number of sweep steps for a single scan. Note you will get `2*sweep_steps` readings if you choose to test hysteresis.
  - `test_hysteresis`: Boolean value representing whether to test hysteresis.
- Both the `transfer()` and `output()` fucntion call return two arrays, `gate_readings` and `drain_readings`. Each of them are numpy array of shape `(2, # of readings)`. For each array, the first column is the output voltage, and the second column is the measuremnt result.
- Simply repeateadly call the `transfer()` and `output()` fucntion if multiple scans are needed by using a `for` loop.
