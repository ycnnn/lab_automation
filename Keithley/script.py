import numpy as np
import pyvisa as pv

def set_smu_ready(address):
    rm = pv.ResourceManager()
    smu = rm.open_resource(address)
    smu.timeout = 500
    smu.write('reset()')
    return smu

def write_script(gate,
                 gate_sweep_volt_list,
                 drain_sweep_volt_list,
                 gate_sweep_mode_list,
                 drain_sweep_mode_list,
                 delay = 0.01,
                 script_name='sweepScript'):
    ########################################
    # Input check
    if gate_sweep_volt_list.shape != gate_sweep_mode_list.shape:
        print('Error: input volage and/or sweep mode list shape incorrect. ')
        return
    if drain_sweep_volt_list.shape != drain_sweep_mode_list.shape:
        print('Error: input volage and/or sweep mode list shape incorrect. ')
        return
    if gate_sweep_mode_list.shape != drain_sweep_volt_list.shape:
        print('Error: input volage and/or sweep mode list shape incorrect. ')
        return
    if len(gate_sweep_volt_list.shape) != 1:
        print('Error: input volage and/or sweep mode list shape incorrect. ')
        return
    if np.max(np.abs(gate_sweep_volt_list)) >= 200 or np.max(np.abs(drain_sweep_volt_list)) >= 200:
        print('Error: input volage too high.')
        return
    

    gate.write('loadscript ' +  script_name)


    gate.write("tsplink.initialize()")
    gate.write("state = tsplink.state")
    gate.write("if state ~= \"online\" then")
    gate.write(" print(\"Error: Check that all SMUs have a different node number; and\")")
    gate.write(" print(\"Check that all SMUs are connected correctly\")")
    gate.write(" return")
    gate.write("end")
    gate.write("reset()")
    ######################## Model 2450 #1 (gate) setup ################
    step_points = len(gate_sweep_volt_list)
    gate.write(f"steppoints = {step_points}")
    #  Set up the source function.
    gate.write("smu.source.configlist.create(\"gateSourceVals\")")
    gate.write("smu.measure.configlist.create(\"gateMeasureVals\")")
    gate.write("smu.source.func = smu.FUNC_DC_VOLTAGE")
    gate.write("smu.source.autorange = smu.ON")
    #  Set up the measure function.

    #  Change me later
    #  smu.measure.func = smu.FUNC_DC_CURRENT
    gate.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
    gate.write("smu.measure.autorange = smu.ON")
    gate.write("smu.measure.terminals = smu.TERMINALS_FRONT")
    #  Set up TSP-Link triggering.
    gate.write("tsplink.line[1].reset()")
    gate.write("tsplink.line[1].mode = tsplink.MODE_SYNCHRONOUS_MASTER")
    gate.write("tsplink.line[2].mode = tsplink.MODE_SYNCHRONOUS_ACCEPTOR")
    gate.write("trigger.tsplinkout[1].stimulus = trigger.EVENT_NOTIFY1")
    gate.write("trigger.tsplinkin[2].clear()")
    gate.write("trigger.tsplinkin[2].edge = trigger.EDGE_RISING")

    # gate.write("for i = 1, 100 do")
    for index in np.arange(step_points):
        gate.write(f"smu.source.level = {gate_sweep_volt_list[index]}")
        gate.write("smu.source.configlist.store(\"gateSourceVals\")")
        if gate_sweep_mode_list[index] == 1:
            gate.write("smu.measure.func = smu.FUNC_DC_CURRENT")
        else:
            gate.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
        gate.write("smu.measure.configlist.store(\"gateMeasureVals\")")
    # gate.write("end")
    #  Set up the trigger model.
    gate.write("trigger.model.setblock(1, trigger.BLOCK_CONFIG_RECALL, \"gateSourceVals\", 1, \"gateMeasureVals\", 1)")
    gate.write("trigger.model.setblock(2, trigger.BLOCK_SOURCE_OUTPUT, smu.ON)")
    gate.write("trigger.model.setblock(3, trigger.BLOCK_MEASURE_DIGITIZE)")
    gate.write("trigger.model.setblock(4, trigger.BLOCK_NOTIFY, trigger.EVENT_NOTIFY1)")
    gate.write("trigger.model.setblock(5, trigger.BLOCK_WAIT, trigger.EVENT_TSPLINK2)")
    gate.write("trigger.model.setblock(6, trigger.BLOCK_CONFIG_NEXT, \"gateSourceVals\", \"gateMeasureVals\")")
    gate.write("trigger.model.setblock(7, trigger.BLOCK_BRANCH_COUNTER, steppoints, 3)")
    gate.write("trigger.model.setblock(8, trigger.BLOCK_SOURCE_OUTPUT, smu.OFF)")

    #  ########################## Model 2450 #2 (drain) setup ################
    gate.write("sweeppoints = steppoints")
    #  Set up the source function.
    gate.write("node[2].smu.source.configlist.create(\"drainSourceVals\")")
    gate.write("node[2].smu.measure.configlist.create(\"drainMeasureVals\")")
    gate.write("node[2].smu.source.func = node[2].smu.FUNC_DC_VOLTAGE")
    gate.write("node[2].smu.source.autorange = node[2].smu.ON")
    gate.write("node[2].smu.source.ilimit.level = 100e-3")
    #  Set up the measure function.


    #  Change me later

    gate.write("node[2].smu.measure.func = node[2].smu.FUNC_DC_VOLTAGE")
    gate.write("node[2].smu.measure.autorange = node[2].smu.ON")
    gate.write("node[2].smu.measure.terminals = node[2].smu.TERMINALS_FRONT")

    #  Set up TSP-Link triggering.
    gate.write("node[2].tsplink.line[2].mode = node[2].tsplink.MODE_SYNCHRONOUS_MASTER")
    gate.write("node[2].tsplink.line[1].mode = node[2].tsplink.MODE_SYNCHRONOUS_ACCEPTOR")
    gate.write("node[2].trigger.tsplinkout[2].stimulus = node[2].trigger.EVENT_NOTIFY2")
    gate.write("node[2].trigger.tsplinkin[1].clear()")
    gate.write("node[2].trigger.tsplinkin[1].edge = node[2].trigger.EDGE_RISING")
    #  Populate the drainSourceVals source config list, with source levels

    for index in np.arange(len(drain_sweep_volt_list)):
        gate.write(f"node[2].smu.source.level = {drain_sweep_volt_list[index]}")
        gate.write("node[2].smu.source.configlist.store(\"drainSourceVals\")")
        if drain_sweep_mode_list[index] == 1:
            gate.write("node[2].smu.measure.func = node[2].smu.FUNC_DC_CURRENT")
            gate.write("node[2].smu.source.autorange = node[2].smu.ON")
        else:
            gate.write("node[2].smu.measure.func = node[2].smu.FUNC_DC_VOLTAGE")
            gate.write("node[2].smu.source.autorange = node[2].smu.ON")
        gate.write("node[2].smu.measure.configlist.store(\"drainMeasureVals\")")
    
    #  Set up the trigger model.
    gate.write("node[2].trigger.model.setblock(1, node[2].trigger.BLOCK_CONFIG_RECALL, \"drainSourceVals\", 1, \"drainMeasureVals\", 1)")
    gate.write("node[2].trigger.model.setblock(2, node[2].trigger.BLOCK_SOURCE_OUTPUT, node[2].smu.ON)")
    gate.write("node[2].trigger.model.setblock(3, node[2].trigger.BLOCK_WAIT, node[2].trigger.EVENT_TSPLINK1)")
    gate.write(f"node[2].trigger.model.setblock(4, node[2].trigger.BLOCK_DELAY_CONSTANT, {delay})")
    gate.write("node[2].trigger.model.setblock(5, node[2].trigger.BLOCK_MEASURE_DIGITIZE)")
    #  new ltrigger flow
    gate.write("node[2].trigger.model.setblock(6, node[2].trigger.BLOCK_NOTIFY, node[2].trigger.EVENT_NOTIFY2)")
    gate.write("node[2].trigger.model.setblock(7, node[2].trigger.BLOCK_CONFIG_NEXT, \"drainSourceVals\", \"drainMeasureVals\")")
    gate.write("node[2].trigger.model.setblock(8, node[2].trigger.BLOCK_BRANCH_COUNTER, sweeppoints, 3)")
    gate.write("node[2].trigger.model.setblock(9, node[2].trigger.BLOCK_SOURCE_OUTPUT, node[2].smu.OFF)")


    #  Start the trigger model for both SMUs and wait until it is complete
    gate.write("node[2].trigger.model.initiate()")
    gate.write("trigger.model.initiate()")
    gate.write("waitcomplete()")
    gate.write('endscript')
    gate.write(script_name + '.save()')

def run_script(gate, script_name):
    gate.write(script_name + '.run()')
    gate.write('script.delete(\"' + script_name +'\")')

def transfer_paramater_generator(
                                 gate_start,
                                 gate_end,
                                 drain_voltage,
                                 sweep_steps,
                                 test_hysteresis,
                                 test_leakage,
                                 ramp_steps,
                                 delay):
    if test_hysteresis:
        gate_sweep_volt_list = np.concatenate((
            np.linspace(0, gate_start, num=ramp_steps),
            np.linspace(gate_start, gate_end, num=sweep_steps),
            np.linspace(gate_end, gate_start, num=sweep_steps),
            np.linspace(gate_start, 0, num=ramp_steps)
        ))
        drain_sweep_volt_list = np.concatenate((
            np.linspace(0, drain_voltage, num=ramp_steps),
            np.linspace(drain_voltage, drain_voltage, num=sweep_steps),
            np.linspace(drain_voltage, drain_voltage, num=sweep_steps),
            np.linspace(drain_voltage, 0, num=ramp_steps)
        ))
    else:
        gate_sweep_volt_list = np.concatenate((
            np.linspace(0, gate_start, num=ramp_steps),
            np.linspace(gate_start, gate_end, num=sweep_steps),
            np.linspace(gate_end, 0, num=ramp_steps)
        ))
        drain_sweep_volt_list = np.concatenate((
            np.linspace(0, drain_voltage, num=ramp_steps),
            np.linspace(drain_voltage, drain_voltage, num=sweep_steps),
            np.linspace(drain_voltage, 0, num=ramp_steps)
        ))

    leakage_indicator = 1 if test_leakage else 0

    gate_sweep_mode_list = np.concatenate((
        np.zeros(ramp_steps),
        np.ones(int(len(drain_sweep_volt_list) - 2 * ramp_steps)) * leakage_indicator,
        np.zeros(ramp_steps)
    ))
    drain_sweep_mode_list = np.concatenate((
        np.zeros(ramp_steps),
        np.ones(int(len(drain_sweep_volt_list) - 2 * ramp_steps)),
        np.zeros(ramp_steps)
    ))
    # steps = 100
    script_name = 'sweepScript'
    # gate_sweep_volt_list = np.linspace(0,1,num=steps)
    # drain_sweep_volt_list = np.linspace(0,1.5,num=steps)
    # gate_sweep_mode_list = np.array([0 if abs(index-50) >=15 else 1 for index in range(steps)])
    # # gate_sweep_mode_list = np.zeros(steps)
    # drain_sweep_mode_list = np.array([0 if abs(index-50) >=15 else 1 for index in range(steps)])
    parameters = {
                  'script_name':script_name,
                  'gate_sweep_volt_list':gate_sweep_volt_list,
                  'drain_sweep_volt_list':drain_sweep_volt_list,
                  'gate_sweep_mode_list':gate_sweep_mode_list,
                  'drain_sweep_mode_list':drain_sweep_mode_list,
                  'delay':delay}
    return parameters

def output_paramater_generator(
                                 drain_start,
                                 drain_end,
                                 gate_voltage,
                                 sweep_steps,
                                 test_hysteresis,
                                 ramp_steps,
                                 delay):
    if test_hysteresis:
        gate_sweep_volt_list = np.concatenate((
            np.linspace(0, gate_voltage, num=ramp_steps),
            np.linspace(gate_voltage, gate_voltage, num=sweep_steps),
            np.linspace(gate_voltage, gate_voltage, num=sweep_steps),
            np.linspace(gate_voltage, 0, num=ramp_steps)
        ))
        drain_sweep_volt_list = np.concatenate((
            np.linspace(0, drain_start, num=ramp_steps),
            np.linspace(drain_start, drain_end, num=sweep_steps),
            np.linspace(drain_end, drain_start, num=sweep_steps),
            np.linspace(drain_start, 0, num=ramp_steps)
        ))
    else:
        gate_sweep_volt_list = np.concatenate((
            np.linspace(0, gate_voltage, num=ramp_steps),
            np.linspace(gate_voltage, gate_voltage, num=sweep_steps),
            np.linspace(gate_voltage, 0, num=ramp_steps)
        ))
        drain_sweep_volt_list = np.concatenate((
            np.linspace(0, drain_start, num=ramp_steps),
            np.linspace(drain_start, drain_end, num=sweep_steps),
            np.linspace(drain_end, 0, num=ramp_steps)
        ))

    gate_sweep_mode_list = np.concatenate((
        np.zeros(ramp_steps),
        np.zeros(int(len(drain_sweep_volt_list) - 2 * ramp_steps)),
        np.zeros(ramp_steps)
    ))
    drain_sweep_mode_list = np.concatenate((
        np.zeros(ramp_steps),
        np.ones(int(len(drain_sweep_volt_list) - 2 * ramp_steps)),
        np.zeros(ramp_steps)
    ))

    script_name = 'sweepScript'
    parameters = {
                  'script_name':script_name,
                  'gate_sweep_volt_list':gate_sweep_volt_list,
                  'drain_sweep_volt_list':drain_sweep_volt_list,
                  'gate_sweep_mode_list':gate_sweep_mode_list,
                  'drain_sweep_mode_list':drain_sweep_mode_list,
                  'delay':delay}
    return parameters

def fetch_readings(gate, timeout):
    for _ in range(int(timeout/(gate.timeout/1000))):
        try:
            status = gate.query('print(trigger.model.state())')
            break
        except:
            print('Sweep started >>>>>>>>', end = '\r')
    gate.clear()
    print('Sweep completed >>>>>>', end='\r')
    gate_query_data = gate.query_ascii_values('printbuffer(1, defbuffer1.n, defbuffer1.sourcevalues, defbuffer1.readings)')
    gate_readings = np.array(gate_query_data).reshape(-1,2)
    drain_query_data = gate.query_ascii_values('printbuffer(1, node[2].defbuffer1.n, node[2].defbuffer1.sourcevalues, node[2].defbuffer1.readings)')
    drain_readings = np.array(drain_query_data).reshape(-1,2)
    return gate_readings, drain_readings

def transfer(
            gate_start,
            gate_end,
            drain_voltage,
            sweep_steps,
            test_hysteresis,
            test_leakage,
            ramp_steps=20,
            delay=0.01,
            gate_address="USB0::0x05E6::0x2450::04096331::INSTR",
            drain_address="USB0::0x05E6::0x2450::04096333::INSTR"):
    
    transfer_params = transfer_paramater_generator(gate_start=gate_start, 
                             gate_end=gate_end,
                             drain_voltage=drain_voltage,
                             ramp_steps=ramp_steps,
                             sweep_steps=sweep_steps,
                             test_hysteresis=test_hysteresis,
                             test_leakage=test_leakage,
                             delay=delay)
    gate = set_smu_ready(gate_address)
    _ = set_smu_ready(drain_address)
    write_script(gate=gate,**transfer_params)
    gate.write(transfer_params['script_name'] + '.run()')
    gate.write('script.delete(\"' + transfer_params['script_name'] +'\")')

    gate_readings, drain_readings = fetch_readings(gate, timeout=36000)
    _ = set_smu_ready(gate_address)
    _ = set_smu_ready(drain_address)

    return gate_readings, drain_readings


def output(
            drain_start,
            drain_end,
            gate_voltage,
            sweep_steps,
            test_hysteresis,
            ramp_steps=20,
            delay=0.01,
            gate_address="USB0::0x05E6::0x2450::04096331::INSTR",
            drain_address="USB0::0x05E6::0x2450::04096333::INSTR"):
    
    output_params = output_paramater_generator(
                                 drain_start=drain_start,
                                 drain_end=drain_end,
                                 gate_voltage=gate_voltage,
                                 sweep_steps=sweep_steps,
                                 test_hysteresis=test_hysteresis,
                                 ramp_steps=ramp_steps,
                                 delay=delay)

    gate = set_smu_ready(gate_address)
    _ = set_smu_ready(drain_address)
    write_script(gate=gate, **output_params)
    gate.write(output_params['script_name'] + '.run()')
    gate.write('script.delete(\"' + output_params['script_name'] +'\")')
    gate_readings, drain_readings = fetch_readings(gate, timeout=36000)
    _ = set_smu_ready(gate_address)
    _ = set_smu_ready(drain_address)

    return gate_readings, drain_readings
