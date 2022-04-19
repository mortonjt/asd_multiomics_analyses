#!/bin/sh
#SBATCH --mail-type=ALL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=jmorton@flatironinstitute.org
#SBATCH -p ccb
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=128
#SBATCH --constraint=rome
#SBATCH --array=1-74%8
#SBATCH --exclusive
#SBATCH --time 100:00:00
export PATH=/mnt/home/jmorton/software/bowtie2/bowtie2:$PATH

echo $SLURM_ARRAY_TASK_ID
file=$(ls fasta/*.fasta | sed -n ${SLURM_ARRAY_TASK_ID}p)

echo `which bowtie2`
WOL=~/databases/wol
fname=$(basename $file .fasta)
mkdir align
file1=$(ls ../fasta/*_1.fastq | sed -n ${SLURM_ARRAY_TASK_ID}p)
file2=$(ls ../fasta/*_2.fastq | sed -n ${SLURM_ARRAY_TASK_ID}p)
fname=$(basename $file1 .fastq)
bowtie2 -x $WOL/databases/bowtie2/WoLr1 -p 16 -1 $file1 -2 $file2 -S ../align/${fname}.sam \
    -k 16 --np 1 --mp "1,1" --rdg "0,1" --rfg "0,1" \
    --score-min "L,0,-0.05" --very-sensitive --no-head --no-unal

# file=$(ls fasta/*_2.fasta | sed -n ${SLURM_ARRAY_TASK_ID}p)
# fname=$(basename $file .fasta)
# bowtie2 -x $WOL/databases/bowtie2/WoLr1 -p 16 -f $file -S align/${fname}.sam \
#     -k 16 --np 1 --mp "1,1" --rdg "0,1" --rfg "0,1" \
#     --score-min "L,0,-0.05" --very-sensitive --no-head --no-unal
