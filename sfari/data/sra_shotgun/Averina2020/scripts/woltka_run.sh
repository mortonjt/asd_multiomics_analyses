#!/bin/sh
#SBATCH -p ccb
#SBATCH --exclusive

cd /mnt/home/jmorton/ceph/sfari/data/sra_shotgun/Averina2020/scripts

WOL=~/databases/wol

# argument: path to read 1.
file=../align
echo `which basename`
echo `basename --version`
echo "File: ${file}"
#fname=$(basename $file _1.sam)
echo "Folder: ${fname}"
mkdir ../genome_mappings
mkdir ../bioms
woltka classify \
    --input $file \
    --map $WOL/taxonomy/taxid.map \
    --nodes $WOL/taxonomy/nodes.dmp \
    --names $WOL/taxonomy/names.dmp \
    --rank species \
    --outmap ../genome_mappings \
    -o ../bioms/species.biom


woltka classify \
  -i $file \
  --coords $WOL/proteins/coords.txt.xz \
  --map $WOL/function/uniref/uniref.map.xz \
  --map $WOL/function/kegg/ko.map.xz \
  --map-as-rank \
  --rank ko \
  --stratify ../genome_mappings \
  -o ../bioms/species_func.biom
