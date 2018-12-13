import os
import os.path as op
import matplotlib.pyplot as plt
import numpy as np


def thecodes(file_to_ana, decod_scr_with_trigger):
    if file_to_ana is 'Guided':
        if decod_scr_with_trigger == 1:
            cow_codes_scr = [40, 42]
        else:
            cow_codes_scr = [40, 50]
        textleft_codes = [40, 45]
        cow_codes = [1060, 1065, 1070, 1075,
                     2060, 2065, 2070, 2075]
        round_codes = [1060, 1065, 1070, 1075,
                       1560, 1565, 1570, 1575]
        left_codes = [1060, 1065, 1560, 1565,
                      2060, 2065, 2560, 2565]
        text_codes = [1060, 1070, 1560, 1570,
                      2060, 2070, 2560, 2570]
    if file_to_ana is 'JustCue':
        cow_codes_scr = []
        textleft_codes = []
        cow_codes = []
        round_codes = [10100, 10110, 10120]
        left_codes = []
        text_codes = []
    if file_to_ana is 'Spontaneous':
        cow_codes_scr = []
        textleft_codes = [40]
        cow_codes = []
        round_codes = []
        left_codes = [1060, 1065]
        text_codes = [1060, 1070]
    return cow_codes_scr, textleft_codes, cow_codes, round_codes, left_codes, text_codes  #noqa


def datatodec(which_channels, epochs):
    if which_channels is 'meg':
        data_to_dec = epochs._data
    elif which_channels is 'eyes':
        data_to_dec = epochs._data[:, epochs.ch_names.index('UADC009-2104'):epochs.ch_names.index('UADC010-2104')+1, :]  # noqa
    elif which_channels is 'trigger':
        data_to_dec = epochs._data[:, None, epochs.ch_names.index('UPPT001'), :]  # noqa
    elif which_channels is 'all':
        data_to_dec = epochs._data
    return data_to_dec


def whattodecod(somecode, y):
    yTD = y.copy()
    yTD[:] = 1
    yTD[np.where(np.in1d(y, somecode))] = 0
    return yTD


def smooth_to_plot(array_of_decod):

    array_of_decod2 = array_of_decod.copy()
    for i in range(len(array_of_decod)-4):
        array_of_decod2[i+2] = (array_of_decod2[i] +
                                   array_of_decod2[i+1] +
                                   array_of_decod2[i+2] +
                                   array_of_decod2[i+3] +
                                   array_of_decod2[i+4])/5
    return array_of_decod2


def thedirectory(path_analyzed_data, which_channels):
    if which_channels is 'meg':
        directory = op.join(path_analyzed_data, 'results/epochs')
    else:
        directory = op.join(path_analyzed_data, 'results/epochs_allchannels')
    if not op.exists(directory):
        # print "directory"
        os.mkdir(directory)
    return directory


def thedirectorydecod(path_analyzed_data, endofpath):
    directorydecod = op.join(path_analyzed_data, endofpath)
    if not op.exists(directorydecod):
        os.mkdir(directorydecod)
    return directorydecod


def plotchanceandlimit(horizontal_extent, horizontal_borders, vertical_extent, vertical_borders):
    for hor_bor in horizontal_borders:
        plt.plot(horizontal_extent, [hor_bor, hor_bor], color='black', linestyle='dashed', alpha=0.5)
    for ver_bor in vertical_borders:
        plt.plot([ver_bor, ver_bor], vertical_extent, color='black', linestyle='dashed', alpha=0.5)
