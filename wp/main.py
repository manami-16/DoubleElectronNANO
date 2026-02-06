import uproot
import awkward as ak
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import os
import yaml
import process_root
import subprocess
import pickle
from Electron_Kinematics_Plotter import aggregate_data, plot_kinematics, plot_id, make_genflav_barplot
import WP_derivation

# source: https://github.com/cms-sw/cmssw/blob/c1b84d22fdf538675959e10095c0fc9b7c36cf6c/PhysicsTools/NanoAOD/plugins/CandMCMatchTableProducer.cc#L50-L57
flav_map = {0: 'unmatched', 
			1: 'prompt ele', 
			15: 'ele from prompt tau', 
			22: 'prompt photon', 
			5: 'ele from B', 
			4:'ele from c', 
			3: 'ele from light or unknown'}

PLOT_OUTPUT_DIR = '/eos/user/m/mkanemur/WebEOS/WorkingPoint'

def main():
	dataset_name = 'HAHM_VBF'
	signal_path = f"processed/{dataset_name}_signal.pkl"
	background_path = f"processed/{dataset_name}_background.pkl"

	with open(signal_path, "rb") as f:
		signal_data = pickle.load(signal_path)
	with open(background_path, 'rb') as f:
		background_data = pickle.load(background_path)
	
			

	# make_genflav_barplot(signal_data, background_path, dataset_name, f'{plot_output_dir}/{dataset_name}')



	# WP_derivation.main(signal_data, background_path)
	
	####### Plot kinematic vars #######


	####### Plot kinematic vars #######
	# vars_to_plot = {'Electron_pt': (0, 20), 'Electron_eta': (-3, 3), 'Electron_phi': (-3, 3)}
	vars_to_plot = {'Electron_phi': (-np.pi, np.pi)}
	# vars_to_plot = {
	# 				 'Electron_lowPtID_10Jun2025': (-10, 10), 
	# 				'Electron_PFEleMvaID_Run3CustomJpsitoEEValue': (-10, 10),
	# 				'Electron_PFEleMvaID_Winter22NoIsoV1Value': (-1, 1)
	# 				}
	params = {
		'sig_data': aggregated_signal_data, 
		'bkg_data': aggregated_background_data, 
		'plot_vars': vars_to_plot, 
		'dataset_name': dataset_name, 
		'output_dir': f'{plot_output_dir}/{dataset_name}/qual/'
	}
	plot_kinematics(**params)

	####### plot IDs #######
	# vars_to_plot = {
	# 'Electron_lowPtID_10Jun2025': [(-20, 20), -1000], 
	# 				'Electron_PFEleMvaID_Run3CustomJpsitoEEValue': [(-11, 11), 20], 
	# 				'Electron_PFEleMvaID_Winter22NoIsoV1Value': [(-1.2, 1.2), 20]}
	# params = {
	# 	'sig_data_path': 'processed/HAHM_VBF_signal.pkl', 
	# 	'bkg_data_path': 'processed/HAHM_VBF_background.pkl', 
	# 	'plot_vars': vars_to_plot, 
	# 	'dataset_name': 'HAHM_VBF', 
	# 	'output_dir': f'{PLOT_OUTPUT_DIR}/HAHM_VBF',
	# 	'log_scale': True
	# }
	# plot_id(**params)

if __name__ == "__main__":
	main()


	