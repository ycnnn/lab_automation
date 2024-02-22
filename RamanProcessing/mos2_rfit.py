
import numpy as np
import pandas as pd
from pathlib import Path
import os
import multiprocessing
from functools import partial
from fit_func import fit

def load_helper(data_path, _width=400):
    data_raw = pd.read_csv(data_path,sep='\t', header=None, index_col=0, comment='#').T.iloc[:-1]
    _total_count, _spectra_len = data_raw.shape
    x = data_raw.columns.to_numpy()
    data = data_raw.to_numpy()
    spec_len = len(x)
    data = data.reshape(-1, _width, spec_len)
    return x, data


def map_fit(x, data, 
            _peak_amp, 
            _peak_width, 
            _Si_amp, 
            _Si_width, 
            _bkg, 
            _max_iters,
            _workers):
    
    fit_partial = partial(fit, 
                      x=x, 
                      amp=_peak_amp, 
                      width=_peak_width, 
                      Si_amp=_Si_amp, 
                      Si_width=_Si_width, 
                      _max_iters=_max_iters,
                      bkg=_bkg)
    
    pool = multiprocessing.Pool(_workers)
    fit_result = pool.map(fit_partial,data)
    pool.close()
    pool.join()
    return fit_result

def unpack(fit_result, _height, _width, correct=True):
    
    _total_count = len(fit_result)
    Si_result = np.zeros((3, _total_count))
    E_result = np.zeros((3, _total_count))
    A_result = np.zeros((3, _total_count))
    bkg_result = np.zeros((3, _total_count))
    
    Si_err = np.zeros((3, _total_count))
    E_err = np.zeros((3, _total_count))
    A_err = np.zeros((3, _total_count))
    bkg_err = np.zeros((3, _total_count))
    
    for index, result in enumerate(fit_result):
        
        Si_result[0,index] = result[1]['Si_center'].value
        Si_result[1,index] = result[1]['Si_amplitude'].value
        Si_result[2,index] = result[1]['Si_fwhm'].value
        Si_err[0,index] = result[1]['Si_center'].stderr
        Si_err[1,index] = result[1]['Si_amplitude'].stderr
        Si_err[2,index] = result[1]['Si_fwhm'].stderr
        
        E_result[0,index] = result[1]['E_center'].value
        E_result[1,index] = result[1]['E_amplitude'].value
        E_result[2,index] = result[1]['E_fwhm'].value
        E_err[0,index] = result[1]['E_center'].stderr
        E_err[1,index] = result[1]['E_amplitude'].stderr
        E_err[2,index] = result[1]['E_fwhm'].stderr
        
        A_result[0,index] = result[1]['A_center'].value
        A_result[1,index] = result[1]['A_amplitude'].value
        A_result[2,index] = result[1]['A_fwhm'].value
        A_err[0,index] = result[1]['A_center'].stderr
        A_err[1,index] = result[1]['A_amplitude'].stderr
        A_err[2,index] = result[1]['A_fwhm'].stderr
        
        bkg_result[0,index] = result[1]['bkg_slope'].value
        bkg_result[1,index] = result[1]['bkg_intercept'].value
        bkg_err[0,index] = result[1]['bkg_slope'].stderr
        bkg_err[1,index] = result[1]['bkg_intercept'].stderr
        
    Si_result = Si_result.reshape((3,-1,_width))
    E_result = E_result.reshape((3,-1,_width))
    A_result = A_result.reshape((3,-1,_width))
    bkg_result = bkg_result.reshape((3,-1,_width))
    
    Si_err = Si_err.reshape((3,-1,_width))
    E_err = E_err.reshape((3,-1,_width))
    A_err = A_err.reshape((3,-1,_width))
    bkg_err = bkg_err.reshape((3,-1,_width))
    
    _, _height, _ = Si_result.shape
    result = np.zeros((4,3,_height, _width))
    err = np.zeros((4,3,_height, _width))
    
    result[0] = Si_result
    result[1] = E_result
    result[2] = A_result
    result[3] = bkg_result
    
    if correct:
        result[1,0] = result[1,0] - (result[0,0] - 520.0)
        result[2,0] = result[2,0] - (result[0,0] - 520.0)
    
    err[0] = Si_err
    err[1] = E_err
    err[2] = A_err
    err[3] = bkg_err
    
    return result, err



class MoS2_Raman():
    def __init__(self, x, data, 
                 _peak_amp = 1000, 
                 _peak_width = 10, 
                 _Si_amp = 1000, 
                 _Si_width = 10, 
                 _bkg = 150, 
                 _max_iters = 5000,
                 _workers=multiprocessing.cpu_count(),
                 _correct=True):
        _height, _width, _spec_len = data.shape
        self.fit_result = map_fit(x=x, 
                                  data=data.reshape(-1,_spec_len), 
                                  _peak_amp = _peak_amp, 
                                  _peak_width = _peak_width, 
                                  _Si_amp = _Si_amp, 
                                  _Si_width = _Si_width, 
                                  _bkg = _bkg, 
                                  _max_iters = _max_iters,
                                  _workers=_workers)

        self.fitted_params, self.fitted_params_err  = unpack(self.fit_result, _height=_height,_width=_width, correct=_correct)   
        self.compute_sd() 
        
    
    def get_fitted(self):
        return self.fitted_params
    
    def get_fitted_err(self):
        return self.fitted_params_err
    
    def compute_sd(self):
        s = self.fitted_params[1,0] * (-0.20) + self.fitted_params[2,0] * (0.03)
        d = self.fitted_params[1,0] * (-0.15) + self.fitted_params[2,0] * (0.47)
        _h, _w = s.shape
        self.sd = np.zeros((2,_h,_w))
        self.sd[0] = s
        self.sd[1] = d
        
    def get_sd(self):
        return self.sd
    

