import os.path as op
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ttest_1samp

from base import decod_stats
from config import *
from basemy import *


# plot_each_session = True
plot_each_subject = True
plot_std = True
testing_significance = True
correct_mult_comp = False

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

# which_decod
colortoplot = {'Cue/Object': colors[4],
               'Cue': colors[1],
               'Object': colors[0],
               'Button': colors[2],
               'Modality': colors[3],
               'Resp_Screen_Object': colors[5],
               'Resp_Screen_Side': colors[7]}

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

                if plot_each_subject:
                    plt.figure(subj_nb+1)
                    plt.plot(timeforplot[type_epo], score, label=which_decod, color=colortoplot[which_decod])  # noqa
                    plotchanceandlimit([timeforplot[type_epo][0], timeforplot[type_epo][-1]], [0.5],
                                       [min(score), max(score)], borders[type_epo])
                    plt.legend()
                    plt.title(file_to_ana + ' ' + subject)

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
                all_scores_subjects_sem = np.std(all_scores_subjects, axis=0)/np.sqrt(len(all_scores_subjects))
            all_scores_subjects_mean = all_scores_subjects.mean(0,)
            # all_scores_subjects = all_scores_subjects.mean(0, keepdims=True)  # noqa
            print(['all subjects after averaging :', all_scores_subjects_mean.shape])  # noqa

            all_scores_subjects_mean = smooth_to_plot(all_scores_subjects_mean)

            # 3. plot group figures
            plt.figure(len(subjects_id)+1)
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
                chance = np.empty(len(timeforplot[type_epo]))
                chance.fill(0.5)
                # plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod], alpha=0.5)
                plt.plot(timeforplot[type_epo], all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod])
                plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, color=colortoplot[which_decod], alpha=1, where=sig1)
                minforplot = min(all_scores_subjects_mean)
                maxforplot = max(all_scores_subjects_mean)
            else:
                plt.plot(timeforplot[type_epo], all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod])
                minforplot = min(all_scores_subjects_mean)
                maxforplot = max(all_scores_subjects_mean)
            plotchanceandlimit([timeforplot[type_epo][0], timeforplot[type_epo][-1]], [0.5],
                               [minforplot, maxforplot], borders[type_epo])
            plt.legend()
            plt.title(file_to_ana + ' all subjects')

    if file_to_ana is 'Guided':

        # for y_nb, type_epo in enumerate(['cue', 'res', 'scr']):
        for y_nb, type_epo in enumerate(['cue']):
            print(['type of epoch: ', type_epo])

            if type_epo is 'scr':
                rangeD = ['Resp_Screen_Object', 'Resp_Screen_Side']
            else:
                rangeD = ['Object', 'Cue', 'Button', 'Modality']

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
                        if plot_each_subject:
                            plt.figure(100+10*(y_nb+1)+(subj_nb+1))
                            plt.plot(timeforplot[type_epo], score, label=which_decod, color=colortoplot[which_decod])  # noqa
                            plotchanceandlimit([timeforplot[type_epo][0], timeforplot[type_epo][-1]], [0.5],
                                               [min(score), max(score)], borders[type_epo])
                            plt.legend()
                            plt.title(file_to_ana + ' ' + type_epo + ' ' + subject)

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
                        all_scores_subjects_sem = np.std(all_scores_subjects, axis=0)/np.sqrt(len(all_scores_subjects))
                    all_scores_subjects_mean = all_scores_subjects.mean(0,)
                    # all_scores_subjects = all_scores_subjects.mean(0, keepdims=True)  # noqa
                    print(['all subjects after averaging: ', all_scores_subjects_mean.shape])  # noqa
                    # all_scores_subjects = all_scores_subjects.squeeze(0)

                    all_scores_subjects_mean = smooth_to_plot(all_scores_subjects_mean)

                    # 3. plot group figures
                    plt.figure(100+10*(y_nb+1)+len(subjects_id)+1)
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
                        chance = np.empty(len(timeforplot[type_epo]))
                        chance.fill(0.5)
                        # plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod], alpha=0.5)
                        plt.plot(timeforplot[type_epo], all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod])
                        plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, color=colortoplot[which_decod], alpha=1, where=sig1)
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

    if file_to_ana is 'Spontaneous':

        print('New type of Spontaneous')

        # for y_nb, type_epo in enumerate(['cue', 'res', 'scr']):
        for y_nb, type_epo in enumerate(['cue']):
            print(['type of epoch: ', type_epo])

            if type_epo is 'scr':
                rangeD = ['Resp_Screen_Side']
            else:
                rangeD = ['Button', 'Modality']

            for which_decod in rangeD:
                print(['type of decoding: ', which_decod])

                all_scores_subjects = list()
                for subj_nb, (subject, sessions) in enumerate(zip(subjects_id, session_subject)):  # noqa

                    go = 0
                    for session_nb, session in enumerate(sessions):
                        fname = op.join(path_data, session)
                        files = os.listdir(fname)
                        runs = list()
                        runs.extend(f for f in files if file_to_ana in f)
                        if len(runs) > 0:
                            go = 1
                    if go == 1:
                        print(subject)

                        fname = op.join(path_analyzed_data,
                                        'results/decoding_together',
                                        '%s_%s_%s_%s_%s.npy'
                                        % (subject, file_to_ana,
                                           which_decod, type_epo,
                                           which_channels))
                        if op.exists(fname):

                            score = np.load(fname)

                            if plot_each_subject:
                                plt.figure(500+100*(y_nb+1)+(subj_nb+1))
                                plt.plot(timeforplot[type_epo], score, label=which_decod, color=colortoplot[which_decod])  # noqa
                                plotchanceandlimit([timeforplot[type_epo][0], timeforplot[type_epo][-1]], [0.5],
                                                   [min(score), max(score)], borders[type_epo])
                                plt.legend()
                                plt.title(file_to_ana + ' ' + type_epo + ' ' + subject)

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
                        all_scores_subjects_sem = np.std(all_scores_subjects, axis=0)/np.sqrt(len(all_scores_subjects))
                    all_scores_subjects_mean = all_scores_subjects.mean(0)  # noqa
                    # all_scores_subjects = all_scores_subjects.mean(0, keepdims=True)  # noqa
                    print(['all subjects after averaging :', all_scores_subjects_mean.shape])  # noqa
                    all_scores_subjects_mean = smooth_to_plot(all_scores_subjects_mean)

                    # 3. plot group figures
                    plt.figure(500+100*(y_nb+1)+len(subjects_id)+1)
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
                        chance = np.empty(len(timeforplot[type_epo]))
                        chance.fill(0.5)
                        # plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod], alpha=0.5)
                        plt.plot(timeforplot[type_epo], all_scores_subjects_mean, label=which_decod, color=colortoplot[which_decod])
                        plt.fill_between(timeforplot[type_epo], chance, all_scores_subjects_mean, color=colortoplot[which_decod], alpha=1, where=sig1)
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
