import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import sys
import seaborn as sns

# The directory and trajectory output file from which to take the
# temperature series.
basedir = '/work/bb1018/b380873/traj_output/test2h/'
traj_file = basedir + 'traj_tst00000751_p001_trim.nc'

# Read in the temperature from the trajectory file above.
# Its dimension will be [time steps, trajectory id].
traj_T_series = xr.open_dataset(traj_file).t.values
traj_w_series = xr.open_dataset(traj_file).w_v.values

deltaT = np.diff(traj_T_series,axis=0).flatten()
deltaw = np.diff(traj_w_series,axis=0).flatten()

print(deltaT.min(),deltaT.mean(),deltaT.max())
print(deltaw.min(),deltaw.mean(),deltaw.max())


fs = 13
fig, ax = plt.subplots(nrows=1,ncols=2,figsize=(10,5))
sns.set_style("whitegrid")
sns.distplot(deltaT,bins=np.linspace(-0.1,0.1,100),ax=ax[0])
ax[0].plot([deltaT.mean(),deltaT.mean()],[0,45],color='red',linewidth=2)
ax[0].set_xlabel(r'traj $\Delta$T [K]',fontsize=fs)
ax[0].set_ylabel('Counts',fontsize=fs)
ax[0].tick_params('both',labelsize=fs)
ax[0].set_xlim([-0.1,0.1])
ax[0].text(0.1,0.9,'mean',color='red',weight='bold',transform=ax[0].transAxes)

sns.distplot(deltaw,bins=np.linspace(-0.04,0.04,100),ax=ax[1],kde_kws={'gridsize':1000,'bw':0.00001})
ax[1].plot([deltaw.mean(),deltaw.mean()],[0,200],color='red',linewidth=2)
ax[1].set_xlabel(r'traj $\Delta$w [m s$^{-1}$]',fontsize=fs)
ax[1].tick_params('both',labelsize=fs)
ax[1].set_xlim([-0.02,0.02])

fig.savefig('../output/deltaT-deltaw-pdf.pdf',bbox_inches='tight')
plt.show()
sys.exit()

# Store the PSDs for multiple temperature time series.
freqs = int(traj_T_series.shape[0]/2 + 1)
traj_id = traj_T_series.shape[1]
all_PSD = np.zeros((2,traj_id,freqs))

# The directory where the power spectral density figure should be saved.
basedir2 = '/work/bb1018/b380873/tropic_vis/output/'

# Iterate over the trajectories and save their PSDs.
for i in np.arange(traj_id):
    # Generate an instance of Class traj_psd with temp = input temperature time series.
    #traj_obj = traj_psd(temp=traj_T_series[:,i])

    # Generate an instance of Class_traj_psd with temp = input vertical velocity series.
    traj_obj = traj_psd(temp=traj_w_series[:,i])

    # Calculate the power spectral density
    ff, Pxx, Nyq = traj_obj.calc_psd()

    # Store it in the all_PSD array.
    all_PSD[0,i] = ff
    all_PSD[1,i] = Pxx

# Copying the plt_psd method from traj_psd.py
fs = 14
fig = plt.figure(figsize=(8,8))

# Plot a 100-subset of the individual trajectory PSDs
n = 100
random_indx = random.sample(np.arange(traj_id),n)
for i in np.arange(n):
    plt.plot(all_PSD[0,i], all_PSD[1,i], color='gray', linewidth=0.5)

# Plot the mean frequency versus the mean power spectral density.
plt.plot(np.nanmean(all_PSD[0],axis=0), np.nanmean(all_PSD[1],axis=0),\
         color='red', linewidth=2,label='online mean (24-s)')

# Plot the Nyquist frequency
plt.plot([Nyq, Nyq], [1e-10, 1e10],color='r',linewidth=1,linestyle='--')
plt.text(0.85,0.7,r'$f_{Nyq}$',fontsize=fs,color='r',transform=plt.gca().transAxes)

# Plot MACPEX
#plt.gca().plot([2e-5, 1e-4, 1e-3, 1e-2, 2e-2], [2e5, 2e4, 50, 2e-2, 2e-4],'b--',label='MACPEX')

#plt.legend(loc='upper center',fontsize=fs-2)
plt.gca().set_xscale('log')
plt.gca().set_yscale('log')

# Since the trajectories are 2 hours long, the minimum frequency is 1/(2*3600) s-1.
plt.gca().set_xlim([1/(2.*3600.), 3e-2])
plt.gca().set_ylim([1e-7, 1e5])

plt.gca().set_xlabel(r'Frequency [s$^{-1}$]',fontsize=fs)
#plt.gca().set_ylabel(r'Power spectral density [K$^2$ s]',fontsize=fs)
#plt.gca().set_title('Temperature',fontsize=fs)
plt.gca().set_ylabel(r'Power spectral density [m$^2$ s$^{-1}$]',fontsize=fs)
plt.gca().set_title('Vertical velocity',fontsize=fs)
plt.gca().tick_params('both',labelsize=fs)

fig.savefig('../output/traj2htest_w_PSD.pdf',bbox_inches='tight')
plt.show()

# Smooth the temperature series with a Hanning window.
#traj_T_series_smooth = traj_obj.smooth(traj_T_series)

# Plotting the original and smoothed temperature series.
#fig = plt.figure(figsize=(10,6))
#plt.plot(traj_T_series,color='r',linewidth=0.75)
#plt.plot(traj_T_series_smooth,color='k',linewidth=1.25)
#plt.show()
