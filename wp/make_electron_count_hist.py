import uproot
import awkward as ak
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import os

# source: https://github.com/cms-sw/cmssw/blob/c1b84d22fdf538675959e10095c0fc9b7c36cf6c/PhysicsTools/NanoAOD/plugins/CandMCMatchTableProducer.cc#L50-L57
flav_map = {0: 'unmatched', 
			1: 'prompt ele', 
			15: 'ele from prompt tau', 
			22: 'prompt photon', 
			5: 'ele from B', 
			4:'ele from c', 
			3: 'ele from light or unknown'}

plot_output_dir = '/eos/user/m/mkanemur/WebEOS/WorkingPoint'

root_dirs = {
	# '2022_2023_JPsiToEE_pth10toInf': 
	# [
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2023BPix/251007_142912/0000/',
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130738/0000/'
	# ], 
	'2022_2023_JPsiToEE_pth0to10_postBfix':
	[
		'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130707/0000/',
		'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2023BPix/251002_142838/0000/',
	],
	# 'INCL_HAHM_13p6TeV_M6p5':
	# [
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/signalSamples/HAHM_DarkPhoton_13p6TeV_Nov2024/allnanoColl/HAHM_DarkPhoton_13p6TeV_Nov2024/crab_HAHM_13p6TeV_M6p5/251010_171612/0000/'
	# ]
}

def plot_pTs(dataset, flav_pts, total_entries, total_flav, output_dir, fig_name, plot_range=(0, 15), genPartFlav=0):
	pt_sig = ak.flatten(flav_pts[genPartFlav])
	pt_sig = np.array(pt_sig)

	# get pT for all bkg: genPartFlav != 0
	pt_bkg = np.concatenate([np.array(ak.flatten(flav_pts[f])) for f in flav_pts if f != genPartFlav])

	if len(pt_sig) > 0:
		plt.figure(figsize=(7,5))
		bins = np.linspace(plot_range[0], plot_range[1], 50)
		plt.hist(pt_sig, bins=bins, range=plot_range, histtype='step', linewidth=1.5, label=f"Signal", color='orange')
		# plt.hist(pt_bkg, bins=bins, range=plot_range, histtype='step', linewidth=1.5, label=f"Background", color='blue')
		# plt.legend(loc='upper right')

		plt.xlabel("Electron $p_T$ [GeV]")
		plt.ylabel("Count")
		plt.title(f"Electron $p_T$ Distribution (genPartFlav = {genPartFlav})\n{dataset}")

		## textbox at top left
		textstr = '\n'.join((
			f'Signal -- ',
			f'Total events: {total_entries:,}',
			f'Electrons (flav={genPartFlav}): {total_flav[genPartFlav]:,}',
			f'Avg pT (Sig): {np.mean(pt_sig):.2f} GeV',
			# f'Avg pT (Bkg): {np.mean(pt_bkg):.2f} GeV',
		))

		plt.gca().text(
			0.97, 0.80, textstr, transform=plt.gca().transAxes,
			fontsize=10, verticalalignment='top', horizontalalignment='right',
			bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8)
		)

		plt.tight_layout()
		plt.savefig(f'{output_dir}/{fig_name}', dpi=300)
		plt.close()
		print(f'the plot was saved in {output_dir}/{fig_name}')
		print('==='*5)
	else:
		print(len(pt_sig), len(pt_bkg))

def plot_genPartFlav(dataset, dataset_name, fig_name):
	genPartFlav_list = [1, 15, 22, 5, 4, 3, 0]
	genPartStatusFlag_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

	genPartFlav_data = np.array(ak.flatten(dataset['Electron_genPartFlav']))
	pt_data = np.array(ak.flatten(dataset['Electron_pt']))
	genPartStatusFlag_data = np.array(ak.flatten(dataset['GenPart_statusFlags']))

	total_flav = {f: 0 for f in genPartFlav_list}
	flav_pts = {f: [] for f in genPartFlav_list}
	unexpected_flav = set()
	total_status_flag = {f: 0 for f in genPartStatusFlag_list}
	statusFlag_pts = {f: [] for f in genPartFlav_list}

	## count the electrons and store pt
	for flav, pt in zip(genPartFlav_data, pt_data):
		if flav in total_flav:
			total_flav[flav] += 1
			flav_pts[flav].append(pt)
		else:
			unexpected_flav.add(flav)

	##Print the countings
	print(f'Electron counts per genPartFlav for {dataset_name}:')
	for flav in genPartFlav_list:
		print(f"	Electron_genPartFlav {flav}: {total_flav[flav]}")
	if unexpected_flav:
		print(f'	Unexpected genPartFlav found: {sorted(unexpected_flav)}')

	## ==================================================================== ##
	## plotting hist of genPartFlav
	x_labels = [str(f) for f in genPartFlav_list]
	y_counts = [total_flav[f] for f in genPartFlav_list]

	plt.figure(figsize=(8,5))
	bars = plt.bar(x_labels, y_counts, color='royalblue', alpha=0.7, edgecolor='black')

	for bar, count in zip(bars, y_counts):
		plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{int(count)}',
				 ha='center', va='bottom', fontsize=9)

	plt.yscale('log')
	plt.xlabel("Electron_genPartFlav")
	plt.ylabel("Number of Electrons")
	plt.title(f"{dataset_name}: Electron_genPartFlav Distribution")

	total_entries = len(genPartFlav_data)
	textstr = f"Total entries: {total_entries}\nTotal electrons: {sum(y_counts)}"
	plt.gca().text(
		0.97, 0.05, textstr, transform=plt.gca().transAxes,
		fontsize=10, verticalalignment='top', horizontalalignment='right',
		bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8)
	)

	plt.tight_layout()
	output_dir = f'{plot_output_dir}/{dataset_name}/{fig_name}'
	os.makedirs(f'{plot_output_dir}/{dataset_name}', exist_ok=True)	
	plt.savefig(f'{output_dir}_Electron_genPartFlavcounts.png', dpi=300)
	plt.close()
	print(f'==== the plot was saved in {output_dir}/{fig_name}_pt.png')

	## ==================================================================== ##
	## plotting hist of genPartStatusFlag
	unique_flags, counts = np.unique(genPartStatusFlag_data, return_counts=True)
	y_counts = [counts[np.where(unique_flags == f)[0][0]] if f in unique_flags else 0 for f in genPartStatusFlag_list]
	x_labels = [str(f) for f in genPartStatusFlag_list]

	plt.figure(figsize=(8,5))
	bars = plt.bar(x_labels, y_counts, color='royalblue', alpha=0.7, edgecolor='black')

	for bar, count in zip(bars, y_counts):
		plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{int(count)}',
				 ha='center', va='bottom', fontsize=9)

	plt.yscale('log')
	plt.xlabel("genPartStatusFlag")
	plt.ylabel("Number of Electrons")
	plt.title(f"{dataset_name}: genPartStatusFlag Distribution")

	total_entries = len(genPartStatusFlag_data)
	textstr = f"Total entries: {total_entries}\nTotal electrons: {sum(y_counts)}"
	plt.gca().text(
		0.97, 0.05, textstr, transform=plt.gca().transAxes,
		fontsize=10, verticalalignment='top', horizontalalignment='right',
		bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8)
	)

	plt.tight_layout()
	output_dir = f'{plot_output_dir}/{dataset_name}/{fig_name}'
	os.makedirs(f'{plot_output_dir}/{dataset_name}', exist_ok=True)	
	plt.savefig(f'{output_dir}_genPartStatusFlag.png', dpi=300)
	plt.close()
	print(f'==== the plot was saved in {output_dir}/{fig_name}_genPartStatusFlag.png')

	## ==================================================================== ##
	## plotting pt for each genPartFlav
	plt.figure(figsize=(8,5))
	# bins = np.linspace(0, max(pt_data)*1.1, 50)
	bins = (0, 15)
	for flav in genPartFlav_list:
		if len(flav_pts[flav]) > 0:
			plt.hist(flav_pts[flav], bins=bins, histtype='step', linewidth=1.5, alpha=0.6, label=f'genPartFlav {flav}')

	plt.xlabel("Electron_pt [GeV]")
	plt.ylabel("Number of Electrons")
	plt.title(f"{dataset_name}: Electron_pt Distribution by genPartFlav")
	plt.legend()
	plt.yscale('log')
	plt.tight_layout()
	plt.savefig(f'{output_dir}_Electron_pt.png', dpi=300)
	plt.close()
	print(f'==== the plot was saved in {output_dir}/{fig_name}_pt.png')

	return None
def process_root(dirs, columns_of_interest:list):
	total_entries = 0
	collected_arrays = {col: [] for col in columns_of_interest}

	for dir_path in dirs:
		dir_path = Path(dir_path)
		for root_path in dir_path.glob("*.root"):
			try:
				with uproot.open(root_path) as f:
					tree = f["Events;1"] if "Events;1" in f else f["Events"]

					available_keys = tree.keys()
					missing = [col for col in columns_of_interest if col not in available_keys]
					if missing:
						print(f"Skipping {root_path.name} -- missing columns: {missing}")
						continue

					n_entries = tree.num_entries
					total_entries += n_entries


					arrays = tree.arrays(columns_of_interest, library='ak')
					for col in columns_of_interest:
						collected_arrays[col].append(arrays[col])

			except Exception as e:
				print(f"Could not read {root_path.name}: {e}")

	data_dict = {col: ak.concatenate(collected_arrays[col]) if collected_arrays[col] else ak.Array([]) for col in columns_of_interest}
	return data_dict, total_entries

def make_plot(data_1, data_2, label_1:str, label_2:str, title:str, plot_range:tuple, xaxis_label:str, dataset_name:str, fig_name:str):
	processed_data_1 = ak.flatten(data_1)
	processed_data_1 = np.array(processed_data_1)
	processed_data_2 = ak.flatten(data_2)
	processed_data_2 = np.array(processed_data_2)

	plt.figure(figsize=(7,5))
	bins = np.linspace(plot_range[0], plot_range[1], 50)

	plt.hist(processed_data_1, bins=bins, range=plot_range, histtype='step', linewidth=1.5, label=label_1, color='orange')
	plt.hist(processed_data_2, bins=bins, range=plot_range, histtype='step', linewidth=1.5, label=label_2, color='blue')

	plt.xlabel(xaxis_label)
	plt.ylabel('Count')
	
	plt.title(f"{title}\n{dataset_name}")
	plt.legend()
	plt.tight_layout()
	
	output_dir = f'{plot_output_dir}/{dataset_name}/{fig_name}'
	os.makedirs(f'{plot_output_dir}/{dataset_name}', exist_ok=True)		
	plt.savefig(output_dir, dpi=300)
	plt.close()
	print(f'the plot was saved in {output_dir}')

	return None

def main():
	## get the data of your interest
	data_dict = {}
	columns_of_interest = ['Electron_pt', 'Electron_eta', 'Electron_phi', 'Electron_genPartFlav', 'Electron_isLowPt', 'Electron_isPF', 'Electron_genPartIdx',
							'GenPart_statusFlags', 'GenPart_pdgId', 'GenPart_status']

	for dataset, dirs in root_dirs.items():
		print(f'Processing {dataset}...')
		data_dict[dataset], _ = process_root(dirs=dirs, columns_of_interest=columns_of_interest)

	## plot pT distribution (lowPT vs PF)
	for dataset in list(data_dict.keys()):
		data = data_dict[dataset]

		lowpt_mask, pf_mask = data['Electron_isLowPt'] == 1, data['Electron_isPF'] == 1
		lowPT_ele = data['Electron_pt'][lowpt_mask]
		PF_ele = data['Electron_pt'][pf_mask]

		plot_arg = {'data_1': lowPT_ele,
					'data_2': PF_ele,
					'label_1': 'lowPT',
					'label_2': 'PF',
					'title': 'pT distribution of lowPT and PF electrons',
					'plot_range': (0, 30),
					'xaxis_label': 'pT [GeV]',
					'dataset_name': dataset}
		if 'Inf' in dataset:
			plot_arg['fig_name'] = 'pt_10ToInf_pT_dist_lowPT_PF'
		else:
			plot_arg['fig_name'] = 'pt_0To10_pT_dist_lowPT_PF'
		make_plot(**plot_arg)

	## plot #electron for each genPartFlav
	for dataset in list(data_dict.keys()):
		data = data_dict[dataset]
		if 'Inf' in dataset:
			fig_name = 'pt_10ToInf_pT_dist_lowPT_PF'
		else:
			fig_name = 'pt_0To10_pT_dist_lowPT_PF'
		plot_genPartFlav(dataset=data, dataset_name=dataset, fig_name=fig_name)

if __name__ == "__main__":
	main()


	