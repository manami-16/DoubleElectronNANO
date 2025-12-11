# What you can do
1. Merge all mass points of nanoAODs and save them into a signle pickle file
2. Split data into signal and background (Definition of Signal: `Electron_genPartFlav = 1, 15, 22`. Background: otherwise)
3. Plot some basics kinematics (pT, phi, and eta)
4. Derive and plot MVA ID cuts
5. Calculate and plot signal/background efficiencies


# How to run step by step

- Default 
```
cmsenv
python3 run_all.py
```

- To specify a dataset, you can choose either VBF or Inclusive
```
cmsenv
python3 run_all.py --dataset VBF
```

- To specify an output directory to save a pikle file, replace pkl_files with your preferred directory. 
```
cmsenv
python3 run_all.py --pkl_outdir pkl_files
```

- To specify an output directory to save plots, replace plot_dirs with your preferred directory. 
```
cmsenv
python3 run_all.py --plot_outdir plot_dirs
```

# If you want to run only for a partial steps
1. To make kinematics plots: `python3 workflows/make_plots.py`
2. To derive and plot MVA ID cuts: `python3 workflows/derive_wp.py`

Note: 1 and 2 assume that you have pickle files created. 