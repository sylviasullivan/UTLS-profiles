# Define the colors and linestyles to use for different simulations
# Color-blind colormap used from https://www.nature.com/articles/nmeth.1618/figures/2
def sim_colors():
    return {'0V1M0A0R': (0.88, 0.3686, 0), '0V2M0A0R': (0, 0.4470, 0.698), #0.8353
            '0V2M0A1R': (0.9411, 0.8941, 0.2588), '0V2M1A0R': (0, 0.6196, 0.4509),
            '0V2M1A1R': (0.9019, 0.6235, 0), '1V1M0A0R': (0.88, 0.3686, 0),
            '1V2M0A0R': (0, 0.4470, 0.698), '1V2M0A1R': (0.9411, 0.8941, 0.2588),
            '1V2M1A0R': (0, 0.6196, 0.4509), '1V2M1A1R': (0.9019, 0.6235, 0),
            'MPI': (0.8, 0.4745, 0.6549), 'ERA': (0, 0, 0),
            'CloudSat': (0.3373, 0.7058, 0.9137), 'CERES': (0.3373, 0.7058, 0.9137),
            'POSIDON': (0.3373, 0.7058, 0.9137), 'ATTREX': (0, 0, 0)}


def sim_ls():
    return {'1V': '-', '0V': '--', 'CE': '-', 'ER': '-'}


# Generally define a file prefix for a set of 0s of length <n>
def general_prefix(j, n):
    # How many zeros do we need?
    m = n - len(str(j))
    return '0' * m + str(j)

# Read in the ICON simulation output files from the file number
# This function prepends the appropriate number of zeros
def file_prefix(j):
    if len(str(j)) == 1:
       return '000'
    elif len(str(j)) == 2:
       return '00'
    elif len(str(j)) == 3:
       return '0'
    else:
       return 'Inappropriate length of input to file_prefix'


# Read in the trajectory module output files from the file number
# This function prepends the appropriate number of zeros
def traj_prefix(j):
    if len(str(j)) == 1:
       return '00'
    elif len(str(j)) == 2:
       return '0'
    else:
       return 'Inappropriate length of input to traj_prefix'


# Helper function to - you guessed it - make sexy axes for generic values
def sexy_axes(ax,fs):
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.tick_params('both',labelsize=fs,rotation=45)


# Helper function to make sexy axes for pressure levels
def sexy_axes2(ax, fs, ylab):
    ax.set_ylim([50,800])
    ax.set_yscale('log')
    ax.set_yticks([800,500,300,100])
    ax.set_yticklabels(['800','500','300','100'])
    if ylab == True:
        ax.set_ylabel('Pressure [hPa]',fontsize=fs)
    ax.invert_yaxis()

    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.tick_params('both',labelsize=fs,rotation=45)


# Define a function to convert radians to degrees.
def rad2deg(x):
    import numpy as np
    return x*180/np.pi


# More helper functions
# Pulling this from the following stackoverflow
# https://stackoverflow.com/questions/30030328/correct-placement-of-colorbar-relative-to-geo-axes-cartopy
def resize_colorbar(event):
    #ax = plt.gca()
    #fig = plt.gcf()
    #cbar_ax = fig.add_axes([0, 0, 0.1, 0.1])
    plt.draw()
    posn = ax.get_position()
    # left, bottom, width, height
    cbar_ax.set_position([posn.x0 + posn.width + 0.01, posn.y0 - 0.018,
                          0.025, posn.height + 0.03])
    #cbar_ax.tick_params(labelsize=fs)


# A solution to plot seaborn jointplots in different subplots of a matplotlib fig
# https://stackoverflow.com/questions/35042255/how-to-plot-multiple-seaborn-jointplot-in-subplot
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import numpy as np
import xarray as xr

class SeabornFig2Grid():

    def __init__(self, seaborngrid, fig,  subplot_spec):
        self.fig = fig
        self.sg = seaborngrid
        self.subplot = subplot_spec
        if isinstance(self.sg, sns.axisgrid.FacetGrid) or \
            isinstance(self.sg, sns.axisgrid.PairGrid):
            self._movegrid()
        elif isinstance(self.sg, sns.axisgrid.JointGrid):
            self._movejointgrid()
        self._finalize()

    def _movegrid(self):
        """ Move PairGrid or Facetgrid """
        self._resize()
        n = self.sg.axes.shape[0]
        m = self.sg.axes.shape[1]
        self.subgrid = gridspec.GridSpecFromSubplotSpec(n,m, subplot_spec=self.subplot)
        for i in range(n):
            for j in range(m):
                self._moveaxes(self.sg.axes[i,j], self.subgrid[i,j])

    def _movejointgrid(self):
        """ Move Jointgrid """
        h= self.sg.ax_joint.get_position().height
        h2= self.sg.ax_marg_x.get_position().height
        r = int(np.round(h/h2))
        self._resize()
        self.subgrid = gridspec.GridSpecFromSubplotSpec(r+1,r+1, subplot_spec=self.subplot)

        self._moveaxes(self.sg.ax_joint, self.subgrid[1:, :-1])
        self._moveaxes(self.sg.ax_marg_x, self.subgrid[0, :-1])
        self._moveaxes(self.sg.ax_marg_y, self.subgrid[1:, -1])

    def _moveaxes(self, ax, gs):
        #https://stackoverflow.com/a/46906599/4124317
        ax.remove()
        ax.tick_params('both',labelsize=18)
        ax.figure=self.fig
        self.fig.axes.append(ax)
        self.fig.add_axes(ax)
        ax._subplotspec = gs
        ax.set_position(gs.get_position(self.fig))
        ax.set_subplotspec(gs)

    def _finalize(self):
        plt.close(self.sg.fig)
        self.fig.canvas.mpl_connect("resize_event", self._resize)
        self.fig.canvas.draw()

    def _resize(self, evt=None):
        self.sg.fig.set_size_inches(self.fig.get_size_inches())


# Function to create a boxplot from 5 percentiles, taken from
# https://stackoverflow.com/questions/27214537/is-it-possible-to-draw-a-matplotlib-boxplot-given-the-percentile-values-instead
# sylvia made n_box and pos function inputs
def customized_box_plot(percentiles, axes, n_box, pos, redraw = True, *args, **kwargs):
    """
    Generates a customized boxplot based on the given percentile values
    """

    box_plot = axes.boxplot([[-9, -4, 2, 4, 9],]*n_box, positions=pos, *args, **kwargs)
    # Creates len(percentiles) no of box plots

    min_y, max_y = float('inf'), -float('inf')

    for box_no, (q1_start,
                 q2_start,
                 q3_start,
                 q4_start,
                 q4_end,
                 fliers_xy) in enumerate(percentiles):

        # Lower cap
        box_plot['caps'][2*box_no].set_ydata([q1_start, q1_start])
        # xdata is determined by the width of the box plot

        # Lower whiskers
        box_plot['whiskers'][2*box_no].set_ydata([q1_start, q2_start])

        # Higher cap
        box_plot['caps'][2*box_no + 1].set_ydata([q4_end, q4_end])

        # Higher whiskers
        box_plot['whiskers'][2*box_no + 1].set_ydata([q4_start, q4_end])

        # Box
        box_plot['boxes'][box_no].set_ydata([q2_start,
                                             q2_start,
                                             q4_start,
                                             q4_start,
                                             q2_start])

        # Median
        box_plot['medians'][box_no].set_ydata([q3_start, q3_start])

        # Outliers
        if fliers_xy is not None and len(fliers_xy[0]) != 0:
            # If outliers exist
            box_plot['fliers'][box_no].set(xdata = fliers_xy[0],
                                           ydata = fliers_xy[1])

            min_y = min(q1_start, min_y, fliers_xy[1].min())
            max_y = max(q4_end, max_y, fliers_xy[1].max())

        else:
            min_y = min(q1_start, min_y)
            max_y = max(q4_end, max_y)

        # The y axis is rescaled to fit the new box plot completely with 10%
        # of the maximum value at both ends
        axes.set_ylim([min_y*1.1, max_y*1.1])

    # If redraw is set to true, the canvas is updated.
    if redraw:
        axes.figure.canvas.draw()

    return box_plot

def confidence_ellipse(x, y, n_std, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.

    Parameters
    ----------
    x, y : array-like, shape (n, )
        Input data.

    ax : matplotlib.axes.Axes
        The axes object to draw the ellipse into.

    n_std : float
        The number of standard deviations to determine the ellipse's radiuses.

    **kwargs
        Forwarded to `~matplotlib.patches.Ellipse`

    Returns
    -------
    matplotlib.patches.Ellipse
    """
    from matplotlib.patches import Ellipse
    import matplotlib.transforms as transforms

    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    #cov = np.cov(x, y)
    xmean = x.mean( dim={'id','time'}, skipna=True )
    ymean = y.mean( dim={'id','time'}, skipna=True )
    n = xr.ufuncs.isnan( x ).sum( dim={'id','time'} )
    temp = (x - xmean)*(y - ymean) / n
    cov = temp.sum( dim={'id','time'}, skipna=True )
    print( 'cov ' + str(cov.values) )
    
    xvar = x.var( dim={'id','time'}, skipna=True )
    yvar = y.var( dim={'id','time'}, skipna=True )
    pearson = cov / np.sqrt(xvar * yvar)
    print( 'pearson ' + str(pearson.values) )
    
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)

    # Calculating the standard deviation of x from
    # the square root of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(xvar) * n_std
    print( 'Ellipse major axis: ' + str(xmean+scale_x - xmean+scale_x) + ' K' )
    print( 'Min x value of major axis: ' + str(xmean-scale_x) + ' K' )
    print( 'Max x value of major axis: ' + str(xmean+scale_x) + ' K' )
    min_majoraxis = xmean - scale_x
    max_majoraxis = xmean + scale_x

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(yvar) * n_std

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(xmean, ymean)

    print(transf)
    #ellipse.set_transform(transf + ax.transData)
    return ellipse, min_majoraxis, max_majoraxis


def stdev_bubble(xmean, ymean, xstd, ystd, cov, n_std, facecolor='none', **kwargs):
    from matplotlib.patches import Ellipse
    import matplotlib.transforms as transforms

    xvar = xstd**2
    yvar = ystd**2
    pearson = cov / np.sqrt(xvar * yvar)

    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    scale_x = np.sqrt(xvar) * n_std
    scale_y = np.sqrt(yvar) * n_std
    Tmin = xmean-scale_x*ell_radius_x/2
    Tmax = xmean+scale_x*ell_radius_x/2
    print('Tmin and Tmax: ' + str(Tmin) + ' ' + str(Tmax))
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    ellipse = Ellipse((xmean, np.log10(ymean)), width=ell_radius_x * scale_x,
                       height=np.log10(ell_radius_y * scale_y),
                       angle=0, facecolor=facecolor, **kwargs)

    return Tmin, Tmax, ellipse

