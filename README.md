# Project summary
## Introduction
This application is extracting raw dislocation segment data from LAMMPS dump files and loading them into CSV files. 
As well as calculating the distance between a pair of dislocations and its average. 

# How to run
This application has 2 ways to run, Command-Line Interface or execute (`main_load_csv.py` and `main_calculate_distance.py`)
## Command-Line Interface
```commandline
python lammps_cli_interface.py -h

Extracting segments data from LAMMPS dump files and load all segment data into CSV files
optional arguments:
  -h, --help           show this help message and exit
  -d, --dumpfile_path  Path pointing to LAMMPS dump files
  -s, --save_path      Path pointing to a saved directory
  -p DUMPFILE_PREFIX, --dumpfile_prefix DUMPFILE_PREFIX  LAMMPS dump files prefix. Default: dump.dislocation_
  -t [TEMPERATURE_LIST ...], --temperature_list [TEMPERATURE_LIST ...]   Dump files temperature that need extracting 
  segments. Default: [10, 200, 400, 600, 800, 1000]
```

```commandline
python lammps_cli_interface.py -h

Calculating SFW data from segments CSV files and load SFW data per frame into CSV data
optional arguments:
  -h, --help                    show this help message and exit
  -c , --csv_file_path          Path pointing to segment CSV files
  -cp , --csv_file_prefix       Segment CSV files prefix
  -sp , --sfw_file_prefix       Prefix of saved SFW CSV files. Default: sfw_frame_
  -af , --sfw_average_flag      Flag to calculate SFW average with 0 - False, 1 - True. Default: 0
  -sf , --sfw_average_filename  SFW average files name. Default: sfw_average.csv

```
