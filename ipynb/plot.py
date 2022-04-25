import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import numpy as np
import matplotlib.patches as mpatches
from scipy.spatial import ConvexHull
from scipy.stats import norm
from adjustText import adjust_text


def rankplot(lr, ax, sort_col='mean'):
    lr = lr.sort_values('effect_size')
    threshold = 1e-3 / len(lr)
    idx = np.arange(len(lr))
    lr = lr.sort_values(sort_col)
    cmap = mpl.cm.get_cmap('seismic')
    lr['index'] = idx
    ax.fill_between(lr['index'], lr['5%'], lr['95%'], fc='b')
    #idx = np.logical_and(lr['prob_lr'] > 0, lr['effect_size'] > 0)
    idx = lr['tstat'] > 0
    i = np.logical_and(lr['pvalue'] < threshold, idx)
    ax.fill_between(lr.loc[i, 'index'], lr.loc[i, '5%'], lr.loc[i, '95%'], fc='r')
    ax.plot(lr['index'], lr['mean'], c='c')
    ax.set_ylabel('log(ASD/Control) + K', labelpad=90, rotation=0, fontsize=14)


def networkplot(pos, ax):
    sns.kdeplot(pos.values[:, 0], pos.values[:, 1], cmap='mako', fill=True,
                thresh=0, levels=100, ax=ax)
    norm = mpl.colors.Normalize(vmin=20, vmax=150)
    cbar = ax.scatter(pos.values[:, 0], pos.values[:, 1], s=.1,
                      c=pos['-log(pvalue)'], norm=norm,
                      label='Compounds', alpha=0.5)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    clb = plt.colorbar(cbar)
    clb.ax.set_title('-log(pvalue)')



def barplot_annotate_brackets(num1, num2, data, center, height,
                              yerr=None, dh=.05, barh=.05, fs=None, maxasterix=None):
    """
    Annotate barplot with p-values.

    :param num1: number of left bar to put bracket over
    :param num2: number of right bar to put bracket over
    :param data: string to write or number for generating asterixes
    :param center: centers of all bars (like plt.bar() input)
    :param height: heights of all bars (like plt.bar() input)
    :param yerr: yerrs of all bars (like plt.bar() input)
    :param dh: height offset over bar / bar + yerr in axes coordinates (0 to 1)
    :param barh: bar height in axes coordinates (0 to 1)
    :param fs: font size
    :param maxasterix: maximum number of asterixes to write (for very small p-values)

    Thank you https://stackoverflow.com/a/52333561/1167475
    """

    if type(data) is str:
        text = data
    else:
        # * is p < 0.05
        # ** is p < 0.005
        # *** is p < 0.0005
        # etc.
        text = ''
        p = .05

        while data < p:
            text += '*'
            p /= 10.

            if maxasterix and len(text) == maxasterix:
                break

        if len(text) == 0:
            text = 'n. s.'

    lx, ly = center[num1], height[num1]
    rx, ry = center[num2], height[num2]

    if yerr:
        ly += yerr[num1]
        ry += yerr[num2]

    ax_y0, ax_y1 = plt.gca().get_ylim()
    dh *= (ax_y1 - ax_y0)
    barh *= (ax_y1 - ax_y0)

    y = max(ly, ry) + dh

    barx = [lx, lx, rx, rx]
    bary = [y, y+barh, y+barh, y]
    mid = ((lx+rx)/2, y+barh)

    plt.plot(barx, bary, c='black')

    kwargs = dict(ha='center', va='bottom')
    if fs is not None:
        kwargs['fontsize'] = fs

    plt.text(*mid, text, **kwargs)


def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x)
    return(rho, phi)


def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)


def slice_patch(X, center=[0, 0], ax=None, pc1=0, pc2=1, **kwargs):
    if ax is None:
        ax = plt.gca()
    center = [center[pc1], center[pc2]]
    center = np.array(center)
    X_ = X[:, [pc1, pc2]] - center
    y = X_[:, 1]
    x = X_[:, 0]
    center = np.array(center)
    rho, phi = cart2pol(x, y)
    phi_amin, phi_amax = phi.argmin(axis=0), phi.argmax(axis=0)
    rho_amax = rho.argmax(axis=0)
    radius = rho.mean()
    theta1, theta2 = phi[phi_amax], phi[phi_amin]
    rho1, rho2 = rho[phi_amax], rho[phi_amin]
    points = np.vstack([center,
                        pol2cart(rho1, theta1) + center,
                        X[rho_amax, [pc1, pc2]],
                        pol2cart(rho2, theta2) + center])
    hull = ConvexHull(points)
    tri = mpatches.Polygon(points[hull.vertices], closed=True, **kwargs)
    ax.add_patch(tri)
    return tri


def vectorplot(X, V, name, color, alpha, scale=10, center=None,
               ax=None, pc1=0, pc2=1):
    if center is None:
        Y = (X.T @ V).values
        center = [0] * V.shape[1]
    else:
        center = (center @ V)
        Y = (X.T @ V).values + center
    ax.quiver(Y[:, pc1], Y[:, pc2], Y[:, pc1], Y[:, pc2],
              label=name, color=color,
              angles='xy', scale_units='xy', scale=scale)
    slice_patch(Y, color=color, alpha=alpha, center=center, ax=ax,
                pc1=pc1, pc2=pc2)


def plot_volcano(data, m_col, s_col, filter_f=None, name_col=None,
                 adjust=False, ax=None, **kwargs):
    """
    Plots volcano like plot.
    Drops taxa `nstd` standard deviations away from zero.

    Parameters
    ----------
    data : pd.DataFrame
       Hosts all of plottable data
    m_col : str
       Column of means
    s_col : str
       Column of standard deviations
    nstd : int
       Number of standard deviations to filter by.
    adjust : bool
       Add and adjust labels on plot
    ax : matplotlib.Axes.axes
       Matplotlib axes object
    """
    m, s = data[m_col].values, data[s_col].values

    scores = np.array(list(map(filter_f, zip(m, s))))
    idx = scores > 0
    ax.scatter(m, s, c='grey', edgecolor=(1,1,1,0), alpha=0.2)
    ax.scatter(m[idx], s[idx], c='r', edgecolor=(1,1,1,0), alpha=0.7)
    names = data.loc[idx, name_col]
    texts = []
    for x, y, l in zip(m[idx], s[idx], names):
        texts.append(plt.text(x, y, l, size=8))

    ax.set_xlabel('Mean')
    ax.set_ylabel('Std dev')
    adjust_text(texts,
                arrowprops=dict(arrowstyle="-", color='k', lw=0.5), **kwargs)


def gaussian_mixture_plot(mixture, differential, ax=None):
    m = np.ravel(mixture.means_)
    s = np.ravel(np.sqrt(mixture.covariances_))
    w = np.ravel(mixture.weights_)
    x = np.linspace(differential.min(), differential.max(), 100)
    sns.distplot(differential, norm_hist=True, kde=False, ax=ax)
    ax.plot(x, w[0]*norm.pdf(x, m[0], s[0]), '-r')
    ax.plot(x, w[1]*norm.pdf(x, m[1], s[1]), '-g')
    ax.plot(x, w[2]*norm.pdf(x, m[2], s[2]), '-b')
