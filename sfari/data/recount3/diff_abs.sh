#!/bin/sh
#SBATCH --mail-type=ALL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=jmorton@flatironinstitute.org
#SBATCH -p ccb
#SBATCH --constraint=rome
#SBATCH --time=100:00:00
#SBATCH --exclusive
source ~/.bashrc
conda activate qiime2-2021.4
module load disBatch/2.0-beta
export TBB_CXX_TYPE=gcc
cd /mnt/home/jmorton/ceph/sfari/data/recount3
# usage: case_control_slurm.py [-h] --biom-table BIOM_TABLE --metadata-file
#                              METADATA_FILE --matching-ids MATCHING_IDS
#                              --groups GROUPS --reference-group REFERENCE_GROUP
#                              [--monte-carlo-samples MONTE_CARLO_SAMPLES]
#                              [--cores CORES] [--processes PROCESSES]
#                              [--nodes NODES] [--memory MEMORY]
#                              [--walltime WALLTIME] [--interface INTERFACE]
#                              --queue QUEUE --output-tensor OUTPUT_TENSOR
echo `which python`
echo `which case_control_slurm.py`
# rm intermediate/*
case_control_disbatch.py \
    --biom-table table.biom \
    --metadata-file sample_metadata.txt \
    --matching-ids Match_IDs \
    --groups Status \
    --treatment-group 'ASD' \
    --monte-carlo-samples 100 \
    --intermediate-directory intermediate \
    --no-overwrite \
    --job-extra "export TBB_CXX_TYPE=gcc" \
    --output-inference age_sex_matched_posterior/rna_differentials-v4.nc

# case_control_merge.py \
#     --biom-table table.biom \
#     --inference-files intermediate/*.nc \
#     --monte-carlo-samples 100 \
#     --output-inference age_sex_matched_posterior/rna_differentials-backup.nc

# Need to give about 100GB per process

# case_control_local.py \
#     --biom-table table_filtered.biom \
#     --metadata-file sample_metadata.txt \
#     --matching-ids Match_IDs \
#     --groups Status \
#     --reference-group 'ASD' \
#     --monte-carlo-samples 1000 \
#     --chains 4 \
#     --chunksize 20 \
#     --cores 30 \
#     --output-tensor age_sex_matched_posterior.nc
