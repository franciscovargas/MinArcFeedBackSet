# MinArcFeedBackSet

Python implementation of Eades et a. (1993).

# Installation Instructions

These instructions are to install the required packages in order for this script to run (numpy, scipy, matplotlib, and networkX)

## Windows and Mac (using conda):

 Open the windows\Mac command prompt and navigate to the directory containing this project the run:


```
C:\...MinArcFeedBackSet> conda install --yes --file conda_requirements.txt
```


## Linux and Max (using pip)

 Open the Unix terminal and navigate to the directory containing this project the run:


```
$ pip install -r pip_requirements.txt
```


# Usage Instructions

## Command Line tool

I have written a command line tool which allows you to use this module with one command (without needing to modify any scripts):

Open the windows/mac/linux terminal and navigate to the directory containing the project. Then run


```
python util.py input.csv output
```


This will open the file input.csv (presumably containing the graph, replace input.csv with your csv's name) and create the files:


```
- DAG_output.csv (csv file with three collumns source , target , weight) containing the cycle removed graph
- partial_output.csv (csv file containing the ordering from Eades (1993) GR-FAS algo)
```


Replace input.csv and output with the corresponding names required.


## Usage as a python module


I am assuming this is not a requirement just yet.
[TODO]
