#!/bin/sh
#SBATCH --mail-type=ALL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=jmorton@flatironinstitute.org
#SBATCH -p ccb
#SBATCH --time=100:00:00
#SBATCH --constraint=rome
source ~/.bashrc
conda activate qiime2-2021.4
export TBB_CXX_TYPE=gcc
module load disBatch/2.0

# for file in schloss knight turnbaugh flores
# do
#     md=metadata/$file
#     echo $file,$md
#     sbatch --wrap "deseq2_parallel.py --biom-table deblur/all.wol.biom --metadata-file $md --groups Sample_Name --control-group sample4 --monte-carlo-samples 100 --processes 120 --output-inference ${file}_posterior"
# done


for file in schloss knight turnbaugh flores
do
    md=metadata/$file
    echo $file,$md
    sbatch --wrap "deseq2_parallel.py --biom-table deblur/all.wol.biom --metadata-file $md --groups Sample_Name --control-group sample14 --monte-carlo-samples 100 --processes 120 --output-inference ${file}_posterior"
done
