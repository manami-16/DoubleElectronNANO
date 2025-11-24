import pickle
from pathlib import Path
import awkward as ak
import uproot
import subprocess
import yaml

def process_root(root_dir: str, columns_of_interest:list):
	root_dir = Path(root_dir)

	total_entries = 0
	collected_arrays = {col: [] for col in columns_of_interest}

	root_files = list(root_dir.glob("*.root"))
	if not root_files:
		print(f"No ROOT files found in directory: {root_dir}")
		return 0, {col: ak.Array([]) for col in columns_of_interest}

	for root_path in root_files:
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

	data_dict = {col: ak.concatenate(collected_arrays[col]) if collected_arrays[col] else ak.Array([]) 
	for col in columns_of_interest}

	return {"data": data_dict, "total_entries": total_entries}

def main():
	sample_yaml = 'sample.yaml'
	plot_output_dir = '/eos/user/m/mkanemur/WebEOS/WorkingPoint'
	output_dir = Path('processed')
	output_dir.mkdir(exist_ok=True)

	with open(sample_yaml, 'r') as file:
		datasets = yaml.safe_load(file)

	## get the data of your interest
	all_data, all_totals = {}, {}
	kinematics_cols = ['Electron_pt', 'Electron_eta', 'Electron_phi', 'Electron_isLowPt', 'Electron_isPF', 'Electron_isPFoverlap']
	gen_cols = ['Electron_genPartFlav','Electron_genPartIdx', 'GenPart_statusFlags', 'GenPart_pdgId', 'GenPart_status']
	id_cols = ['Electron_lowPtID_10Jun2025', 'Electron_PFEleMvaID_Run3CustomJpsitoEEValue', 'Electron_PFEleMvaID_Winter22NoIsoV1Value']

	columns_of_interest = kinematics_cols + gen_cols + id_cols

	for dataset_name, mass_points, in datasets.items():
		print(f"Processing dataset category: {dataset_name}")

		dataset_output = {}
		for mass_entry in mass_points: ## mass_point = [{M1: ...}, {M2:...}, ...]
			for mass_point, dirs in mass_entry.items():

				total_events_sum = 0
				merged_data_dict = None

				for dir_path in dirs:
					result = process_root(root_dir=dir_path, columns_of_interest=columns_of_interest)

					total_events_sum += result['total_entries']
					merged_data_dict = result['data']

				dataset_output[mass_point] = {"data": merged_data_dict, "total_entries": total_events_sum}

				print(f"\tDone: {mass_point} — {total_events_sum} total events")

		## save one pkl per dataset
		output_path = output_dir/f"{dataset_name}_processed.pkl"
		with open(output_path, "wb") as f:
			pickle.dump(dataset_output, f)
		print(f'Saved -> {output_path}')

if __name__ == "__main__":
	main()



