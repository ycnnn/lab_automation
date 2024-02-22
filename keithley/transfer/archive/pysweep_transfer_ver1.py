import numpy as np

def generate_script(inst,
                    gate_start=0,
                    gate_end=1,
                    sweep_num=40,
                    drain_voltage=0.1,
                    script_name='TransferSweep'):
    ########################################################################
    # Setting up TSP link.
    inst.write('loadscript ' + script_name)
    # Reset the instruments and the TSP-Link connection, and clear the bufferS
    inst.write('tsplink.initialize()')
    # If the tsplink state is not online, print an error message and quit'
    inst.write('state = tsplink.state')
    inst.write('if state ~= "online" then')
    inst.write(' print("Error:-Check that all SMUs have a different node number")')
    inst.write(' print("-Check that all SMUs are connected correctly")')
    inst.write(' return')
    inst.write('end')
    inst.write('reset()')

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
    inst.write(f'smu.source.level = 0')
    inst.write('smu.source.output = smu.ON')

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
    # inst.write('node[2].trigger.model.setblock(9, node[2].trigger.BLOCK_SOURCE_OUTPUT, node[2].smu.OFF)')



    # Start the trigger model for both SMUs and wait until it is complete
    inst.write('node[2].trigger.model.initiate()')
    inst.write('trigger.model.initiate()')
    inst.write('waitcomplete()')
    inst.write('smu.source.output = smu.OFF')

    # #  Print the formatted readings.
    # inst.write('if defbuffer1.n == 0 then')
    # inst.write('    print("No readings in buffer")')
    # inst.write('   else')
    # inst.write('    for k = 1, sweeppoints do')
    # inst.write('    print(string.format("%f\t%f\t\t%f\t%f\t\t%f\t%f\t\t%f\t%f",')
    # inst.write('    node[2].defbuffer1.sourcevalues[k], node[2].defbuffer1[k],')
    # inst.write('    node[2].defbuffer1.sourcevalues[k+sweeppoints],')
    # inst.write('    node[2].defbuffer1[k+sweeppoints],')
    # inst.write('    node[2].defbuffer1.sourcevalues[k+sweeppoints*2],')
    # inst.write('    node[2].defbuffer1[k+sweeppoints*2],')
    # inst.write('    node[2].defbuffer1.sourcevalues[k+sweeppoints*3],')
    # inst.write('    node[2].defbuffer1[k+sweeppoints*3]))')
    # inst.write('    end')
    # inst.write('   end')

    inst.write('endscript')
    inst.write(script_name + '.save()')
    inst.write(script_name + '.run()')
    inst.write('script.delete(\"' + script_name +'\")')

    return

