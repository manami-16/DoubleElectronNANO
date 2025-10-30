import uproot
import awkward as ak
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# source: https://github.com/cms-sw/cmssw/blob/c1b84d22fdf538675959e10095c0fc9b7c36cf6c/PhysicsTools/NanoAOD/plugins/CandMCMatchTableProducer.cc#L50-L57
flav_map = {0: 'unmatched', 
			1: 'prompt ele', 
			15: 'ele from prompt tau', 
			22: 'prompt photon', 
			5: 'ele from B', 
			4:'ele from c', 
			3: 'ele from light or unknown'}

root_dirs = {
	'2022_2023_JPsiToEE_pth10toInf': 
	[
		'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2023BPix/251007_142912/0000/',
		'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth10toInf_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130738/0000/'
	], 
	'2022_2023_JPsiToEE_pth0to10_postBfix':
	[
		'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2022postEE/251024_130707/0000/',
    	'/eos/cms/store/group/cmst3/group/xee/tree_v1/backgroundSamples/allnanoColl/JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8/crab_JPsiToEE_pth0to10_TuneCP5_13p6TeV_pythia8_2023BPix/251002_142838/0000/',
    ]
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

def plot_genPartFlav(dataset, total_flav, genPartFlav, total_entries, output_dir, fig_name):
    # Prepare data for plotting
    x_labels = [str(flav) for flav in genPartFlav]
    y_counts = [total_flav[flav] for flav in genPartFlav]

    plt.figure(figsize=(7, 5))
    bars = plt.bar(x_labels, y_counts, color='royalblue', alpha=0.7, edgecolor='black')

    # Annotate counts above bars
    for bar, count in zip(bars, y_counts):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{int(count)}',
                 ha='center', va='bottom', fontsize=9)

    plt.yscale('log')
    plt.xlabel("Electron_genPartFlav")
    plt.ylabel("Number of Electrons")
    plt.title(f"{dataset}: Electron_genPartFlav Distribution")

    # Add text box for total entries
    textstr = f"Total entries: {total_entries}\nTotal electrons: {sum(y_counts)}"
    plt.gca().text(
        0.97, 0.05, textstr, transform=plt.gca().transAxes,
        fontsize=10, verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', alpha=0.8)
    )

    plt.tight_layout()
    plt.savefig(f'{output_dir}/{fig_name}', dpi=300)
    plt.close()

def process_root(dataset, dirs):
	total_entries = 0
	genPartFlav = [1, 15, 22, 5, 4, 3, 0]
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
	## plot a hist of genPartFlav distribution
	plot_arg = {'dataset': dataset, 
				'total_flav': total_flav,
				'genPartFlav': genPartFlav,
				'total_entries': total_entries, 
				'output_dir': '/eos/user/m/mkanemur/WebEOS/WorkingPoint',
				'fig_name': f'genPartFlav_dist_{dataset}.png'}
	plot_genPartFlav(**plot_arg)

	## plot a hist of pT distribution for each genPartFlav
	# for flav in genPartFlav:
	# 	plot_arg['genPartFlav'] = flav
	# 	plot_arg['fig_name'] = f'flav{flav}_pT_dist_{dataset}.png'
	# 	plot_arg['flav_pts'] = flav_pts
	# 	print(f'Plotting genPartFlav={flav}...')
	# 	plot_pTs(**plot_arg)


for dataset, dirs in root_dirs.items():
	print(f'Processing {dataset}...')
	process_root(dataset, dirs)



	