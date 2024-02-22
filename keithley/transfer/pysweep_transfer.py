import numpy as np
import pyvisa as pv

gate_address = "USB0::0x05E6::0x2450::04096331::INSTR"
drain_address = "USB0::0x05E6::0x2450::04096333::INSTR"

def ramp_gate(inst,
              gate_ramp_start=0,
              gate_ramp_end=1,
              gate_ramp_steps=20,
              delay=0.01,
              script_name='RampGate'):
    inst.write('loadscript ' +  script_name)
    inst.write('smu.source.configlist.create(\"sweepVals\")')
    inst.write('smu.source.func = smu.FUNC_DC_VOLTAGE')
    inst.write('smu.source.autorange = smu.ON')
    inst.write('smu.source.ilimit.level = 100e-3')
    inst.write('smu.measure.func = smu.FUNC_DC_VOLTAGE')
    inst.write('smu.measure.autorange = smu.ON')
    inst.write(f'gatesweeppoints={gate_ramp_steps}')
    for volt in np.linspace(gate_ramp_start, gate_ramp_end, num=gate_ramp_steps):
        inst.write(f'smu.source.level = {volt}')
        inst.write('smu.source.configlist.store(\"sweepVals\")')

    inst.write('trigger.model.setblock(1, trigger.BLOCK_CONFIG_RECALL, \"sweepVals\")')
    inst.write(f'trigger.model.setblock(2, trigger.BLOCK_DELAY_CONSTANT, {delay})')
    inst.write('trigger.model.setblock(3, trigger.BLOCK_MEASURE_DIGITIZE)')
    inst.write('trigger.model.setblock(4, trigger.BLOCK_CONFIG_NEXT, \"sweepVals\")')
    inst.write('trigger.model.setblock(5, trigger.BLOCK_BRANCH_COUNTER, gatesweeppoints,2)')
    inst.write('trigger.model.setblock(6, trigger.BLOCK_DELAY_CONSTANT, 0)')
    inst.write('trigger.model.initiate()')
    inst.write('waitcomplete()')
    inst.write('endscript')
    inst.write(script_name + '.save()')

    return

def ramp_drain(inst,
              drain_ramp_start=0,
              drain_ramp_end=1,
              drain_ramp_steps=20,
              delay=0.01,
              script_name='RampDrain'):
    inst.write('loadscript ' + script_name)
    inst.write('node[2].smu.source.configlist.create(\"drainSweepVals\")')
    inst.write('node[2].smu.source.func = node[2].smu.FUNC_DC_VOLTAGE')
    inst.write('node[2].smu.source.autorange = node[2].smu.ON')
    inst.write('node[2].smu.source.ilimit.level = 100e-3')
    inst.write('node[2].smu.measure.func = node[2].smu.FUNC_DC_VOLTAGE')
    inst.write('node[2].smu.measure.autorange = node[2].smu.ON')
    inst.write(f'drainSweeppoints={drain_ramp_steps}')
    for volt in np.linspace(drain_ramp_start, drain_ramp_end, num=drain_ramp_steps):
        inst.write(f'node[2].smu.source.level = {volt}')
        inst.write('node[2].smu.source.configlist.store(\"drainSweepVals\")')

    inst.write('node[2].trigger.model.setblock(1, node[2].trigger.BLOCK_CONFIG_RECALL, \"drainSweepVals\")')
    inst.write(f'node[2].trigger.model.setblock(2, node[2].trigger.BLOCK_DELAY_CONSTANT, {delay})')
    inst.write('node[2].trigger.model.setblock(3, node[2].trigger.BLOCK_MEASURE_DIGITIZE)')
    inst.write('node[2].trigger.model.setblock(4, node[2].trigger.BLOCK_CONFIG_NEXT, \"drainSweepVals\")')
    inst.write('node[2].trigger.model.setblock(5, node[2].trigger.BLOCK_BRANCH_COUNTER, drainSweeppoints,2)')
    inst.write('node[2].trigger.model.setblock(6, node[2].trigger.BLOCK_DELAY_CONSTANT, 0)')
    inst.write('node[2].trigger.model.setblock(7, node[2].trigger.BLOCK_DELAY_CONSTANT, 0)')
    inst.write('node[2].trigger.model.setblock(8, node[2].trigger.BLOCK_DELAY_CONSTANT, 0)')
    inst.write('node[2].trigger.model.initiate()')
    inst.write('waitcomplete()')
    inst.write('endscript')
    inst.write(script_name + '.save()')

    return

def transfer(inst,
                    gate_start=0,
                    gate_end=1,
                    sweep_num=40,
                    drain_voltage=0.1,
                    script_name='TransferSweep'):
    ########################################################################
    # Setting up TSP link.
    inst.write('loadscript ' + script_name)
    # Reset the instruments and the TSP-Link connection, and clear the bufferS
    # inst.write('tsplink.initialize()')
    # # If the tsplink state is not online, print an error message and quit'
    # inst.write('state = tsplink.state')
    # inst.write('if state ~= "online" then')
    # inst.write(' print("Error:-Check that all SMUs have a different node number")')
    # inst.write(' print("-Check that all SMUs are connected correctly")')
    # inst.write(' return')
    # inst.write('end')
    # inst.write('reset()')

    # Basic setup of gate SMU.
    inst.write(f'steppoints = {sweep_num}')
    #  Set up the source function
    inst.write('smu.source.configlist.create(\"stepVals\")')
    inst.write('smu.source.func = smu.FUNC_DC_VOLTAGE')
    inst.write('smu.source.autorange = smu.ON')
    #  Set up the measure function.')

    ## Whether to measure leakage
    # inst.write('smu.measure.func = smu.FUNC_DC_CURRENT')
    inst.write('smu.measure.func = smu.FUNC_DC_VOLTAGE')


    inst.write('smu.measure.autorange = smu.ON')
    inst.write('smu.measure.terminals = smu.TERMINALS_FRONT')

    # Set up TSP-Link triggering.
    inst.write('tsplink.line[1].reset()')
    inst.write('tsplink.line[1].mode = tsplink.MODE_SYNCHRONOUS_MASTER')
    inst.write('tsplink.line[2].mode = tsplink.MODE_SYNCHRONOUS_ACCEPTOR')
    inst.write('trigger.tsplinkout[1].stimulus = trigger.EVENT_NOTIFY1')
    inst.write('trigger.tsplinkin[2].clear()')
    inst.write('trigger.tsplinkin[2].edge = trigger.EDGE_RISING')

    for i in np.linspace(gate_start, gate_end, num=sweep_num):
        inst.write(f'smu.source.level = {i}')
        inst.write('smu.source.configlist.store(\"stepVals\")')
    #  Set up the trigger model.
    # inst.write(f'smu.source.level = 0')
    # inst.write('smu.source.output = smu.ON')

    inst.write('trigger.model.setblock(1, trigger.BLOCK_CONFIG_RECALL, \"stepVals\")')
    inst.write('trigger.model.setblock(2, trigger.BLOCK_MEASURE_DIGITIZE)')
    inst.write('trigger.model.setblock(3, trigger.BLOCK_NOTIFY, trigger.EVENT_NOTIFY1)')
    inst.write('trigger.model.setblock(4, trigger.BLOCK_WAIT, trigger.EVENT_TSPLINK2)')
    inst.write('trigger.model.setblock(5, trigger.BLOCK_CONFIG_NEXT, \"stepVals\")')
    inst.write('trigger.model.setblock(6, trigger.BLOCK_BRANCH_COUNTER, steppoints, 2)')

    
    # Model 2450 #2 (drain) setup
    inst.write('sweeppoints = 1')
    inst.write('node[2].smu.source.configlist.create(\"sweepVals\")')
    inst.write('node[2].smu.source.func = node[2].smu.FUNC_DC_VOLTAGE')
    inst.write('node[2].smu.source.autorange = node[2].smu.ON')
    inst.write('node[2].smu.source.ilimit.level = 100e-3')
    #  Set up the measure function
    inst.write('node[2].smu.measure.func = node[2].smu.FUNC_DC_CURRENT')
    inst.write('node[2].smu.measure.autorange = node[2].smu.OFF')
    inst.write('node[2].smu.measure.terminals = node[2].smu.TERMINALS_FRONT')
    inst.write('node[2].smu.measure.range = 100e-3')
    # Enable the following 3 lines to test the pure communication overhead. For current srtup, the overhead is 2.5 s
    # inst.write('node[2].smu.measure.func = node[2].smu.FUNC_DC_VOLTAGE')
    # inst.write('node[2].smu.measure.autorange = node[2].smu.ON')
    # inst.write('node[2].smu.measure.terminals = node[2].smu.TERMINALS_FRONT')

    # Set up TSP-Link triggering
    inst.write('node[2].tsplink.line[2].mode = node[2].tsplink.MODE_SYNCHRONOUS_MASTER')
    inst.write('node[2].tsplink.line[1].mode = node[2].tsplink.MODE_SYNCHRONOUS_ACCEPTOR')
    inst.write('node[2].trigger.tsplinkout[2].stimulus = node[2].trigger.EVENT_NOTIFY2')
    inst.write('node[2].trigger.tsplinkin[1].clear()')
    inst.write('node[2].trigger.tsplinkin[1].edge = node[2].trigger.EDGE_RISING')


    inst.write(f'node[2].smu.source.level = {drain_voltage}')
    inst.write('node[2].smu.source.configlist.store(\"sweepVals\")')


    # Set up the trigger model
    inst.write('node[2].trigger.model.setblock(1, node[2].trigger.BLOCK_CONFIG_RECALL, \"sweepVals\")')
    inst.write('node[2].trigger.model.setblock(2, node[2].trigger.BLOCK_SOURCE_OUTPUT, node[2].smu.ON)')
    inst.write('node[2].trigger.model.setblock(3, node[2].trigger.BLOCK_WAIT, node[2].trigger.EVENT_TSPLINK1)')
    inst.write('node[2].trigger.model.setblock(4, node[2].trigger.BLOCK_DELAY_CONSTANT, 0.0001)')
    inst.write('node[2].trigger.model.setblock(5, node[2].trigger.BLOCK_MEASURE_DIGITIZE)')
    inst.write('node[2].trigger.model.setblock(6, node[2].trigger.BLOCK_CONFIG_NEXT, \"sweepVals\")')
    inst.write('node[2].trigger.model.setblock(7, node[2].trigger.BLOCK_NOTIFY, node[2].trigger.EVENT_NOTIFY2)')
    inst.write('node[2].trigger.model.setblock(8, node[2].trigger.BLOCK_BRANCH_COUNTER, steppoints,3)')


    # Start the trigger model for both SMUs and wait until it is complete
    inst.write('node[2].trigger.model.initiate()')
    inst.write('trigger.model.initiate()')
    inst.write('waitcomplete()')
    # inst.write('smu.source.output = smu.OFF')

    inst.write('endscript')
    inst.write(script_name + '.save()')
    

    return

def set_smu_ready(address):
    rm = pv.ResourceManager()
    smu = rm.open_resource(address)
    smu.timeout = 500
    smu.write('reset()')
    smu.write('smu.source.func = smu.FUNC_DC_VOLTAGE')
    # smu.write('smu.source.output = smu.ON')
    return smu

def set_gate_drain_ready(gate_address,
                         drain_address):
    gate = set_smu_ready(gate_address)
    drain = set_smu_ready(drain_address)
    gate.write('smu.source.output = smu.ON')
    gate.write('node[2].smu.source.output = node[2].smu.ON')
    return gate

def ramp_gate_drain(gate,
                    gate_ramp_start,
                    gate_ramp_end,
                    gate_ramp_steps,
                    drain_ramp_start,
                    drain_ramp_end,
                    drain_ramp_steps):
    gate_script_name = 'rampGate'
    ramp_gate(gate, 
            gate_ramp_start=gate_ramp_start,
            gate_ramp_end=gate_ramp_end,
            gate_ramp_steps=gate_ramp_steps,
            script_name=gate_script_name)
    # gate.write(gate_script_name + '.run()')
    # gate.write('script.delete(\"' + gate_script_name +'\")')

    drain_script_name = 'rampDrain'
    ramp_drain(gate, 
            drain_ramp_start=drain_ramp_start,
            drain_ramp_end=drain_ramp_end,
            drain_ramp_steps=drain_ramp_steps,
            script_name=drain_script_name)
    # gate.write(drain_script_name + '.run()')
    # gate.write('script.delete(\"' + drain_script_name +'\")')
    gate.write(gate_script_name + '.run()')
    gate.write(drain_script_name + '.run()')
    gate.write('script.delete(\"' + gate_script_name +'\")')
    gate.write('script.delete(\"' + drain_script_name +'\")')
    ####################################################################

def transfer_sweep_gate_drain(gate,
                              gate_start, 
                              gate_end,
                              sweep_steps,
                              drain_voltage):
    script_name = 'tc'
    transfer(gate,
            gate_start=gate_start,
            gate_end=gate_end,
            sweep_num=sweep_steps,
            drain_voltage=drain_voltage, 
            script_name=script_name)
    gate.write(script_name + '.run()')
    gate.write('script.delete(\"' + script_name +'\")')

def fetch_readings(gate,
                   timeout,
                   gate_ramp_steps,
                   drain_ramp_steps):
    gate.write('smu.source.output = smu.OFF')
    gate.write('node[2].smu.source.output = node[2].smu.OFF')

    for _ in range(int(timeout/(gate.timeout/1000))):
        try:
            status = gate.query('print(trigger.model.state())')
            break
        except:
            print('Sweep started.', end = '\r')
    gate.clear()
    print('Sweep completed.', end='\r')
    gate_query_data = gate.query_ascii_values('printbuffer(1, defbuffer1.n, defbuffer1.sourcevalues, defbuffer1.readings)')
    gate_readings = np.array(gate_query_data).reshape(-1,2)[gate_ramp_steps:-gate_ramp_steps]
    drain_query_data = gate.query_ascii_values('printbuffer(1, node[2].defbuffer1.n, node[2].defbuffer1.sourcevalues, node[2].defbuffer1.readings)')
    drain_readings = np.array(drain_query_data).reshape(-1,2)[drain_ramp_steps:-drain_ramp_steps]
    return gate_readings, drain_readings

def transfer_sweep(gate_ramp_steps,
                   drain_ramp_steps,
                   sweep_steps,
                   drain_voltage,
                   gate_start,
                   gate_end,
                   timeout=1800,
                   gate_address=gate_address,
                   drain_address=drain_address,
                   test_hysteresis=True):

    gate = set_gate_drain_ready(gate_address=gate_address,
                                drain_address=drain_address)

    ramp_gate_drain(gate=gate,
                        gate_ramp_start=0,
                        gate_ramp_end=gate_start,
                        gate_ramp_steps=gate_ramp_steps,
                        drain_ramp_start=0,
                        drain_ramp_end=drain_voltage,
                        drain_ramp_steps=drain_ramp_steps)


    transfer_sweep_gate_drain(gate=gate,gate_start=gate_start,
                            gate_end=gate_end,
                            sweep_steps=sweep_steps,
                            drain_voltage=drain_voltage)

    if test_hysteresis:

        transfer_sweep_gate_drain(gate=gate,gate_start=gate_end,
                                gate_end=gate_start,
                                sweep_steps=sweep_steps,
                                drain_voltage=drain_voltage)
        
    gate_ramp_down_start = gate_start if test_hysteresis else gate_end
    ramp_gate_drain(gate=gate,
                        gate_ramp_start=gate_ramp_down_start,
                        gate_ramp_end=0,
                        gate_ramp_steps=gate_ramp_steps,
                        drain_ramp_start=drain_voltage,
                        drain_ramp_end=0,
                        drain_ramp_steps=drain_ramp_steps)
    
    gate_readings, drain_readings = fetch_readings(gate=gate,
                                                gate_ramp_steps=gate_ramp_steps,
                                                drain_ramp_steps=drain_ramp_steps,
                                                timeout=timeout)
    return gate_readings, drain_readings