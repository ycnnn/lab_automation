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
- (For transfer measurement only:) Initialize TSP-Link. For each Keithley,press MENU, click Communication, go to the TSP-Link tab, select node number as follows, and click Initialize.
  - For the SMU used as the gate, set the node number as 1.
  - For the SMU used as the drain, set the node number as 2.
