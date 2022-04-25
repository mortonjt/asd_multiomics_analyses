# asd_multiomics_analyses

This repository contains all of the analysis notebooks and scripts used to analyze the ASD multiomics meta-analysis [in this paper](https://www.biorxiv.org/content/10.1101/2022.02.25.482050v1).

This repository does not contain the datasets required to reproduce the analyses (it amounts to several TB, plus much of the data is confidential).  But we have provided the exact directory structure and conda environments used to facilitate the preprocessing and analysis.

## Preprocessing pipeline

The 16S metadata preprocessing and workflows can be found under the `sfari/data/sra` folder.

The SMS workflows can be found under the `sfari/data/sra_shotgun`, `sfari/data/diaimmune` and `sfari/data/sra_ibd_shotgun` folders.

The RNAseq preprocessing workflows can be found under the `sfari/data/recount3` folder.

## Jupyter notebooks

To get started on understanding how to parse the results of the case-control differential abundance pipeline, see the `ipynb/main-differential-notebook.ipynb`.
This will give a high-level overview of the pipeline, how to analyze and interpret the results.

### Metabolic analysis
`A-gather-compounds.nbconvert.ipynb`
