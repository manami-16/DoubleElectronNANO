import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path
import os, argparse

def get_signal_data(data):
	flav = data["Electron_genPartFlav"]
	signal_mask = (flav == 1) | (flav == 15) | (flav == 22)
	background_mask = ~signal_mask

	signal_data = {k: v[signal_mask] for k, v in data.items()}
	background_data = {k: v[background_mask] for k, v in data.items()}

	return signal_data, background_data

def split_lowpt_pf(data):
	lowpt_mask = data['Electron_isLowPt'] == True
	pf_mask    = data['Electron_isPF'] == True

	lowpt_data = {k: v[lowpt_mask] for k, v in data.items()}
	pf_data = {k: v[pf_mask] for k, v in data.items()}

	return lowpt_data, pf_data


def derive_mvaID_cut(data, id_type: str, threshold: int, pt_step=0.2):
	valid_ids = [
		'Electron_PFEleMvaID_Run3CustomJpsitoEEValue', 
		'Electron_PFEleMvaID_Winter22NoIsoV1Value', 
		'Electron_lowPtID_10Jun2025'
	]
	assert id_type in valid_ids, f'id_type must be one of: {valid_ids}'

	pt = data['Electron_pt']
	min_pt = np.floor(np.min(pt))

	## lowpt
	pt_bins = np.arange(min_pt, 10 + pt_step, pt_step)
	percentile_values = []

	## Note: we want to get the percentile from higher to lower pt, whereas numpy does from lower to higher
	upper_threshold = 100 - threshold

	# print(f'getting {threshold} percentile...')

	for i in range(len(pt_bins) - 1):
		lo, hi = pt_bins[i], pt_bins[i+1]
		pt_mask = (pt >= lo) & (pt < hi)

		cropped_data = {k: v[pt_mask] for k, v in data.items()}
		cropped_id = cropped_data[id_type]		

		## get percentile
		if len(cropped_id) == 0:
			percentile_values.append(None)
		else:
			perc = np.percentile(cropped_id, upper_threshold)
			percentile_values.append(perc)

	return pt_bins[:-1], percentile_values

def plot_mva(pt_bins, perc_vals, id_type, output_dir, dataset_name):
	
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	wps = perc_vals.keys()
	norm = plt.Normalize(min(wps), max(wps))
	cmap = plt.cm.cividis  # gradient colormap
	for wp in wps:
		color = cmap(norm(wp))
		plt.plot(pt_bins, perc_vals[wp]['mvaID'], label=f'WP{wp}', marker='*', color=color)

	legend_elements = []
	for wp in wps:
		color = cmap(norm(wp))
		legend_elements.append(
			Line2D([0], [0], color=color, lw=3, label=f"WP{wp}")  # no marker
		)

	# plt.yscale('log')
	plt.xlabel('pT')
	plt.ylabel('mvaID cut')
	plt.title(f"MVA ID: {id_type}\n{dataset_name}")
	plt.legend()
	plt.tight_layout()
	fig_name = f'mvaID_cut_{id_type}.png'
	save_path = output_dir/fig_name
	plt.savefig(save_path, dpi=300)
	plt.close()
	print(f'the plot was saved in {output_dir}/{fig_name}')


def get_efficiency(data: dict, id_type: str, percentile_values: list, pt_step=0.2, background=False):
	valid_ids = [
		'Electron_PFEleMvaID_Run3CustomJpsitoEEValue', 
		'Electron_PFEleMvaID_Winter22NoIsoV1Value', 
		'Electron_lowPtID_10Jun2025'
	]
	assert id_type in valid_ids, f'id_type must be one of: {valid_ids}'

	if background:
		pt = data[1]['Electron_pt']
		min_pt = np.floor(np.min(data[1]['Electron_pt']))
		mva = data[1][id_type]
	else:
		pt = data[0]['Electron_pt']
		min_pt = np.floor(np.min(pt))
		mva = data[0][id_type]

	pt_bins = np.arange(min_pt, 10 + pt_step, pt_step)
	efficiencies = []

	# Loop over the bins and calculate efficiency
	for i in range(len(pt_bins) - 1):
		lo, hi = pt_bins[i], pt_bins[i+1]
		cut_val = percentile_values[i]
		if cut_val is None:
			efficiencies.append(0)
			continue

		# mask electrons falling in pt range
		pt_mask = (pt >= lo) & (pt < hi)

		all_electrons = np.sum(pt_mask)
		if all_electrons == 0:
			efficiencies.append(0)  # avoid division by zero
			continue

		# those passing the MVA cut
		passed_electrons = np.sum(mva[pt_mask] > cut_val)
		eff = passed_electrons / all_electrons
		efficiencies.append(eff)
		
	return pt_bins[:-1], efficiencies

def plot_efficiency(pt_bins, wp_perc, id_type, output_dir, dataset_name, background=False):
	
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)
	
	wps = wp_perc.keys()
	
	# Set up coloring for different working points
	norm = plt.Normalize(min(wps), max(wps))
	cmap = plt.cm.cividis

	for wp in wps:
		color = cmap(norm(wp))
		
		if background:
			data = wp_perc[wp]['bkg_eff']
		else: 
			data = wp_perc[wp]['sig_eff']

		plt.plot(pt_bins, data, label=f'WP{wp}', marker='o', linestyle='-', color=color)

	plt.xlabel('Electron $p_T$ [GeV]')
	plt.ylabel('Efficiency')
	if background:
		plt.title(f"Background Electron ID Efficiency:\n{dataset_name} - {id_type}")
		fig_name = f'background_eff_{id_type}.png'
	else:
		plt.title(f"Signal Electron ID Efficiency:\n{dataset_name} - {id_type}")
		fig_name = f'signal_eff_{id_type}.png'

	plt.grid(True, which='both', linestyle='--', linewidth=0.5)
	plt.ylim(0, 1)

	# Create custom legend elements (optional, can also use plt.legend() directly)
	legend_elements = []
	for wp in wps:
		color = cmap(norm(wp))
		legend_elements.append(
			Line2D([0], [0], color=color, lw=2, marker='o', label=f"WP{wp}") 
		)

	plt.legend(handles=legend_elements, loc='best', title='Working Point')
	plt.tight_layout()
	
	save_path = output_dir/fig_name
	plt.savefig(save_path, dpi=300)
	plt.close()
	print(f'The efficiency plot was saved in {output_dir}/{fig_name} ')

def run_mva_workflow(signal_data, background_data, dataset_name, output_dir):
	sig_lowpt, sig_pf = split_lowpt_pf(signal_data)
	bkg_lowpt, bkg_pf = split_lowpt_pf(background_data)
	thresholds = list(np.arange(50, 95, 5))

	id_params = {
		'Electron_PFEleMvaID_Run3CustomJpsitoEEValue': [sig_pf, bkg_pf],
		'Electron_PFEleMvaID_Winter22NoIsoV1Value':     [sig_pf, bkg_pf], 
		'Electron_lowPtID_10Jun2025':                   [sig_lowpt, bkg_lowpt]
	}

	for id_type, datasets in id_params.items():
		print(f"\n*** {dataset_name}/{id_type} ***")

		wp_perc = {}
		for wp in thresholds:
			print(f"Deriving WP {wp}...")
			pt_bins, perc_vals = derive_mvaID_cut(
				data=datasets[0],
				id_type=id_type,
				threshold=wp,
				pt_step=0.2
			)
			wp_perc[wp] = {'mvaID': perc_vals}

			_, sig_eff = get_efficiency(datasets, id_type, perc_vals)
			_, bkg_eff = get_efficiency(datasets, id_type, perc_vals, background=True)
			wp_perc[wp]['sig_eff'] = sig_eff
			wp_perc[wp]['bkg_eff'] = bkg_eff

		plot_mva(pt_bins, wp_perc, id_type, output_dir, dataset_name)
		plot_efficiency(pt_bins, wp_perc, id_type, output_dir, dataset_name)
		plot_efficiency(pt_bins, wp_perc, id_type, output_dir, dataset_name, background=True)

	print("\nAll plots generated.")
