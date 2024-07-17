'''
    ---------------------------------------------------------------------------
    OpenCap processing: main.py
    ---------------------------------------------------------------------------
    Copyright 2022 Stanford University and the Authors
    
    Author(s): Antoine Falisse, Scott Uhlrich
    
    Licensed under the Apache License, Version 2.0 (the "License"); you may not
    use this file except in compliance with the License. You may obtain a copy
    of the License at http://www.apache.org/licenses/LICENSE-2.0
    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    
    This code makes use of CasADi, which is licensed under LGPL, Version 3.0;
    https://github.com/casadi/casadi/blob/master/LICENSE.txt.
    
    Install requirements:
        - Visit https://github.com/stanfordnmbl/opencap-processing for details.        
        - Third-party software packages:
            - CMake: https://cmake.org/download/.
            - (Windows only)
                - Visual studio: https://visualstudio.microsoft.com/downloads/.
                    - Make sure you install C++ support.
                    - Code tested with community editions 2017-2019-2022.
            
    Please contact us for any questions: https://www.opencap.ai/#contact
'''

# %% Directories, paths, and imports. You should not need to change anything.
import os
import sys

from InquirerPy import inquirer

from Adapt_to_usage.DataController import DataController
from UtilsDynamicSimulations.OpenSimAD.mainOpenSimAD import run_tracking
from UtilsDynamicSimulations.OpenSimAD.utilsOpenSimAD import processInputsOpenSimAD, plotResultsOpenSimAD
from utils import *

baseDir = os.getcwd()
opensimADDir = os.path.join(baseDir, 'UtilsDynamicSimulations', 'OpenSimAD')
sys.path.append(baseDir)
sys.path.append(opensimADDir)

# from utilsOpenSimAD import processInputsOpenSimAD, plotResultsOpenSimAD
# from mainOpenSimAD import run_tracking

# %% User inputs.
'''
Please provide:
    
    session_id:     This is a 36 character-long string. You can find the ID of
                    all your sessions at https://app.opencap.ai/sessions.
                    
    trial_name:     This is the name of the trial you want to simulate. You can
                    find all trial names after loading a session.
                    
    motion_type:    This is the type of activity you want to simulate. Options
                    are 'running', 'walking', 'drop_jump', 'sit-to-stand', and
                    'squats'. We provide pre-defined settings that worked well
                    for this set of activities. If your activity is different,
                    select 'other' to use generic settings or set your own
                    settings in settingsOpenSimAD. See for example how we tuned
                    the 'running' settings to include periodic constraints in
                    the 'my_periodic_running' settings.
                    
    time_window:    This is the time interval you want to simulate. It is
                    recommended to simulate trials shorter than 2s. Set to []
                    to simulate full trial. For 'squats' or 'sit_to_stand', we
                    built segmenters to separate the different repetitions. In
                    such case, instead of providing the time_window, you can
                    provide the index of the repetition (see below) and the
                    time_window will be automatically computed.
                    
    repetition:     Only if motion_type is 'sit_to_stand' or 'squats'. This
                    is the index of the repetition you want to simulate (0 is 
                    first). There is no need to set the time_window. 
                    
    case:           This is a string that will be appended to the file names
                    of the results. Dynamic simulations are optimization
                    problems, and it is common to have to play with some
                    settings to get the problem to converge or converge to a
                    meaningful solution. It is useful to keep track of which
                    solution corresponds to which settings; you can then easily
                    compare results generated with different settings.
                    
    (optional)
    treadmill_speed:This an optional parameter that indicates the speed of
                    the treadmill in m/s. A positive value indicates that the
                    subject is moving forward. You should ignore this parameter
                    or set it to 0 if the trial was not measured on a
                    treadmill. By default, treadmill_speed is set to 0.
    (optional)
    contact_side:   This an optional parameter that indicates on which foot to
                    add contact spheres to model foot-ground contact. It might
                    be useful to only add contact spheres on one foot if only
                    that foot is in contact with the ground. We found this to
                    be helpful for simulating for instance single leg dropjump
                    as it might prevent the optimizer to cheat by using the
                    other foot to stabilize the model. Options are 'all', 
                    'left', and 'right'. By default, contact_side is set to
                    'all', meaning that contact spheres are added to both feet.
    
See example inputs below for different activities. Please note that we did not
verify the biomechanical validity of the results; we only made sure the
simulations converged to kinematic solutions that were visually reasonable.

Please contact us for any questions: https://www.opencap.ai/#contact
'''


def menu():
    print()
    res = inquirer.select(message="What do you want to do?",
                          choices=["Setup datas", "Disconnect from Opencap", "exit"]).execute()
    print()

    if res == "Disconnect from Opencap":
        if os.path.exists(".env"):
            os.remove(".env")
            print("You have been disconnected from OpenCap. Please restart the program to reconnect.")
        else:
            print("No active session found to disconnect.")
        sys.exit()
    elif res == "exit":
        sys.exit()
    else:
        dc.setup()


dc = DataController()
menu()

solveProblem = True
analyzeResults = True

dataFolder = os.path.join(baseDir, 'Data')

if not 'contact_side' in locals():
    contact_side = 'all'

settings = processInputsOpenSimAD(baseDir, dataFolder, dc.session_id, dc.trial_name,
                                  dc.motion_type, time_window=dc.time_window, repetition=dc.repetition,
                                  treadmill_speed=dc.treadmill_speed, contact_side=contact_side)

# %% Simulation.
run_tracking(baseDir, dataFolder, dc.session_id, settings, case=dc.case,
             solveProblem=solveProblem, analyzeResults=analyzeResults)

# %% Plots.
# To compare different cases, add to the cases list, eg cases=['0','1'].
plotResultsOpenSimAD(dataFolder, dc.session_id, dc.trial_name, settings, cases=[dc.case])
