import pyvisa as pv
import numpy as np
import time

# drain_address = "USB0::0x05E6::0x2450::04096333::INSTR"
# gate_address = "USB0::0x05E6::0x2450::04096331::INSTR"

def set_smu_ready(address,tsplink_head=''):
    rm = pv.ResourceManager()
    smu = rm.open_resource(address)
    smu.write('reset()')
    smu.write('smu.source.func = smu.FUNC_DC_VOLTAGE')
    smu.write('smu.source.autorange = smu.ON')
    return smu

def close_smu(smu,tsplink_head=''):
    smu.write('smu.source.output = smu.OFF')
    smu.close()


def write_list(smu, volt_list, mode_list, delay=0.001,tsplink_head=''):

    smu.write("smu.source.configlist.create(\"SourceSweep\")")
    smu.write("smu.measure.configlist.create(\"MeasureSweep\")")
    for index, volt in enumerate(volt_list):
        smu.write('smu.source.level = ' + str(volt))
        smu.write('smu.source.configlist.store(\"SourceSweep\")')
        mode = 'smu.measure.func = smu.FUNC_DC_VOLTAGE' if mode_list[index] ==0 else 'smu.measure.func = smu.FUNC_DC_CURRENT'
        smu.write(mode)
        #########################################
        smu.write('smu.measure.autorange = smu.ON')
        #########################################
        smu.write('smu.measure.configlist.store(\"MeasureSweep\")')

    smu.write(f'trigger.model.load(\'ConfigList\',\'MeasureSweep\',\'SourceSweep\', {delay})')
    smu.write('trigger.model.setblock(8,trigger.BLOCK_DELAY_CONSTANT, 0)')


def start_sweep(smu, timeout,tsplink_head=''):
    smu.write('trigger.model.initiate()')

    for i in range(int(timeout/0.25)):
        time.sleep(0.25)
        status = smu.query('print(trigger.model.state())')
        # print(status)
        if i >= 1 and status[14:18] == 'IDLE':
            smu.clear()
            data = np.array(smu.query_ascii_values('printbuffer(1, defbuffer1.n, defbuffer1.sourcevalues, defbuffer1.readings)')).reshape(-1,2)
            # smu.write('smu.source.output = smu.OFF')
            return data[:,:]
    print('Error: scan timeout')
    return
        
def ramp(smu, start_volt=0, end_volt=1,ramp_steps=10,delay=0.001,timeout=3600):

    volt_list = np.linspace(start_volt,end_volt, num=ramp_steps)
    mode_list = np.zeros(ramp_steps) 
    write_list(smu=smu,
               volt_list=volt_list,
               mode_list=mode_list,
               delay=delay)
    _ = start_sweep(smu=smu, timeout=timeout)


def full_sweep(smu, 
          start_volt=-1, 
          end_volt=1,
          ramp_steps=25,
          scan_steps=50, 
          delay=0.001,
          timeout=3600,
          hyst=False):
    
    if hyst:
        volt_list = np.concatenate((np.linspace(0,start_volt, num=ramp_steps),
                        np.linspace(start_volt,end_volt,num=scan_steps),
                        np.linspace(end_volt,start_volt,num=scan_steps),
                        np.linspace(start_volt,0, num=ramp_steps)))
        mode_list = np.concatenate((np.zeros(ramp_steps),
                        np.ones(scan_steps),
                        np.ones(scan_steps),
                        np.zeros(ramp_steps)))
    else:
        volt_list = np.concatenate((np.linspace(0,start_volt, num=ramp_steps),
                        np.linspace(start_volt,end_volt,num=scan_steps),
                        np.linspace(end_volt,0, num=ramp_steps)))
        mode_list = np.concatenate((np.zeros(ramp_steps),
                        np.ones(scan_steps),
                        np.zeros(ramp_steps)))

    write_list(smu=smu,
               volt_list=volt_list,
               mode_list=mode_list,
               delay=delay)
    data = start_sweep(smu=smu, timeout=timeout)[ramp_steps:-ramp_steps]
    close_smu(smu)

    return data

########################################################################################
# Final output code
def output(gate_voltages,
           scan_start,
           scan_end,
           hyst=False,
           scan_steps=25,
           ramp_delay=0.025,
           scan_delay=0.025,
           drain_address="USB0::0x05E6::0x2450::04096333::INSTR",
           gate_address="USB0::0x05E6::0x2450::04096331::INSTR"
           ):

    extended_gate_voltage = np.zeros(len(gate_voltages)+1)
    extended_gate_voltage[1:] = gate_voltages
    results = []

    gate = set_smu_ready(address=gate_address)

    for index, gate_voltage in enumerate(gate_voltages):
        ramp_start, ramp_end = (extended_gate_voltage[index],extended_gate_voltage[index+1])
        ramp(gate, start_volt=ramp_start, end_volt=ramp_end, delay=ramp_delay)
        drain = set_smu_ready(address=drain_address)
        data = full_sweep(smu=drain,
                        start_volt=scan_start,
                        end_volt=scan_end,
                        scan_steps=scan_steps,
                        delay=scan_delay,
                        hyst=hyst
        )
        results.append(data)
    ramp(gate, start_volt=ramp_end, end_volt=0, delay=ramp_delay)
    close_smu(gate)
    return gate_voltages, np.array(results)