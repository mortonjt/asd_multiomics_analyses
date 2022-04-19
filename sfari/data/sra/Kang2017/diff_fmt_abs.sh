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
rm -r fmt
mkdir -p fmt/intermediate
#
case_control_disbatch.py \
    --biom-table week0_week18.biom \
    --metadata-file asd_metadata.txt \
    --matching-ids match_ids \
    --groups week \
    --treatment-group '18' \
    --monte-carlo-samples 1000 \
    --local-directory /scratch \
    --intermediate-directory fmt/intermediate \
    --output-inference fmt/differentials.nc

# case_control_merge.py \
#     --biom-table age_sex_match_week18.biom \
#     --inference-files week18/intermediate/*.nc \
#     --monte-carlo-samples 1000 \
#     --output-inference week18/differentials.nc
