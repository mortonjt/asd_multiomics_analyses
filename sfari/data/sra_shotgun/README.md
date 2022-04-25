# Shotgun metagenomics sequencing preprocessing

This folder contains preprocessing scripts and Jupyter notebooks for metadata preprocessing.

Each subfolder contains scripts to launch Bowtie jobs and differential abundance jobs

`launch.sh` is the script to launch the Bowtie alignment scripts using [disBatch](https://github.com/flatironinstitute/disBatch)

`wolkta_ogus.sh` is the script to aggregate Bowtie alignment files to create biom tables.

`diff_abs.sh` contains differential abundance scripts
