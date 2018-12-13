

# **** path ************************************************************
computer = 'work'  # 'home' 'work' 'biowulf'
if computer is 'work':
    path_data = '/Users/vernetmc/Documents/MEG_data'
    path_analyzed_data = '/Users/vernetmc/Documents/MEG_analyzed_data'


# **** subjects ************************************************************
subjects_id = ['meg01', 'meg02']

# **** sessions ************************************************************
session_subject = [['meg01_20180622', 'meg01_20180801', 'meg01_20180927', 'meg01_20181016'],  # noqa
                   ['meg02_20180815', 'meg02_20180913', 'meg02_20180928', 'meg02_20181108']]  # noqa

# **** file ************************************************************
files_to_ana = ['JustCue', 'Guided', 'Spontaneous']
# files_to_ana = ['JustCue', 'Spontaneous']
# files_to_ana = ['JustCue', 'Guided']
# files_to_ana = ['JustCue']
# files_to_ana = ['Guided']
# files_to_ana = ['Spontaneous']
# file_to_ana = 'SpontaneousMotor'
# file_to_ana = 'TriggeredMotor'
# file_to_ana = 'mar_MarGuided'


# **** which channels to decode *****************************************
which_channels = 'meg'
# which_channels = 'eyes'
# which_channels = 'trigger'
# which_channels = 'all'


# **** if you want to decode the response screen with the trigger ****
# decod_scr_with_trigger = 0
decod_scr_with_trigger = 1
