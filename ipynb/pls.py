import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.mixture import GaussianMixture
from scipy.stats import multivariate_normal as mvn
from scipy.special import expit as sigmoid

from skbio.diversity._util import _vectorize_counts_and_tree


def clr(X):
    if isinstance(X, pd.DataFrame):
        return X - X.mean(axis=1).values.reshape(-1, 1)
    if isinstance(X, np.ndarray):
        return X - X.mean(axis=1).reshape(-1, 1)
    raise ValueError(f'Type {type(X)} is unsupported')


class PLSBalance(object):
    def __init__(self, bootstraps=10, robust=True, threshold=0.02, percentile=0.95):

        self._estimator_type = 'classifier'
        self.bootstraps = bootstraps
        self.robust = robust
        self.threshold = threshold
        self.percentile = percentile


    def _preprocess(self, X):
        if isinstance(X, pd.DataFrame):
            self.columns = X.columns
            X_ = X.values
        elif isinstance(X, np.ndarray):
            self.columns = np.arange(X.shape[1])
            X_ = X.copy()

        boots = []
        for _ in range(self.bootstraps):
            boots.append(
                clr(
                    np.vstack(
                        [np.random.dirichlet(X_[i] + 1) for i in range(X.shape[0])]
                    )
                )
            )
        X_ = np.dstack(boots)
        return X_

    def fit(self, X, Y, U=None):
        X_ = self._preprocess(X)
        if U is not None:
            self.p = U.shape[1]
        else:
            self.p = 0
        N, D, S = X_.shape
        self.regressors = list()
        for s in range(S):
            if U is not None:
                X__ = np.hstack((X_[:, :, s], U.values))
            else:
                X__ = X_[:, :, s]
            self.regressors.append(
                PLSRegression(n_components=1).fit(X__.squeeze(), Y)
            )
        return self

    def balance(self):
        if self.p > 0:
            weights = np.dstack([reg.x_weights_[:-self.p]
                                 for reg in self.regressors]).squeeze()  # D x S
        else:
            weights = np.dstack([reg.x_weights_
                                 for reg in self.regressors]).squeeze()  # D x S

        weights = weights - weights.mean(axis=0)

        # gmod = GaussianMixture(n_components=3)
        # gmod.fit(X=weights)

        spectrum = pd.DataFrame({'mean': weights.mean(axis=1),
                                 'std': weights.std(axis=1)},
                                index=self.columns)
        # sorts by distribution, namely, left, middle and right
        # pdfs = np.vstack(
        #     [mvn.pdf(weights,
        #              mean=gmod.means_[i], cov=gmod.covariances_[i])
        #      for i in np.argsort(gmod.means_.mean(axis=1))]
        # ).T
        #
        # cluster_labels = np.argmax(pdfs, axis=1)
        # gm = np.sort(gmod.means_.mean(axis=1))
        # reference_frame = gm[1]  # set ANCOM-BC like delta

        spectrum['prob_num'] = np.mean(weights > self.threshold, axis=1)
        spectrum['prob_denom'] = np.mean(weights < -self.threshold, axis=1)

        def cluster_f(x):
            if x['prob_num'] > self.percentile:
                return 'num'
            if x['prob_denom'] > self.percentile:
                return 'denom'
            return 'neutral'

        spectrum['cluster_name'] = spectrum.apply(cluster_f, axis=1)

        # zero out regressor weights
        #spectrum['idx'] = np.arange(len(spectrum))
        #idx = spectrum.loc[spectrum['cluster_name'] == 'neutral', 'idx'].values
        #S = weights.shape[1]
        #for s in range(S):
        #    self.regressors[s].x_weights_[idx] = 0
        return spectrum

    def predict(self, X, U=None):
        X_ = self._preprocess(X)

        N, D, S = X_.shape
        preds = np.zeros((N, S))

        spectrum = self.balance()
        if not self.robust:
            for s in range(S):
                if U is not None:
                    X__ = np.hstack((X_[:, :, s], U.values))
                else:
                    X__ = X_[:, :, s]
                preds[:, s] = self.regressors[s].predict(X__.squeeze()).squeeze()
            return np.round(np.clip(preds.mean(axis=1), a_min=0, a_max=1))
        else:
            spectrum['idx'] = np.arange(len(spectrum))
            top = spectrum.loc[spectrum['cluster_name'] == 'num'].index
            bot = spectrum.loc[spectrum['cluster_name'] == 'denom'].index
            assert len(top) > 0
            assert len(bot) > 0

            num = np.log(X.loc[:, top] + 1).mean(axis=1)
            denom = np.log(X.loc[:, bot] + 1).mean(axis=1)

            bal = (num - denom).squeeze()
            return bal

    def score(self, X, y):
        scores = np.zeros(S)
        for s in range(S):
            scores[s] = self.regressors[s].score(X_[:, :, s].squeeze(), y).squeeze()
        return np.mean(scores)


class PLSUnifrac(PLSBalance):
    def __init__(self, bootstraps=10, robust=True, threshold=0.02):

        self._estimator_type = 'classifier'
        self.bootstraps = bootstraps
        self.robust = robust
        self.threshold = threshold

    def predict(self, X):
        X_ = self._preprocess(X)
        N, D, S = X_.shape
        preds = np.zeros((N, S))

        spectrum = self.balance()

        # zero out regressor weights
        spectrum['idx'] = np.arange(len(spectrum))
        idx = spectrum.loc[spectrum['cluster_name'] == 'neutral', 'idx'].values
        for s in range(S):
            self.regressors[s].x_weights_[idx] = 0

        for s in range(S):
            preds[:, s] = self.regressors[s].predict(X_[:, :, s].squeeze()).squeeze()

        return np.round(np.clip(preds.mean(axis=1), a_min=0, a_max=1))


class AgeSexClassifier(object):
    def __init__(self, diffs, threshold=0.02, percentile=0.95):
        self.diffs = diffs
        self._estimator_type = 'classifier'
        self.threshold = threshold
        self.percentile = percentile

    # def fit(self, X, Y):
    #     return self

    def balance(self):
        weights = self.diffs - self.diffs.mean(axis=0)
        spectrum = pd.DataFrame({'mean': weights.mean(axis=1),
                                 'std': weights.std(axis=1)},
                                index=self.diffs.index)
        spectrum['prob_num'] = np.mean(weights > self.threshold, axis=1)
        spectrum['prob_denom'] = np.mean(weights < -self.threshold, axis=1)

        def cluster_f(x):
            if x['prob_num'] > self.percentile:
                return 'num'
            if x['prob_denom'] > self.percentile:
                return 'denom'
            return 'neutral'

        spectrum['cluster_name'] = spectrum.apply(cluster_f, axis=1)
        return spectrum

    def predict(self, X, y, m):
        """
        Parameters
        ----------
        X : pd.DataFrame
           Abundance table
        y : pd.Series
           Outcomes
        m : pd.Series
           Match IDs

        Returns
        -------
        cc_diff : pd.Series
           Case control balance differences.
        """
        spectrum = self.balance()
        # assert set(X.index) & set(spectrum.index) == set(X.index)
        spectrum['idx'] = np.arange(len(spectrum))
        top = spectrum.loc[spectrum['cluster_name'] == 'num'].index
        bot = spectrum.loc[spectrum['cluster_name'] == 'denom'].index
        assert len(top) > 0
        assert len(bot) > 0

        num = np.log(X.loc[:, top] + 1).mean(axis=1)
        denom = np.log(X.loc[:, bot] + 1).mean(axis=1)

        bal = (num - denom).squeeze()

        res = pd.DataFrame({'X': bal, 'y': y, 'Match_IDs': m})
        res = res.sort_values('y')
        cc_diff = res.groupby('Match_IDs').apply(lambda x: x['X'][0] - x['X'][1])
        return cc_diff
