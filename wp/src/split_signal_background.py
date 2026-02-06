import awkward as ak
import pickle
import numpy as np

def get_col_of_interest(dataset_name):
	kinematics_cols = ['Electron_pt', 'Electron_eta', 'Electron_phi', 'Electron_isLowPt', 'Electron_isPF', 'Electron_isPFoverlap']
	gen_cols = ['Electron_genPartFlav','Electron_genPartIdx', 'GenPart_statusFlags', 'GenPart_pdgId', 'GenPart_status']
	id_cols = ['Electron_lowPtID_10Jun2025', 'Electron_PFEleMvaID_Run3CustomJpsitoEEValue', 'Electron_PFEleMvaID_Winter22NoIsoV1Value']

	if 'HAHM' in dataset_name:
		columns_of_interest = kinematics_cols + gen_cols + id_cols
	elif 'JPsiToEE' in dataset_name:
		columns_of_interest = kinematics_cols
		columns_of_interest.append('Electron_genPartFlav')

	return columns_of_interest

def aggregate_data(data, HAHM=True):
	'''
	Aggregates data regardless of mass point
	Returns the dictionaries of variables and ignores mass point. One dict for signal and another for background
	'''

	sig_arr_list, bkg_arr_list = {}, {}

	if HAHM:
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

	else:
		vars_list = list(data['data']['signal'].keys())
		for var in vars_list:
			sig_arr_list[var] = []
			bkg_arr_list[var] = []

		try:
			current_sig_data = data['data']['signal']
			current_bkg_data = data['data']['background']

			for var in vars_list:
				sig_arr = current_sig_data.get(var)
				bkg_arr = current_bkg_data.get(var)

				sig_arr_list[var].append(sig_arr)
				bkg_arr_list[var].append(bkg_arr)

		except KeyError as e:
			print(f'Skiping due to missing data structure key: {e}')

	aggregated_signal, aggregated_background = {}, {}

	for var in vars_list:
		if sig_arr_list[var]:
			aggregated_signal[var] = np.concatenate(sig_arr_list[var])
		if bkg_arr_list[var]:
			aggregated_background[var] = np.concatenate(bkg_arr_list[var])

	return aggregated_signal, aggregated_background

def split_sig_bkg(pkl_fname, pkl_outdir):
	with open(pkl_fname, 'rb') as file:
		data = pickle.load(file)
	dataset_name = pkl_fname.split('/')[1].split('.')[0].replace('_processed', '')  ## i.e., HAHM_VBF
	columns_of_interest = get_col_of_interest(dataset_name)

	if 'HAHM' in pkl_fname:
		## goal: get a signal/bkg where Electron_genPartFlav == 1, 12, 22
		mass_points = list(data.keys())  ## M1, M3p1, etc
		for mass_point in mass_points:
			electrons = {var: data[mass_point]['data'].get(var) for var in columns_of_interest}

			if electrons['Electron_pt'] is None or electrons['Electron_genPartFlav'] is None:
				print(f'Missing Electron_pt or Electron_genPartFlav in {mass_point}')
				continue

			## set up signal and background
			flav = electrons['Electron_genPartFlav']
			signal_mask = (flav == 1) | (flav == 15) | (flav == 22)
			bkg_mask = ~signal_mask
			
			signal, background = {}, {}

			if 'VBF' in pkl_fname:
				for var, arr in electrons.items():
					# bad = ak.num(arr) != ak.num(electrons['Electron_genPartFlav'])
					sig = arr[signal_mask]
					bkg = arr[bkg_mask]

					sig_np = ak.to_numpy(ak.flatten(sig))
					bkg_np = ak.to_numpy(ak.flatten(bkg))
					signal[var] = sig_np
					background[var] = bkg_np

			else:
				match = ak.num(flav) == ak.num(electrons["Electron_pt"])
				for var, arr in electrons.items():
					# case 1: branch matches flav exactly → apply signal mask
					if ak.all(ak.num(arr) == ak.num(flav)):
						sig = arr[signal_mask]
						bkg = arr[~signal_mask]

						signal[var] = ak.to_numpy(ak.flatten(sig))
						background[var] = ak.to_numpy(ak.flatten(bkg))

					# case 2: branch does NOT match → cannot apply flavor mask
					else:
						# keep all values, unclassified
						signal[var] = ak.to_numpy(ak.flatten(arr[match]))     # only keep events with usable flavor
						background[var] = ak.to_numpy(ak.flatten(arr[~match]))  # or leave empty

			## Each variable is stored as np array
			data[mass_point]['data']['signal'] = signal
			data[mass_point]['data']['background'] = background
			print(f"{mass_point}: signal = {len(signal['Electron_pt'])}, background = {len(background['Electron_pt'])}")
		aggregated_signal_data, aggregated_background_data = aggregate_data(data, HAHM=True)

	else:
		electrons = {var: data['data'].get(var) for var in columns_of_interest}

		if electrons['Electron_pt'] is None or electrons['Electron_genPartFlav'] is None:
			print('Missing Electron_pt or Electron_genPartFlav')

		## set up signal and background
		flav = electrons['Electron_genPartFlav']
		signal_mask = (flav == 1) | (flav == 15) | (flav == 22)
		bkg_mask = ~signal_mask
		
		signal, background = {}, {}

		for var, arr in electrons.items():
			if arr is None:
				print("None column:", var)
			sig = arr[signal_mask]
			bkg = arr[bkg_mask]

			sig_np = ak.to_numpy(ak.flatten(sig))
			bkg_np = ak.to_numpy(ak.flatten(bkg))
			signal[var] = sig_np
			background[var] = bkg_np

		## Each variable is stored as np array
		data['data']['signal'] = signal
		data['data']['background'] = background
		print(f"signal = {len(signal['Electron_pt'])}, background = {len(background['Electron_pt'])}")
		aggregated_signal_data, aggregated_background_data = aggregate_data(data, HAHM=False)

	## Save signal / background files as pkl
	output_path = f"{pkl_outdir}/{dataset_name}_signal.pkl"
	with open(output_path, "wb") as f:
		pickle.dump(aggregated_signal_data, f)
		print(f'Saved signal data in {output_path}')

	output_path = f"{pkl_outdir}/{dataset_name}_background.pkl"
	with open(output_path, "wb") as f:
		pickle.dump(aggregated_background_data, f)
		print(f'Saved background data in {output_path}')

	return aggregated_signal_data, aggregated_background_data

	
