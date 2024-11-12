import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.pyplot import figure
from matplotlib import cm as mpl_cm
from matplotlib import colors as mpl_colors
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D


svg = {'bbox_inches':'tight', 'transparent':True,'pad_inches':0}
font_size = 10

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


def format(fig=None,
           linewidth=0.5):
    
    fig = fig or plt.gcf()

    for ax in fig.axes:

        ax.tick_params(axis="y",direction="in")
        ax.tick_params(axis="x",direction="in")
        for axis in ['top','bottom','left','right']:
            ax.spines[axis].set_linewidth(linewidth)
        ax.xaxis.set_tick_params(width=linewidth)
        ax.yaxis.set_tick_params(width=linewidth)


        
def label_format(fig=None,
           label_size=font_size,
           decimal_digits=0,
           x_format='{x:<.1f}',
           y_format='{x:<.1f}',
           x_label_pad=5,
           y_label_pad=0,
           show_ticks=True,
           show_labels=True):
    
    fig = fig or plt.gcf()
    for ax in fig.axes:
        if show_ticks:
            # ax.xaxis.set_major_formatter(x_format)
            # ax.yaxis.set_major_formatter(y_format)
            ax.yaxis.labelpad = y_label_pad
            ax.xaxis.labelpad = x_label_pad
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

    
# def set_size(figsize, ax=None, unit_pt=True):
#     ax = ax or plt.gca()
#     cm = 1/2.54
#     pt = 1/72
#     """ w, h: width, height in inches """
#     w, h = figsize
#     l = ax.figure.subplotpars.left
#     r = ax.figure.subplotpars.right
#     t = ax.figure.subplotpars.top
#     b = ax.figure.subplotpars.bottom
#     figw = float(w)/(r-l)
#     figh = float(h)/(t-b)
#     if unit_pt:
#         ax.figure.set_size_inches(figw*pt, figh*pt)
#     else:
#         ax.figure.set_size_inches(figw*cm, figh*cm)
   
def boxplot(data,
            ax=None,
            whis=1.5,
            linewidth=0.5,
            whisker_color = 'black',
            box_color = (1,0,0,0.5),
            med_color = 'black',
            cap_color = 'black',
            empty_face=False,
            **kwargs):
    ax = ax or plt.gca()
    # handles np.nan values
    if np.sum(np.isnan(data)) > 0:
        mask = ~np.isnan(data)
        data = [d[m] for d, m in zip(data.T, mask.T)]
    face_color = 'none' if empty_face else box_color
    boxplot = ax.boxplot(data, whis=whis, 
                         patch_artist=True,
                         boxprops=dict(facecolor=face_color, edgecolor='black'), **kwargs)

    for whis in boxplot['whiskers']:
        whis.set_color(whisker_color)
        whis.set_linewidth(linewidth)

    for box in boxplot['boxes']:
        # box.set_color(box_color)        
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
                   linewidth=0.5,
                   markersize=10):
    
    scatter.set_edgecolor(edgecolor)
    scatter.set_facecolor(facecolor)
    scatter.set_linewidth(linewidth)
    scatter.set_sizes([markersize])
    
def line_format(lines, 
                   color='red',
                   linewidth=1,
                   linestyle='solid'):
    for line in lines:
        line.set_color(color)
        line.set_linewidth(linewidth)
        line.set_linestyle(linestyle)


def abline(slope,x,y,ax=None,_linewidth=0.5):
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
  
  
  
def boxplot_2d_helper(x,y, ax, whis=1.5, linewidth=0.5,
               boxcolor='black',
               boxfillcolor=(1,0,0,0.4),
               linecolor='black',
               mediancolor='black',
               markercolor='red',
               markersize=10,
               zero_spacing=1E-3):
    
    props = {'linewidth': 0.5,'linestyle':'dashed'}
    props_solid = {'linewidth': 0.5,'linestyle':'solid'}
    x = x[~np.isnan(x)]
    y = y[~np.isnan(y)]
    xlimits = [np.percentile(x, q) for q in (25, 50, 75)]
    ylimits = [np.percentile(y, q) for q in (25, 50, 75)]
    if xlimits[2] - xlimits[0] <= 1E-6:
        hwhisbar_r = xlimits[1] + zero_spacing
        hwhisbar_l = xlimits[1] - zero_spacing
        print('Zero variance x input encountered.')
    else:
        hwhisbar_r = xlimits[2] 
        hwhisbar_l = xlimits[0]

    ##the box
    box = Rectangle(
        (xlimits[0],ylimits[0]),
        (xlimits[2]-xlimits[0]),
        (ylimits[2]-ylimits[0]),
        facecolor=boxfillcolor,
        edgecolor = boxcolor,
        fill=True,
        linewidth=0.5, linestyle='solid',
        zorder=0
    )
    ax.add_patch(box)

    ##the x median
    vline = Line2D(
        [xlimits[1],xlimits[1]],[ylimits[0],ylimits[2]],
        color=linecolor,
        **props,
        zorder=1
    )
    ax.add_line(vline)

    ##the y median
    hline = Line2D(
        [xlimits[0],xlimits[2]],[ylimits[1],ylimits[1]],
        color=linecolor,
        **props,
        zorder=1
    )
    ax.add_line(hline)

    ##the central point
    ax.scatter([xlimits[1]],[ylimits[1]], marker='o',
            facecolor='None',
            edgecolor=markercolor,
            **props,
            s=markersize)

    iqr = xlimits[2]-xlimits[0]

    ##left
    left = np.min(x[x > xlimits[0]-whis*iqr])
    whisker_line = Line2D(
        [left, xlimits[0]], [ylimits[1],ylimits[1]],
        color = linecolor,
        **props,
        zorder = 1
    )
    ax.add_line(whisker_line)
    whisker_bar = Line2D(
        [left, left], [ylimits[0],ylimits[2]],
        color = linecolor,
        **props_solid,
        zorder = 1
    )
    ax.add_line(whisker_bar)

    ##right
    right = np.max(x[x < xlimits[2]+whis*iqr])
    whisker_line = Line2D(
        [right, xlimits[2]], [ylimits[1],ylimits[1]],
        color = linecolor,
        **props,
        zorder = 1
    )
    ax.add_line(whisker_line)
    whisker_bar = Line2D(
        [right, right], [ylimits[0],ylimits[2]],
        color = linecolor,
        **props_solid,
        zorder = 1
    )
    ax.add_line(whisker_bar)

    ##the y-whisker
    iqr = ylimits[2]-ylimits[0]

    ##bottom
    bottom = np.min(y[y > ylimits[0]-whis*iqr])
    whisker_line = Line2D(
        [xlimits[1],xlimits[1]], [bottom, ylimits[0]], 
        color = linecolor,
        **props,
        zorder = 1
    )
    ax.add_line(whisker_line)

    whisker_bar = Line2D(
        [hwhisbar_l,hwhisbar_r], [bottom, bottom], 
        color = linecolor,
        **props_solid,
        zorder = 1
    )
    ax.add_line(whisker_bar)

    ##top
    top = np.max(y[y < ylimits[2]+whis*iqr])
    whisker_line = Line2D(
        [xlimits[1],xlimits[1]], [top, ylimits[2]], 
        color = linecolor,
        **props,
        zorder = 1
    )
    ax.add_line(whisker_line)
    whisker_bar = Line2D(
        [hwhisbar_l,hwhisbar_r], [top, top], 
        color = linecolor,
        **props_solid,
        zorder = 1
    )
    ax.add_line(whisker_bar)

    #outliers
    x_mask = (x<left)|(x>right)
    y_mask = (y<bottom)|(y>top)
    ax.scatter(
        x[x_mask],y[y_mask],
        facecolors='none', edgecolors=markercolor, s=markersize, **props
    )

