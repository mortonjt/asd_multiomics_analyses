#!/bin/sh
#SBATCH --mail-type=ALL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=jmorton@flatironinstitute.org
#SBATCH -p ccb
#SBATCH --time=100:00:00
#SBATCH --constraint=rome
# --constraint=broadwell
source ~/.bashrc
module load disBatch/2.0
conda activate qiime2-2021.4
export TBB_CXX_TYPE=gcc
cd /mnt/home/jmorton/research/SPARK-autism/sfari/data/sra/Benchmarking
echo `which python`
# mkdir intermediate
# rm /scratch/*.nc
# for i in {0..6}
# do
#     echo $i
#     rm intermediate_${i}/*
#     #mkdir intermediate_${i}
#     sbatch -p ccb -c 4 -n 32 --wrap "case_control_disbatch.py --biom-table matched_${i}.biom --metadata-file match_metadata_${i}.txt --matching-ids Match_IDs --groups Status --treatment-group 'ASD' --monte-carlo-samples 100 --intermediate-directory intermediate_${i} --output-inference differentials_${i}-v5.nc --no-overwrite"
# done
# i=7
# sbatch -p ccb -c 4 -n 32 --wrap "case_control_disbatch.py --biom-table matched_${i}.biom --metadata-file match_metadata_${i}.txt --matching-ids Match_IDs --groups Status --treatment-group 'ASD' --monte-carlo-samples 100 --intermediate-directory intermediate_${i} --output-inference differentials_${i}-v3.nc --no-overwrite"

for i in {0..6}
do
    sbatch -p ccb --exclusive --constraint=rome --wrap "deseq2_parallel.py --biom-table matched_${i}.biom --metadata-file match_metadata_${i}.txt --groups Status --control-group Control --processes 32 --output-inference mean_differentials_${i}-v2.nc --monte-carlo-samples 100"
done
