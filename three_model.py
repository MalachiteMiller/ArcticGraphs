import plot_tools as pt
import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import re

# Relative or absolute path to input files.
canoe_file = 'models/CanOE2_NAA-EPM032_365h_19840101_19841231_ptrc_T.nc'
pisces_file = 'models/PISCES_NAA-EPM032_365h_19840101_19841231_ptrc_T.nc'
cmoc_file = 'models/CMOC_NAA-EPM032_365h_19840101_19931231_ptrc_T.nc'

# Names of the variables to compare.
canoe_vars = ['alk']
pisces_cmoc_vars = ['alk']  # PISCES and CMOC should be the same....

# Target depth in metres to plot.
target_depth = 10

# If you want to control the scale of the colour bar enter a number here. To auto config, leave as [].
upper_colour_bar = []
lower_colour_bar = []
# Number of discrete colors in the color bar, default None
color_bar_steps = None

# Set to True to get a 2x3 plot with anomalies. If True, the data will be regrided to 1x1 degrees.
anomaly = True

# Variable name to compare to, must be  present in OBS.
anom_vars = ['asd']

# Set the scale of the colour bar of the anomalies.
anom_upper_colour_bar = []
anom_lower_colour_bar = []

# Dictionary relating the names of observation data to the files they come from.
OBS = {
    # 'NO3': 'arctic_obs/OA2013_2x2_ORCA1_zlevels_clean.nc',
    # 'O2': 'arctic_obs/OA2013_2x2_ORCA1_zlevels_clean.nc',
    # 'TAlk': 'arctic_obs/GLODAP_1_2_merged_2x2_ORCA1_zlevels_clean.nc',
    # 'DIC': 'arctic_obs/GLODAP_1_2_merged_2x2_ORCA1_zlevels_clean.nc',
    # 'salt': 'arctic_obs/OA2013_2x2_ORCA1_zlevels_clean.nc',
    # 'temp': 'arctic_obs/OA2013_2x2_ORCA1_zlevels_clean.nc',
}

if os.path.isdir('./plots'):
    print("plots directory exists...overwriting")
    shutil.rmtree('./plots')
else:
    print("Creating ./plots/ ...")

os.mkdir('./plots')

for i in range(0, len(canoe_vars)):
    if anomaly:
        data1, units1, lon, lat, depths, dimensions, years1 = pt.load_remap(canoe_file, canoe_vars[i], 'canoe')
        data2, units2, _, _, _, _, years2 = pt.load_remap(pisces_file, pisces_cmoc_vars[i], 'pisces')
        data3, units3, _, _, _, _, years3 = pt.load_remap(cmoc_file, pisces_cmoc_vars[i], 'cmoc')
        try:
            anom_data, _, _, _, _, _, _ = pt.load_remap(OBS[anom_vars[i]], anom_vars[i])
        except KeyError:
            print 'Anomaly variable used must be in the obs dictionary, \'{}\' is not.'.format(anom_vars[i])
            continue
        if anom_data.shape == 4:
            anom_data = anom_data[0, :, :, :]

    else:
        data1, units1, lon, lat, depths, dimensions, years1 = pt.load(canoe_file, canoe_vars[i], 'canoe')
        data2, units2, _, _, _, _, years2 = pt.load(pisces_file, pisces_cmoc_vars[i], 'pisces')
        data3, units3, _, _, _, _, years3 = pt.load(cmoc_file, pisces_cmoc_vars[i], 'cmoc')

    depth_index = (np.abs(depths - target_depth)).argmin()  # Find the nearest depth to the one requested
    plot_depth = depths[depth_index]

    pargs = pt.default_pcolor_args(data1, color_bar_steps)
    pargs2 = pt.default_pcolor_args(data2)
    pargs3 = pt.default_pcolor_args(data3)
    if not upper_colour_bar:
        pargs['vmax'] = max(pargs['vmax'], pargs2['vmax'], pargs3['vmax'])
    else:
        pargs['vmax'] = upper_colour_bar[0]
    if not lower_colour_bar:
        pargs['vmin'] = min(pargs['vmin'], pargs2['vmin'], pargs3['vmin'])
    else:
        pargs['vmin'] = lower_colour_bar[0]

    if anomaly:
        anom_pargs = pt.default_pcolor_args(data1 - anom_data, True)
        pargs5 = pt.default_pcolor_args(data2 - anom_data, True)
        pargs6 = pt.default_pcolor_args(data3 - anom_data, True)
        if not anom_upper_colour_bar:
            anom_pargs['vmax'] = max(anom_pargs['vmax'], pargs5['vmax'], pargs6['vmax'])
        else:
            anom_pargs['vmax'] = anom_upper_colour_bar[0]
        if not anom_lower_colour_bar:
            anom_pargs['vmin'] = min(anom_pargs['vmin'], pargs5['vmin'], pargs6['vmin'])
        else:
            anom_pargs['vmin'] = anom_lower_colour_bar[0]

    print 'plotting at {:.2f}m'.format(plot_depth)

    if len(data1.shape) == 4:
        data1 = data1[:, depth_index, :, :]
        data1_multiyear = True
    elif len(data1.shape) == 3:
        data1 = data1[depth_index, :, :]
        data1_multiyear = False
    else:
        raise ValueError('Malformed input data, CanOE')

    if len(data2.shape) == 4:
        data2 = data2[:, depth_index, :, :]
        data2_multiyear = True
    elif len(data2.shape) == 3:
        data2 = data2[depth_index, :, :]
        data2_multiyear = False
    else:
        raise ValueError('Malformed input data, PISCES')

    if len(data3.shape) == 4:
        data3 = data3[:, depth_index, :, :]
        data3_multiyear = True
    elif len(data3.shape) == 3:
        data3 = data3[depth_index, :, :]
        data3_multiyear = False
    else:
        raise ValueError('Malformed input data, CMOC')

    if anomaly:
        anom_data = anom_data[depth_index, :, :]

    print 'Plotting graph of {}...'.format(canoe_vars[i])
    year_list = list(set(years1).intersection(years2, years3))  # Find the years common to all data sets,
    for j in range(0, len(year_list)):                          # Plot each one
        print 'Plotting graph {} of {}...'.format(j + 1, len(year_list))

        if anomaly:
            fig, axes = plt.subplots(3, 2, figsize=(19, 24))
        else:
            fig, axes = plt.subplots(3, 1, figsize=(8, 24))

        ax_args1 = {'title': re.findall('/\S+?_', canoe_file)[0][1:-1],
                    }
        ax_args2 = {'title': re.findall('/\S+?_', pisces_file)[0][1:-1],
                    }
        ax_args3 = {'title': re.findall('/\S+?_', cmoc_file)[0][1:-1],
                    }
        if anomaly:
            ax_args4 = {'title': '{} anomaly'.format(re.findall('/\S+?_', canoe_file)[0][1:-1],),
                        }
            ax_args5 = {'title': '{} anomaly'.format(re.findall('/\S+?_', pisces_file)[0][1:-1],),
                        }
            ax_args6 = {'title': '{} anomaly'.format(re.findall('/\S+?_', cmoc_file)[0][1:-1],),
                        }
        try:
            if not anomaly:
                axes[0].text(0, .984, canoe_vars[i] + '\n' + str(year_list[j]), fontsize=12, transform=axes[0].transAxes)
                if data1_multiyear:
                    year_index = years1.index(year_list[j])
                    pt.npolar_map(lon, lat, data1[year_index, :, :], ax_args1, pargs, units1, plot_depth, axes[0],
                                  remap=False)
                else:
                    pt.npolar_map(lon, lat, data1, ax_args1, pargs, units1, plot_depth, axes[0], remap=False)

                axes[1].text(0, .984, canoe_vars[i] + '\n' + str(year_list[j]), fontsize=12, transform=axes[1].transAxes)
                if data2_multiyear:
                    year_index = years2.index(year_list[j])
                    pt.npolar_map(lon, lat, data2[year_index, :, :], ax_args2, pargs, units2, plot_depth, axes[1],
                                  remap=False)
                else:
                    pt.npolar_map(lon, lat, data2, ax_args2, pargs, units2, plot_depth, axes[1], remap=False)

                axes[2].text(0, .984, canoe_vars[i] + '\n' + str(year_list[j]), fontsize=12, transform=axes[2].transAxes)
                if data3_multiyear:
                    year_index = years3.index(year_list[j])
                    pt.npolar_map(lon, lat, data3[year_index, :, :], ax_args3, pargs, units3, plot_depth, axes[2],
                                  remap=False)
                else:
                    pt.npolar_map(lon, lat, data3, ax_args3, pargs, units3, plot_depth, axes[2], remap=False)
            else:

                axes[0, 0].text(0, .984, canoe_vars[i] + '\n' + str(year_list[j]), fontsize=12,
                                transform=axes[0, 0].transAxes)
                axes[0, 1].text(0, .984, canoe_vars[i] + '\n' + str(year_list[j]), fontsize=12,
                                transform=axes[0, 1].transAxes)
                if data1_multiyear:
                    year_index = years1.index(year_list[j])
                    pt.npolar_map(lon, lat, data1[year_index, :, :], ax_args1, pargs, units1, plot_depth, axes[0, 0])
                    pt.npolar_map(lon, lat, data1[year_index, :, :] - anom_data, ax_args4, anom_pargs, units1,
                                  plot_depth, axes[0, 1], True)
                else:
                    pt.npolar_map(lon, lat, data1, ax_args1, pargs, units1, plot_depth, axes[0, 0])
                    pt.npolar_map(lon, lat, data1 - anom_data, ax_args4, anom_pargs, units1, plot_depth, axes[0, 1],
                                  True)

                axes[1, 0].text(0, .984, canoe_vars[i] + '\n' + str(year_list[j]), fontsize=12,
                                transform=axes[1, 0].transAxes)
                axes[1, 1].text(0, .984, canoe_vars[i] + '\n' + str(year_list[j]), fontsize=12,
                                transform=axes[1, 1].transAxes)
                if data2_multiyear:
                    year_index = years2.index(year_list[j])
                    pt.npolar_map(lon, lat, data2[year_index, :, :], ax_args2, pargs, units2, plot_depth, axes[1, 0])
                    pt.npolar_map(lon, lat, data2[year_index, :, :] - anom_data, ax_args5, anom_pargs, units2,
                                  plot_depth, axes[1, 1], True)
                else:
                    pt.npolar_map(lon, lat, data2, ax_args2, pargs, units2, plot_depth, axes[1, 0])
                    pt.npolar_map(lon, lat, data2 - anom_data, ax_args5, anom_pargs, units2, plot_depth, axes[1, 1],
                                  True)

                axes[2, 0].text(0, .984, canoe_vars[i] + '\n' + str(year_list[j]), fontsize=12,
                                transform=axes[2, 0].transAxes)
                axes[2, 1].text(0, .984, canoe_vars[i] + '\n' + str(year_list[j]), fontsize=12,
                                transform=axes[2, 1].transAxes)
                if data3_multiyear:
                    year_index = years3.index(year_list[j])
                    pt.npolar_map(lon, lat, data3[year_index, :, :], ax_args3, pargs, units3, plot_depth, axes[2, 0])
                    pt.npolar_map(lon, lat, data3[year_index, :, :] - anom_data, ax_args6, anom_pargs, units3,
                                  plot_depth, axes[2, 1], True)
                else:
                    pt.npolar_map(lon, lat, data3, ax_args3, pargs, units3, plot_depth, axes[2, 0])
                    pt.npolar_map(lon, lat, data3 - anom_data, ax_args6, anom_pargs, units3, plot_depth, axes[2, 1],
                                  True)

            if len(year_list) > 1:
                plot_name = 'plots/{}_{:.2f}_three_model{}_{}.pdf'.format(canoe_vars[i], plot_depth,
                                                                          '_anom' if anomaly else '', year_list[j])
            else:
                plot_name = 'plots/{}_{:.2f}_three_model{}.pdf'.format(canoe_vars[i], plot_depth,
                                                                       '_anom' if anomaly else '')
            plt.savefig(plot_name, bbox_inches='tight')
        except ValueError:
            print 'Graph number {} of {} has no data, skipping...'.format(j + 1, canoe_vars[i])
            raise
        plt.close(fig)
