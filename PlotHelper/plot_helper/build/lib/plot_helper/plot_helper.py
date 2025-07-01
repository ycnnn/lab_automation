import numpy as np
import logging
logging.basicConfig(level=logging.INFO)

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
from matplotlib.patheffects import withStroke
from matplotlib.ticker import MaxNLocator

svg = {'bbox_inches':'tight', 'pad_inches':0.1}
pdf = {'bbox_inches':'tight', 'pad_inches':0.1}
png = {'bbox_inches':'tight', 'pad_inches':0.1, 'dpi':750}
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
           x_label_pad=2,
           y_label_pad=2,
           show_ticks=True,
           show_labels=True,
           set_size_global=False):
    
    fig = fig or plt.gcf()
    for ax in fig.axes:
        ax_title = ax.get_title()
        if len(ax_title) > 0:
            ax.set_title(ax_title, fontsize=label_size)
        for text in ax.texts:
            text.set_fontsize(label_size) 
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
        if set_size_global:
            plt.rcParams.update({'font.size': label_size})
  


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



def generate_horizontal_cbar(cbar_ax, cmap='bwr', vmin=0, vmax=1, 
                             title='Colorbar',
                             label_position=[0.08,0.5,0.92],
                             custom_labels = [],
                             foreground=(1,1,1,0.75),
                             delta_pad=0,
                             title_delta_pad=0
                             ):

    cbar = cbar_ax.imshow(np.linspace([0,0],[1,1], num=500).T, aspect='auto', cmap=cmap)
    cbar.set_clim(vmin=vmin, vmax=vmax)
    fig = plt.gcf()
        # Get the bounding box of the axes in pixels
    bbox = cbar_ax.get_window_extent()

    # Convert the size to points (1 inch = 72 points)
    width_in_points = bbox.width / fig.dpi * 72
    height_in_points = bbox.height / fig.dpi * 72

    pad = -height_in_points/2
    cbar_ax.set_yticks([])
    cbar_ax.tick_params(axis='x', which='both', length=0) 
    cbar_ax.tick_params(axis='x', labelbottom=True, labeltop=False, pad=pad + delta_pad)
    
    for label in cbar_ax.get_xticklabels():
        label.set_path_effects([withStroke(linewidth=3, foreground=foreground)])
        label.set_verticalalignment('center')
    label_position = np.array(label_position).reshape(-1) * 500
    cbar_ax.set_xticks(label_position)
    
    if len(custom_labels)==0:
        tick_labels = [vmin, title, vmax]
    elif len(custom_labels)==2:
        tick_labels = [custom_labels[0], title, custom_labels[1]]
        
    else:
        tick_labels = custom_labels
    
    cbar_ax.set_xticklabels(tick_labels)
    
    if title_delta_pad !=0:
        x_tick_labels = cbar_ax.get_xticklabels()
        x_tick_labels[1].set_y(title_delta_pad)

def add_scale_bar(ax,
                  x_start, x_end,
                  y_start, y_end,
                  scale_label='',
                  text_x_offset=0,
                  text_y_offset=-5,
                  color='black'):
    
    ax.plot([x_start, x_end],[y_start, y_end], linewidth=4, color=(1,1,1,0.75))
    ax.plot([x_start, x_end],[y_start, y_end], linewidth=1, color='black')
    text_artist = ax.text((x_start + x_end)/ 2 + text_x_offset, (y_start + y_end)/ 2 + text_y_offset, scale_label, color=color, 
            ha='center', va='center', fontsize=font_size)

    text_artist.set_path_effects([withStroke(linewidth=3, foreground=(1,1,1,0.75))])

def set_tick_num(ax, x_tick_num=None, y_tick_num=None):
    ax = ax if ax else plt.gca()
    if x_tick_num:
        ax.xaxis.set_major_locator(MaxNLocator(nbins=x_tick_num))  # Control the x-axis ticks
    if y_tick_num:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=y_tick_num))

def change_axis_color(ax=None, axis='x', orientation='left', color='blue'):
    axis = axis.lower()
    orientation = orientation.lower()
    if (axis, orientation) not in [
        ('x','top'),
        ('x','bottom'),
        ('y','left'),
        ('y','right'),
    ]:
        raise RuntimeError('Orientation or axis or teir combination incorrect')
    ax = ax if ax else plt.gca()
    fig = plt.gcf()
    for iterate_ax in fig.axes:
        iterate_ax.spines[orientation].set_color([0,0,0,0])
    ax.spines[orientation].set_color(color)  # Change the color of the left spine (y-axis)
    ax.tick_params(axis=axis, colors=color)
    if axis == 'x':
        label = ax.get_xlabel()
    elif axis == 'y':
        label = ax.get_ylabel()
    ax.set_ylabel(label, color=color)
    
def text_format(text,ax=None, color=None, facecolor=(1,1,1,0.5), edgecolor='none', rotation=None):
    ax = ax if ax else plt.gca()
    text.set_bbox(dict(facecolor=facecolor, 
                  edgecolor=edgecolor))
    if color:
        text.set_color(color)
    if rotation:
        text.set_rotation(rotation)
    

def generate_img_plot(
    data,
    img_title=None,
    fig=None,
    fig_height = None,
    fig_width = None,
    img_size_compression_factor = 100,
    img_margin = 0.05,# in inch
    cbar_height = 0.1,# in inch
    cbar_width = 0.5,# in inch
    set_cbar_same_width_with_img=False,
    vmin = None,
    vmax = None,
    cmap='bwr',
    cbar_vmin=0,
    cbar_vmax=1,
    cbar_title='Colorbar',
    cbar_label_position=[0.08, 0.5, 0.92],# in percent
    cbar_custom_labels=[],
    cbar_foreground_color=(1, 1, 1, 0.75),
    cbar_delta_pad=-10,# in percent
    cbar_title_delta_pad=0,# in percent
    auto_format=True):
    
    if fig_height and fig_width:
        raise RuntimeError('Both figure height and figure width is supplied. Please only supply one.')
    if not fig_height and not fig_width:
        logging.info('None of the figure height and figure width is supplied. Will use orignal scale.')
    
    fig = plt.gcf() if not fig else fig
    raw_img_height, raw_img_width = data.shape 
    img_height = raw_img_height / img_size_compression_factor
    img_width = raw_img_width / img_size_compression_factor
    total_height = img_height + cbar_height + 4 * img_margin
    total_width = img_width + 2 * img_margin
    
    if set_cbar_same_width_with_img:
        cbar_width = img_width
        logging.info('Color bar width has been set as the same as that of the image. The supplied cbar width will be ignored.')
    
    scale_factor = 1
    if fig_height:
        scale_factor = fig_height/total_height
    if fig_width:
        scale_factor = fig_width/total_width
    fig.set_size_inches((total_width*scale_factor, total_height*scale_factor))
    

    ax = fig.add_axes((
    img_margin/total_width, 
    img_margin/total_height,
    img_width/total_width, 
    img_height/total_height
    ))

    cbar_ax = fig.add_axes((
        (total_width - img_margin - cbar_width)/total_width,
        (2 * img_margin + img_height)/total_height,
        cbar_width/total_width,
        cbar_height/total_height
        ))

    img = ax.imshow(data, vmin=vmin, vmax=vmax)

    img.set_cmap(cmap)
    generate_horizontal_cbar(
        cbar_ax=cbar_ax,
        cmap=cmap,
        vmin=cbar_vmin,
        vmax=cbar_vmax,
        title=cbar_title,
        label_position=cbar_label_position,
        custom_labels=cbar_custom_labels,
        foreground=cbar_foreground_color,
        delta_pad=cbar_delta_pad,
        title_delta_pad=cbar_title_delta_pad
    )

    ax.set_xticks([])
    ax.set_yticks([])
    
    if img_title:
        ax.set_xlabel(img_title)
    
    if auto_format:
        label_format()
        format()
    
    
    
    return fig, ax, cbar_ax