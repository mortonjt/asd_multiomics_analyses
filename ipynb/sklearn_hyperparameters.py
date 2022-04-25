
import biom
import argparse
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier as RFC
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from bayes_opt import BayesianOptimization
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
import warnings
warnings.simplefilter("ignore")


def svc_cv(C, gamma, data, targets):
    """SVC cross validation.
    This function will instantiate a SVC classifier with parameters C and
    gamma. Combined with data and targets this will in turn be used to perform
    cross validation. The result of cross validation is returned.
    Our goal is to find combinations of C and gamma that maximizes the roc_auc
    metric.
    """
    estimator = SVC(C=C, gamma=gamma, random_state=2)
    cval = cross_val_score(estimator, data, targets, scoring='roc_auc', cv=4)
    return cval.mean()


def rfc_cv(n_estimators, min_samples_split, max_features, data, targets):
    """Random Forest cross validation.
    This function will instantiate a random forest classifier with parameters
    n_estimators, min_samples_split, and max_features. Combined with data and
    targets this will in turn be used to perform cross validation. The result
    of cross validation is returned.
    Our goal is to find combinations of n_estimators, min_samples_split, and
    max_features that minimzes the log loss.
    """
    estimator = RFC(
        n_estimators=n_estimators,
        min_samples_split=min_samples_split,
        max_features=max_features,
        random_state=2
    )
    cval = cross_val_score(estimator, data, targets,
                           scoring='neg_log_loss', cv=4)
    return cval.mean()


def optimize_svc(data, targets):
    """Apply Bayesian Optimization to SVC parameters."""
    def svc_crossval(expC, expGamma):
        """Wrapper of SVC cross validation.
        Notice how we transform between regular and log scale. While this
        is not technically necessary, it greatly improves the performance
        of the optimizer.
        """
        C = 10 ** expC
        gamma = 10 ** expGamma
        return svc_cv(C=C, gamma=gamma, data=data, targets=targets)

    optimizer = BayesianOptimization(
        f=svc_crossval,
        pbounds={"expC": (-3, 2), "expGamma": (-4, -1)},
        random_state=1234,
        verbose=2
    )
    optimizer.maximize(n_iter=10)

    print("Final result:", optimizer.max)


def optimize_rfc(data, targets):
    """Apply Bayesian Optimization to Random Forest parameters."""
    def rfc_crossval(n_estimators, min_samples_split, max_features):
        """Wrapper of RandomForest cross validation.
        Notice how we ensure n_estimators and min_samples_split are casted
        to integer before we pass them along. Moreover, to avoid max_features
        taking values outside the (0, 1) range, we also ensure it is capped
        accordingly.
        """
        return rfc_cv(
            n_estimators=int(n_estimators),
            min_samples_split=int(min_samples_split),
            max_features=max(min(max_features, 0.999), 1e-3),
            data=data,
            targets=targets,
        )

    optimizer = BayesianOptimization(
        f=rfc_crossval,
        pbounds={
            "n_estimators": (10, 250),
            "min_samples_split": (2, 25),
            "max_features": (0.1, 0.999),
        },
        random_state=1234,
        verbose=2
    )
    optimizer.maximize(n_iter=10)

    print("Final result:", optimizer.max)


if __name__ == "__main__":

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
    train_m = matches[len(matches) // 4:]
    test_m = matches[:len(matches) // 4]
    kf = KFold(n_splits=4)

    train_idx = md['Match_IDs'].apply(lambda x: x in train_m)
    test_idx = md['Match_IDs'].apply(lambda x: x in test_m)

    data = gclr.loc[train_idx].values
    targets = md.loc[train_idx, 'Status'].values
    print('Test matches', test_m)

    print("--- Optimizing SVM ---")
    optimize_svc(data, targets)

    print("--- Optimizing Random Forest ---")
    optimize_rfc(data, targets)
