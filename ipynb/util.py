import glob
import pandas as pd
import numpy as np
from collections import defaultdict
import arviz as az
from biom import load_table
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import svds
from scipy.stats import ttest_1samp
from gneiss.balances import sparse_balance_basis
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import binom_test
from sklearn.mixture import GaussianMixture

import random


def ranking(x, reference_percentile=0.5, reference_frame=None, log_probs=False):
    """ Computes several rankings given a differential posterior"""
    x = x - x.mean(axis=0)   # CLR transform posterior
    s = x.std(axis=1)
    m = x.mean(axis=1)
    mi = np.percentile(x, q=50, axis=1)  # gives the median
    lo = np.percentile(x, q=5, axis=1)
    hi = np.percentile(x, q=95, axis=1)
    index = x.index
    diffs = pd.DataFrame({'mean': m, 'std' : s, '5%': lo, '50%': mi, '95%': hi},
                         index=index)

    # Compute log-odds ranking
    if log_probs:
        b = x.apply(np.argmin, axis=0)
        t = x.apply(np.argmax, axis=0)
        countb = b.value_counts()
        countt = t.value_counts()
        countb.index = x.index[countb.index]
        countt.index = x.index[countt.index]
        countb.name = 'counts_bot'
        countt.name = 'counts_top'
        diffs = pd.merge(diffs, countb, left_index=True, right_index=True, how='left')
        diffs = pd.merge(diffs, countt, left_index=True, right_index=True, how='left')
        diffs = diffs.fillna(0)
        diffs['prob_top'] = (diffs['counts_top'] + 1) / (diffs['counts_top'] + 1).sum()
        diffs['prob_bot'] = (diffs['counts_bot'] + 1) / (diffs['counts_bot'] + 1).sum()
        diffs['prob_lr'] = diffs.apply(
            lambda x: np.log(x['prob_top'] / x['prob_bot']), axis=1)
        diffs = diffs.replace([np.inf, -np.inf, np.nan], 0)

    # Compute effect size
    y = x - x.mean(axis=0)   # CLR transform posterior
    ym, ys = y.mean(axis=1), y.var(axis=1, ddof=1)
    ye = ym / ys
    diffs['effect_size'] = ye
    diffs['effect_std'] = 1 / ys
    # Compute effect size pvalues
    if reference_frame is None:
        reference_frame = np.percentile(ym, q=reference_percentile)
    tt, pvals = ttest_1samp(y.values, popmean=reference_frame, axis=1)
    diffs['tstat'] = tt
    diffs['pvalue'] = pvals
    return diffs


def extract_differentials(filename, features=None):
    """ Extract bootstrapped differentials from file. """
    posterior = az.from_netcdf(filename)
    x = posterior['posterior']['diff'].to_dataframe()
    x = x.reset_index().pivot(
        index='features', columns=['chain', 'draw'], values='diff')
    return x

def extract_differentials_from_folder(filename):
    files = glob.glob(f'{filename}/*.nc')
    def read_f(x):
        basename_f = lambda x: x.split('/')[-1][:-3]
        f = az.from_netcdf(x).posterior['diff'].to_dataframe()
        f = f.rename(columns={'diff': basename_f(x)})
        return f
    return pd.concat(list(map(read_f, files)), axis=1).T

def select_features(lr, alpha=1e-3, prob_lr=False):
    """ Performs BH FDR correction to select candidate features.

    Specifically, we will select features based on effect size
    and log-odds ranking.

    Parameters
    ----------
    lr : pd.DataFrame
       List of statistics for each feature.
       Columns are different statistics including effect size,
       logodds rankings, average log fold change, etc
    """
    # idx1 = lr['pvalue'] < alpha / len(lr)
    idx1 = multipletests(lr['pvalue'], method='fdr_bh', alpha=alpha)[0]
    if prob_lr:
        idx2 = np.logical_and(lr['prob_lr'] > 0, lr['effect_size'] > 0)
        idx3 = np.logical_and(lr['prob_lr'] < 0, lr['effect_size'] < 0)
    else:
        # idx2 = lr['effect_size'] > 0
        # idx3 = lr['effect_size'] < 0
        idx2 = lr['tstat'] > 0
        idx3 = lr['tstat'] < 0
    asd = lr.loc[np.logical_and(idx1, idx2)]
    con = lr.loc[np.logical_and(idx1, idx3)]
    return con, asd

def get_genomic_data(filename, gotu_lookup=None):
    """ Obtain a genes per microbe table.

    Parameters
    ----------
    filename : path
        Path to stratified biom table output from woltka
    gotu_lookup : dict
        Convert GOTU ids to genome ids if mapping is provided

    Returns
    -------
    Table of microbes by gene counts
    """
    func_table = load_table(filename)
    func_ids = func_table.ids(axis='observation')
    if gotu_lookup is not None:
        func_df = pd.DataFrame(list(map(lambda x: x.split('_'), func_ids)))
        func_df[0] = list(map(lambda x: gotu_lookup[x], func_df[0]))
        func_df[1] = list(map(lambda x: 'K' + '0' * (5 - len(x)) + x, func_df[1]))
    else:
        func_df = pd.DataFrame(list(map(lambda x: x.split('|'), func_ids)))

    # convert to sparse matrix for convenience
    func_df.columns = ['OGU', 'KEGG']
    func_df['count'] = 1

    ogus = list(set(func_df['OGU']))
    ogu_lookup = pd.Series(np.arange(0, len(ogus)), ogus)
    keggs = list(set(func_df['KEGG']))
    kegg_lookup = pd.Series(np.arange(0, len(keggs)), keggs)
    func_df['OGU_id'] = func_df['OGU'].apply(lambda x: ogu_lookup.loc[x]).astype(np.int64)
    func_df['KEGG_id'] = func_df['KEGG'].apply(lambda x: kegg_lookup.loc[x]).astype(np.int64)
    c, i, j = func_df['count'].values, func_df['OGU_id'].values, func_df['KEGG_id'].values
    data = coo_matrix((c, (i, j)))
    ko_ogu = pd.DataFrame(data.todense(), index=ogus, columns=keggs)
    return ko_ogu


def log_pvalue(lr, alpha=0.1, filter=True):
    """ Converts pvalues to -log(pvalue)

    Also performs Boniferroni correction.
    """
    lr = lr.reset_index()
    # lr.columns = ['KEGG', 'pvalue']
    lr['-log(pvalue)'] = -np.log(lr['pvalue'] + 1e-200)
    res = multipletests(lr['pvalue'], method='fdr_bh', alpha=alpha)
    lr['pvalue_corrected'] = res[1]
    if filter:
        lr = lr.loc[res[0]]
        return lr
    return lr


def collapse_transcripts(rna):
    """ Removes isoform information. """
    idx = list(map(lambda x: x.split('.')[0], rna.index))
    rna = rna.reset_index()
    rna.index = idx
    return rna


def aggregate_pathways(pathway_name_file, pathway_to_ko_file, features,
                       columns=['Pathway', 'KO']):
    """ Aggregate microbial KEGGs at pathway level. """
    pwy2kegg = read_kegg_dict(pathway_to_ko_file, columns)
    pwy_name = pd.read_table(pathway_name_file, header=None)
    pwy_name.columns = ['Pathway', 'Name']
    pwy2kegg = pd.merge(pwy2kegg, pwy_name, left_on='Pathway', right_on='Pathway')

    lookup = {d: i for i, d in enumerate(pwy2kegg['Name'].value_counts().index)}
    pwy2kegg['ID'] = pwy2kegg['Name'].apply(lambda x: lookup[x])
    col = list(set(columns) - {'Pathway'})
    if col == 'HSA':
        col2 = 'HSA'
    else:
        col2 = 'KEGG'
    sig = pd.merge(pwy2kegg, features,
                   left_on=col, right_on=col2).drop_duplicates()
    return sig


def btest(pa1, pa2, seed=0, return_proportions=False):
    """ Performs genome wide binomial test between two groups of taxa

    Parameters
    ----------
    df1 : pd.DataFrame
        Rows are taxa, columns are genes
    df2 : pd.DataFrame
        Rows are taxa, columns are genes

    Returns
    -------
    pd.Series : list of genes associated with df1
    pd.Series : list of genes associated with df2
    """
    np.random.seed(seed)
    random.seed(seed)
    #pa1 = df1 > 0
    #pa2 = df2 > 0
    idx = list(set(pa1.columns) | set(pa2.columns))
    idx.sort()
    pa1 = pa1.sum(axis=0).reindex(idx).fillna(0)
    pa2 = pa2.sum(axis=0).reindex(idx).fillna(0)
    n = pa1 + pa2
    obs = list(zip(list(pa1.values), list((pa2.values + 1) / (pa2 + 1).sum()), list(n.values)))
    pvals = pd.Series([binom_test(a, n, b, 'two-sided') for (a, b, n) in obs],
                      index=n.index)
    if return_proportions:
        res = pd.DataFrame({'groupA': pa1, 'groupB': pa2, 'pval': pvals})
        def relabel_f(x):
            if x['groupA'] < x['groupB']:
                return 'groupB'
            else:
                return 'groupA'
        res['side'] = res.apply(relabel_f, axis=1)
        return res

    return pvals


def read_kegg_dict(fname, columns, combine=False):
    """ Reads in KEGG mapping.

    Parameters
    ----------
    columns : list
       Specifies key and value names
    combine : bool
       Specifies if value names should be concatenated or not.

    Returns
    -------
    pd.DataFrame : Key-value pairs
    """
    K2V = list()
    with open(fname) as f:
        for line in f:
            toks = line.rstrip().split('\t')
            if combine:
                class_ = ' '.join(toks[2:])
                pwy = toks[0]
                pk = [(pwy, class_)]
            else:
                keggs = toks[1:]
                pwy = [toks[0]] * len(keggs)
                pk = list(zip(pwy, keggs))
            K2V += pk
    K2V = pd.DataFrame(K2V, columns=columns)
    return K2V


def rename_clades(tree):
    subtree = tree.copy()
    i = 0
    observed = set()
    for n in subtree.levelorder():
        if n.name is None:
            n.name = f'clade{i}'
            i += 1
        elif n.name in observed:
            n.name = f'{n.name}{i}'
            i += 1
        else:
            observed.add(n.name)
    return subtree


def ilr_transform_differentials(tree, *args, transform_per_diff=False):
    if not transform_per_diff:
        Psi, ast = sparse_balance_basis(tree)
    for a in args:
        if transform_per_diff:
            tips = [n.name for n in tree.tips()]
            feature_ids = list(set(tips) & set(a.index))
            subtree = tree.shear(feature_ids)
            Psi, ast = sparse_balance_basis(subtree)
            yield pd.DataFrame(Psi @ a.loc[feature_ids], index=ast)
        else:
            yield pd.DataFrame(Psi @ a, index=ast)


def all_feature_ids(*args):
    common_ids = set()
    for a in args:
        common_ids |= set(a.index)
    return list(common_ids)


def match_all_differentials(*args):
    common_ids = set(args[0].index)
    for a in args[1:]:
        common_ids &= set(a.index)
    for a in args:
        yield a.loc[common_ids]

def match_all_differentials_and_tree(tree, *args):
    tips = set([n.name for n in tree.tips()])
    common_ids = set(args[0].index) & tips
    for a in args[1:]:
        common_ids &= set(a.index)
    for a in args:
        yield a.loc[common_ids]


def create_projection(X, k=2):
    U, S, V = svds(X, k=k)
    allS = np.linalg.svd(X)[1]
    V = V.T @ np.diag(S)
    proportion_explained = (allS ** 2) / (allS ** 2).sum()
    return V, proportion_explained[:k]

def project_data(X, V):
    return X.T @ V


def match_table(table, md, match_col='Match_IDs',
                group_col='Status', trt='ASD'):
    """ Computes clr matched table"""
    tab_clr = np.log(table + 1)
    tab_clr = tab_clr - tab_clr.mean(axis=1).values.reshape(-1, 1)
    tab_clr = pd.merge(md[[match_col, group_col]], tab_clr,
                       left_index=True, right_index=True)
    tab_clr = tab_clr.sort_values(by=['Status', 'Match_IDs'])
    trt_g = tab_clr.loc[tab_clr[group_col] == trt]
    ref_g = tab_clr.loc[tab_clr[group_col] != trt]

    tab_trt_ref = pd.DataFrame(
        trt_g.iloc[:, 2:].values - trt_g.iloc[:, 2:].values,
        index=trt_g[match_col], columns=ref_g.columns[2:])
    return tab_trt_ref


def balance_classifier(table, md, stats,
                       match_col='Match_IDs',
                       group_col='Status',
                       t=1, b=1):
    pairs = {}
    for n, pair in md.groupby(match_col):
        p = pair.sort_values(group_col)
        asd, con = p.index[0], p.index[1]
        top = stats.tail(t).index
        bot = stats.head(b).index
        asd_top_lr = np.log(table.loc[asd, top] + 1).mean()
        asd_bot_lr = np.log(table.loc[asd, bot] + 1).mean()
        asd_lr = asd_top_lr - asd_bot_lr

        con_top_lr = np.log(table.loc[con, top] + 1).mean()
        con_bot_lr = np.log(table.loc[con, bot] + 1).mean()
        con_lr = con_top_lr - con_bot_lr

        pairs[n] = asd_lr - con_lr
    pairs = pd.Series(pairs)
    p = np.mean(pairs > 0)    # accuracy
    n = np.mean(pairs ** 2)   # mean squared error
    return p, n


def solve(w1, w2, m1, m2, std1, std2):
    r""" Solves for the intersection between Gaussians.

    Parameters
    ----------
    w1: float
        The weight of the first distribution
    w2: float
        The weight of the second distribution
    m1: float
        The mean of the first distribution
    m2: float
        The mean of the second distribution
    std1: float
        The standard deviation of the first distribution
    std2: float
        The standard deviation of the second distribution

    Returns
    -------
    np.array :
        List of intersection points
    """
    # from stackoverflow
    # https://stackoverflow.com/a/22579904/1167475
    a = 1/(2*std1**2) - 1/(2*std2**2)
    b = m2/(std2**2) - m1/(std1**2)
    c = m1**2 /(2*std1**2) - m2**2 / (2*std2**2) - np.log((w1/w2) * np.sqrt(std2/std1))
    return np.roots([a,b,c])

def reorder(mid, m):
    """ Reorders indexes so that the means are in increasing order. """
    lookup = {0: [1, 2], 1: [0, 2], 2: [0, 1]}
    l, r = lookup[mid]
    if m[l] > m[r]:
        l, r = r, l
    return l, mid, r

def balance_thresholds(spectrum):
    """ Calculates thresholds for the balances.

    Parameters
    ----------
    spectrum : np.array
        The axis of interest.
        This will rank all of the features for the balance selection.
    """
    gmod = GaussianMixture(n_components=3)
    gmod.fit(X=spectrum)
    m = gmod.means_
    std = np.sqrt(np.ravel(gmod.covariances_))
    w = gmod.weights_

    # first identify the distribution closest to zero
    mid = np.argmin(np.abs(m))

    # solve for intersections closest to zero
    l, mid, r = reorder(mid, m)
    lsol = solve(w[mid], w[l], m[mid], m[l], std[mid], std[l])
    rsol = solve(w[mid], w[r], m[mid], m[r], std[mid], std[r])

    lsol = lsol[np.argmin(np.abs(lsol))]
    rsol = rsol[np.argmin(np.abs(rsol))]
    return lsol, rsol, gmod
