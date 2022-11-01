# asd_multiomics_analyses

This repository contains all of the analysis notebooks and scripts used to analyze the ASD multiomics meta-analysis [in this paper](https://www.biorxiv.org/content/10.1101/2022.02.25.482050v1).

This repository does not contain the datasets required to reproduce the analyses (it amounts to several TB, plus much of the data is confidential).  But we have provided the exact directory structure and conda environments used to facilitate the preprocessing and analysis.

## Installation

To install the woltka processing utilities, run
`conda create env -f woltka.yml`

To install the analysis processing utilities, run
`conda create env -f analysis.yml`

We strongly recommend keeping these two environments separate, since there could dependency issues otherwise.

## Preprocessing pipeline

The 16S metadata preprocessing and workflows can be found under the `sfari/data/sra` folder.

The SMS workflows can be found under the `sfari/data/sra_shotgun` folder.

The RNAseq preprocessing workflows can be found under the `sfari/data/recount3` folder.

## Jupyter notebooks

The notebooks are labeled according to the figure numbering in the main paper.
