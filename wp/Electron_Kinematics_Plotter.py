import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
from pathlib import Path
import os


def aggregate_data(data):
	'''
	Aggregates data regardless of mass point
	Returns the dictionaries of variables and ignores mass point. One dict for signal and another for background
	'''

	sig_arr_list, bkg_arr_list = {}, {}

	first_layer = list(data.keys())
	vars_list = list(data[first_layer[0]]['data']['signal'].keys())

	for var in vars_list:
		sig_arr_list[var] = []
		bkg_arr_list[var] = []

	for mass_point, mp_data in data.items():
		
		try:
			current_sig_data = mp_data['data']['signal']
			current_bkg_data = mp_data['data']['background']

			for var in vars_list:
				sig_arr = current_sig_data.get(var)
				bkg_arr = current_bkg_data.get(var)

				sig_arr_list[var].append(sig_arr)
				bkg_arr_list[var].append(bkg_arr)

		except KeyError as e:
			print(f'Skiping {mass_point} due to missing data structure key: {e}')
			continue

	aggregated_signal, aggregated_background = {}, {}

	for var in vars_list:
		if sig_arr_list[var]:
			aggregated_signal[var] = np.concatenate(sig_arr_list[var])
		if bkg_arr_list[var]:
			aggregated_background[var] = np.concatenate(bkg_arr_list[var])

	return aggregated_signal, aggregated_background



def plot_kinematics(sig_data: dict, bkg_data: dict, plot_vars: dict, dataset_name: str, output_dir: str):
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	## plot_vars = {'Electron_pt': (0, 20), 'Electron_eta': (-3, 3), 'Electron_phi': (-3, 3)}

	for var_to_plot, plot_range in plot_vars.items():

		## basic stats
		total_sig_ele = len(sig_data[var_to_plot])
		total_bkg_ele = len(bkg_data[var_to_plot])

		## plot vars
		plt.figure(figsize=(7, 5))
		bins = np.linspace(plot_range[0], plot_range[1], 50)

		plt.hist(sig_data[var_to_plot], bins=bins, histtype='step', label='Signal', linewidth=1.8, color='orange')
		plt.hist(bkg_data[var_to_plot], bins=bins, histtype='step', label='Background', linewidth=1.8, color='blue')

		plt.xlabel(var_to_plot)
		plt.ylabel("Count")
		plt.title(f"{var_to_plot} Distribution\n{dataset_name}")
		plt.legend(loc='upper right')

		textstr = '\n'.join((
			f'# Signal ele: {total_sig_ele:,}',
			f'# Background ele: {total_bkg_ele:,}',
			f'Avg (Sig): {np.mean(sig_data[var_to_plot]):.2f}',
			f'Avg (Bkg): {np.mean(bkg_data[var_to_plot]):.2f}',
		))
		plt.gca().text(
			0.97, 0.80, textstr, transform=plt.gca().transAxes,
			fontsize=10, verticalalignment='top', horizontalalignment='right',
			bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8)
		)

		plt.tight_layout()
		fig_name = f'{var_to_plot}.png'
		save_path = output_dir/fig_name
		plt.savefig(save_path, dpi=300)
		plt.close()
		print(f'the plot was saved in {output_dir}/{fig_name}')

def plot_id(sig_data: dict, bkg_data: dict, plot_vars: dict, dataset_name: str, output_dir: str, num_bins=50, log_scale=False):
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)
	sig_lowpt_mask = sig_data['Electron_isLowPt'] == True
	sig_pf_mask    = sig_data['Electron_isPF'] == True

	bkg_lowpt_mask = bkg_data['Electron_isLowPt'] == True
	bkg_pf_mask    = bkg_data['Electron_isPF'] == True

	## plot_vars = {ID_name: [(plot range), overflow bin]}
	def plot_one(var, sig_arr, bkg_arr, plot_range, overflow_val, label_suffix, log_scale=False):
		plt.figure(figsize=(7, 5))

		visible_bins = np.linspace(plot_range[0], plot_range[1], num_bins + 1)
		bin_width = visible_bins[1] - visible_bins[0]

		## Signal
		sig_overflow_mask = (sig_arr == overflow_val)
		sig_in_range_mask = (sig_arr != overflow_val)

		sig_overflow_count = np.sum(sig_overflow_mask)
		sig_in_range_data  = sig_arr[sig_in_range_mask]

		plt.hist(sig_in_range_data, bins=visible_bins, histtype='step', label=f"Signal", linewidth=1.8, color='orange', log=log_scale)
		sig_overflow_x = plot_range[1] + bin_width / 2
		plt.bar(sig_overflow_x, sig_overflow_count, width=bin_width, color='orange', alpha=0.5, edgecolor='orange', linewidth=1.8)

		# ------------------------
		## Backgrouund
		bkg_overflow_mask = (bkg_arr == overflow_val)
		bkg_in_range_mask = (bkg_arr != overflow_val)

		bkg_overflow_count = np.sum(bkg_overflow_mask)
		bkg_in_range_data  = bkg_arr[bkg_in_range_mask]

		plt.hist(bkg_in_range_data, bins=visible_bins, histtype='step', label=f"Background", linewidth=1.8, color='blue', log=log_scale)

		bkg_overflow_x = plot_range[1] + bin_width / 2
		plt.bar(bkg_overflow_x, bkg_overflow_count, width=bin_width, color='blue', alpha=0.5, edgecolor='blue', linewidth=1.8)

		# Axis formatting
		plt.xlim(plot_range[0], plot_range[1] + 2 * bin_width)

		current_ticks = plt.xticks()[0]
		current_labels = [f"{t:.1f}" for t in current_ticks]

		plt.xticks(list(current_ticks) + [sig_overflow_x], current_labels + [f"Overflow (={overflow_val})"],rotation=20)

		plt.xlabel(var)
		plt.ylabel("Count")
		plt.title(f"{var} Distribution {label_suffix}\n{dataset_name}")
		plt.legend(loc='upper right')
		plt.grid(axis='y', alpha=0.3)
		plt.tight_layout()

		fig_name = f"{var}_{label_suffix}.png"
		plt.savefig(output_dir / fig_name, dpi=300)
		plt.close()

		print(f"Saved: {fig_name}")

	for var, plot_customization in plot_vars.items():

		plot_range   = plot_customization[0]
		overflow_val = plot_customization[1]

		# LowPt-only
		plot_one(var, sig_data[var][sig_lowpt_mask], bkg_data[var][bkg_lowpt_mask], plot_range, overflow_val, log_scale=log_scale, label_suffix="LowPt")
		# PF-only
		plot_one(var, sig_data[var][sig_pf_mask], bkg_data[var][bkg_pf_mask], plot_range, overflow_val, log_scale=log_scale, label_suffix="PF")

def make_genflav_barplot(sig_data, bkg_data, dataset_name, output_dir):

	# Extract arrays
	sig_genpartflav = sig_data["Electron_genPartFlav"]
	bkg_genpartflav = bkg_data["Electron_genPartFlav"]

	sig_lowpt_mask = sig_data['Electron_isLowPt'] == True
	sig_pf_mask    = sig_data['Electron_isPF'] == True

	bkg_lowpt_mask = bkg_data['Electron_isLowPt'] == True
	bkg_pf_mask    = bkg_data['Electron_isPF'] == True

	lowpt_flav = np.concatenate([sig_genpartflav[sig_lowpt_mask], bkg_genpartflav[bkg_lowpt_mask]])
	pf_flav = np.concatenate([sig_genpartflav[sig_pf_mask], bkg_genpartflav[bkg_pf_mask]])

	def plot_one(flav_data, reco_type):
		all_flavs = np.unique(flav_data)
		counts = np.array([np.sum(flav_data == f) for f in all_flavs])

		print(f'{reco_type} ---- ')
		print(f'all flavors -- {all_flavs}')
		print(counts)

		# Plot
		x = np.arange(len(all_flavs))
		plt.figure(figsize=(10, 6))
		bars = plt.bar(all_flavs, counts, log=True)
		# Add counts on top of bars
		for bar, count in zip(bars, counts):
			height = bar.get_height()
			plt.text(
				bar.get_x() + bar.get_width() / 2,
				height,
				f"{count:,}",   # formatted with commas
				ha="center",
				va="bottom",
				fontsize=10
			)

		plt.xticks(x, all_flavs)
		plt.xlabel(f"Electron_genPartFlav - {reco_type}")
		plt.ylabel("Number of electrons")
		plt.title(f"{dataset_name}: Electron_genPartFlav distribution {(reco_type)}")

		os.makedirs(output_dir, exist_ok=True)
		outfile = os.path.join(output_dir, f"{dataset_name}_{reco_type}__genPartFlav.png")

		plt.tight_layout()
		plt.savefig(outfile)
		plt.close()

		print(f"Plot is saved at {outfile}")

	## plot lowpt and pf 
	plot_one(lowpt_flav, 'LowPT')
	plot_one(pf_flav, 'PF')






