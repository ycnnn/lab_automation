import numpy as np
from lmfit.models import LinearModel, LorentzianModel


def fit(y,x, 
        amp=1000, 
        width=10, 
        Si_amp=1000, 
        Si_width=10, 
        bkg=150,
        _max_iters=5000,
        summary=False):
    
    iters = _max_iters    
    rmodel = (LorentzianModel(prefix='E_') 
            + LorentzianModel(prefix='A_') 
            + LorentzianModel(prefix='Si_')  
            + LinearModel(prefix='bkg_'))

    params = rmodel.make_params(E_center=dict(value=383.0, min=373.0, max=395.0),
                                E_amplitude=dict(value=amp, min=0),
                                E_width=width,
                                # A_center=dict(value=400.0, min=393.0, max=400.5),
                                # A_center=dict(value=401.0, min=393.0, max=400.2),
                                A_center=dict(value=401.0, min=393.0, max=405.0),
                                A_amplitude=dict(value=amp, min=0),
                                A_width=width,
                                Si_center=dict(value=520.0, min=505.0, max=535.0),
                                Si_amplitude=dict(value=amp, min=0),
                                Si_width=Si_width,
                                bkg_slope=0,
                                bkg_intercept=bkg)
    result = rmodel.fit(y, params, x=x, max_nfev=iters)
    
    if not summary:
        return result.best_fit, result.params
    else:
        return result.best_fit, result.params, result.nfev


    
