

source activate woltka

export PATH=/mnt/home/jmorton/software/bowtie2/bowtie2-2.4.3:$PATH
echo -e "Running task ${DISBATCH_TASKID} on $(hostname) using:\n$(which fastp)\n$(which bowtie2)"
cd /mnt/home/jmorton/ceph/sfari/data/sra_shotgun/Averina2020/scripts
WOL=~/databases/wol

# argument: path to read 1.
file1=$1
file2=${file1/_1.fastq/_2.fastq}

nprocs=${SLURM_CPUS_PER_TASK}

# temp directory for trimming, avoiding collisions.
tmpDirRoot=${ALIGN_TMPDIRROOT:-/scratch}
trim_dir=$(mktemp -d ${tmpDirRoot}/${USER}_trim_XXXXXXXXXX)

function cleanup {
    rm -rf ${trim_dir} || echo "Check for \"${trim_dir}\" on $(hostname)."
}
# This runs the cleanup function when the script exits (normally or
# due to an error).
trap cleanup EXIT

fname1=$(basename $file1 .fastq)
fname2=$(basename $file2 .fastq)

# Trimming
trim1="${trim_dir}/${fname1}.fastq"
trim2="${trim_dir}/${fname2}.fastq"
echo -e "Files:\n${file1}\n${file2}\n${trim1}\n${trim2}"
(
    #REMOVE
    fastp -l 100 -i $file1 -I $file2 \
        -o $trim1 -O $trim2 -w 10

    # Bowtie2 alignment
    align="${trim_dir}/${fname1}.sam"
    #REMOVE
    bowtie2 -x $WOL/databases/bowtie2/WoLr1 \
       -p $nprocs -1 $trim1 -2 $trim2 -S $align \
       -k 16 --np 1 --mp "1,1" --rdg "0,1" --rfg "0,1" \
       --score-min "L,0,-0.05" --very-sensitive --no-head --no-unal
    #REMOVE
    cp $align ../align/${fname1}.sam
) &> ${fname1}_${nprocs}.log
