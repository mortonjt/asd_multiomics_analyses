This folder contains all of the core analysis Jupyter notebooks

We recommend to get started looking at the `main-differential-notebook.ipynb`, since that provides a clear overview on how to load inference data objects and compute basic statistics.
The classification results and the comparative genomics analyses are split between the `core-classification.ipynb` and the `core-cross-validation.ipynb` notebooks.

Reproducing the RNAseq analyses will require first running `ensembl2kegg.ipynb` to match the ensemble ids to KEGG ids.

The metabolic analyses can be found under `pathway-preprocessing`, `A-gather-compounds.ipynb`, `B-metabolic-network-preprocessing.ipynb` and `C-metabolic-network-embedding.ipynb`.

The cytokine analysis can be found under `cytokine-analysis.ipynb`.

The comparisons between ASD, IBD and T1D can be found under `meta-disease-analysis.ipynb`.

The investigation of confounders can be found under `sibling-vs-age-sex-matching.ipynb` and `confounder-differences.ipynb`

The FMT analysis can be found under `core-FMT-analysis.ipynb`

The dietary analysis can be found under `core-dietary-analysis.ipynb`

The comparison between 16S and SMS can be found under `core-16S-SMS-comparison.ipynb`

The metabolomics analyses can be found under `metabolomics-preprocessing.ipynb` and `metabolite-differential-analysis.ipynb`.

The microbe-viral analysis can be found under `microbe-viral-embeddings.ipynb`.

Benchmarking notebooks can be found under
`omics-diagnostics-r2.ipynb`, `benchmarking.ipynb` , `preprocess-simulations.ipynb` and `post-process-simulation.ipynb`.
