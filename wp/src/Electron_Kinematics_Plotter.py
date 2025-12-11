import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os

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

def plot_id(sig_data, bkg_data, plot_vars: list, dataset_name: str, output_dir: str, num_bins=50, log_scale=False):
	output_dir = Path(output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	## Set up masks
	sig_lowpt_mask = sig_data['Electron_isLowPt'] == True
	sig_pf_mask    = sig_data['Electron_isPF'] == True

	bkg_lowpt_mask = bkg_data['Electron_isLowPt'] == True
	bkg_pf_mask    = bkg_data['Electron_isPF'] == True

	# sig_eta_mask = (abs(sig_data['Electron_eta']) > 1.5) & (abs(sig_data['Electron_eta']) < 2.5)  # eta restriction: get only endcap 
	# bkg_eta_mask = (abs(bkg_data['Electron_eta']) > 1.5) & (abs(bkg_data['Electron_eta']) < 2.5)  # eta restriction: get only endcap 

	## plot_vars = {ID_name: [(plot range), overflow bin]}
	def plot_one(var, sig_arr, bkg_arr, label_suffix, log_scale=False):
		plt.figure(figsize=(7, 5))

		## Set up xaxis of the plots
		data_min = min(np.min(sig_arr), np.min(bkg_arr))
		data_max = max(np.max(sig_arr), np.max(bkg_arr))
		xmin = np.floor(data_min)
		xmax = np.ceil(data_max)
		visible_bins = np.linspace(xmin, xmax, num_bins + 1)

		## Signal
		plt.hist(sig_arr, bins=visible_bins, histtype='step', label="Signal", linewidth=1.8, color='orange', log=log_scale)

		## Backgrouund
		plt.hist(bkg_arr, bins=visible_bins, histtype='step', label="Background", linewidth=1.8, color='blue', log=log_scale)

		plt.xlim(xmin, xmax)
		plt.xlabel(var)
		plt.ylabel("Count")
		plt.title(f"{var} Dist {label_suffix}\n{dataset_name}")
		plt.legend(loc='upper right')
		plt.grid(axis='y', alpha=0.3)
		plt.tight_layout()

		fig_name = f"{var}_{label_suffix}.png"
		plt.savefig(output_dir / fig_name, dpi=300)
		plt.close()

		print(f"Saved: {fig_name}")

	for var in plot_vars:
		if 'lowPt' in var:
			# LowPt-only
			plot_one(var, sig_data[var][sig_lowpt_mask], bkg_data[var][bkg_lowpt_mask], log_scale=log_scale, label_suffix="LowPt")
		elif 'PF' in var:
			# PF-only
			plot_one(var, sig_data[var][sig_pf_mask], bkg_data[var][bkg_pf_mask], log_scale=log_scale, label_suffix="PF")

def make_genflav_barplot(sig_data, bkg_data, dataset_name, output_dir):
	genpartflav_flags = [0, 1, 15, 22, 5, 4, 3]
	# Extract arrays
	sig_genpartflav = sig_data["Electron_genPartFlav"]
	bkg_genpartflav = bkg_data["Electron_genPartFlav"]

	# sig_lowpt_mask = sig_data['Electron_isLowPt'] == True
	# sig_pf_mask    = sig_data['Electron_isPF'] == True

	# bkg_lowpt_mask = bkg_data['Electron_isLowPt'] == True
	# bkg_pf_mask    = bkg_data['Electron_isPF'] == True

	flav = np.concatenate([sig_genpartflav, bkg_genpartflav])
	# lowpt_flav = np.concatenate([sig_genpartflav[sig_lowpt_mask], bkg_genpartflav[bkg_lowpt_mask]])
	# pf_flav = np.concatenate([sig_genpartflav[sig_pf_mask], bkg_genpartflav[bkg_pf_mask]])

	def plot_one(flav_data):
		x_labels = sorted(genpartflav_flags)

		counts_dict = {flag: 0 for flag in x_labels} 
		unique_flavs, counts = np.unique(flav_data, return_counts=True)
		
		# Update the dictionary with actual counts
		for flav, count in zip(unique_flavs, counts):
			if flav in counts_dict:
				counts_dict[flav] = count
		
		# Convert the dictionary values back to a list/array in the correct order
		final_counts = np.array([counts_dict[flag] for flag in x_labels])

		# Plot
		x_pos = np.arange(len(x_labels))
		plt.figure(figsize=(10, 6))
		bars = plt.bar(x_pos, final_counts, log=True)
		
		# Add counts on top of bars
		for bar, count in zip(bars, final_counts):
			height = bar.get_height()
			
			# Only display the count text if the height is not zero
			if height > 0:
				plt.text(
					bar.get_x() + bar.get_width() / 2,
					height,
					f"{count:,}",  # formatted with commas
					ha="center",
					va="bottom",
					fontsize=10
				)

		# Set the ticks to use the correct integer flavor flags
		plt.xticks(x_pos, x_labels)
		plt.xlabel("Electron_genPartFlav")
		plt.ylabel("Number of electrons")
		plt.title(f"{dataset_name}: Electron_genPartFlav distribution")

		os.makedirs(output_dir, exist_ok=True)
		outfile = os.path.join(output_dir, f"{dataset_name}_genPartFlav.png")

		plt.tight_layout()
		plt.savefig(outfile)
		plt.close()

		print(f"Plot is saved at {outfile}")

	## plot lowpt and pf 
	plot_one(flav)
