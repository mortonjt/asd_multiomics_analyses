#!/bin/sh
#SBATCH --mail-type=ALL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=jmorton@flatironinstitute.org
#SBATCH -p ccb
#SBATCH --time=100:00:00
#SBATCH --constraint=rome
source ~/.bashrc
module load disBatch/2.0-beta
conda activate qiime2-2021.4
export TBB_CXX_TYPE=gcc
cd /mnt/home/jmorton/research/SPARK-autism/sfari/data/sra_ibd_shotgun/Combined
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
#mkdir intermediate
#mkdir sex_matched_posterior
rm intermediate/*
case_control_disbatch.py \
    --biom-table combined.biom \
    --metadata-file combined_metadata.txt \
    --matching-ids Match_IDs \
    --groups Status \
    --treatment-group 'CD' \
    --monte-carlo-samples 100 \
    --intermediate-directory intermediate \
    --output-inference sex_matched_posterior/wgs_differentials-v2.nc --no-overwrite
