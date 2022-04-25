# RNAseq preprocessing

This folder contains differential abundance scripts for analyzing RNAseq data from recount3

`diff_abs.sh` contains differential abundance scripts

It is important to note that the compute for RNAseq is substantially more demanding (there are >60k transcripts).
You may need to run `case_control_merge.py` to rescue the intermediate files and create your aggregated inference data files yourself.
If there are errors (i.e. some runs throw errors), make sure to delete those files and rerun `case_control_disbatch.py`
