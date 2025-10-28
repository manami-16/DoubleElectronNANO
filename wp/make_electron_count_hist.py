
# For pT = [0, 10], JPsi 
## import root files
## root_path = '/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2023BPix/251002_142838/0000'

'''
For each reco ele, 
1. if Electron_genPartFlav == 1: signal
2. else: background

Then, plot a histogram (pT vs #ele) for sig and bkg
'''


import uproot
import awkward as ak
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

root_dirs = {
	'2022_2023_JPsiToEE_pth10toInf': 
	[
		'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2023BPix/251007_142912/0000/',
		'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130738/0000/'
	], 
	# '2022_2023_JPsiToEE_pth0to10_postBfix':
	# [
	# 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130707/0000/',
    # 	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2023BPix/251002_142838/0000/',
    # ]
}

def plot_pTs(dataset, flav_pts, total_entries, total_flav, output_dir, fig_name, plot_range=(0, 15), genPartFlav=0):
    pt_sig = ak.flatten(flav_pts[genPartFlav])
    pt_sig = np.array(pt_sig)

    # get pT for all bkg: genPartFlav != 0
    # pt_bkg = ak.flatten([flav_pts[f] for f in flav_pts if f != genPartFlav])
    pt_bkg = np.concatenate([np.array(ak.flatten(flav_pts[f])) for f in flav_pts if f != genPartFlav])

    if len(pt_sig) > 0 and len(pt_bkg) > 0:
        plt.figure(figsize=(7,5))
        bins = np.linspace(plot_range[0], plot_range[1], 50)
        plt.hist(pt_sig, bins=bins, range=plot_range, histtype='step', linewidth=1.5, label=f"Signal")
        plt.hist(pt_bkg, bins=bins, range=plot_range, histtype='step', linewidth=1.5, label=f"Background", color='orange')

        plt.xlabel("Electron $p_T$ [GeV]")
        plt.ylabel("Count")
        plt.title(f"Electron $p_T$ Distribution (genPartFlav = {genPartFlav})\n{dataset}")

      	## textbox at top left
        textstr = '\n'.join((
        	f'Signal -- ',
            f'Total events: {total_entries:,}',
            f'Electrons (flav={genPartFlav}): {total_flav[0]:,}',
            f'Avg pT (Sig): {np.mean(pt_sig):.2f} GeV',
            f'Avg pT (Bkg): {np.mean(pt_bkg):.2f} GeV',
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
    else:
    	print(len(pt_sig), len(pt_bkg))

def process_root(dataset, dirs):
	total_entries = 0
	genPartFlav = [1, 15, 22, 511, 0]
	total_flav = {f: 0 for f in genPartFlav}
	flav_pts = {f: [] for f in genPartFlav}

	for dir_path in dirs:
		dir_path = Path(dir_path)
		for root_path in dir_path.glob("*.root"):
			try:
				with uproot.open(root_path) as f:
					tree = f["Events;1"] if "Events;1" in f else f["Events"]

					if not any("Electron_" in key for key in tree.keys()):
						print(f'Skipping {root_path.name} -- no Electron branches')
						continue

					n_entries = tree.num_entries
					total_entries += n_entries

					electron_flav = tree['Electron_genPartFlav'].array(library="ak")
					electron_pt = tree['Electron_pt'].array(library='ak')

					for flav in genPartFlav:
					    mask = electron_flav == flav
					    total_flav[flav] += ak.sum(mask)
					    flav_pts[flav].extend(ak.to_list(electron_pt[mask]))

			except Exception as e:
				print(f"Could not read {root_path.name}: {e}")

	print("\n=== Summary ===")
	print(dataset)
	print(f"Total events across all files: {total_entries}")
	for flav in genPartFlav:
		print(f"Flav {flav}: {total_flav[flav]} electrons, pT count: {len(flav_pts[flav])}")

	## make a hist
	plot_arg = {'dataset': dataset, 
				'flav_pts': flav_pts, 
				'total_entries': total_entries, 
				'plot_range': (0, 15), 
				'total_flav': total_flav,
				'genPartFlav': 0,
				'output_dir': '/eos/user/m/mkanemur/WebEOS/WorkingPoint',
				'fig_name': f'{dataset}_v1.png'}
	plot_pTs(**plot_arg)


for dataset, dirs in root_dirs.items():
	print(f'Processing {dataset}...')
	process_root(dataset, dirs)



	