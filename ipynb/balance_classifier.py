import argparse
import numpy as np
import pandas as pd
import arviz as az
from biom import load_table
from util import balance_classifier, match_table
from util import extract_differentials, ranking
from multiprocessing import Pool


parser = argparse.ArgumentParser()
parser.add_argument(
    '--biom-table', help='Biom table of counts.', required=True)
parser.add_argument(
    '--metadata-file', help='Sample metadata file.', required=True)
parser.add_argument(
    '--matching-ids', help='Column specifying matchings.', required=True)
parser.add_argument(
    '--groups', help=('Column specifying groups '
                      '(i.e. treatment vs control groups).'),
    required=True)
parser.add_argument(
    '--treatment-group', help='The name of the control group.',
    required=True)
parser.add_argument(
    '--differentials', help='The computed differentials.',
    required=True)
parser.add_argument(
    '--processes', help='Number of parallel processes.',
    required=False, default=1, type=int)
parser.add_argument(
    '--results-file', help='The location of the results file.',
    required=True)
args = parser.parse_args()

diffs =  extract_differentials(args.differentials)
stats = ranking(diffs, reference_percentile=50)

table = load_table(args.biom_table)
counts = pd.DataFrame(np.array(table.matrix_data.todense()).T,
                      index=table.ids(),
                      columns=table.ids(axis='observation'))
metadata = pd.read_table(args.metadata_file, comment='#', dtype=str)
metadata = metadata.set_index(metadata.columns[0])

stats = stats.loc[table.ids(axis='observation')].sort_values('tstat')
# diff_table = match_table(counts, metadata, args.matching_ids, args.groups)

print('Data loaded')
def classifier_func(x):
    t, b = x
    res = balance_classifier(counts, metadata, stats['tstat'],
                             args.matching_ids, args.groups, t, b)
    return res, t, b

coords = []
d = counts.shape[1]
f = 2
for t in range(1, counts.shape[1]):
    for b in range(t):
        if t > d / f and b < d / f:
            coords.append((t, b))
print('Spawning processes.')

runs = []
with Pool(args.processes) as p:
    for coord in p.imap(classifier_func, coords, chunksize=50):
        (p, n), t, b = coord
        print(t, b, p, n)
        runs.append((t, b, p, n))
res = pd.DataFrame(runs, columns=['upper', 'lower', 'percent_correct', 'mse'])
res.to_csv(args.results_file)
