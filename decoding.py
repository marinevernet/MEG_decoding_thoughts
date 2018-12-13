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
directorydecod = thedirectorydecod(path_analyzed_data, 'results/decoding')

for file_to_ana in files_to_ana:

    # ******** the codes *********
    cow_codes_scr, textleft_codes, cow_codes, round_codes, left_codes, text_codes = thecodes(file_to_ana, decod_scr_with_trigger)

    for subj_nb, (subject, sessions) in enumerate(zip(subjects_id, session_subject)): # noqa
        for session_nb, session in enumerate(sessions):

            # ******** defining the runs to load *********
            fname = op.join(path_data, session)
            files = os.listdir(fname)
            runs = list()
            runs.extend(f for f in files if file_to_ana in f)

            if runs:

                if file_to_ana is 'JustCue':

                    # ******** loading the epochs *********
                    fname = op.join(directory,
                                    '%s_%s_session%s-epo.fif'
                                    % (subject, file_to_ana, session_nb))

                    epochs = mne.read_epochs(fname)
                    y = epochs.events[:, 2].copy()
                    data_to_dec = datatodec(which_channels, epochs)

                    # ******** what to decode *********
                    y1 = whattodecod(round_codes, y)  # round vs. square
                    rangeY = [y1]
                    rangeD = ['Cue']

                    # ******** decoding and saving *********
                    for nb_yy, (yy, which_decod) in enumerate(zip(rangeY,
                                                                  rangeD)):

                        scores = cross_val_multiscore(clf, data_to_dec,
                                                      yy, cv=5,
                                                      n_jobs=-1)
                        scores = scores.mean(0)
                        fname = op.join(directorydecod,
                                        '%s_%s_session%s_%s_%s.npy'
                                        % (subject, file_to_ana,
                                           session_nb,
                                           which_decod,
                                           which_channels))
                        np.save(fname, scores)

                if (file_to_ana is 'Guided' or file_to_ana is 'Spontaneous'):

                    for type_epo in ['cue', 'res', 'scr']:

                        # ******** loading the epochs *********
                        fname = op.join(directory,
                                        '%s_%s_session%s_epochs_%s-epo.fif'  # noqa
                                        % (subject, file_to_ana,
                                           session_nb,
                                           type_epo))

                        epochs = mne.read_epochs(fname)
                        y = epochs.events[:, 2].copy()
                        data_to_dec = datatodec(which_channels, epochs)

                        if file_to_ana is 'Guided':

                            # ******** what to decode *********
                            if type_epo is 'scr':
                                y1 = whattodecod(cow_codes_scr, y)  # cow vs. bicycle  # noqa
                                y2 = whattodecod(textleft_codes, y)  # textleft vs. imageleft  # noqa
                                rangeY = [y1, y2]
                                rangeD = ['Resp_Screen_Object', 'Resp_Screen_Side']  # noqa
                            else:
                                y1 = whattodecod(cow_codes, y)  # cow vs. bicycle  # noqa
                                y2 = whattodecod(round_codes, y)  # round vs. square  # noqa
                                y3 = whattodecod(left_codes, y)  # left vs. right  # noqa
                                y4 = whattodecod(text_codes, y)  # text vs. image  # noqa
                                rangeY = [y1, y2, y3, y4]
                                rangeD = ['Object', 'Cue', 'Button', 'Modality']  # noqa

                        if file_to_ana is 'Spontaneous':

                            # ******** what to decode *********
                            if type_epo is 'scr':
                                y1 = whattodecod(textleft_codes, y)  # textleft vs. imageleft  # noqa
                                rangeY = [y1]
                                rangeD = ['Resp_Screen_Side']
                            else:
                                y1 = whattodecod(left_codes, y)  # left vs. right  # noqa
                                y2 = whattodecod(text_codes, y)  # text vs. image  # noqa
                                rangeY = [y1, y2]
                                rangeD = ['Button', 'Modality']

                        # ******** decoding and saving *********
                        for nb_yy, (yy, which_decod) in enumerate(zip(rangeY,
                                                                      rangeD)):

                            scores = cross_val_multiscore(clf, data_to_dec,
                                                          yy, cv=5,
                                                          n_jobs=-1)
                            scores = scores.mean(0)
                            fname = op.join(directorydecod,
                                            '%s_%s_session%s_%s_%s_%s.npy'  # noqa
                                            % (subject, file_to_ana,
                                               session_nb,
                                               which_decod, type_epo,
                                               which_channels))
                            np.save(fname, scores)
