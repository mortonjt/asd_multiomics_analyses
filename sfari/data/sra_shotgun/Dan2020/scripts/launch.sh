source ~/jumpstart.sh
source activate woltka
export PATH=/mnt/home/jmorton/ceph/sfari/data/sra_shotgun/Dan2020/scripts:$PATH
module load disBatch/2.0-beta
sbatch -p ccb -c 8 -n 25 disBatch tasks --retry -r tasks_disBatch_210520215130_342_status.txt
