import numpy as np
import matplotlib.pyplot as plt
import fit_func 

def mos2_fit(x, data, max_iters=1000): 

    height, width, _ = data.shape

    mean_spectra = np.mean(data, axis=(0,1))
    silicon_ref_range = (x > 450.0) & (x < 600.0)
    mos2_ref_range = (x > 330.0) & (x < 450.0)
    silicon_init_params, _ = fit_func.single_peak_fit(mean_spectra[silicon_ref_range], 
                                                      x[silicon_ref_range])
    init_params, _ = fit_func.double_peak_fit(mean_spectra[mos2_ref_range], 
                                              x[mos2_ref_range])

    Si_map_results = fit_func.map_fit(x[silicon_ref_range], 
                    data.reshape((-1,1340))[:,silicon_ref_range], 
                    fit_function=fit_func.single_peak_fit,
                    _max_iters=max_iters,
                    **silicon_init_params
                    )
    map_results = fit_func.map_fit(x[mos2_ref_range], 
                    data.reshape((-1,1340))[:,mos2_ref_range], 
                    fit_function=fit_func.double_peak_fit,
                    _max_iters=max_iters,
                    **init_params
                    )
    return map_results, Si_map_results