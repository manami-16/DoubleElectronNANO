#!/usr/bin/env python3
import argparse
from pathlib import Path
import pickle
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.WP_derivation import run_mva_workflow

PLOT_OUTPUT_DIR = '/eos/user/m/mkanemur/WebEOS/WorkingPoint'

def main():
    parser = argparse.ArgumentParser(description="Derive working points (WP) using signal & background files.")
    parser.add_argument("--dataset", default='VBF', choices=['VBF', 'Inclusive'], help='Choose one from the available datasets')
    parser.add_argument("--outdir", default=PLOT_OUTPUT_DIR, help="Directory for plot outputs.")

    args = parser.parse_args()

    dataset = args.dataset
    dataset_matchup = {'VBF': 'HAHM_VBF', 'Inclusive': 'HAHM_Inclusive',}
    dataset_name = dataset_matchup[dataset]
    sig_path = Path(f'processed/{dataset_name}_signal.pkl')
    bkg_path = Path(f'processed/{dataset_name}_background.pkl')

    outdir = Path(f'{args.outdir}/{dataset_name}/test')
    outdir.mkdir(parents=True, exist_ok=True)

    with open(sig_path, 'rb') as f:
        signal_data = pickle.load(f)

    with open(bkg_path, 'rb') as f:
        background_data = pickle.load(f)

    run_mva_workflow(signal_data, background_data, dataset_name, outdir)
    print("WP derivation completed.")


if __name__ == "__main__":
    main()
