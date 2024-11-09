import os
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir) 
from external_instrument_drivers.model_335_temp_controller import temprature_controller
import time

if __name__=='__main__':

    instr = temprature_controller()
    curr_temp = instr.measure()
    # Measure the temperatre every 5 seconds
    interval = 5
    temp_list = []

    for ind in range(1000000):
        time.sleep(interval)
        new_temp = instr.measure()
        temp_list.append(new_temp)
        print(f'Time = {interval * ind} s')
        print(f'New temprature = {new_temp:.2f} K, the temp changed {(new_temp - curr_temp):.2f} K in {interval} seconds  >>>>', end='\n\n')
        curr_temp= new_temp
