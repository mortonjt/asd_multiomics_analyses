#!/bin/bash

conda activate mmvec

# mmvec paired-omics \
#     --microbe-file ../deblur/all.ogu.biom \
#     --metabolite-file diet.biom \
#     --epochs 5000 \
#     --latent-dim 10 \
#     --batch-size 1000 \
#     --summary-dir mmvec-ogu-latent10-results \
#     --summary-interval 1 \
#     --training-column Training

# mmvec paired-omics \
#     --microbe-file ../deblur/all.ogu.biom \
#     --metabolite-file diet.biom \
#     --epochs 5000 \
#     --latent-dim 0 \
#     --batch-size 1000 \
#     --summary-dir mmvec-ogu-null-results \
#     --summary-interval 1 \
#     --training-column Training


mmvec paired-omics \
    --microbe-file ../deblur/vsearch/clustered_table/feature-table.biom \
    --metabolite-file diet.biom \
    --epochs 10000 \
    --latent-dim 2 \
    --min-feature-count 1 \
    --batch-size 1000 \
    --summary-dir mmvec-ogu-latent5-results-v2 \
    --summary-interval 1 \
    --training-column Training



mmvec paired-omics \
    --microbe-file ../deblur/vsearch/clustered_table/feature-table.biom \
    --metabolite-file diet.biom \
    --epochs 10000 \
    --latent-dim 0 \
    --min-feature-count 1 \
    --batch-size 1000 \
    --summary-dir mmvec-ogu-null-results-v2 \
    --summary-interval 1 \
    --training-column Training
