# This block is just for importing the necessary libraries.
# Numerical libraries
import biom
import pandas as pd
import numpy as np
import numpy.ma as ma

from statsmodels.discrete.conditional_models import ConditionalLogit
from patsy import dmatrix
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import KFold
from sklearn.ensemble import RandomForestClassifier


def rclr(table):
    masked = ma.array(table.values, mask=table.values == 0)
    log = ma.log(masked)
    clr_data = log - log.mean(axis=1).reshape(-1, 1)
    clr_data = pd.DataFrame(clr_data, index=table.index, columns=table.columns).fillna(0)
    return clr_data


def clogit_predict(X, beta, groups):
    """ Assumes that groups is ordered. """
    cats = np.unique(groups)
    pred = []
    for c in cats:
        idx = [groups == c]
        X_ = X[idx]
        p = np.exp(X_[0] @ beta) / (np.exp(X_[0] @ beta) + np.exp(X_[1] @ beta))
        pred.append(p)
    return pd.Series(pred, index=cats)


def conditional_logistic_regression(table, metadata, matching, outcome,
                                    train, test, **kwargs):
    X_train, md_train = table.loc[train], metadata.loc[train]
    X_test, md_test = table.loc[test], metadata.loc[test]
    y_train = (md_train[outcome] == 'ASD').astype(np.int64)
    # y_test = (md_test[outcome] == 'ASD').astype(np.int64)

    le = LabelEncoder()
    groups = le.fit_transform(md_train[matching].values)

    model = ConditionalLogit(endog=y_train, exog=X_train, groups=groups)
    res = model.fit_regularized(**kwargs)
    train_probs = clogit_predict(X_train.values, res.params, md_train[matching].values)
    test_probs = clogit_predict(X_test.values, res.params, md_test[matching].values)

    return train_probs, test_probs, res
