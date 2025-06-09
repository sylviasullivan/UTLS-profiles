# -*- coding: utf-8 -*-

import numpy as np
import scipy as sc
from scipy import signal

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx

class traj_psd(object):

    def __init__(self, temp = None, name = None, path = None, plotname = None):

        self.temp = [temp]

        self.dt_on = 24 # What is the resolution of the trajectories?
        self.window_length = 3
        self.Fnyq = list()
        self.Pxx = list()
        self.Pxx_smooth = list()
        self.f = list()

        self.name = [name]
        self.path = path
        if plotname != None:
            self.plotname = plotname
        else:
            self.plotname = self.name[0]

    def add_temp(self, temp, name = None):
        if self.temp[0] == None:
            self.temp = list()
            self.name = list()

        self.temp.append(temp)
        self.name.append(name)


    def smooth(self, x,window_len=11,window='hanning'):
        """smooth the data using a window with requested size.

        This method is based on the convolution of a scaled window with the signal.
        The signal is prepared by introducing reflected copies of the signal
        (with the window size) in both ends so that transient parts are minimized
        in the begining and end part of the output signal.

        input:
            x: the input signal
            window_len: the dimension of the smoothing window; should be an odd integer
            window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                flat window will produce a moving average smoothing.

        output:
            the smoothed signal

        example:

        t=linspace(-2,2,0.1)
        x=sin(t)+randn(len(t))*0.1
        y=smooth(x)

        see also:

        numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
        scipy.signal.lfilter

        TODO: the window parameter could be the window itself if an array instead of a string
        NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
        """

        if x.ndim != 1:
            raise ValueError("smooth only accepts 1 dimension arrays.")

        if x.size < window_len:
            raise ValueError("Input vector needs to be bigger than window size.")


        if window_len<3:
            return x


        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


        s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
        #print(len(s))
        if window == 'flat': #moving average
            w=np.ones(window_len,'d')
        else:
            w=eval('np.'+window+'(window_len)')  # >> sylvia_20201030 numpy -> np

        y=np.convolve(w/w.sum(),s,mode='valid')
        return y


    def calc_psd(self):
        for data_t in self.temp:

            if np.std(data_t)!= 0:
                data_t = data_t-np.mean(data_t)
                f, Pxx = signal.periodogram(data_t,window = np.hanning(len(data_t)),fs = 1./self.dt_on);
            self.f.append(f)
            self.Pxx.append(Pxx)
            self.Fnyq.append(1./(2.*self.dt_on))
            #Nf = floor(length(data_t)./2+1)

            #smoothing
            self.Pxx_smooth.append(self.smooth(Pxx, window_len = self.window_length, window = 'flat')[int((self.window_length-1)/2):-int((self.window_length-1)/2)])

        return self.f[0], self.Pxx_smooth[0], self.Fnyq
        #return None; >> sylvia_20201030, Outputting the frequencies and PSD directly now

    def plt_psd(self):

        fig = plt.figure()
        ax = fig.add_subplot(111)

        jet = cm = plt.get_cmap('jet')
        cNorm  = colors.Normalize(vmin=0, vmax=len(self.f)-1)
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)

        for ii, (ff, Ppxx, FFnyq, nn) in enumerate(zip(self.f, self.Pxx_smooth, self.Fnyq, self.name)):
            if len(self.f) > 1:
                colorVal = scalarMap.to_rgba(ii)
                ax.plot(ff, Ppxx, color=colorVal, label = nn)
            else:
                ax.plot(ff, Ppxx, c = 'b')

            ax.plot([FFnyq, FFnyq], [1e-10, 1e10], c = 'b')

        ax.set_xscale('log')
        ax.set_yscale('log')

        ax.set_xlim([2e-5, 3e-2])
        ax.set_ylim([1e-6, 1e6])

        # Plot Erika online trajs
        ax.plot([2e-5, 1e-4, 1e-3, 1e-2, 2e-2], [5e4, 2e3, 2, 5e-4, 1e-5], 'r--', label = 'on. trajs.')

        # Plot MACPEX
        ax.plot([2e-5, 1e-4, 1e-3, 1e-2, 2e-2], [2e5, 2e4, 50, 2e-2, 2e-4], 'g--', label = 'MACPEX')

        plt.legend(loc = 'upper right', fontsize = 9)
        ax.set_xlabel(r'frequency (s$^{-1}$)')
        ax.set_ylabel(r'PSD (K$^2$s)')
        if self.plotname != None:
            plt.title(self.plotname)

        if self.path != None and self.name != None:
            print('Hallo')
            #plt.savefig(self.path + '/' + self.plotname + '.png', dpi = 300, bbox_inches='tight')
            #plt.savefig(self.path + '/' + self.plotname + '.pdf', bbox_inches='tight')
        else:
            plt.show()
        plt.show()

        return None;


