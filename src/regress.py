# %% Imports

import datetime

import numpy as np
import pandas as pd

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.linear_model import LinearRegression

# %% Basic setup

epsilon = 0.001

country_regions = [
    'US',
    'Canada',
    'Italy',
    'Iran',
    'United Kingdom',
    'France',
    'Spain',
    'Germany',
]

# %% Load the data

data_full = pd.read_parquet("data/combined.parquet")
data_country_region = data_full.drop(columns=['province_state', 'state', 'city', 'county', 'lat', 'lon'])

statuses = sorted(list(set(data_country_region['status'].values)))

data = {}
for country_region in country_regions:
    data[country_region] = {}
    for status in statuses:
        location = (data_country_region['status'] == status) & (data_country_region['country_region'] == country_region)
        data[country_region][status] = data_country_region.loc[location].drop(columns=['status', 'country_region'])
        data[country_region][status] = data[country_region][status].groupby(['date']).sum().asfreq('D')
        data[country_region][status]['days'] = data[country_region][status].index.to_julian_date().tolist()
        data[country_region][status]['days'] = data[country_region][status]['days'] - np.min(data[country_region][status]['days'])
        data[country_region][status]['log2count'] = np.log2(data[country_region][status]['count'] + epsilon)
        del location

# %% Fit the regression models

n_days_back_fit = 7 * 2 + 1
n_days_extrapolate = [-n_days_back_fit, 0, 7, 14]


def regress(df: pd.DataFrame):

    df = df.iloc[-(n_days_back_fit + 1):]

    reg = LinearRegression()
    reg.fit(df['days'].values.reshape(-1, 1), df['log2count'].values.reshape(-1, 1),
            sample_weight=np.linspace(0.0, 1.0, n_days_back_fit + 1) * (df['count'].values > 0.0))

    log2_weekly_multiplier = 7 * reg.coef_[0][0]
    weekly_multiplier = np.exp2(log2_weekly_multiplier)

    dates = [df.index[-1] + n_days * df.index.freq for n_days in n_days_extrapolate]
    days = [df.iloc[-1]['days'] + n_days for n_days in n_days_extrapolate]
    log2count = reg.predict(np.array(days).reshape(-1, 1))[:, 0]
    count = np.exp2(log2count)

    return {
        'weekly_multiplier': weekly_multiplier,
        'interpolation': {'dates': dates[0:2], 'days': days[0:2], 'log2count': log2count[0:2], 'count': count[0:2]},
        'extrapolation': {'dates': dates[1:],  'days': days[1:],  'log2count': log2count[1:],  'count': count[1:]},
    }


regression = {}
for country_region in country_regions:
    regression[country_region] = {}
    for status in statuses:
        regression[country_region][status] = regress(data[country_region][status])

# %% Set up the plots

sns.set()
palette = sns.color_palette("colorblind")

plt.rcParams['figure.figsize'] = [11, 8.5]

fig, ax = plt.subplots()

n_days_back_plot = 7 * 6 + 1

# %% Plot the data and regressions

country_region = 'US'

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

markersize = 16.0
linewidth = 4.0

#|fig, ax = plt.subplots()  # FIXME (Needs to loop) BEGIN

latest_date = max([data[country_region][status].index[-1].to_pydatetime().date() for status in statuses])
latest_date_str = latest_date.strftime('%B %d, %Y')

plt.title(f"{country_region} Counts as of {latest_date_str} UTC End of Day")


def plot_markers():
    for status in statuses:
        df = data[country_region][status].iloc[-(n_days_back_plot + 1):]
        ax.semilogy(df.index.to_pydatetime(), df['count'] + epsilon, '.', color=marker_color[status], markersize=markersize)


plot_markers()  # plot the markers and set the axes

for status in statuses:
    df = data[country_region][status]
    rgi = regression[country_region][status]['interpolation']
    ax.semilogy(rgi['dates'], rgi['count'], color=line_color[status], linestyle='-', linewidth=linewidth)
    rge = regression[country_region][status]['extrapolation']
    ax.semilogy(rge['dates'], rge['count'], color=line_color[status], linestyle=':', linewidth=linewidth)
    for index in range(-3,0):
        annotation_date = rge['dates'][index].to_pydatetime().date().strftime('%b %d')
        annotation_count = f"{int(rge['count'][index] + 0.5):,}"
        annotation = f"{annotation_count}\n{annotation_date}"
        va = 'center'
        if index == -3 and df.iloc[-3]['count'] > 0:
            annotation = f"{annotation}\n"
            va = 'bottom'
        plt.annotate(annotation, xy=(rge['dates'][index], rge['count'][index]),
                     fontweight='bold', ha='center', va=va)

plot_markers()  # replot the markers so they are on top of the lines

ax.get_xaxis().set_major_locator(mpl.dates.WeekdayLocator(byweekday=mpl.dates.MONDAY))
ax.get_xaxis().set_major_formatter(mpl.dates.DateFormatter('%b %d'))
ax.set_xlabel(f"Date", labelpad=12)

ax.set_ylim(ymin=1)
ax.get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
ax.set_ylabel("People")

plt.grid(b=True, which='major', axis='x', linewidth=1.0)
plt.grid(b=True, which='major', axis='y', linewidth=1.0)
plt.grid(b=True, which='minor', axis='y', linewidth=0.5)

fig.legend([label.title() for label in statuses], loc='upper left', bbox_to_anchor=(0.11, 0.950),
           frameon=False, prop={'weight': 'bold'})
fig.autofmt_xdate()

plt.show()  # FIXME (Needs to loop) END

# %% TODO Start Here!

# ax.legend([f"https://github.com/CSSEGISandData/COVID-19\nRaw Count Data (US, Confirmed) {datetime.date.today()} EOD",
#            f"Weekly Count Multiplier: {weekly_multiplier:.2f}"])
