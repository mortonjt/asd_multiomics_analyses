#!/bin/bash
for i in {1..12}
do
    # songbird multinomial --input-biom deblur/ogus.biom --metadata-file cytokine_metadata.txt --formula 'IL6+TGFb+IL1b+IL4+IFNgamma' --summary-dir cytokine-differentials-${i} --epochs $((3000+i)) --learning-rate 0.1
    songbird multinomial --input-biom deblur/vsearch/clustered_table/feature-table.biom --metadata-file cytokine_metadata.txt --formula 'IL6+TGFb+IL1b+IL4+IFNgamma' --summary-dir cytokine-differentials-${i} --epochs $((3000+i)) --learning-rate 0.1 --min-feature-count 4
done

#songbird multinomial --input-biom deblur/ogus.biom --metadata-file cytokine_metadata.txt --formula '1' --summary-dir cytokine-intercept --epochs 10000
