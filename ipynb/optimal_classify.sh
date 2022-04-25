#!/bin/bash

amp_directory=../sfari/data/sra/Combined
wgs_directory=../sfari/data/sra_shotgun/Combined
results_dir=../results
kang_directory=../sfari/data/sra/Kang2017

# python balance_classifier.py \
#     --biom-table $kang_directory/age_sex_match_week0_ogu.biom \
#     --metadata-file $kang_directory/combined_sample_metadata_0.txt \
#     --differentials $kang_directory/week0_ogu/differentials-v7.nc \
#     --matching-ids Match_IDs \
#     --groups Status \
#     --treatment-group ASD \
#     --processes 128 \
#     --results-file ../results/classification/amp_results-v3.csv

python balance_classifier.py \
    --biom-table $wgs_directory/ogus_table.biom \
    --metadata-file $wgs_directory/sample_metadata.txt \
    --differentials $wgs_directory/age_sex_matched_posterior/ogus_differentials-v4.nc \
    --matching-ids Match_IDs \
    --groups Status \
    --treatment-group ASD \
    --processes 128 \
    --results-file ../results/classification/wgs_results.csv
