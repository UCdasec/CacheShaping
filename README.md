# CacheShaping

This repository contains the source code and data for Cache Shaping, a software-level defense algorithm against cache-based website fingerprinting attacks. Cache Shaping is able to reduce the attack accuracy to a low level by introducing dummy I/O operations with multiple processes.

**The dataset and code are for research purposes only**. The results of this study are published in the following paper: 

Haipeng Li, Nan Niu, Boyang Wang, “Cache Shaping: An Effective Defense Against Cache-Based Website Fingerprinting,” the 12th ACM Conference on Data and Application Security and Privacy (**ACM CODASPY 2022**), April 24–27, 2022, Baltimore, MD, USA. 


## Content

The `auto_cache_collection` directory contains the code to automatically launch cache occupancy attack and collect the cache occupancy information from user's system. 

The `attack` directory contains the code for CNN and LSTM models.
python cnn_

The `open_world` directory contains the codes for open-world evaluation.

The `defense` directory contains the code for CacheShaping algorithm

The `detection` directory contains the html and JavaScript files for cache occupancy attack detection.

The `utils` directory contains the code for preprocessing datasets.

## Dataset

All the original data (i.e., non-defended cache data), defended data and the list of wesites we used both closed-world setting and open-world setting can be found below (**last modified: Jan. 2022**)

https://mailuc-my.sharepoint.com/:f:/g/personal/wang2ba_ucmail_uc_edu/EnJCf-CuaRpNs-Uy3NUM0jkBLZVrdLm2jVRBdGBDlEapwg?e=oWGBSu 

Note: the above links need to be updated every 6 months due to certain settings of OneDrive. If you find the links are expired and you cannot access the data, please feel free to email us (boyang.wang@uc.edu). We will be update the links as soon as we can. Thanks!


## Neural Networks

We leveraged CNN and LSTM to evaluate the attack and defense performance. Details of the structure and tuned hyperparameters can be found in our paper. 

## Citation

When reporting results that use the dataset or code in this repository, please cite:

Haipeng Li, Nan Niu, Boyang Wang, “Cache Shaping: An Effective Defense Against Cache-Based Website Fingerprinting,” the 12th ACM Conference on Data and Application Security and Privacy (ACM CODASPY 2022), April 24–27, 2022, Baltimore, MD, USA. 


## Contacts

Haipeng Li, li2hp@mail.uc.edu, University of Cincinnati

Boyang Wang, boyang.wang@uc.edu, University of Cincinnati
