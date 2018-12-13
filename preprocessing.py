import numpy as np
import mne
from mne.io import read_raw_ctf
import os.path as op
import os
from mne import Epochs
import matplotlib.pyplot as plt

# from sklearn.cross_validation import StratifiedKFold

from config import *
from basemy import *


directory = thedirectory(path_analyzed_data, which_channels)

# **** loading files ****
n = 1
for subject, sessions in zip(subjects_id, session_subject):
    for session_nb, session in enumerate(sessions):
    # for session_nb_V0, session in enumerate(sessions):
    #     session_nb = 3
        for file_to_ana in files_to_ana:
            fname7 = op.join(path_data, session)
            files = os.listdir(fname7)
            runs = list()
            runs.extend(f for f in files if file_to_ana in f)

            for run_number, this_run in enumerate(runs):
                run_to_load = op.join(fname7, this_run)
                raw = read_raw_ctf(run_to_load, preload=True)

                # **** reading the triggering channel ****
                trigger_ch_number = raw.ch_names.index('UPPT001')
                trigger = raw.get_data()[trigger_ch_number]

                # **** reading the eye movements channels ****
                raw_eyeA = raw.get_data()[raw.ch_names.index('UADC009-2104')]
                raw_eyeB = raw.get_data()[raw.ch_names.index('UADC010-2104')]
                raw_eyes = np.array([raw_eyeA, raw_eyeB])

                # **** reading the button press channels and photodiode ****
                button_red = raw.get_data()[raw.ch_names.index('UADC005-2104')]
                button_200 = raw.get_data()[raw.ch_names.index('UADC007-2104')]
                photodiode = raw.get_data()[raw.ch_names.index('UADC016-2104')]
                photodiode = photodiode*10.0

                # **** transforming the button presses in one channel ****
                red_value = np.where([item > 2 for item in button_red])
                blue_value = np.where([item > 2 for item in button_200])
                button_press = np.copy(button_red)
                button_press[:] = 0
                button_press[red_value] = 1
                button_press[blue_value] = 2

                # **** removing wrong values in the trigger chanel ****
                if file_to_ana is 'JustCue':
                    good_values = [0, 10, 20, 30, 100, 110, 120]
                if file_to_ana is 'Guided':
                    good_values = [0, 10, 15, 20, 25, 40, 45, 50, 55, 60, 65,
                                   70, 75, 100, 110, 130, 135, 140, 145]
                if file_to_ana is 'Spontaneous':
                    good_values = [0, 10, 40, 50, 60, 65,
                                   70, 75, 100, 110, 130, 135, 140, 145]
                # if (file_to_ana is 'SpontaneousMotor') or \
                #    (file_to_ana is 'TriggeredMotor') or \
                #    (file_to_ana is 'mar_MarGuided'):
                #     good_values = [0, 10, 60, 65, 70, 75]
                wrong = np.where(np.array([item not in good_values
                                           for item in trigger]))
                trigger[wrong[0]] = trigger[wrong[0]+1]
                if (file_to_ana is 'Guided' and decod_scr_with_trigger == 1):
                    trigger[np.where(np.array([item == 50 for item
                                               in trigger]))] = 42
                data = raw.get_data()
                data[trigger_ch_number] = trigger
                raw._data = data

                # **** plotting to check ****
                # check time-lag between photodiode and trigger for vision
                # no time lag between button press and trigger for motor
                if computer is 'work':
                    plt.figure(n)
                    n = n+1
                    plt.plot(photodiode)
                    plt.plot(trigger)
                    plt.plot(button_press)
                    plt.figure(n)
                    n = n+1
                    plt.plot(raw_eyes[0])
                    plt.plot(raw_eyes[1])

                # **** detecting the events from the triggering channels ****
                events_meg = mne.find_events(raw, stim_channel="UPPT001",
                                             consecutive=True,
                                             shortest_event=1)
                time_lag = 24

                # be careful: for the 2 first sessions of s01 and s02
                # 50 is motor for JustCue
                # it has been changed to 30 for the remaining of the experiment
                if (file_to_ana is 'Guided' and decod_scr_with_trigger == 1):  # noqa
                    elements_visuel = [0, 10, 15, 20, 25, 40, 45, 42, 55,
                                       100, 110, 120]
                else:
                    elements_visuel = [0, 10, 15, 20, 25, 40, 45, 50, 55,
                                       100, 110, 120]
                elements_motor = [30, 60, 65, 70, 75, 130, 135, 140, 145]
                events_vis = np.where(np.in1d(events_meg[:, 2],
                                              elements_visuel))
                events_meg[events_vis, 0] = events_meg[events_vis, 0] + \
                    time_lag

                # change the cue code according to subject's answer for Guided
                code_R1 = [60, 65, 70, 75]
                responses = np.where(np.in1d(events_meg[:, 2], code_R1))
                events_meg_cue = events_meg.copy()
                events_meg_res = events_meg.copy()

                # change the cue code according to the feedback for JustCue
                code_F = [100, 110, 120]
                feedback = np.where(np.in1d(events_meg[:, 2], code_F))
                events_meg_fee = events_meg.copy()

                # if file_to_ana is 'JustCue':
                #     event_id = {'Square': 20, 'Round': 10}

                if file_to_ana is 'JustCue':
                    print('yaya')
                    for eve in feedback[0]:
                        print(eve)
                        if events_meg_fee[eve-1, 2] in [30, 50]:
                            events_meg_fee[eve-2, 2] = \
                                1000*events_meg_fee[eve-2, 2] + \
                                events_meg_fee[eve, 2]
                        else:
                            events_meg_fee[eve-1, 2] = \
                                1000*events_meg_fee[eve-1, 2] + \
                                events_meg_fee[eve, 2]
                    code_possible_fee = [10100, 10110, 10120,  # round  no feedback, correct, incorrect  # noqa
                                        20100, 20110, 20120]  # square no feedback, correct, incorrect  # noqa
                    event_of_interest_fee = np.where(
                        np.in1d(events_meg_fee[:, 2], code_possible_fee))

                if file_to_ana is 'Guided':
                    for eve in responses[0]:
                        events_meg_cue[eve-2, 2] = \
                            100*events_meg_cue[eve-2, 2] + \
                            events_meg_cue[eve, 2]
                        events_meg_res[eve, 2] = \
                            100*events_meg_res[eve-2, 2] + \
                            events_meg_res[eve, 2]
                    code_possible = [1060, 1065, 1070, 1075,  # co ro LT/I RT/I
                                     1560, 1565, 1570, 1575,  # bi ro LT/I RT/I
                                     2060, 2065, 2070, 2075,  # co sq LT/I RT/I
                                     2560, 2565, 2570, 2575]  # bi sq LT/I RT/I
                    event_of_interest_cue = np.where(
                        np.in1d(events_meg_cue[:, 2], code_possible))
                    event_of_interest_res = np.where(
                        np.in1d(events_meg_res[:, 2], code_possible))
                    if decod_scr_with_trigger == 1:
                        event_id_RS1 = {'cow_text_left': 40,
                                        'bicycle_text_left': 45,
                                        'cow_text_right': 42,
                                        'bicycle_text_right': 55}
                    else:
                        event_id_RS1 = {'cow_text_left': 40,
                                        'bicycle_text_left': 45,
                                        'cow_text_right': 50,
                                        'bicycle_text_right': 55}

                if file_to_ana is 'Spontaneous':
                    for eve in responses:
                        events_meg_cue[eve-2, 2] = \
                            100*events_meg_cue[eve-2, 2] + \
                            events_meg_cue[eve, 2]
                        events_meg_res[eve, 2] = \
                            100*events_meg_res[eve-2, 2] + \
                            events_meg_res[eve, 2]
                    code_possible = [1060, 1065, 1070, 1075]  # LT/I RT/I
                    event_of_interest_cue = np.where(
                        np.in1d(events_meg_cue[:, 2], code_possible))
                    event_of_interest_res = np.where(
                        np.in1d(events_meg_res[:, 2], code_possible))
                    event_id_RS1 = {'text_left': 40, 'text_right': 50}

                # **** filtering ****
                raw.filter(0.05, 30)

                # **** epoching ****
                if (file_to_ana is 'Guided' or file_to_ana is 'Spontaneous'):

                    for type_epo in ['cue', 'res', 'scr']:

                        if type_epo is 'cue':
                            epochs = Epochs(raw,
                                                events_meg_cue[event_of_interest_cue], # noqa
                                                event_id=None,
                                                tmin=-0.5, tmax=7,
                                                preload=True,
                                                baseline=(None, 0), decim=5)
                        elif type_epo is 'res':
                            epochs = Epochs(raw,
                                                events_meg_res[event_of_interest_res],# noqa
                                                event_id=None,
                                                tmin=-4, tmax=4, preload=True,
                                                baseline=(None, 0), decim=5)
                        elif type_epo is 'scr':
                            epochs = Epochs(raw, events_meg, event_id_RS1,
                                                tmin=-4, tmax=4, preload=True,
                                                baseline=(None, 0), decim=5)

                        # **** resampling and keeping only MEG channel ****
                        # epochs_cue.resample(120)
                        if which_channels is 'meg':
                            epochs.pick_types()

                        # **** save epochs ****
                        directory = thedirectory(path_analyzed_data, which_channels)
                        fname8 = op.join(directory,
                                        '%s_%s_session%s_run%s_epochs_%s-epo.fif'
                                        % (subject, file_to_ana,
                                           session_nb, run_number, type_epo))
                        epochs.save(fname8)

                else:

                    # if file_to_ana is 'JustCue':
                    #     epochs = Epochs(raw, events_meg, event_id,
                    #                     tmin=-0.5, tmax=7, preload=True,
                    #                     baseline=(None, 0), decim=5)

                    if file_to_ana is 'JustCue':
                        epochs = Epochs(raw,
                                        events_meg_fee[event_of_interest_fee],
                                        event_id=None,
                                        tmin=-0.5, tmax=7, preload=True,
                                        baseline=(None, 0), decim=5)

                    # **** resampling and keeping only MEG channel ****
                    # epochs_cue.resample(120)
                    if which_channels is 'meg':
                        epochs.pick_types()

                    # **** save epochs ****
                    directory = thedirectory(path_analyzed_data, which_channels)
                    fname9 = op.join(directory,
                                    '%s_%s_session%s_run%s-epo.fif'
                                    % (subject, file_to_ana,
                                       session_nb, run_number))
                    epochs.save(fname9)

# **** NEW PART ****
# **** Concatenate the run together ****

if 'epochs' in locals():
    del epochs

for file_to_ana in files_to_ana:

    if file_to_ana is 'Guided':

        for type_epo in ['cue', 'res', 'scr']:
            for subj_nb, (subject, sessions) in enumerate(zip(subjects_id, session_subject)): # noqa
                for session_nb, session in enumerate(sessions):
                # for session_nb_V0, session in enumerate(sessions):
                #     session_nb = 3
                    # ******** defining the runs to load *********
                    fname1 = op.join(path_data, session)
                    files = os.listdir(fname1)
                    runs = list()
                    runs.extend(f for f in files if file_to_ana in f)

                    # ******** loading and concatenating the epochs *********
                    for run_number, this_run in enumerate(runs):
                        fname2 = op.join(directory,
                                        '%s_%s_session%s_run%s_epochs_%s-epo.fif'
                                        % (subject, file_to_ana,
                                           session_nb, run_number, type_epo))

                        if 'epochs' not in locals():
                            epochs = mne.read_epochs(fname2)
                        else:
                            epochs2 = mne.read_epochs(fname2)
                            epochs2.info['dev_head_t'] = \
                                epochs.info['dev_head_t']
                            epochs = mne.concatenate_epochs([epochs, epochs2])

                    # **** save epochs ****
                    if 'epochs' in locals():
                        fname3 = op.join(directory,
                                        '%s_%s_session%s_epochs_%s-epo.fif'
                                        % (subject, file_to_ana,
                                           session_nb, type_epo))
                        epochs.save(fname3)
                        print(fname3)
                        del epochs

    if file_to_ana is 'JustCue':

        for subj_nb, (subject, sessions) in enumerate(zip(subjects_id, session_subject)): # noqa
            for session_nb, session in enumerate(sessions):
            # for session_nb_V0, session in enumerate(sessions):
            #     session_nb = 3
                # ******** defining the runs to load *********
                fname1 = op.join(path_data, session)
                files = os.listdir(fname1)
                runs = list()
                runs.extend(f for f in files if file_to_ana in f)

                # ******** loading and concatenating the epochs *********
                for run_number, this_run in enumerate(runs):
                    fname2 = op.join(directory,
                                    '%s_%s_session%s_run%s-epo.fif'
                                    % (subject, file_to_ana,
                                       session_nb, run_number))

                    if 'epochs' not in locals():
                        epochs = mne.read_epochs(fname2)
                    else:
                        epochs2 = mne.read_epochs(fname2)
                        epochs2.info['dev_head_t'] = \
                            epochs.info['dev_head_t']
                        epochs = mne.concatenate_epochs([epochs, epochs2])

                # **** save epochs ****
                if 'epochs' in locals():
                    fname3 = op.join(directory,
                                    '%s_%s_session%s-epo.fif'
                                    % (subject, file_to_ana,
                                       session_nb))
                    epochs.save(fname3)
                    print(fname3)
                    del epochs

    if file_to_ana is 'Spontaneous':

        for type_epo in ['cue', 'res', 'scr']:

            for subj_nb, (subject, sessions) in enumerate(zip(subjects_id, session_subject)): # noqa
                for session_nb, session in enumerate(sessions):
                # for session_nb_V0, session in enumerate(sessions):
                #     session_nb = 3

                    # ******** defining the runs to load *********
                    fname4 = op.join(path_data, session)
                    files = os.listdir(fname4)
                    runs = list()
                    runs.extend(f for f in files if file_to_ana in f)

                    # ******** loading and concatenating the epochs *******
                    for run_number, this_run in enumerate(runs):

                        fname5 = op.join(directory,
                                        '%s_%s_session%s_run%s_epochs_%s-epo.fif'  # noqa
                                        % (subject, file_to_ana,
                                           session_nb, run_number,
                                           type_epo))

                        if 'epochs' not in locals():
                            epochs = mne.read_epochs(fname5)
                        else:
                            epochs2 = mne.read_epochs(fname5)
                            epochs2.info['dev_head_t'] = \
                                epochs.info['dev_head_t']
                            epochs = mne.concatenate_epochs([epochs, epochs2])

                    # **** save epochs ****
                    if 'epochs' in locals():
                        fname6 = op.join(directory,
                                        '%s_%s_session%s_epochs_%s-epo.fif'
                                        % (subject, file_to_ana,
                                           session_nb, type_epo))
                        epochs.save(fname6)
                        print(fname6)
                        del epochs
