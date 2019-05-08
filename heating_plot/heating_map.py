import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def parse(filename):
    with open(filename) as inputfile:
        header = {}
        for i, line in enumerate(inputfile):
            key, value = (token.strip() for token in line.split(":,", maxsplit=1))
            header[key] = value
            if key == 'end':
                break
        data = pd.read_csv(inputfile, sep=',')
    return data, header


def format_map_data(data, header):
    data = data.sort_values(by=['y_pixel', 'x_pixel'])
    xvalues = data['x_iphoto'].values.reshape(int(header['y scan density']), int(header['x scan density']))
    yvalues = data['y_iphoto'].values.reshape(int(header['y scan density']), int(header['x scan density']))
    return xvalues, yvalues


def save_formatted_map_data(f, data):
    np.savetxt(f, data, delimiter=',')


def plot_heating_data(xvalues, yvalues, fig=None, ax1=None, ax2=None, xamax=None, xamin=None, yamax=None,
                      yamin=None, ax1title='iphoto X', ax2title='iphoto Y', clb1title='current (mA)',
                      clb2title='current (mA)'):
    if not fig and not ax1 and not ax2:
        fig, (ax1, ax2) = plt.subplots(1,2)
    xamax = xamax if xamax else np.amax(xvalues)
    yamax = yamax if yamax else np.amax(yvalues)
    xamin = xamin if xamin else np.amin(xvalues)
    yamin = yamin if yamin else np.amin(yvalues)
    ax1.title.set_text(ax1title)
    ax2.title.set_text(ax2title)
    im1 = ax1.imshow(xvalues, cmap=plt.cm.coolwarm, interpolation='nearest', origin='lower', vmax=xamax, vmin=xamin)
    im2 = ax2.imshow(yvalues, cmap=plt.cm.coolwarm, interpolation='nearest', origin='lower', vmax=yamax, vmin=yamin)
    clb1 = fig.colorbar(im1, ax=ax1)
    clb2 = fig.colorbar(im2, ax=ax2)
    clb1.set_label(clb1title, rotation=270, labelpad=20)
    clb2.set_label(clb2title, rotation=270, labelpad=20)
    plt.show()

f = 'C:\\Users\\Ruoyu\\Desktop\\test_map scan__2.csv'
data, header = parse(f)
x, y = format_map_data(data, header)
plot_heating_data(x, y)
f_format = 'C:\\Users\\Ruoyu\\Desktop\\formatted_x.csv'
save_formatted_map_data(f_format, x)



