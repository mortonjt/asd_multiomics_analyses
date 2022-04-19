
This folder is dedicated to processing 16S data.  We don't make the original data publically available (due to constraints), but we have "attempted" to document our software analyses and scripts.

So if you are interested in producing these results, it may be a challenge, don't hestitate to reach out and raise issues.

First, within each study folder, you need to start with an `SraRunTable.txt`, with lists all of the SRA accessions (one accession per sample).
See [here](https://www.ncbi.nlm.nih.gov/Traces/study/?WebEnv=MCID_625da304f5afb80fa3541e6e&query_key=2&GALAXY_URL=https%3A%2F%2Fusegalaxy.org%2Ftool_runner%3Ftool_id%3Dsra_source) for results from the RunSelector from the [Dan et al study](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA453621). The SRA interface may require some tinkering -- see the [SRA help page](https://www.ncbi.nlm.nih.gov/sra/docs/sradownload/) for more information.

Once you have your `SraRunTable.txt`, AND you have installed the [GetData](git@github.com:mortonjt/GetData.git) package, you can denoise your sequences using Deblur as follows

get_sra.py -i SraRunTable.txt -p `dirname $(which deblur)` --split-files

This will create a `deblur` folder with biom tables and fasta files.  All of our analyses work downstream of this.

We have also included some customized scripts for a select few studies, such as `David2021`, `Son2015`, `Kang2017`.

The Jupyter notebooks here are largely for metadata curation.  All of the combined 16S biom tables should be allocated to `Combined`.
Benchmarking scripts can be found in the `Benchmarking` folder.
