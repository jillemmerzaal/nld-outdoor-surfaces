# visualizations.py
import matplotlib.pyplot as plt
import seaborn as sns


def simple_plot(y, ax=None, plt_kwargs=None):
    if plt_kwargs is None:
        plt_kwargs = {}
    if ax is None:
        ax = plt.gca()
    sns.lineplot(data=y, ax=ax, **plt_kwargs)
    sns.despine(offset=10)
    return ax


def multiple_custom_plots(y_l, x_s1, y_s1, x_s2, y_s2, ax=None, plt_kwargs=None, sct_kwargs=None):
    if sct_kwargs is None:
        sct_kwargs = {}
    if plt_kwargs is None:
        plt_kwargs = {}
    if ax is None:
        ax = plt.gca()
    sns.lineplot(data=y_l, ax=ax, **plt_kwargs)
    ax.scatter(x_s1, y_s1, **sct_kwargs)

    ax.scatter(x_s2, y_s2, **sct_kwargs)

    sns.despine(offset=10)
    return ax


def complex_plot(y_l, ax=None, **plt_kwargs):
    if ax is None:
        ax = plt.gca()
    sns.lineplot(data=y_l, ax=ax, **plt_kwargs)
