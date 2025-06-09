from traj_psd import traj_psd
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import time, random, sys, os
import pickle
sys.path.append(os.path.abspath("/work/bb1018/b380873/tropic_vis/"))
from plotting_utilities import traj_prefix

# The directory and trajectory output file from which to take the time series.
#basedir = '/work/bb1018/b380873/traj_output/test2h/'
#traj_file = basedir + 'traj_tst00000751_p001_trim.nc'

# The directory where the power spectral density figure should be saved.
basedir2 = '/work/bb1018/b380873/tropic_vis/output/'

# The directory where the trajectory output lives.
#basedir = '/scratch/b/b380873/traj_full51h_fast/'
basedir = '/work/bb1018/b380873/traj_output/traj_CLAMS-Tf_0V2M0A0R/'

# Lists to which we append the power spectral density and frequency values.
# If this boolean is True, then the power spectra for all trajectory files is recalculated
PSDcalc = True
file_num = 25
# We have <file_num> files and 3826 frequencies. I don't know where the latter number comes from.
PSD_ff_mean = np.zeros((file_num, 3826))
PSD_Pxx_mean = np.zeros((file_num, 3826))
if PSDcalc == True:
    PSD_ff = [[] for i in np.arange(file_num)]
    PSD_Pxx = [[] for i in np.arange(file_num)]
    for j in np.arange(1, file_num+1):
        print(j)
        # Read in the temperature from the trajectory file above.
        # Its dimension will be [time steps, trajectory id].
        #traj_file = basedir + 'traj_tst00000450_p' + file_prefix(j) + str(j) + '_trim.nc'
        #traj_T_series = xr.open_dataset(traj_file).t.values
        #traj_Tfluc_series = traj_T_series.T - np.nanmean(traj_T_series,axis=1)
        #traj_w_series = xr.open_dataset(traj_file).w_v.values

        traj_file = basedir + 'cirrus_tst00000450_p' + traj_prefix(j) + str(j) + '_trim_clams.nc'
        #traj_T_series = xr.open_dataset(traj_file)['T'].values
        traj_w_series = xr.open_dataset(traj_file)['w_v'].values

        # Store the PSDs for multiple temperature time series.
        freqs = int(traj_T_series.shape[0]/2 + 1)
        traj_id = traj_T_series.shape[1]
        #all_PSD = np.zeros((2,traj_id,freqs))

        # Iterate over the trajectories and save their PSDs.
        for i in np.arange(traj_id):
            # Generate an instance of Class traj_psd with temp = input temperature time series.
            #traj_obj = traj_psd(temp=traj_T_series[:7651,i])

            # Generate an instance of Class_traj_psd with temp = input vertical velocity series.
            traj_obj = traj_psd(temp=traj_w_series[:7651,i])

            # Calculate the power spectral density
            ff, Pxx, Nyq = traj_obj.calc_psd()

            # Add these values to the lists.
            PSD_ff[j-1].append(ff)
            PSD_Pxx[j-1].append(Pxx)
            #all_PSD[0,i] = ff
            #all_PSD[1,i] = Pxx

        PSD_ff_mean[j-1] = np.nanmean(PSD_ff[j-1],axis=0)
        PSD_Pxx_mean[j-1] = np.nanmean(PSD_Pxx[j-1],axis=0)

    np.save('../output/w_PSD_ff_0V2M0A0R_traj_Tf.npy', PSD_ff_mean)
    np.save('../output/w_PSD_Pxx_0V2M0A0R_traj_Tf.npy', PSD_Pxx_mean)

#else:
#   PSD_ff =

# Copying the plt_psd method from traj_psd.py
fs = 14
fig = plt.figure(figsize=(8,8))

# Plot a 10-subset of the individual trajectory PSDs
n = 200
random_indx = random.sample(np.arange(traj_id),n)
for i in np.arange(n):
    plt.plot(PSD_ff[0][i], PSD_Pxx[0][i], color='gray', linewidth=0.5)

# Plot the mean frequency versus the mean power spectral density.
#plt.plot(np.nanmean(PSD_ff[0],axis=0), np.nanmean(PSD_Pxx[0],axis=0),\
#         color='red', linewidth=2,label='online mean (24-s)')
plt.plot(PSD_ff_mean[0], PSD_Pxx_mean[0], color='red', linewidth=2, label='online mean (24-s)')

print(np.log10(np.nanmean(PSD_ff[0],axis=0)[2:]))
print(np.log10(np.nanmean(PSD_Pxx[0],axis=0)[2:]))

coef = np.polyfit(np.log10(np.nanmean(PSD_ff[0],axis=0)[2:]), np.log10(np.nanmean(PSD_Pxx[0],axis=0)[2:]),1)
print(coef)
xx = np.logspace(-4.5,-3.5) # subset of frequencies
plt.plot(xx, 10**coef[1]*xx**coef[0], linestyle='--', color='k', linewidth=2)
plt.text(0.3,0.44,"{:.2f}".format(coef[0]),fontsize=16,color='k',transform=plt.gca().transAxes)

# Plot the Nyquist frequency
plt.plot([Nyq, Nyq], [1e-10, 1e10],color='r',linewidth=1,linestyle='--')
plt.text(0.85,0.7,r'$f_{Nyq}$',fontsize=fs,color='r',transform=plt.gca().transAxes)

# Plot MACPEX
#plt.gca().plot([2e-5, 1e-4, 1e-3, 1e-2, 2e-2], [2e5, 2e4, 50, 2e-2, 2e-4],'b--',label='MACPEX')

#plt.legend(loc='upper center',fontsize=fs-2)
plt.gca().set_xscale('log')
plt.gca().set_yscale('log')

# Since the trajectories are 51 hours long, the minimum frequency is 1/(51*3600) s-1.
plt.gca().set_xlim([10**-5, 3e-2])
plt.gca().set_ylim([1e-7, 1e7])
#plt.gca().set_ylim([1,1e9])

plt.gca().set_xlabel(r'Frequency [s$^{-1}$]',fontsize=fs)
#plt.gca().set_ylabel(r'Power spectral density [K$^2$ s]',fontsize=fs)
#plt.gca().set_title('Temperature',fontsize=fs)
plt.gca().set_ylabel(r'Power spectral density [K$^2$ s$^{-1}$]',fontsize=fs)
plt.gca().set_title('Temperature PSD',fontsize=fs)
plt.gca().tick_params('both',labelsize=fs)
plt.gca().spines['top'].set_color('none')
plt.gca().spines['right'].set_color('none')

#fig.savefig('../output/traj51h_T_PSD_7651.pdf',bbox_inches='tight')
plt.show()
sys.exit()

# Smooth the temperature series with a Hanning window.
#traj_T_series_smooth = traj_obj.smooth(traj_T_series)

# Plotting the original and smoothed temperature series.
#fig = plt.figure(figsize=(10,6))
#plt.plot(traj_T_series,color='r',linewidth=0.75)
#plt.plot(traj_T_series_smooth,color='k',linewidth=1.25)
#plt.show()
