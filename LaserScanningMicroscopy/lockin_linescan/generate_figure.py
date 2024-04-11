from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import plot_helper as ph

def generate_figure_3ch(fig,scale,
                colormap,auto_scale,
                val_range_1,
                val_range_2,
                val_range_3,
                line_color,
                # pixels,
                l_ch1, i_ch1,
                l_ch2, i_ch2,
                l_ch3, i_ch3):
    # l_ch1,l_ch2,l_ch3,i_ch1,i_ch2,i_ch3 = data_random
    # set the layout scale
    # h -> top line plot height, in inches
    # d -> spacing, in inches
    # l -> size of each channel image, in inches
    # scale -> scaling effect, 0 ~ 1

    h,l,d = (3,9.5,1.25)
    width, height = (3*l+6*d, h+l+3.5*d) 


    top_ch_1 = fig.add_axes((d/width,(2*d+l)/height,l/width, h/height))
    line_ch_1 = top_ch_1.plot(l_ch1)
    top_ch_1.set_xticklabels([])
    top_ch_1.set_xlim(0,len(l_ch1)-1)
    ph.line_format(line_ch_1,color=line_color)

    chan_1 = fig.add_axes((d/width,d/height,l/width, l/height))
    chan_1_image = chan_1.imshow(i_ch1)
    chan_1_image.set_cmap(colormap)
    chan_1.set_xticklabels([])
    chan_1.set_yticklabels([])


    top_ch_2 = fig.add_axes(((l+3*d)/width,(2*d+l)/height,l/width, h/height))
    line_ch_2 = top_ch_2.plot(l_ch2)
    top_ch_2.set_xticklabels([])
    top_ch_2.set_xlim(0,len(l_ch2)-1)
    ph.line_format(line_ch_2,color=line_color)

    chan_2 = fig.add_axes(((l+3*d)/width,d/height,l/width, l/height))
    chan_2_image = chan_2.imshow(i_ch2)
    chan_2_image.set_cmap(colormap)
    chan_2.set_xticklabels([])
    chan_2.set_yticklabels([])

    top_ch_3 = fig.add_axes(((2*l+5*d)/width,(2*d+l)/height,l/width, h/height))
    line_ch_3 = top_ch_3.plot(l_ch3)
    top_ch_3.set_xticklabels([])
    top_ch_3.set_xlim(0,len(l_ch3)-1)
    ph.line_format(line_ch_3,color=line_color)

    chan_3 = fig.add_axes(((2*l+5*d)/width,d/height,l/width, l/height))
    chan_3_image = chan_3.imshow(i_ch3)
    chan_3_image.set_cmap(colormap)
    chan_3.set_xticklabels([])
    chan_3.set_yticklabels([])


    if not auto_scale:
        top_ch_1.set_ylim(val_range_1[0],val_range_1[1])
        chan_1_image.set_clim(vmin=val_range_1[0],vmax=val_range_1[1])
        top_ch_2.set_ylim(val_range_2[0],val_range_2[1])
        chan_2_image.set_clim(vmin=val_range_2[0],vmax=val_range_2[1])
        top_ch_3.set_ylim(val_range_3[0],val_range_3[1])
        chan_3_image.set_clim(vmin=val_range_3[0],vmax=val_range_3[1])

    for ax in [top_ch_1,top_ch_2,top_ch_3]:
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))

    fig.set_size_inches(width*scale, height*scale)

    return (top_ch_1, chan_1, line_ch_1[0], chan_1_image,
            top_ch_2, chan_2, line_ch_2[0], chan_2_image,
            top_ch_3, chan_3, line_ch_3[0], chan_3_image)


def generate_figure_1ch(fig,scale,
                colormap,auto_scale,val_range,line_color,pixels,l_ch1, i_ch1):
    # l_ch1,l_ch2,l_ch3,i_ch1,i_ch2,i_ch3 = data_random
    # set the layout scale
    # h -> top line plot height, in inches
    # d -> spacing, in inches
    # l -> size of each channel image, in inches
    # scale -> scaling effect, 0 ~ 1

    h,l,d = (3,9.5,1.25)
    width, height = (1*l+2*d, h+l+3.5*d) 


    top_ch_1 = fig.add_axes((d/width,(2*d+l)/height,l/width, h/height))
    line_ch_1 = top_ch_1.plot(l_ch1)
    top_ch_1.set_xticklabels([])
    top_ch_1.set_xlim(0,len(l_ch1)-1)

    # Optional figure formatting
    ph.line_format(line_ch_1,color=line_color)

    chan_1 = fig.add_axes((d/width,d/height,l/width, l/height))
    chan_1_image = chan_1.imshow(i_ch1)
    chan_1_image.set_cmap(colormap)
    chan_1.set_xticklabels([])
    chan_1.set_yticklabels([])


    if not auto_scale:
        top_ch_1.set_ylim(val_range[0],val_range[1])
        chan_1_image.set_clim(vmin=val_range[0],vmax=val_range[1])

    fig.set_size_inches(width*scale, height*scale)
    return top_ch_1, chan_1, line_ch_1[0], chan_1_image