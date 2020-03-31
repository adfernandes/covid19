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
from scipy.optimize import least_squares

from ruamel_yaml import YAML

original_np_seterr = np.seterr(all='raise')  # raise exceptions rather than warnings

# %% The initial set of countries that we're interested in

countries = ["Australia", "Austria", "Belgium", "Brazil", "Canada", "Chile", "China", "Czechia", "Denmark", "Ecuador", "Finland", "France", "Germany", "Greece", "Iceland", "Indonesia", "Iran", "Ireland", "Israel", "Italy", "Japan", "Luxembourg", "Malaysia", "Netherlands", "Norway", "Pakistan", "Poland", "Portugal", "Saudi Arabia", "South Korea", "Spain", "Sweden", "Switzerland", "Thailand", "Turkey", "United States", "United Kingdom"]

use_all_countries = False  # if set to 'True', reset 'countries' to all countries found in the data, after the data is loaded

us_states = ['California', 'New York', 'Washington'];  # cherrypick these states from the NY Times US Data Set

statuses = ['confirmed', 'deaths']  # leave out 'recovered' for now since they are less informative and make the plots confusing

# %% Load the data from the external repository

ts_global = {
    'confirmed': pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv", header=0, index_col=1),
    'deaths':    pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv", header=0, index_col=1),
    'recovered': pd.read_csv("https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv", header=0, index_col=1),
}

ts_nytimes = pd.read_csv("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv", header=0, index_col=0)

# %% Normalize the time-series data, summing across all 'Province/State' entries of each 'Country/Region'

for status in ts_global:
    ts_global[status].rename(index={"Taiwan*": "Taiwan", "Korea, South": "South Korea", "US": "United States"}, inplace=True)
    ts_global[status] = ts_global[status].drop(columns=['Province/State', 'Lat', 'Long']).transpose()
    ts_global[status].index = pd.to_datetime(ts_global[status].index, dayfirst=False, yearfirst=False, utc=True)
    ts_global[status] = ts_global[status].groupby(ts_global[status].columns, axis='columns').aggregate(np.sum)
    ts_global[status] = ts_global[status].asfreq('D')

if use_all_countries:
    countries = sorted(list(set(ts_global['confirmed'].columns.tolist()) & set(ts_global['deaths'].columns.tolist())))

ts_nytimes.index = pd.to_datetime(ts_nytimes.index, dayfirst=False, yearfirst=False, utc=True)
ts_nytimes = ts_nytimes.drop(columns=['fips'])
ts_nytimes = ts_nytimes.groupby(ts_nytimes.columns, axis='columns').aggregate(np.sum)

for us_state in us_states:
    us_state_name = f"US@{us_state}"
    ts_global['confirmed'][us_state_name] = ts_nytimes.loc[ts_nytimes['state'] == us_state]['cases']
    ts_global['deaths'   ][us_state_name] = ts_nytimes.loc[ts_nytimes['state'] == us_state]['deaths']
    countries.append(us_state_name)


def fix_us_sorting(countries):
    """Ensure that US States sort with the 'United States' country name"""
    def mangle(string):
        if string == "United States":
            return "United States zzzzzzz"
        else:
            return string.replace("US@", "United States ")
    return sorted(countries, key=mangle)


countries = fix_us_sorting(countries)

# %% Split the global time-series data by country then by status

data = {}
for country in countries:
    data[country] = {}
    for status in statuses:
        data[country][status] = pd.DataFrame(ts_global[status][country]).rename(columns={country: "count"})
        data[country][status]['days'] = data[country][status].index.to_julian_date().tolist()
        data[country][status]['days'] = data[country][status]['days'] - np.min(data[country][status]['days'])
        data[country][status]['log2count'] = np.log2(data[country][status]['count'].map(lambda c: c if c > 0 else np.NaN))

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

countries = fix_us_sorting(sorted(list(set(countries) - too_few)))

# %% Save the country list for external use

countries_filename = "site/_data/countries.yaml"

if os.path.exists(countries_filename):
    os.remove(countries_filename)

yaml = YAML()
yaml.default_flow_style = False
with open(countries_filename, 'w') as countries_file:
    yaml.dump(countries, countries_file)


# %% Define the exponential regression model

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


# %% Define the logistic regression model

# Note that the parameterization of the logistic regression model
# is a little different than what is normally presented.
#
# Specifically, choose a parameterization that allows us to use
# unconstrained optimization. So the population count "theoretical
# maximum" of `y_max` is `(1.0 + np.exp2(c[2])) * observed_max`,
# for example.
#
# Also, just as exponential regression, where the residuals are
# computed in log-space, for this logistic regression the residuals
# are computed in "logit" space coordinates.


def predict_logistic(c, t, observed_max):
    log2it = c[0] + c[1] * t
    p = 1.0 / (1.0 + np.exp2(-log2it))
    y_max = (1.0 + np.exp2(c[2])) * observed_max
    y = p * y_max
    return y


def residuals_logistic(c, t, y, observed_max):
    predicted_log2it = c[0] + c[1] * t
    y_max = (1.0 + np.exp2(c[2])) * observed_max
    observed_p = y / y_max
    observed_log2it = np.log2(observed_p / (1.0 - observed_p))
    residual = observed_log2it - predicted_log2it
    return residual


def regress_logistic(df: pd.DataFrame):

        df = df.iloc[-n_days_train:]
        rv = {}  # return value

        observed_max = df['count'].max()
        c_guess = np.array([0, 1, -3])
        result = least_squares(residuals_logistic, c_guess, args=(df['days'].values, df['count'].values, observed_max))
        if not result.success:
            raise RuntimeError(f"failed to converge for reason '{result.status}': {result.message}")

        def predict(rv: dict, which: str, coeff: np.array, offsets: np.array) -> None:
            """
            :param rv: where to place the resulting dict
            :param which: one of 'interpolation' or 'extrapolation'
            :param offsets: the array of day offsets which to predict
            """
            rv[which] = {}
            rv[which]['days'] = df.iloc[-1]['days'] + offsets
            rv[which]['dates'] = df.index[-1] + (df.index.freq * offsets)
            rv[which]['count'] = predict_logistic(coeff, np.array(rv[which]['days']), observed_max)
            rv[which]['log2count'] = np.log2(rv[which]['count'])

        c = result.x

        predict(rv, 'interpolation', c, days_offset_train)
        predict(rv, 'extrapolation', c, days_offset_predict)

        rv['weekly_multiplier'] = rv['extrapolation']['count'][7] / rv['extrapolation']['count'][0]
        rv['expected_maximum'] = (1.0 + np.exp2(c[2])) * observed_max
        rv['observed_maximum'] = observed_max

        return rv


# %% Do the regression calculations for all countries and statuses

exponential = {}
logistic = {}
for country in countries:
    exponential[country] = {}
    logistic[country] = {}
    for status in statuses:
        print(f"regressing: {country}, status: {status}")
        exponential[country][status] = regress_semilog(data[country][status])
        logistic[country][status] = regress_logistic(data[country][status])

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


image_formats = {'svg': {}, 'pdf': {}, 'png': {'dpi': 300}}

n_days_back_plot = 7 * 6  # only plot this many of the most-recent days

site_plots_directory = "site/plots"

# %% Remove any old plots so that outdated ones don't accidentally survive

for image_format in image_formats:
    for file in glob.glob(f"{site_plots_directory}/*/{image_format}/*.{image_format}"):
        os.remove(file)

# %% Plot the data, regressions, and predictions for each country

np.seterr(**original_np_seterr)  # plotting produces many spurious errors that are ignored by default

models = {'exponential': exponential, 'logistic': logistic}

for model, regression in models.items():

    site_plots_model_directory = f"{site_plots_directory}/{model}"

    for country in countries:

        print(f"plotting: {country}")

        fig, ax = plt.subplots()
        ax_facecolor = ax.get_facecolor()

        latest_date = max([data[country][status].index[-1].to_pydatetime().date() for status in statuses])
        latest_date_str = latest_date.strftime('%B %d, %Y')

        country_title = country.replace("US@", "US | ")
        data_source = "JHU CSSE" if not country_title.startswith("US | ") else "NY Times"
        plt.title(f"{country_title} COVID-19 Cases as of {latest_date_str} UTC EOD, {data_source} Data")

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
        label_spacing = 1.0 if model == 'logistic' else None
        for status in statuses:
            line_label = f"{regression[country][status]['weekly_multiplier']:.1f} $\\times$ per week"
            if 'expected_maximum' in regression[country][status]:
                expected_maximum = regression[country][status]['expected_maximum']
                observed_maximum = regression[country][status]['observed_maximum']
                if expected_maximum < 10.0 * observed_maximum:
                    expected_maximum = int(expected_maximum + 0.5)
                    expected_maximum = f"{expected_maximum:,}"
                    line_label = f"{line_label}\n{expected_maximum} maximum"
            legend_labels.append(line_label)
        fig.legend(legend_labels, ncol=2, labelspacing=label_spacing, frameon=False, prop={'weight': 'bold'}, loc='upper left', bbox_to_anchor=(0, 1), bbox_transform=ax.transAxes)

        fig.autofmt_xdate()

        for image_format in image_formats:
            plt.savefig(f"{site_plots_model_directory}/{image_format}/{country}.{image_format}", **(image_formats[image_format]))

        if plt.isinteractive():
            plt.show()
        else:
            plt.close()

# %% Done
