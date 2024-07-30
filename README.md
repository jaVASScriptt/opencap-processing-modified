# OpenCap Processing
This code is a copy of OpenCap Processing, with some additional features and a better user experience. The original code can be found [here](https://github.com/stanfordnmbl/opencap-processing).

## Install requirements
### General
1. Install [Anaconda](https://www.anaconda.com/)
2. Open Anaconda prompt
3. Create environment (python 3.11 recommended): `conda create -n opencap-processing python=3.11`
4. Activate environment: `conda activate opencap-processing`
5. Install OpenSim: `conda install -c opensim-org opensim=4.5=py311np123`
    - Test that OpenSim was successfully installed:
        - Start python: `python`
        - Import OpenSim: `import opensim`
            - If you don't get any error message at this point, you should be good to go.
        - You can also double check which version you installed : `opensim.GetVersion()`
        - Exit python: `quit()`
    - Visit this [webpage](https://opensimconfluence.atlassian.net/wiki/spaces/OpenSim/pages/53116061/Conda+Package) for more details about the OpenSim conda package.
6. Clone the repository to your machine: 
    - Navigate to the directory where you want to download the code: eg. `cd Documents`. Make sure there are no spaces in this path.
    - Clone the repository: `git clone https://github.com/stanfordnmbl/opencap-processing.git`
    - Navigate to the directory: `cd opencap-processing`
8. Install required packages: `python -m pip install -r requirements.txt`
9. Run `python main.py` 
    
### Muscle-driven simulations
1. **Windows only**: Install [Visual Studio](https://visualstudio.microsoft.com/downloads/)
    - The Community variant is sufficient and is free for everyone.
    - During the installation, select the *workload Desktop Development with C++*.
    - The code was tested with the 2017, 2019, and 2022 Community editions.
2. **Linux only**: Install OpenBLAS libraries
    - `sudo apt-get install libopenblas-base`
