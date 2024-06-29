import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import figure
from matplotlib import cm as mpl_cm
from matplotlib import colors as mpl_colors
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap



svg = {'bbox_inches':'tight', 'transparent':True,'pad_inches':0}
svg_dark = {'bbox_inches':'tight','pad_inches':0}

def generate_colormap(N=1024):
    
    blue = np.linspace(1,0, int(N))
    green = np.linspace(1,0, int(N))
    red = np.ones(int(N))
    alpha = np.ones(int(N))

    custom_colors = np.ones((N,4))
    custom_colors[:,0] = red
    custom_colors[:,1] = green
    custom_colors[:,2] = blue
    custom_colors[:,3] = alpha

    cmap_red = ListedColormap(custom_colors)



    red = np.linspace(1,0, int(N))
    green = np.linspace(1,0, int(N))
    blue = np.ones(int(N))
    alpha = np.ones(int(N))

    custom_colors = np.ones((N,4))
    custom_colors[:,0] = red
    custom_colors[:,1] = green
    custom_colors[:,2] = blue
    custom_colors[:,3] = alpha

    cmap_blue = ListedColormap(custom_colors)

    blue = np.linspace(0,0, int(N))
    green = np.linspace(0,0, int(N))
    red = np.linspace(0,1, int(N))
    alpha = np.ones(int(N))

    custom_colors = np.ones((N,4))
    custom_colors[:,0] = red
    custom_colors[:,1] = green
    custom_colors[:,2] = blue
    custom_colors[:,3] = alpha

    cmap_red_black = ListedColormap(custom_colors)
    

    blue = np.linspace(0,1, int(N))
    green = np.linspace(0,0, int(N))
    red = np.linspace(0,0, int(N))
    alpha = np.ones(int(N))

    custom_colors = np.ones((N,4))
    custom_colors[:,0] = red
    custom_colors[:,1] = green
    custom_colors[:,2] = blue
    custom_colors[:,3] = alpha

    cmap_blue_black = ListedColormap(custom_colors)
    
    return cmap_red, cmap_blue, cmap_red_black, cmap_blue_black


def format(figsize, 
           ax=None,
           linewidth=0.5, 
           unit_pt=True):
    
    ax = ax or plt.gca()
    width, height = figsize
    ax.tick_params(axis="y",direction="in")
    ax.tick_params(axis="x",direction="in")
    ax.set_box_aspect(height/width)
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(linewidth)
    ax.xaxis.set_tick_params(width=linewidth)
    ax.yaxis.set_tick_params(width=linewidth)
    set_size(figsize, unit_pt=unit_pt)
    
def format_no_resize(ax=None,
           linewidth=0.5):
    
    ax = ax or plt.gca()
 
    ax.tick_params(axis="y",direction="in")
    ax.tick_params(axis="x",direction="in")
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(linewidth)
    ax.xaxis.set_tick_params(width=linewidth)
    ax.yaxis.set_tick_params(width=linewidth)

        
def label_format(ax=None,
           label_size=7,
           decimal_digits=0,
           show_ticks=True,
           show_labels=True):
    
    ax = ax or plt.gca()
    if show_ticks:
        ax.xaxis.set_major_formatter('{x:<.0f}')
        ax.yaxis.set_major_formatter('{x:<.0f}')
        for label in ax.get_xticklabels():
            label.set_fontsize(label_size)   
        for label in ax.get_yticklabels():
            label.set_fontsize(label_size)
    else:
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
    if show_labels:
        ax.xaxis.label.set_size(label_size)
        ax.yaxis.label.set_size(label_size)
  


def font_format(font_global="Arial"):
    plt.rcParams.update({"font.family": font_global})
    mpl.rcParams['mathtext.fontset'] = 'custom'
    mpl.rcParams['mathtext.it'] = font_global + ':italic'
    mpl.rcParams['mathtext.rm'] = font_global
    mpl.rcParams['mathtext.bf'] = font_global  + ':bold'

    
def set_size(figsize, ax=None, unit_pt=True):
    ax = ax or plt.gca()
    cm = 1/2.54
    pt = 1/72
    """ w, h: width, height in inches """
    w, h = figsize
    l = ax.figure.subplotpars.left
    r = ax.figure.subplotpars.right
    t = ax.figure.subplotpars.top
    b = ax.figure.subplotpars.bottom
    figw = float(w)/(r-l)
    figh = float(h)/(t-b)
    if unit_pt:
        ax.figure.set_size_inches(figw*pt, figh*pt)
    else:
        ax.figure.set_size_inches(figw*cm, figh*cm)
   
def boxplot(data,
            ax=None,
            whis=1.5,
            linewidth=0.5,
            whisker_color = 'black',
            box_color = 'black',
            med_color = 'black',
            cap_color = 'black',
            **kwargs):
    ax = ax or plt.gca()
    boxplot = ax.boxplot(data, whis=whis, **kwargs)

    for whis in boxplot['whiskers']:
        whis.set_color(whisker_color)
        whis.set_linewidth(linewidth)

    for box in boxplot['boxes']:
        box.set_color(box_color)
        box.set_linewidth(linewidth)
        
    for med in boxplot['medians']:
        med.set_color(med_color)
        med.set_linewidth(linewidth)

    for cap in boxplot['caps']:
        cap.set_color(cap_color)
        cap.set_linewidth(linewidth)
    
    return boxplot

def scatter_format(scatter, 
                   edgecolor='red',
                   facecolor='None',
                   linewidth=0.25,
                   markersize=10):
    scatter.set_edgecolor(edgecolor)
    scatter.set_facecolor(facecolor)
    scatter.set_linewidth(linewidth)
    scatter.set_sizes([markersize])
    
def line_format(lines, 
                   color='black',
                   linewidth=0.5,
                   linestyle='solid'):
    for line in lines:
        line.set_color(color)
        line.set_linewidth(linewidth)
        line.set_linestyle(linestyle)


def abline(slope,x,y,ax=None):
    ax = ax or plt.gca()
    """Plot a line from slope and intercept"""
    x0 = np.mean(x)
    y0 = np.mean(y)
    xlim = np.array(ax.get_xlim())
    x_vals = np.mean(xlim) + (xlim-np.mean(xlim))*1.2
    
    y_vals = y0 + slope * (x_vals-x0)
    ax.plot(x_vals, y_vals, '--', color='gray', linewidth=_linewidth)

red, blue, red_black, blue_black = generate_colormap()

def generate_cbar(cmap=red,cbar_ticks=[0,0.25,0.5,0.75,1],
                  fig=None,ax=None):
    fig = fig or plt.gcf()
    ax = ax or plt.gca()
    norm = mpl_colors.Normalize(0, 1)
    
    cbar = fig.colorbar(mpl_cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
    cbar.set_ticks([])
    cbar.set_ticklabels([])
    ax.axis('off')
  