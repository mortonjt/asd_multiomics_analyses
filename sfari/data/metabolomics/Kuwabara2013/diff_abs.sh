#!/bin/bash

#module load gcc/11.1.0
CXX=g++
TBB_CXX_TYPE=gcc
qiime tools import --input-path plasma.biom --output-path plasma.qza --type FeatureTable[Frequency]

qiime matchmaker normal-case-control \
   --i-table plasma.qza \
   --m-matching-ids-file plasma_sample_metadata.txt \
   --m-matching-ids-column Match_IDs \
   --m-groups-file plasma_sample_metadata.txt \
   --m-groups-column Status \
   --p-control-group Control \
   --p-control-loc 50 \
   --p-control-scale 200 \
   --o-differentials differential.qza \
   --verbose



# Usage: qiime matchmaker normal-case-control [OPTIONS]
#
#   Fits a Positive Normal model to estimate biased log-fold change
#
# Inputs:
#   --i-table ARTIFACT FeatureTable[Frequency]
#                           Input table of counts.                    [required]
# Parameters:
#   --m-matching-ids-file METADATA
#   --m-matching-ids-column COLUMN  MetadataColumn[Categorical]
#                           The matching ids to link case-control samples
#                                                                     [required]
#   --m-groups-file METADATA
#   --m-groups-column COLUMN  MetadataColumn[Categorical]
#                           The categorical sample metadata column to test for
#                           differential abundance across.            [required]
#   --p-control-group TEXT  Specifies the control group.              [required]
#   --p-monte-carlo-samples INTEGER
#                           Number of monte carlo samples to draw from
#                           posterior distribution.              [default: 2000]
#   --p-mu-scale NUMBER     The mean of the differential prior.   [default: 1.0]
#   --p-sigma-scale NUMBER  The scale of the differential prior.  [default: 1.0]
#   --p-disp-scale NUMBER   The scale of the overdispersion factor.
#                                                                 [default: 1.0]
#   --p-control-loc NUMBER  The mean of the control abundances. [default: 100.0]
#   --p-control-scale NUMBER
#                           The scale of the control abundances.
#                                                               [default: 100.0]
# Outputs:
#   --o-differentials ARTIFACT
#     MonteCarloTensor      Output posterior differentials learned from the
#                           Positive normal model.                    [required]
#
