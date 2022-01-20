# CacheShaping

This repository contains the source code and data for CacheShaping, a new proposed software-level defense algorithm against cache occupancy channel based website fingerprinting. CacheShaping is able to reduce the attack accuracy to a low level by introducing dummy I/O operations with multiple processes.

**The dataset and code are for research purposes only**. The results of this study are published in the following paper: 

******.  

## Content

The `auto_cache_collection` directory contains the code to automatically launch cache occupancy attack and collect the cache occupancy information from user's system. 

The `attack` directory contains the code for CNN and LSTM models.

The `open_world` directory contains the codes for open-world evaluation.

The `defense` directory contains the code for CacheShaping algorithm

The `detection` directory contains the html and JavaScript files for cache occupancy attack detection.

The `utils` directory contains the code for preprocessing datasets.

## Dataset

All the original data (i.e., non-defended cache data), defended data and the list of wesites we used both closed-world setting and open-world setting can be found below:

http:*********


## Neural Networks

We leveraged CNN and LSTM to evaluate the attack and defense performance. Details of the structure and tuned hyperparameters can be found in our paper. 

## Citation

When reporting results that use the dataset or code in this repository, please cite:

******. 


## Contacts

Haipeng Li, li2hp@mail.uc.edu, University of Cincinnati

Boyang Wang, boyang.wang@uc.edu, University of Cincinnati