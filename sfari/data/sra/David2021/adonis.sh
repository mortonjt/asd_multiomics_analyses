#!/bin/bash
qiime diversity adonis --i-distance-matrix deblur/all.ogus.distances.filtered.qza --p-formula "Pair + Gender + age_month_ok" --m-metadata-file sample_metadata_JM-v2.txt --p-n-jobs 40 --o-visualization adonis.qzv
