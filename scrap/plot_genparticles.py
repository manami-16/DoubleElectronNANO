#!/usr/bin/env python3
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import uproot
import awkward as ak
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

PLOT_OUTPUT_DIR = '/eos/user/m/mkanemur/WebEOS/WorkingPoint'

def plot_kinematics(output_dir: Path, arrays, mask, ambiguity=True):
    # vars_to_plot = ['GenPart_phi', 'GenPart_eta', 'GenPart_mass', 'GenPart_pt']
    vars_to_plot = ['Electron_genPartFlav']
    x_axis = [0, 1, 3, 4, 5, 15, 22]

    output_dir.mkdir(parents=True, exist_ok=True)

    for var in vars_to_plot:
        vals = ak.flatten(arrays[var][mask], axis=None)
        vals_np = ak.to_numpy(vals)

        plt.figure(figsize=(7, 5))
        bins = np.linspace(min(vals_np), max(vals_np), 50)
        # plt.hist(vals_np, bins=bins, histtype='step', linewidth=1.8)

        counts = np.array([(vals_np == k).sum() for k in x_axis])
        plt.bar(x_axis, counts)
        plt.xticks(x_axis)

        plt.xlabel(f'{var}')
        plt.ylabel('Count')
        plt.title(f'Gen-Matched PF Electrons: {var}')

        plt.tight_layout()
        fig_name = f'{var}_PF_ambiguity{ambiguity}.png'
        plt.savefig(output_dir/fig_name, dpi=300)
        plt.close()
        print(f'Saved {fig_name}')

    return None

def main():
    output_dir = PLOT_OUTPUT_DIR + 'HAHM_VBF'
    root_dirs = [
        '../BParkingNano/test/nohlt_maxDeltaR0p3_finalGenParticlesBPark_ambiguitiesTrue.root',
        '../BParkingNano/test/VBF_2024_versionB_maxDeltaR0p3_finalGenParticlesBPark.root',
    ]

    with uproot.open(root_dirs[1]) as f:
        tree = f['Events']
        print('Events are loaded')

    needed = ['GenPart_pdgId', 'GenPart_statusFlags', 'GenPart_status', 'GenPart_phi', 'GenPart_eta', 'GenPart_mass', 'GenPart_pt']
    needed += ['Electron_eta', 'Electron_phi', 'Electron_pt']
    needed += ['Electron_genPartFlav', 'Electron_isPF', 'Electron_isLowPt']
    arrays = tree.arrays(needed, library='ak')

    # pdg = arrays['GenPart_pdgId']
    # flags = arrays['GenPart_statusFlags']
    # status = arrays['GenPart_status']

    # pdg = arrays['Electron_pdgId']
    # flags = arrays['Electron_statusFlags']
    # status = arrays['Electron_status']

    # is_electron = (abs(pdg) == 11)
    # is_final = (status == 1)
    # is_prompt = (flags & (1 << 0)) != 0 ## flags are bits
    # mask = is_electron & is_final & is_prompt
    mask = arrays['Electron_isPF'] == True

    plot_kinematics(Path(output_dir), arrays, mask, ambiguity=True)

if __name__ == "__main__":
    main()