#!/bin/sh
#SBATCH --mail-type=ALL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=jmorton@flatironinstitute.org
#SBATCH -p ccb
#SBATCH --time=100:00:00
#SBATCH --constraint=rome
source ~/.bashrc
module load disBatch/2.0
conda activate qiime2-2021.4
export TBB_CXX_TYPE=gcc
cd /mnt/home/jmorton/research/SPARK-autism/sfari/data/sra/Son2015
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
# mkdir intermediate
#rm intermediate/*
case_control_disbatch.py \
    --biom-table deblur/all.ogus.biom \
    --metadata-file sample_metadata.txt \
    --matching-ids Household \
    --groups Diagnosis \
    --treatment-group 'ASD' \
    --monte-carlo-samples 100 \
    --intermediate-directory intermediate \
    --output-inference sibling_matched_posterior/differentials.nc
