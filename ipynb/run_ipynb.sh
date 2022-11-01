#!/bin/bash
#SBATCH --mail-type=ALL         # Mail events (NONE, BEGIN, END, FAIL, ALL)
#SBATCH --mail-user=jmorton@flatironinstitute.org
#SBATCH -p ccb
#SBATCH --constraint=rome
#SBATCH --time=100:00:00
#SBATCH --exclusive
source ~/.bashrc
conda activate qiime2-2021.4
cd /mnt/home/jmorton/research/SPARK-autism/ipynb

# # Generate Figure 2 (differentials) and Figure 4 (Kang FMT)
# jupyter nbconvert --to notebook --execute September-update-version1.ipynb
# jupyter nbconvert --to notebook --execute PTHS-analysis.ipynb
# Gather molecules across omics levels and extract embedding
jupyter nbconvert --to notebook --execute A-gather-compounds.ipynb
jupyter nbconvert --to notebook --execute B-metabolic-network-preprocessing.ipynb
jupyter nbconvert --to notebook --execute C-metabolic-network-embedding.ipynb
# # Generate viral interactions
jupyter nbconvert --to notebook --execute preprocess-microbe-viral-interactions.ipynb
jupyter nbconvert --to notebook --execute microbe-viral-embeddings.ipynb
# Comparision between 16S and WGS
jupyter nbconvert --to notebook --execute 16S-WGS-comparison.ipynb
# Benchmarking figures
jupyter nbconvert --to notebook --execute benchmark-figure.ipynb
# # Run metabolomics analysis
# jupyter nbconvert --to notebook --execute metabolomics-preprocessing.ipynb
# jupyter nbconvert --to notebook --execute metabolite-differential-analysis.ipynb
# # Generate diagnostics
jupyter nbconvert --to notebook --execute omics-diagnostics-r2.ipynb
