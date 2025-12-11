import argparse
import glob
import pickle
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.process_root import merge_mass_points
from src.split_signal_background import split_sig_bkg
from src.WP_derivation import run_mva_workflow

PLOT_OUTPUT_DIR = '/eos/user/m/mkanemur/WebEOS/WorkingPoint'

parser = argparse.ArgumentParser(description="Concatenate nanoAODs for multiple mass points into a single pkl file")
parser.add_argument("--dataset", default='VBF', choices=['VBF', 'Inclusive', 'JPsi'], help='Choose one from the available datasets')
parser.add_argument("--pkl_outdir", default='processed', help="Directory for saving a pikle file.")
parser.add_argument("--plot_outdir", default=PLOT_OUT_DIR, help="Directory for saving plots.")

args = parser.parse_args()
dataset_name = args.dataset
pkl_outdir = args.pkl_outdir
plot_outdir = args.plot_outdir

# Check if you've already produced pkl files. 
pattern = os.path.join(pkl_outdir, f"{dataset_name}*")
existing_files = glob.glob(pattern)
has_processed = any(f.endswith("_processed.pkl") for f in existing_files)
has_signal = any(f.endswith("_signal.pkl") for f in existing_files)
has_background = any(f.endswith("_background.pkl") for f in existing_files)

if has_signal and has_background:
	print('You have splitted signal and background. Deriving WP/efficiency...')
	signal_pkl = [f for f in existing_files if f.endswith("_signal.pkl")][0]
	background_pkl = [f for f in existing_files if f.endswith("_background.pkl")][0]

	with open(signal_pkl, 'rb') as f:
		signal_data = pickle.load(f)
	with open(background_pkl, 'rb') as f:
		background_data = pickle.load(f)
	run_mva_workflow(signal_data=signal_data, background_data=background_data, dataset_name=dataset_name, output_dir=plot_outdir)

elif has_processed:
	print('You have merged all mass points of nanoAODs into a single pkl file')
	processed_pkl = [f for f in existing_files if f.endswith("_processed.pkl")][0]
	signal_data, background_data = split_sig_bkg(pkl_fname=processed_pkl, pkl_outdir=pkl_outdir)
	run_mva_workflow(signal_data=signal_data, background_data=background_data, dataset_name=dataset_name, output_dir=plot_outdir)

else:
	print('Welcome. Running full workflow...')
	processed_pkl = merge_mass_points(dataset_name, pkl_outdir)
	signal_data, background_data = split_sig_bkg(pkl_fname=str(processed_pkl), pkl_outdir=pkl_outdir)
	run_mva_workflow(signal_data=signal_data, background_data=background_data, dataset_name=dataset_name, output_dir=plot_outdir)