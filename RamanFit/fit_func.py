from functools import partial
import multiprocessing
import numpy as np
# import pandas as pd
import modin.pandas as pd
from lmfit.models import LinearModel, LorentzianModel

def load_helper(data_path, _width=400):
    data_raw = pd.read_csv(data_path,sep='\t', header=None, index_col=0, comment='#').T.iloc[:-1]
    _total_count, _spectra_len = data_raw.shape
    x = data_raw.columns.to_numpy()
    data = data_raw.to_numpy()
    spec_len = len(x)
    data = data.reshape(-1, _width, spec_len)
    return x, data

def single_peak_fit(y,x, 
        _max_iters=5000,
        peak_0_center=520,
        peak_0_amplitude=1000, 
        peak_0_sigma=10, 
        _slope=0,
        _intercept=150):
    
    iters = _max_iters    
    rmodel = (LorentzianModel(prefix='peak_0_') + LinearModel(prefix='_'))

    params = rmodel.make_params(
                                peak_0_center=dict(value=peak_0_center, 
                                                   min=peak_0_center-10.0, 
                                                   max=peak_0_center+10.0),
                                peak_0_amplitude=dict(value=peak_0_amplitude, min=0),
                                peak_0_sigma=peak_0_sigma,
                                _slope=_slope,
                                _intercept=_intercept)
    result = rmodel.fit(y, params, x=x, max_nfev=iters)
    params_val = {}
    params_std ={}
    for param in result.params:
        if 'fwhm' not in param and 'height' not in param:
            params_val[param] = result.params[param].value
            params_std[param] = result.params[param].stderr

    return params_val, (params_std, result.nfev, result.best_fit)

def double_peak_fit(y,x, 
        _max_iters=5000,
        peak_0_center=380,
        peak_0_amplitude=1000, 
        peak_0_sigma=10, 
        peak_1_center=404,
        peak_1_amplitude=1000, 
        peak_1_sigma=10, 
        _slope=0,
        _intercept=150):
    print(f'Running initial fit, guess {peak_0_center} and {peak_1_center}...')
    iters = _max_iters    
    rmodel = (LorentzianModel(prefix='peak_0_') 
              + LorentzianModel(prefix='peak_1_')
              + LinearModel(prefix='_'))

    params = rmodel.make_params(
                                peak_0_center=dict(value=peak_0_center, 
                                                   min=peak_0_center-5.0, 
                                                   max=peak_0_center+5.0),
                                peak_0_amplitude=dict(value=peak_0_amplitude, min=0),
                                peak_0_sigma=peak_0_sigma,
                                peak_1_center=dict(value=peak_1_center, 
                                                   min=peak_1_center-5.0, 
                                                   max=peak_1_center+5.0),
                                peak_1_amplitude=dict(value=peak_1_amplitude, min=0),
                                peak_1_sigma=peak_1_sigma,
                                _slope=_slope,
                                _intercept=_intercept)
    
    result = rmodel.fit(y, params, x=x, max_nfev=iters)
    params_val = {}
    params_std ={}
    for param in result.params:
        if 'fwhm' not in param and 'height' not in param:
            params_val[param] = result.params[param].value
            params_std[param] = result.params[param].stderr
 
    return params_val, (params_std, result.nfev, result.best_fit)

def map_fit(x, data, 
            fit_function,
            _max_iters=5000,
            _workers=16,
            **kwargs):
    if len(data.shape) != 2:
        raise AssertionError("Input data shape incorrect.")
    fit_partial = partial(fit_function, 
                          x=x, 
                          _max_iters=_max_iters, 
                          **kwargs)
    
    pool = multiprocessing.Pool(_workers)
    fit_result = pool.map(fit_partial, data)
    pool.close()
    pool.join()
    return fit_result