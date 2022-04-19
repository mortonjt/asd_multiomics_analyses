#!/bin/sh
#SBATCH --mail-type=ALL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=jmorton@flatironinstitute.org
#SBATCH -p ccb
#SBATCH --time=100:00:00
source ~/.bashrc
conda activate qiime2-2021.4
module load disBatch/2.0-beta
export TBB_CXX_TYPE=gcc
cd /mnt/home/jmorton/research/SPARK-autism/sfari/data/sra_shotgun/Dan2020
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
# mkdir age_sex_matched_posterior
case_control_disbatch.py \
    --biom-table bioms/virome.biom \
    --metadata-file sample_metadata_JM.txt \
    --matching-ids Match_IDs \
    --groups Status \
    --treatment-group 'ASD' \
    --monte-carlo-samples 100 \
    --output-inference age_sex_matched_posterior/viral_differentials-v2.nc

# case_control_disbatch.py \
#     --biom-table bioms/ogus-corrected.biom \
#     --metadata-file sample_metadata_JM.txt \
#     --matching-ids Match_IDs \
#     --groups Status \
#     --treatment-group 'ASD' \
#     --monte-carlo-samples 100 \
#     --intermediate-directory intermediate \
#     --job-extra "export TBB_CXX_TYPE=gcc" \
#     --no-overwrite \
#     --output-inference age_sex_matched_posterior/ogus_differentials-v2.nc
