#!/bin/sh
#SBATCH --mail-type=ALL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=jmorton@flatironinstitute.org
#SBATCH -p ccb
#SBATCH --time=100:00:00
#SBATCH --constraint=rome
source ~/.bashrc
conda activate qiime2-2021.4
export TBB_CXX_TYPE=gcc
module load disBatch/2.0-beta
cd /mnt/home/jmorton/research/SPARK-autism/sfari/data/sra/Kang2017
# usage: case_control_slurm.py [-h] --biom-table BIOM_TABLE --metadata-file
#                              METADATA_FILE --matching-ids MATCHING_IDS
#                              --groups GROUPS --reference-group REFERENCE_GROUP
#                              [--monte-carlo-samples MONTE_CARLO_SAMPLES]
#                              [--cores CORES] [--processes PROCESSES]
#                              [--nodes NODES] [--memory MEMORY]
#                              [--walltime WALLTIME] [--interface INTERFACE]
#                              --queue QUEUE --output-tensor OUTPUT_TENSOR
echo `which python`


# OGU analysis
# mkdir -p donor_ogu/intermediate
# mkdir -p week0_ogu/intermediate
# mkdir -p fmt10_ogu/intermediate
# mkdir -p fmt18_ogu/intermediate
# mkdir -p fmt100_ogu/intermediate


# ASD vs control
rm week0_ogu/intermediate/*
case_control_disbatch.py \
    --biom-table age_sex_match_week0_ogu.biom \
    --metadata-file combined_sample_metadata_0.txt \
    --matching-ids Match_IDs \
    --batch-ids Cohort \
    --groups Status \
    --treatment-group 'ASD' \
    --monte-carlo-samples 100 \
    --intermediate-directory week0_ogu/intermediate \
    --output-inference week0_ogu/differentials-v8.nc --no-overwrite


rm fmt10_ogu/intermediate/*
case_control_disbatch.py \
    --biom-table week0_week10_ogu.biom \
    --metadata-file asd_metadata_w10.txt \
    --matching-ids host_subject_id \
    --batch-ids Cohort \
    --groups week_time \
    --treatment-group 'A10' \
    --monte-carlo-samples 100 \
    --intermediate-directory fmt10_ogu/intermediate \
    --output-inference fmt10_ogu/differentials-v8.nc --no-overwrite

# week 0 vs week 18
rm fmt18_ogu/intermediate/*
case_control_disbatch.py \
    --biom-table week0_week18_ogu.biom \
    --metadata-file asd_metadata_w18.txt \
    --matching-ids host_subject_id \
    --batch-ids Cohort \
    --groups week_time \
    --treatment-group 'A18' \
    --monte-carlo-samples 100 \
    --intermediate-directory fmt18_ogu/intermediate \
    --output-inference fmt18_ogu/differentials-v8.nc --no-overwrite

# week 0 vs week 100
rm fmt100_ogu/intermediate/*
case_control_disbatch.py \
    --biom-table week0_week100_ogu.biom \
    --metadata-file asd_metadata_w100.txt \
    --matching-ids host_subject_id \
    --batch-ids Cohort \
    --groups week_time \
    --treatment-group 'A100' \
    --monte-carlo-samples 100 \
    --intermediate-directory fmt100_ogu/intermediate \
    --output-inference fmt100_ogu/differentials-v8.nc --no-overwrite

# Host-Donor matching
rm donor_ogu/intermediate/*
case_control_disbatch.py \
    --biom-table donor_ogu.biom \
    --metadata-file donor_metadata.txt \
    --matching-ids donor_matching \
    --batch-ids Cohort \
    --groups GROUP \
    --treatment-group 'autism' \
    --monte-carlo-samples 100 \
    --intermediate-directory donor_ogu/intermediate \
    --output-inference donor_ogu/differentials-v8.nc --no-overwrite


#### Regular diff abs
# rm week0/intermediate/*
# case_control_disbatch.py \
#     --biom-table age_sex_match_week0.biom \
#     --metadata-file combined_sample_metadata_0.txt \
#     --matching-ids Match_IDs \
#     --groups Status \
#     --treatment-group 'ASD' \
#     --monte-carlo-samples 100 \
#     --intermediate-directory week0/intermediate \
#     --output-inference week0/differentials-v6.nc --no-overwrite


# ## Before and after FMT
# # week 0 vs week 10
# rm fmt10/intermediate/*
# case_control_disbatch.py \
#     --biom-table week0_week10.biom \
#     --metadata-file asd_metadata_w10.txt \
#     --matching-ids host_subject_id \
#     --groups week_time \
#     --treatment-group 'A10' \
#     --monte-carlo-samples 100 \
#     --intermediate-directory fmt10/intermediate \
#     --output-inference fmt10/differentials-v6.nc --no-overwrite
#
# # week 0 vs week 18
#rm fmt18/intermediate/*
# case_control_disbatch.py \
#     --biom-table week0_week18.biom \
#     --metadata-file asd_metadata_w18.txt \
#     --matching-ids host_subject_id \
#     --groups week_time \
#     --treatment-group 'A18' \
#     --monte-carlo-samples 100 \
#     --intermediate-directory fmt18/intermediate \
#     --output-inference fmt18/differentials-v6.nc --no-overwrite

# # week 0 vs week 100
# rm fmt100/intermediate/*
# case_control_disbatch.py \
#     --biom-table week0_week100.biom \
#     --metadata-file asd_metadata_w100.txt \
#     --matching-ids host_subject_id \
#     --groups week_time \
#     --treatment-group 'A100' \
#     --monte-carlo-samples 100 \
#     --intermediate-directory fmt100/intermediate \
#     --output-inference fmt100/differentials-v6.nc --no-overwrite

# # Host-Donor matching
#rm donor/intermediate/*
# case_control_disbatch.py \
#     --biom-table donor.biom \
#     --metadata-file donor_metadata.txt \
#     --matching-ids donor_matching \
#     --groups GROUP \
#     --treatment-group 'autism' \
#     --monte-carlo-samples 100 \
#     --intermediate-directory donor/intermediate \
#     --output-inference donor/differentials-v6.nc --no-overwrite
