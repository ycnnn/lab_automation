**Fast Hyperspectral Raman Microscopy Analysis**

This is a Python implementation for peak fitting the Raman mapping data collected from hyperspectral Raman microscopy. Compared with standard peak fitting functionality provided by NanoPhoton, this tool offers > 10x acceleration in achieveing same accuracy. As a comparasion, for a 400 x 160 pixels Raman mapping data, where each pixel represents a single Raman spectrum, performing a 3-peak fitting will take ~ 500s in the NanoPhoton software, but only ~ 50s using this code.

*Why is the peak fitting in this tool so fast?*

We has applied multiple optimizing strategies, including:

- Better initial values: before running the whole-scale fit, we runa fast, initial fit on the average spectra from every pixel to provide a good initial parameter set.
- Multiprocessing acceleration: we use the multi-processing fuctionality to speed up the process of loading of data into memory up to 3x faster.
- GPU parallel acceleration: we use GPU-compatible, `PyTorch`-based model to speed up fitting up to 100x faster.

- Required libraries:`NumPy`, `Pandas`, `Modin`, `PyTorch`, `lmfit`, `tqdm`.
