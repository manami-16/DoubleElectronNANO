#!/usr/bin/env python3
"""
Standalone script (single input ROOT file):
- Reads ONE NanoAOD ROOT file that contains mixed events (data-like)
- Builds the same {"data": {...}, "total_entries": N} structure you already use
- Splits into "signal" and "background" by calling YOUR existing split function
- Makes ONLY the Electron_genPartFlav plot (no plot settings changed)

Usage:
  python standalone_single_root_split_and_genflav.py \
    --dataset VBF \
    --root /path/to/test.root \
    --pkl_outdir processed_test \
    --plot_outdir /eos/user/m/mkanemur/WebEOS/WorkingPoint
"""

import argparse
from pathlib import Path
import os
import sys
import pickle

import awkward as ak
import uproot
import yaml  # kept (you use it elsewhere; harmless)
import numpy as np  # kept (you use it elsewhere; harmless)

# Keep your src imports path convention
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.split_signal_background import split_sig_bkg
from src.Electron_Kinematics_Plotter import make_genflav_barplot

DEFAULT_PLOT_OUTDIR = "/eos/user/m/mkanemur/WebEOS/WorkingPoint"


def process_single_root(root_path: str, columns_of_interest: list[str]):
    """
    Read ONE ROOT file and return:
      {"data": {col: ak.Array}, "total_entries": int}
    Same style as your process_root(), just without directory scanning.
    """
    root_path = Path(root_path).expanduser().resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"ROOT file not found: {root_path}")
    if root_path.suffix != ".root":
        raise ValueError(f"Input is not a .root file: {root_path}")

    try:
        with uproot.open(root_path) as f:
            tree = f["Events;1"] if "Events;1" in f else f["Events"]

            available_keys = set(tree.keys())
            print(available_keys)
            missing = [col for col in columns_of_interest if col not in available_keys]
            if missing:
                raise KeyError(f"Missing branches in {root_path.name}: {missing}")

            n_entries = tree.num_entries
            arrays = tree.arrays(columns_of_interest, library="ak")

    except Exception as e:
        raise RuntimeError(f"Could not read {root_path}: {e}")

    data_dict = {col: arrays[col] for col in columns_of_interest}
    return {"data": data_dict, "total_entries": int(n_entries)}


def main():
    parser = argparse.ArgumentParser(
        description="Single ROOT -> processed.pkl -> split signal/background -> plot Electron_genPartFlav"
    )
    parser.add_argument("--dataset", default="VBF", choices=["VBF", "Inclusive", "JPsi"])
    # parser.add_argument("--root", required=True, help="Path to a single NanoAOD ROOT file.")

    parser.add_argument("--pkl_outdir", default="processed_test", help="Where to write intermediate pkls.")
    parser.add_argument("--plot_outdir", default=DEFAULT_PLOT_OUTDIR, help="Base directory for plot outputs.")

    args = parser.parse_args()

    dataset_matchup = {"VBF": "HAHM_VBF", "Inclusive": "HAHM_Inclusive", "JPsi": "JPsiToEE"}
    dataset_name = dataset_matchup[args.dataset]

    # Same branch sets you used in merge_mass_points()
    kinematics_cols = [
        "Electron_pt",
        "Electron_eta",
        "Electron_phi",
        "Electron_isLowPt",
        "Electron_isPF",
        "Electron_isPFoverlap",
    ]
    gen_cols = [
        "Electron_genPartFlav",
        "Electron_genPartIdx",
    ]
    id_cols = [
        "Electron_lowPtID_10Jun2025",
        "Electron_PFEleMvaID_Run3CustomJpsitoEEValue",
        "Electron_PFEleMvaID_Winter22NoIsoV1Value",
    ]

    columns_of_interest = kinematics_cols + gen_cols + id_cols if "HAHM" in dataset_name else kinematics_cols + gen_cols

    pkl_outdir = Path(args.pkl_outdir)
    pkl_outdir.mkdir(parents=True, exist_ok=True)

    # 1) Read the single ROOT file
    base = '../BParkingNano/production'
    # base = ''
    root = '/DoubleElectronNANO_Run3_2024_data_allNano_2025Oct13_test.root'
    root_path = base + root
    print(f"[{dataset_name}] Reading: {root_path}")
    processed_struct = process_single_root(root_path, columns_of_interest=columns_of_interest)
    print(f"[{dataset_name}] Entries read: {processed_struct['total_entries']}")

    # 2) Save it in the same *_processed.pkl style (but for a single "test" container)
    #    IMPORTANT: split_sig_bkg in your workflow expects a processed.pkl path.
    processed_pkl = pkl_outdir / f"test/{dataset_name}_single_processed.pkl"
    with open(processed_pkl, "wb") as f:
        pickle.dump(processed_struct, f)
    print(f"Saved -> {processed_pkl}")

    # 3) Split using your existing splitter (no reinvention)
    print("Splitting into signal/background using split_sig_bkg…")
    signal_data, background_data = split_sig_bkg(pkl_fname=str(processed_pkl), pkl_outdir=str(pkl_outdir))
    print("Split completed.")

    # 4) Plot Electron_genPartFlav (same call signature as your plot script)
    outdir = Path(f"{args.plot_outdir}/{dataset_name}/qual")
    outdir.mkdir(parents=True, exist_ok=True)

    print("Plotting Electron_genPartFlav distributions…")
    make_genflav_barplot(
        sig_data=signal_data,
        bkg_data=background_data,
        dataset_name=dataset_name,
        output_dir=outdir,
    )

    print("Done.")


if __name__ == "__main__":
    main()
