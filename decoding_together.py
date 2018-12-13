import os
import os.path as op
import numpy as np
import mne

from mne.decoding import SlidingEstimator, cross_val_multiscore
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

from config import *
from basemy import *


# make estimator
clf = make_pipeline(StandardScaler(), LogisticRegression())
clf = SlidingEstimator(clf, scoring='roc_auc', n_jobs=-1)

directory = thedirectory(path_analyzed_data, which_channels)
directorydecod = thedirectorydecod(path_analyzed_data, 'results/decoding_together')

for file_to_ana in files_to_ana:

    # ******** the codes *********
    cow_codes_scr, textleft_codes, cow_codes, round_codes, left_codes, text_codes = thecodes(file_to_ana, decod_scr_with_trigger)

    if file_to_ana is 'Guided':

        for type_epo in ['cue', 'res', 'scr']:
        # for type_epo in ['res', 'scr']:
            for subj_nb, (subject, sessions) in enumerate(zip(subjects_id, session_subject)): # noqa
                for session_nb, session in enumerate(sessions):

                    # ******** defining the runs to load *********
                    fname = op.join(path_data, session)
                    files = os.listdir(fname)
                    runs = list()
                    runs.extend(f for f in files if file_to_ana in f)

                    # ******** loading and concatenating the epochs *********
                    if runs:
                        fname = op.join(directory,
                                        '%s_%s_session%s_epochs_%s-epo.fif'  # noqa
                                        % (subject, file_to_ana,
                                           session_nb,
                                           type_epo))

                        if 'epochs' not in locals():
                            epochs = mne.read_epochs(fname)
                        else:
                            epochs2 = mne.read_epochs(fname)
                            epochs2.info['dev_head_t'] = \
                                epochs.info['dev_head_t']
                            if session == 'meg13_20181113':
                                epochs.pick_channels(epochs2.ch_names)
                            epochs = mne.concatenate_epochs([epochs, epochs2])

                if 'epochs' in locals():
                    # ******** one y per subject for all Guided files *********
                    y = epochs.events[:, 2].copy()
                    data_to_dec = datatodec(which_channels, epochs)

                    # ******** what to decode *********
                    if type_epo is 'scr':
                        y1 = whattodecod(cow_codes_scr, y)  # cow vs. bicycle
                        y2 = whattodecod(textleft_codes, y)  # textleft vs. imageleft # noqa
                        rangeY = [y1, y2]
                        rangeD = ['Resp_Screen_Object', 'Resp_Screen_Side']
                    else:
                        y1 = whattodecod(cow_codes, y)  # cow vs. bicycle
                        y2 = whattodecod(round_codes, y)  # round vs. square
                        y3 = whattodecod(left_codes, y)  # left vs. right
                        y4 = whattodecod(text_codes, y)  # text vs. image
                        rangeY = [y1, y2, y3, y4]
                        rangeD = ['Object', 'Cue', 'Button', 'Modality']

                    # ******** decoding and saving *********
                    for nb_yy, (yy, which_decod) in enumerate(zip(rangeY, rangeD)):

                        scores = cross_val_multiscore(clf, data_to_dec,
                                                      yy, cv=5,
                                                      n_jobs=-1)
                        scores = scores.mean(0)
                        fname = op.join(directorydecod,
                                        '%s_%s_%s_%s_%s.npy'
                                        % (subject, file_to_ana,
                                           which_decod, type_epo,
                                           which_channels))
                        np.save(fname, scores)

                    del epochs

    if file_to_ana is 'JustCue':

        for subj_nb, (subject, sessions) in enumerate(zip(subjects_id, session_subject)): # noqa
            for session_nb, session in enumerate(sessions):

                # ******** defining the runs to load *********
                fname = op.join(path_data, session)
                files = os.listdir(fname)
                runs = list()
                runs.extend(f for f in files if file_to_ana in f)

                # ******** loading and concatenating the epochs *********
                if runs:
                    fname = op.join(directory,
                                    '%s_%s_session%s-epo.fif'
                                    % (subject, file_to_ana, session_nb))

                    if 'epochs' not in locals():
                        epochs = mne.read_epochs(fname)
                    else:
                        epochs2 = mne.read_epochs(fname)
                        epochs2.info['dev_head_t'] = \
                            epochs.info['dev_head_t']
                        if session == 'meg13_20181113':
                            epochs.pick_channels(epochs2.ch_names)
                        elif (session == 'meg13_20181116' or session == 'meg13_20181119'):  # noqa
                            epochs2.pick_channels(epochs.ch_names)
                        epochs = mne.concatenate_epochs([epochs, epochs2])

            if 'epochs' in locals():
                # ******** one y per subject for all JustCue files *********
                y = epochs.events[:, 2].copy()
                data_to_dec = datatodec(which_channels, epochs)

                # ******** what to decode *********
                y1 = whattodecod(round_codes, y)  # round vs. square
                rangeY = [y1]
                rangeD = ['Cue']

                # ******** decoding and saving *********
                for nb_yy, (yy, which_decod) in enumerate(zip(rangeY, rangeD)):

                    scores = cross_val_multiscore(clf, data_to_dec,
                                                  yy, cv=5,
                                                  n_jobs=-1)
                    scores = scores.mean(0)
                    fname = op.join(directorydecod,
                                    '%s_%s_%s_%s.npy'
                                    % (subject, file_to_ana,
                                       which_decod,
                                       which_channels))
                    np.save(fname, scores)

                del epochs

    if file_to_ana is 'Spontaneous':
        print('Spontaneous')
        for subj_nb, (subject, sessions) in enumerate(zip(subjects_id, session_subject)): # noqa

            # ******** one y per subject for all Spontaneous (old) files *********  # noqa
            if 'epochs' in locals():
                y = epochs.events[:, 2].copy()
                data_to_dec = datatodec(which_channels, epochs)

                # ******** what to decode *********
                y1 = whattodecod(left_codes, y)  # left vs. right
                y2 = whattodecod(text_codes, y)  # text vs. image
                rangeY = [y1, y2]
                rangeD = ['Button', 'Modality']

                # ******** decoding and saving *********
                for nb_yy, (yy, which_decod) in enumerate(zip(rangeY, rangeD)):

                    scores = cross_val_multiscore(clf, data_to_dec,
                                                  yy, cv=5,
                                                  n_jobs=-1)
                    scores = scores.mean(0)
                    fname = op.join(directorydecod,
                                    '%s_%s_earlysessions_%s_%s.npy'
                                    % (subject, file_to_ana,
                                       which_decod,
                                       which_channels))
                    np.save(fname, scores)

                del epochs

        for type_epo in ['cue', 'res', 'scr']:

            for subj_nb, (subject, sessions) in enumerate(zip(subjects_id, session_subject)): # noqa
                for session_nb, session in enumerate(sessions):

                    # ******** defining the runs to load *********
                    fname = op.join(path_data, session)
                    files = os.listdir(fname)
                    runs = list()
                    runs.extend(f for f in files if file_to_ana in f)

                    # ******** loading and concatenating the epochs *******
                    if runs:
                        fname = op.join(directory,
                                        '%s_%s_session%s_epochs_%s-epo.fif'  # noqa
                                        % (subject, file_to_ana,
                                           session_nb,
                                           type_epo))

                        if 'epochs' not in locals():
                            epochs = mne.read_epochs(fname)
                        else:
                            epochs2 = mne.read_epochs(fname)
                            epochs2.info['dev_head_t'] = \
                                epochs.info['dev_head_t']
                            epochs = mne.concatenate_epochs([epochs, epochs2])

                # ******** one y per subject for all Spontaneous (new) files *********  # noqa
                if 'epochs' in locals():
                    y = epochs.events[:, 2].copy()
                    data_to_dec = datatodec(which_channels, epochs)

                    # ******** what to decode *********
                    if type_epo is 'scr':
                        y1 = whattodecod(textleft_codes, y)  # textleft vs. imageleft   # noqa
                        rangeY = [y1]
                        rangeD = ['Resp_Screen_Side']
                    else:
                        y1 = whattodecod(left_codes, y)  # left vs. right
                        y2 = whattodecod(text_codes, y)  # text vs. image
                        rangeY = [y1, y2]
                        rangeD = ['Button', 'Modality']

                    # ******** decoding and saving *********
                    for nb_yy, (yy, which_decod) in enumerate(zip(rangeY, rangeD)):

                        scores = cross_val_multiscore(clf, data_to_dec,
                                                      yy, cv=5,
                                                      n_jobs=-1)
                        scores = scores.mean(0)
                        fname = op.join(directorydecod,
                                        '%s_%s_%s_%s_%s.npy'
                                        % (subject, file_to_ana,
                                           which_decod, type_epo,
                                           which_channels))
                        np.save(fname, scores)

                    del epochs
