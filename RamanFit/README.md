**Fast Hyperspectral Raman Microscopy Analysis**

This is a Python implementation for peak fitting the Raman mapping data collected from hyperspectral Raman microscopy. Compared with standard peak fitting functionality provided by NanoPhoton, this tool offers > 10x acceleration in achieveing same accuracy. As a comparasion, for a 400 x 160 pixels Raman mapping data, where each pixel represents a single Raman spectrum, performing a 3-peak fitting will take ~ 500s in the NanoPhoton software, but only ~ 50s using this code.

If you use this code in your research, please cite as follows:
```
@software{Zhang_2D_Reserach_Automation_2024,
author = {Zhang, Yue},
doi = {10.5281/zenodo.10724769},
month = feb,
title = {{2D Reserach Automation Tools}},
url = {https://github.com/ycnnn/lab_automation},
version = {2.0},
year = {2024}
}
```

*Why is the peak fitting in this tool so fast?*

We have applied multiple optimizing strategies, including:

- Better initial values: before running the whole-scale fit, we runa fast, initial fit on the average spectra from every pixel to provide a good initial parameter set.
- Multiprocessing acceleration: we use the multi-processing fuctionality to speed up the process of loading of data into memory up to 3x faster.
- GPU parallel acceleration: we use GPU-compatible, `PyTorch`-based model to speed up fitting up to 100x faster.

Required libraries:`NumPy`, `Pandas`, `Modin`, `PyTorch`, `lmfit`, `tqdm`.

**How to use this script:**

There are two ways to use this script, you can either run it on command line or inside a Jupyter notebook.

(Recommended) To run it on Jupyter notebook, download the `RamanFit` folder, put the `txt` raw Raman mapping file into the `RamanFit` folder,and follow `demo.ipynb`.

To run it on command line:
- Download the `RamanFit` folder.
- Put the `txt` raw Raman mapping file into the `RamanFit` folder. It should be the same folder where you see other files such as `torch_fit.py`.
- Open your command line window (`cmd` on Windows or `Terminal` on Linux/MacOS). Go to the `RamanFit` folder by using `cd` command. You should see `__your__computer__name RamanFit %` in the command tool window.
- Enter this command: `ulimit -n 512`. This line sets the maximum files the script can open. This is ncessary because the script is highly parallelized.
- Assume the filename of the `txt` file is `spectrums.txt`. Run this command: `python start_fitting.py spectrums.txt`.
- Wait about 20s.
- You should see a progress bar appearing, looking like: `Apple M series GPU acceleration enabled.
Running initial fit, guess 384.01 and 404.01...
Loss 5.472247808 : 100%|██████████████████████████████████████████████████████████████████████████████████████| 250/250 [00:15<00:00, 16.11it/s]
`.
- Wait thill finish. Once finish, you will see 3 `csv` files appearing in the `RamanFit` folder, anmely `Si_peak_position.csv`, `E_peak_position.csv` and `A_peak_position.csv`. These are peaking distribution maps.
- (Optional) if you want customization of code, do not run  `python start_fitting.py spectrums.txt`, instead run  `python start_fitting.py spectrums.txt 0`.
  - The system will then ask for each paramter:
  - For `Initial E peak position guess (in cm-1) ? `, enter your initial guess of the E peak position.
  - For `Initial A peak position guess (in cm-1) ? `, enter your initial guess of the A peak position.
  - For `How to save the result? Enter 0 for .csv file, enter 1 for .npy file. `, enter 0 to save all results in `csv` format, otherwise in `npy` format. 
