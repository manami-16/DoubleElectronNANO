#!/usr/bin/env python3
import argparse
from pathlib import Path
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.Electron_Kinematics_Plotter import (
    plot_kinematics,
    plot_id,
    make_genflav_barplot
)

PLOT_OUTPUT_DIR = '/eos/user/m/mkanemur/WebEOS/WorkingPoint'

def main():
    parser = argparse.ArgumentParser(description="Generate electron kinematics and variable plots.")
    parser.add_argument("--dataset", default='VBF', choices=['VBF', 'Inclusive'], help='Choose one from the available datasets')
    parser.add_argument("--outdir", default=PLOT_OUTPUT_DIR, help="Directory for plot outputs.")
    parser.add_argument("--plot", nargs="+", default=["kinematics", "id", 'genPartFlav'], help="Which plots to run: kinematics, id, or genPartFlav.")

    args = parser.parse_args()

    dataset = args.dataset
    dataset_matchup = {'VBF': 'HAHM_VBF', 'Inclusive': 'HAHM_Inclusive', 'JPsi': 'JPsiToEE'}
    dataset_name = dataset_matchup[dataset]
    sig_path = Path(f'processed/{dataset_name}_signal.pkl')
    bkg_path = Path(f'processed/{dataset_name}_background.pkl')
    
    outdir = Path(f'{args.outdir}/{dataset_name}')
    outdir.mkdir(parents=True, exist_ok=True)

    # Load data
    import pickle
    with open(sig_path, "rb") as f:
        signal_data = pickle.load(f)
    with open(bkg_path, "rb") as f:
        background_data = pickle.load(f)

    print(f"{dataset_name} - Loaded signal/background data")

    # Run plots based on selection
    if "kinematics" in args.plot:
        print("Plotting basic kinematics…")
        plot_vars = {'Electron_pt': (0, 20), 'Electron_eta': (-2.5, 2.5), 'Electron_phi': (-3, 3)}
        plot_kinematics(sig_data=signal_data, bkg_data=background_data, output_dir=outdir, dataset_name=dataset_name, plot_vars=plot_vars)

    if "id" in args.plot:
        print("→ Plotting ID distributions…")
        vars_to_plot = ['Electron_lowPtID_10Jun2025',
                        'Electron_PFEleMvaID_Run3CustomJpsitoEEValue',
                        'Electron_PFEleMvaID_Winter22NoIsoV1Value']
        plot_id(sig_data=signal_data, bkg_data=background_data, plot_vars=vars_to_plot, 
                dataset_name=dataset_name, output_dir=outdir)

    if "genPartFlav" in args.plot:
        print("Plotting Electron_genPartFlav distributions…")
        make_genflav_barplot(sig_data=signal_data, bkg_data=background_data, dataset_name=dataset_name, output_dir=outdir)

    print("Plot generation completed.")

if __name__ == "__main__":
    main()
