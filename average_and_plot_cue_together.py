import os.path as op
import os
import numpy as np
import matplotlib.pyplot as plt
from mne.filter import filter_data
from scipy.stats import ttest_1samp

from base import decod_stats
from config import *
from basemy import *


# plot_each_session = True
plot_each_subject = True
plot_std = False
testing_significance = True
correct_mult_comp = False
fill_from_chance = False

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

# which_decod
colortoplot = {'Cue/Object': colors[4],
               'Cue': colors[1],
               'Object': colors[0],
               'Button': colors[2],
               'Modality': colors[3],
               'Resp_Screen_Object': colors[5],
               'Resp_Screen_Side': colors[7],
               'Control_cue': colors[6]}

# type_epo
timeforplot = {'cue': np.linspace(-0.5, 7, 901),
               'res': np.linspace(-4, 4, 961),
               'scr': np.linspace(-4, 4, 961)}
borders = {'cue': [0, 0.5, 4],
           'res': [0],
           'scr': [-3.5, 0]}


for file_to_ana in files_to_ana:
    print(['file_to_ana: ', file_to_ana])

    if file_to_ana is 'JustCue':

        type_epo = 'cue'
        which_decod = 'Cue'
        print(['type of decoding: ', which_decod])

        all_scores_subjects = list()
        for subj_nb, subject in enumerate(subjects_id):
            print(subject)

            fname = op.join(path_analyzed_data,
                            'results/decoding_together',
                            '%s_%s_%s_%s.npy'
                            % (subject, file_to_ana,
                               which_decod,
                               which_channels))

            if op.exists(fname):

                score = np.load(fname)

                all_scores_subjects.append(score)

        if len(all_scores_subjects) > 0:
            all_scores_subjects = np.array(all_scores_subjects)
            print(['all subjects before averaging :', all_scores_subjects.shape])  # noqa
            if len(all_scores_subjects) > 1:
                if correct_mult_comp:
                    decod_p_values = decod_stats(all_scores_subjects - 0.5)
                else:
                    _, decod_p_values = ttest_1samp(all_scores_subjects, 0.5)
                sig1 = decod_p_values <= 0.05
                sig2 = np.empty(len(decod_p_values))
                sig2[:] = np.nan
                sig2[np.where(decod_p_values <= 0.5)] = 1
                all_scores_subjects_sem = np.std(all_scores_subjects, axis=0)/np.sqrt(len(all_scores_subjects))
                all_scores_subjects_mean = all_scores_subjects.mean(0,)
                # all_scores_subjects = all_scores_subjects.mean(0, keepdims=True)  # noqa
            else:
                all_scores_subjects_mean = all_scores_subjects
            print(['all subjects after averaging :', all_scores_subjects_mean.shape])  # noqa

            # filtering for vizualization
            all_scores_subjects_mean = smooth_to_plot(all_scores_subjects_mean)
            # all_scores_subjects = filter_data(all_scores_subjects, 120, 0, 15)

            # 3. plot group figures
            if (len(all_scores_subjects) > 1 and plot_std):
                mean1 = all_scores_subjects_mean + all_scores_subjects_sem
                mean2 = all_scores_subjects_mean - all_scores_subjects_sem
                minforplot = min(mean2)
                maxforplot = max(mean1)
                if testing_significance:
                    plt.fill_between(timeforplot[type_epo], mean1, mean2, color=colortoplot['Control_cue'], alpha=0.5)
                    plt.fill_between(timeforplot[type_epo], mean1, mean2, label='Control Cue', color=colortoplot['Control_cue'], alpha=1, where=sig1)
                else:
                    plt.fill_between(timeforplot[type_epo], mean1, mean2, label='Control Cue', color=colortoplot['Control_cue'], alpha=0.5)
                    # plt.plot(timeforplot[type_epo], mean1, color=colortoplot['Control_cue'])
                    # plt.plot(timeforplot[type_epo], mean2, label='Control Cue', color=colortoplot['Control_cue'])
            elif (len(all_scores_subjects) > 1 and testing_significance):
                if fill_from_chance:
                    chance = np.empty(len(timeforplot[type_epo]))
                    chance.fill(0.5)
                    # plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, label='Control Cue', color=colortoplot['Control_cue'], alpha=0.5)
                    plt.plot(timeforplot[type_epo], all_scores_subjects_mean, label='Control Cue', color=colortoplot['Control_cue'])
                    plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, color=colortoplot['Control_cue'], alpha=1, where=sig1)
                else:
                    # plt.plot(timeforplot[type_epo], all_scores_subjects_mean, color=colortoplot['Control_cue'], alpha=0.8, linestyle='dashed')
                    plt.plot(timeforplot[type_epo], all_scores_subjects_mean, color=colortoplot['Control_cue'], alpha=0.4)
                    plt.plot(timeforplot[type_epo], all_scores_subjects_mean*sig2, label='Control Cue', color=colortoplot['Control_cue'], linewidth=3)
                minforplot = min(all_scores_subjects_mean)
                maxforplot = max(all_scores_subjects_mean)
            else:
                plt.plot(timeforplot[type_epo], all_scores_subjects_mean, label='Control Cue', color=colortoplot['Control_cue'])
                minforplot = min(all_scores_subjects_mean)
                maxforplot = max(all_scores_subjects_mean)
            plotchanceandlimit([timeforplot[type_epo][0], timeforplot[type_epo][-1]], [0.5],
                               [minforplot, maxforplot], borders[type_epo])
            plt.legend()
            plt.title(file_to_ana + ' all subjects')

    if file_to_ana is 'Guided':

        type_epo = 'cue'
        rangeD = ['Object', 'Cue']

        for which_decod in rangeD:
            print(['type of decoding: ', which_decod])

            all_scores_subjects = list()
            for subj_nb, subject in enumerate(subjects_id):
                print(subject)

                fname = op.join(path_analyzed_data,
                                'results/decoding_together',
                                '%s_%s_%s_%s_%s.npy'
                                % (subject, file_to_ana,
                                   which_decod, type_epo,
                                   which_channels))

                if op.exists(fname):
                    score = np.load(fname)

                    all_scores_subjects.append(score)

            if len(all_scores_subjects) > 0:
                all_scores_subjects = np.array(all_scores_subjects)
                print(['all subjects before averaging :', all_scores_subjects.shape])  # noqa
                if len(all_scores_subjects) > 1:
                    if correct_mult_comp:
                        decod_p_values = decod_stats(all_scores_subjects - 0.5)
                    else:
                        _, decod_p_values = ttest_1samp(all_scores_subjects, 0.5)
                    sig1 = decod_p_values <= 0.05
                    sig2 = np.empty(len(decod_p_values))
                    sig2[:] = np.nan
                    sig2[np.where(decod_p_values <= 0.5)] = 1
                    all_scores_subjects_sem = np.std(all_scores_subjects, axis=0)/np.sqrt(len(all_scores_subjects))
                    all_scores_subjects_mean = all_scores_subjects.mean(0,)
                    # all_scores_subjects = all_scores_subjects.mean(0, keepdims=True)  # noqa
                else:
                    all_scores_subjects_mean = all_scores_subjects
                print(['all subjects after averaging :', all_scores_subjects_mean.shape])  # noqa

                # filtering for vizualization
                all_scores_subjects_mean = smooth_to_plot(all_scores_subjects_mean)
                # all_scores_subjects = filter_data(all_scores_subjects, 120, 0, 15)

                # 3. plot group figures
                if (len(all_scores_subjects) > 1 and plot_std):
                    mean1 = all_scores_subjects_mean + all_scores_subjects_sem
                    mean2 = all_scores_subjects_mean - all_scores_subjects_sem
                    minforplot = min(mean2)
                    maxforplot = max(mean1)
                    if testing_significance:
                        plt.fill_between(timeforplot[type_epo], mean1, mean2, color=colortoplot[which_decod], alpha=0.5)
                        plt.fill_between(timeforplot[type_epo], mean1, mean2, label=which_decod, color=colortoplot[which_decod], alpha=1, where=sig1)
                    else:
                        plt.fill_between(timeforplot[type_epo], mean1, mean2, label=which_decod, color=colortoplot[which_decod], alpha=0.5)
                        # plt.plot(timeforplot[type_epo], mean1, color=colortoplot[which_decod])
                        # plt.plot(timeforplot[type_epo], mean2, label=which_decod, color=colortoplot[which_decod])
                elif (len(all_scores_subjects) > 1 and testing_significance):
                    if fill_from_chance:
                        chance = np.empty(len(timeforplot[type_epo]))
                        chance.fill(0.5)
                        # plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod], alpha=0.5)
                        plt.plot(timeforplot[type_epo], all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod])
                        plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, color=colortoplot[which_decod], alpha=1, where=sig1)
                    else:
                        # plt.plot(timeforplot[type_epo], all_scores_subjects_mean, color=colortoplot[which_decod], alpha=0.8, linestyle='dashed')
                        plt.plot(timeforplot[type_epo], all_scores_subjects_mean, color=colortoplot[which_decod], alpha=0.4)
                        plt.plot(timeforplot[type_epo], all_scores_subjects_mean*sig2, label=which_decod, color=colortoplot[which_decod], alpha=1, linewidth=3)
                    minforplot = min(all_scores_subjects_mean)
                    maxforplot = max(all_scores_subjects_mean)
                else:
                    plt.plot(timeforplot[type_epo], all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod])
                    minforplot = min(all_scores_subjects_mean)
                    maxforplot = max(all_scores_subjects_mean)
                plotchanceandlimit([timeforplot[type_epo][0], timeforplot[type_epo][-1]], [0.5],
                                   [minforplot, maxforplot], borders[type_epo])
                plt.legend()
                plt.title(file_to_ana + ' ' + type_epo + ' all subjects')
