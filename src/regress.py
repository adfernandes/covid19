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

# %% The initial set of countries that we're interested in

countries = ["Australia", "Austria", "Belgium", "Brazil", "Canada", "Chile", "China", "Czechia", "Denmark", "Ecuador", "Finland", "France", "Germany", "Greece", "Iceland", "Indonesia", "Iran", "Ireland", "Israel", "Italy", "Japan", "Luxembourg", "Malaysia", "Netherlands", "Norway", "Pakistan", "Poland", "Portugal", "Saudi Arabia", "South Korea", "Spain", "Sweden", "Switzerland", "Thailand", "Turkey", "United States", "United Kingdom"]

use_all_countries = False  # if set to 'True', reset 'countries' to all countries found in the data, after the data is loaded

statuses = ['confirmed', 'deaths']  # leave out 'recovered' for now since they are less informative and make the plots confusing

# %% Load the data from the external repository

ts_global = {
    'confirmed': pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv", header=0, index_col=1),
    'deaths':    pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv", header=0, index_col=1),
    'recovered': pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv", header=0, index_col=1),
}

# %% Normalize the time-series data, summing across all 'Province/State' entries of each 'Country/Region'

for status in ts_global:
    ts_global[status].rename(index={"Taiwan*": "Taiwan", "Korea, South": "South Korea", "US": "United States"}, inplace=True)
    ts_global[status] = ts_global[status].drop(columns=['Province/State', 'Lat', 'Long']).transpose()
    ts_global[status].index = pd.to_datetime(ts_global[status].index, dayfirst=False, yearfirst=False, utc=True)
    ts_global[status] = ts_global[status].groupby(ts_global[status].columns, axis='columns').aggregate(np.sum)
    ts_global[status] = ts_global[status].asfreq('D')

if use_all_countries:
    countries = sorted(list(set(ts_global['confirmed'].columns.tolist()) & set(ts_global['deaths'].columns.tolist())))

# %% Split the global time-series data by country then by status

data = {}
for country in countries:
    data[country] = {}
    for status in statuses:
        data[country][status] = pd.DataFrame(ts_global[status][country]).rename(columns={country: "count"})
        data[country][status]['days'] = data[country][status].index.to_julian_date().tolist()
        data[country][status]['days'] = data[country][status]['days'] - np.min(data[country][status]['days'])
        data[country][status]['log2count'] = np.log2(data[country][status]['count'])

# %% Set the regression model training and prediction windows
#
#    Offsets are from the LAST observation, so '0' represents
#    the most recent observation, '-1' repreents the second-most
#    recent observation, and '1' represents a future prediction
#    for one day after the most recent observation.

n_days_train = 9  # train the model on this many most-recent days

days_offset_train = np.array(range(-(n_days_train - 1), 1))

days_offset_predict = np.array(range(15))         # two weeks, in total
days_offset_predict_label = np.array([0, 7, 14])  # now, week one and two

# %% Remove countries that have too few observations

too_few = set()

for country in countries:
    for status in statuses:
        counts = data[country][status]['count'][-n_days_train:]
        if len(counts) < n_days_train or any(counts < 1):
            too_few.add(country)

print(f"too_few: {sorted(list(too_few))}")

for remove in too_few:
    del data[remove]

countries = sorted(list(set(countries) - too_few))

# %% Save the country list for external use

countries_filename = "site/_data/countries.yaml"

if os.path.exists(countries_filename):
    os.remove(countries_filename)

yaml = YAML()
yaml.default_flow_style = False
with open(countries_filename, 'w') as countries_file:
    yaml.dump(countries, countries_file)


# %% Define the regression functions

def regress_semilog(df: pd.DataFrame):

    df = df.iloc[-n_days_train:]
    rv = {}  # return value

    reg = LinearRegression()
    sample_weight = np.linspace(0.25, 1.0, n_days_train)  # these were selected as a hyperparamer by inspection

    reg.fit(df['days'].values.reshape(-1, 1), df['log2count'].values.reshape(-1, 1), sample_weight=sample_weight)

    log2_weekly_multiplier = 7 * reg.coef_[0][0]
    rv['weekly_multiplier'] = np.exp2(log2_weekly_multiplier)

    def predict(rv: dict, which: str, offsets: np.array) -> None:
        """
        :param rv: where to place the resulting dict
        :param which: one of 'interpolation' or 'extrapolation'
        :param offsets: the array of day offsets which to predict
        """
        rv[which] = {}
        rv[which]['days'] = df.iloc[-1]['days'] + offsets
        rv[which]['dates'] = df.index[-1] + (df.index.freq * offsets)
        rv[which]['log2count'] = reg.predict(np.array(rv[which]['days']).reshape(-1, 1))[:, 0]
        rv[which]['count'] = np.exp2(rv[which]['log2count'])

    predict(rv, 'interpolation', days_offset_train)
    predict(rv, 'extrapolation', days_offset_predict)

    return rv


def regress_logistic(df: pd.DataFrame):

        df = df.iloc[-n_days_train:]
        rv = {}  # return value

        # TODO - START HERE

        return rv


# %% Do the regression calculations for all countries and statuses

regression = {}
for country in countries:
    regression[country] = {}
    for status in statuses:
        print(f"regressing: {country} {status}")
        regression[country][status] = regress_semilog(data[country][status])

# %% Set up the plots and the plotting parameters

sns.set()
palette = sns.color_palette("colorblind")

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

line_width = 4.0
marker_size = 16.0

plt.rcParams['figure.figsize'] = [11, 8.5]

site_plots = "site/plots"

image_formats = {'svg': {}, 'pdf': {}, 'png': {'dpi': 300}}

n_days_back_plot = 7 * 6  # only plot this many of the most-recent days

# %% Remove any old plots so that outdated ones don't accidentally survive

for image_format in image_formats:
    for file in glob.glob(f"{site_plots}/{image_format}/*.{image_format}"):
        os.remove(file)

# %% Plot the data, regressions, and predictions for each country

for country in countries:

    print(f"plotting: {country}")

    fig, ax = plt.subplots()
    ax_facecolor = ax.get_facecolor()

    latest_date = max([data[country][status].index[-1].to_pydatetime().date() for status in statuses])
    latest_date_str = latest_date.strftime('%B %d, %Y')

    plt.title(f"{country} COVID-19 Cases as of {latest_date_str} UTC EOD, JHU CSSE Data")

    # Plot the actual observations as markers, limited to the selected most-recent days
    #
    for status in statuses:
        df = data[country][status].iloc[-n_days_back_plot:]
        ax.semilogy(df.index.to_pydatetime(), df['count'], '.', color=marker_color[status], markersize=marker_size)

    # Plot the interpolating, predicted line
    #
    for status in statuses:
        rgi = regression[country][status]['interpolation']
        ax.semilogy(rgi['dates'], rgi['count'], color=line_color[status], linestyle='-', linewidth=line_width)

    # Plot the extrapolated, predicted line
    #
    for status in statuses:
        rge = regression[country][status]['extrapolation']
        ax.semilogy(rge['dates'], rge['count'], color=line_color[status], linestyle=':', linewidth=line_width)

        for index in days_offset_predict_label:

            label_date = rge['dates'][index].to_pydatetime().date().strftime('%b %d')
            label_count = f"{int(rge['count'][index] + 0.5):,}"
            annotation = f"{label_count}\n{label_date}"
            va = 'center'  # vertical alignment
            alpha = 0.65

            if index == 0:
                annotation = f"{annotation}\n"
                va = 'bottom'  # vertical alignment
                alpha = 0.0

            text = plt.text(rge['dates'][index], rge['count'][index], annotation, fontweight='bold', ha='center', va=va)
            text.set_bbox({'facecolor': ax_facecolor, 'edgecolor': 'none', 'alpha': alpha})

    ax.get_xaxis().set_major_locator(mpl.dates.WeekdayLocator(byweekday=mpl.dates.MONDAY))
    ax.get_xaxis().set_major_formatter(mpl.dates.DateFormatter('%b %d'))
    ax.set_xlabel(f"Date", labelpad=12)

    ax.set_ylim(ymin=1)
    ax.get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax.set_ylabel("People")

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

    if plt.isinteractive():
        plt.show()
    else:
        plt.close()

# %% Done
