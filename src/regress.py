# %% Imports

import os
import glob

import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import seaborn as sns

from sklearn.linear_model import LinearRegression

from ruamel_yaml import YAML

# %% Basic setup

countries = [
    # This list may be overridden, below, where we choose a larger swath of countries
    "Australia", "Austria", "Belgium", "Brazil", "Canada", "Chile", "China", "Czechia", "Denmark", "Ecuador", "Finland", "France", "Germany", "Greece", "Iceland", "Indonesia", "Iran", "Ireland", "Israel", "Italy", "Japan", "Luxembourg", "Malaysia", "Netherlands", "Norway", "Pakistan", "Poland", "Portugal", "Saudi Arabia", "South Korea", "Spain", "Sweden", "Switzerland", "Thailand", "Turkey", "United States", "United Kingdom",
]

# %% Load the data

ts_global = {
    'confirmed': pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv", header=0, index_col=1),
    'deaths':    pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv", header=0, index_col=1),
    'recovered': pd.read_csv("https://github.com/adfernandes/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv", header=0, index_col=1),
}

for status in ts_global:
    ts_global[status].rename(index={"Taiwan*": "Taiwan", "Korea, South": "South Korea", "US": "United States"}, inplace=True)
    ts_global[status] = ts_global[status].drop(columns=['Province/State', 'Lat', 'Long']).transpose()
    ts_global[status].index = pd.to_datetime(ts_global[status].index, dayfirst=False, yearfirst=False, utc=True)
    ts_global[status] = ts_global[status].groupby(ts_global[status].columns, axis='columns').aggregate(np.sum)
    ts_global[status] = ts_global[status].asfreq('D')

statuses = sorted(list(set(ts_global) - set(['recovered'])))  # FIXME The 'recovered' population make the plots messy and do not increase understanding :-(

# | # Select all countries in the data set, overriding any previous list value
# | countries = sorted(list(set(ts_global['confirmed'].columns.tolist()) & set(ts_global['deaths'].columns.tolist())))

data = {}
for country in countries:
    data[country] = {}
    for status in statuses:
        data[country][status] = pd.DataFrame(ts_global[status][country]).rename(columns={country: "count"})
        data[country][status]['days'] = data[country][status].index.to_julian_date().tolist()
        data[country][status]['days'] = data[country][status]['days'] - np.min(data[country][status]['days'])
        data[country][status]['log2count'] = np.log2(data[country][status]['count'])

# %% Fit the regression models

n_days_back_fit = 9
n_days_extrapolate = [-(n_days_back_fit-1)-7, -(n_days_back_fit-1), 0, 7, 14]


too_few = set()
for country in countries:
    for status in statuses:
        if any(data[country][status]['count'][-n_days_back_fit:] < 1):
            too_few.add(country)
print(f"too_few: {sorted(list(too_few))}")
for remove in too_few: del data[remove]
countries = sorted(list(set(countries) - too_few))


yaml = YAML()
yaml.default_flow_style = False
contries_filename = "site/_data/countries.yaml"
with open(contries_filename, 'w') as countries_file:
    yaml.dump(countries, countries_file)


def regress(df: pd.DataFrame):

    df = df.iloc[-n_days_back_fit:]

    reg = LinearRegression()
    sample_weight = np.linspace(0.25, 1.0, n_days_back_fit) * (df['count'].values >= 1.0)
    reg.fit(df['days'].values.reshape(-1, 1), df['log2count'].values.reshape(-1, 1), sample_weight=sample_weight)

    log2_weekly_multiplier = 7 * reg.coef_[0][0]
    weekly_multiplier = np.exp2(log2_weekly_multiplier)

    dates = [df.index[-1] + n_days * df.index.freq for n_days in n_days_extrapolate]
    days = [df.iloc[-1]['days'] + n_days for n_days in n_days_extrapolate]
    log2count = reg.predict(np.array(days).reshape(-1, 1))[:, 0]
    count = np.exp2(log2count)

    return {
        'weekly_multiplier': weekly_multiplier,
        'interpolation': {'dates': dates[1:3], 'days': days[1:3], 'log2count': log2count[1:3], 'count': count[1:3]},
        'extrapolation': {'dates': dates[2: ], 'days': days[2: ], 'log2count': log2count[2: ], 'count': count[2: ]},
    }


regression = {}
for country in countries:
    regression[country] = {}
    for status in statuses:
        print(f"regressing: {country} {status}")
        regression[country][status] = regress(data[country][status])

# %% Set up the plots

sns.set()
palette = sns.color_palette("colorblind")

plt.rcParams['figure.figsize'] = [11, 8.5]

image_formats = {'svg': {}, 'pdf': {}, 'png': {'dpi': 300}}

marker_color = {
    'confirmed': palette[0],
    'deaths': palette[3],
    'recovered': palette[2],
}

line_color = {
    'confirmed': palette[9],
    'deaths': palette[1],
    'recovered': palette[8],
}

site_plots = "site/plots"

markersize = 16.0
linewidth = 4.0

n_days_back_plot = 7 * 6

# %% Plot the data and regressions

for image_format in image_formats:
    for file in glob.glob(f"{site_plots}/{image_format}/*.{image_format}"):
        os.remove(file)

for country in countries:

    print(f"plotting: {country}")

    fig, ax = plt.subplots()  # FIXME (Needs to loop) BEGIN
    ax_facecolor = ax.get_facecolor()

    # | axs = ax.twinx() # FIXME https://github.com/matplotlib/matplotlib/issues/16405
    # | axs.get_yaxis().set_major_locator(plt.NullLocator())
    # | axs.get_yaxis().set_major_formatter(plt.NullFormatter())

    latest_date = max([data[country][status].index[-1].to_pydatetime().date() for status in statuses])
    latest_date_str = latest_date.strftime('%B %d, %Y')

    plt.title(f"{country} COVID-19 Cases as of {latest_date_str} UTC EOD, JHU CSSE Data")

    for status in statuses:
        df = data[country][status].iloc[-(n_days_back_plot + 1):]
        ax.semilogy(df.index.to_pydatetime(), df['count'], '.', color=marker_color[status], markersize=markersize, zorder=1)

    for status in statuses:
        df = data[country][status]
        rgi = regression[country][status]['interpolation']
        ax.semilogy(rgi['dates'], rgi['count'], color=line_color[status], linestyle='-', linewidth=linewidth)
    for status in statuses:
        rge = regression[country][status]['extrapolation']
        ax.semilogy(rge['dates'], rge['count'], color=line_color[status], linestyle=':', linewidth=linewidth)
        for index in range(-3,0):
            annotation_date = rge['dates'][index].to_pydatetime().date().strftime('%b %d')
            annotation_count = f"{int(rge['count'][index] + 0.5):,}"
            annotation = f"{annotation_count}\n{annotation_date}"
            va = 'center'
            alpha = 0.65
            if index == -3 and df.iloc[-3]['count'] > 0:
                annotation = f"{annotation}\n"
                va = 'bottom'
                alpha = 0.0
            text = plt.text(rge['dates'][index], rge['count'][index], annotation, fontweight='bold', ha='center', va=va)
            text.set_bbox({'facecolor': ax_facecolor, 'edgecolor': 'none', 'alpha': alpha})

    ax.get_xaxis().set_major_locator(mpl.dates.WeekdayLocator(byweekday=mpl.dates.MONDAY))
    ax.get_xaxis().set_major_formatter(mpl.dates.DateFormatter('%b %d'))
    ax.set_xlabel(f"Date", labelpad=12)

    ax.set_ylim(ymin=1)
    ax.get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.set_ylabel("People")

    # | axs.get_yaxis().set_ticks(rge['count']) # FIXME See the 'twinx' comment, above
    # | Now use this to annotate the right-hand y-axis, rather than the lines

    plt.grid(b=True, which='major', axis='x', linewidth=1.0)
    plt.grid(b=True, which='major', axis='y', linewidth=1.0)
    plt.grid(b=True, which='minor', axis='y', linewidth=0.5)

    legend_labels = [label.title() for label in statuses]
    for status in statuses:
        legend_labels.append(f"{regression[country][status]['weekly_multiplier']:.1f} $\\times$ per week")
    fig.legend(legend_labels, ncol=2, frameon=False, prop={'weight': 'bold'}, loc='upper left', bbox_to_anchor=(0, 1), bbox_transform=ax.transAxes)

    fig.autofmt_xdate()

    for image_format in image_formats:
        plt.savefig(f"{site_plots}/{image_format}/{country}.{image_format}", **(image_formats[image_format]))

    plt.close()  # | plt.show()

# %% Done
