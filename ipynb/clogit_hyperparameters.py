
import biom
import argparse
import pandas as pd
import numpy as np
from logit import conditional_logistic_regression
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from bayes_opt import BayesianOptimization
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
import warnings
warnings.simplefilter("ignore")

state = np.random.RandomState(0)

parser = argparse.ArgumentParser()
parser.add_argument(
    '--biom-table', help='Biom table of counts.', required=True)
parser.add_argument(
    '--metadata-file', help='Sample metadata file.', required=True)
parser.add_argument(
    '--checkpoint', help='Loads the logs from json.', required=False)
parser.add_argument(
    '--log-file', help='Saves the logs to json.', required=True)
args = parser.parse_args()


# read in data
table = biom.load_table(args.biom_table).to_dataframe().T
md = pd.read_table(args.metadata_file, index_col=0)

# Load taxonomy
taxonomy = pd.read_table('~/databases/wol/taxonomy/ranks.tsv', index_col=0)
taxid = pd.read_table('~/databases/wol/taxonomy/taxid.map', header=None, dtype=str)
taxid.columns = ['GOTU', 'genome']
mapping = pd.merge(taxid, taxonomy, left_on='GOTU', right_index=True)
mapping = mapping.set_index('genome')

md = md.sort_values(['Status', 'Match_IDs'])
table = table.loc[md.index]
print('Read in data and collapsing taxonomy')
# collapse to genus level
cols = ['kingdom' ,'phylum', 'class', 'order', 'family', 'genus']
genus_lineage = mapping.apply(lambda x: ';'.join(map(str, x[cols])), axis=1)
genera = pd.merge(table.T, pd.DataFrame({'genus': genus_lineage}),
                  left_index=True, right_index=True).groupby('genus').sum()

gclr = np.log(genera + 1).T - np.log(genera + 1).T.mean(axis=1).values.reshape(-1, 1)

# define function for cross-validation
cohorts = md['Cohort'].unique()
matches = state.permutation(md['Match_IDs'].unique())
train_matches = matches[len(matches) // 4:]
test_matches = matches[:len(matches) // 4]
kf = KFold(n_splits=4)


print('Test matches', test_matches)
def run_clogit_split(train_m, test_m, alpha, L1_wt):
    """ Split by match pairs """
    train_idx = md['Match_IDs'].apply(lambda x: x in train_m)
    test_idx = md['Match_IDs'].apply(lambda x: x in test_m)
    train_p, test_p, summary = conditional_logistic_regression(
        gclr, md, 'Match_IDs', 'Status',
        train_idx, test_idx, alpha=alpha, L1_wt=L1_wt
    )
    return train_p, test_p, summary


def bayes_box(alpha, L1_wt):
    alpha = np.exp(alpha) / (1 + np.exp(alpha))
    L1_wt = np.exp(L1_wt) / (1 + np.exp(L1_wt))
    cv = []
    for train_m, test_m in kf.split(train_matches):
        pp = run_clogit_split(matches[train_m], matches[test_m],
                              alpha=alpha, L1_wt=L1_wt)
        train_p, test_p, res = pp
        cv.append(test_p.mean())
    return np.mean(cv)


# Bounded region of parameter space
pbounds = {'alpha': (-20, 20), 'L1_wt': (-20, 20)}

optimizer = BayesianOptimization(
    f=bayes_box,
    pbounds=pbounds,
)
if args.checkpoint is not None:
    load_logs(optimizer, logs=[args.checkpoint]);

logger = JSONLogger(path=args.log_file)
optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)

optimizer.maximize(
    init_points=2,
    n_iter=20
)
print('Printing results')
print(optimizer.max)
for i, res in enumerate(optimizer.res):
    print("Iteration {}: \n\t{}".format(i, res))
