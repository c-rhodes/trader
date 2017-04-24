# trader
Traffic Light Phases Aware Driving for Reduced Congestion

Running Locally (Tested on Ubuntu 16.04)
----------------------------------------
Download and install the following:

* https://www.python.org/downloads/
* https://sourceforge.net/projects/sumo/

The source contains three scenarios:

* pedestrian_crossing
* grid8
* abstract

Each scenario contains a `runner.py` script to run the simulation. Before running these scripts an environment variable `SUMO_HOME` must be defined, which contains the path to the SUMO source. For instance:

    export SUMO_HOME=/home/cullenrhodes/workspace/sumo/sumo-0.28.0
  
The typical workflow is as follows:

    cd pedestrian_crossing
    python runner.py --rundir baseline --nogui
    python runner.py --rundir trader --nogui --with-trader
    
The above will run the simulations for the baseline (without trader) and with trader. The files created during the simulation will be added to the specified `rundir` folder, i.e. `baseline` for the baseline simulation. This dir will contain the `tripinfo` XML files which are used to generated the statistics.

If you wish to run the simulation with the gui then do not specify the `--nogui` parameter. The `runner.py` scripts for the `grid8` and `abstract` scenarios also take an additional parameter `-n`, which specifies the number of vehicles in the simulation (default 3600).

In the root of the project there is a `stats.py` script that can be used to compare two simulations, for the previous example this would look like the following:

    python stats.py pedestrian_crossing/baseline pedestrian_crossing/trader -n 3
    
The `-n` flag tells the stats.py how many times the simulation was run, the default is 3. This script will output statistics for the Average Travel Time and Travel Time Index.
