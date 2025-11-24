import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
from pathlib import Path


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

def plot_id(sig_data: dict, bkg_data: dict, plot_vars: dict, dataset_name: str, output_dir: str, num_bins=50):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ## plot_vars = {ID_name: [(plot range), overflow bin]}

    for var_to_plot, plot_customization in plot_vars.items():
        
        plot_range = plot_customization[0]
        overflow_val = plot_customization[1]

        ## basic stats
        total_sig_ele = len(sig_data[var_to_plot])
        total_bkg_ele = len(bkg_data[var_to_plot])

        ## plot vars
        plt.figure(figsize=(7, 5))
        visible_bins = np.linspace(plot_range[0], plot_range[1], num_bins + 1)
        bin_width = visible_bins[1] - visible_bins[0]

        ## signal
        sig_overflow_mask = (sig_data[var_to_plot] == overflow_val)
        sig_in_range_mask = (sig_data[var_to_plot] != overflow_val)
        sig_overflow_count = np.sum(sig_overflow_mask)
        sig_in_range_data = sig_data[var_to_plot][sig_in_range_mask]
        sig_overflow_count = np.sum(sig_overflow_mask)

        sig_counts, _, _ = plt.hist(sig_in_range_data, bins=visible_bins, histtype='step', label='Signal', linewidth=1.8, color='orange')
        sig_overflow_x = plot_range[1] + bin_width / 2.0
        plt.bar(
            sig_overflow_x,                         # X-position (center of the new bin)
            sig_overflow_count,                     # Y-height (count)
            width=bin_width,                        # Same width as other bins
            align='center',                         # Center the bar at sig_overflow_x
            color='orange', 
            alpha=0.5,                              # Use alpha to distinguish the overflow bin
            edgecolor='orange',
            linewidth=1.8
        )

        ## background
        bkg_overflow_mask = (bkg_data[var_to_plot] == overflow_val)
        bkg_in_range_mask = (bkg_data[var_to_plot] != overflow_val)
        bkg_overflow_count = np.sum(bkg_overflow_mask)
        bkg_in_range_data = bkg_data[var_to_plot][bkg_in_range_mask]
        bkg_overflow_count = np.sum(bkg_overflow_mask)
        bkg_counts, _, _ = plt.hist(bkg_in_range_data, bins=visible_bins, histtype='step', label='Background', linewidth=1.8, color='blue')
        bkg_overflow_x = plot_range[1] + bin_width / 2.0
        plt.bar(
            bkg_overflow_x,                         # X-position (center of the new bin)
            bkg_overflow_count,                     # Y-height (count)
            width=bin_width,                        # Same width as other bins
            align='center',                         # Center the bar at sig_overflow_x
            color='blue', 
            alpha=0.5,                              # Use alpha to distinguish the overflow bin
            edgecolor='blue',
            linewidth=1.8
        )


        x_lim_max = plot_range[1] + bin_width * 2 # Extend past the overflow bin
        plt.xlim(plot_range[0], x_lim_max) 
        
        # Manually add a tick mark and label for the overflow bin
        current_ticks = plt.xticks()[0]
        current_labels = [f'{t:.1f}' for t in current_ticks]
        
        # Add the overflow tick and label at the overflow center
        plt.xticks(
            list(current_ticks) + [sig_overflow_x], 
            current_labels + [f'Overflow (> {plot_range[1]:.0f})'],
            rotation=20
        )

        plt.xlabel(var_to_plot)
        plt.ylabel("Count")
        plt.title(f"{var_to_plot} Distribution\n{dataset_name}")
        plt.legend(loc='upper right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()

        fig_name = f'{var_to_plot}.png'
        save_path = output_dir/fig_name
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f'the plot was saved in {output_dir}/{fig_name}')