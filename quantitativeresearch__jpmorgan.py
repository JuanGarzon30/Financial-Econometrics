# -*- coding: utf-8 -*-
"""QuantitativeResearch _JPMorgan.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fFOe_LxYXLRxB1mIvIiqNuA_WVYwBp79

## Task #1
"""

#using pandas library to import the data series
import pandas as pd
#using matplotlib library to graph
import matplotlib.pyplot as plt
#rename the origial data "Nat_gas" as "data"
data = pd.read_csv(r"/content/Nat_Gas.csv")

print(data)

#graph to have a first look about the data
#variables
dates = data["Dates"]
price = data["Prices"]

#Plot
plt.figure(figsize=(10, 6))
plt.plot(dates, price, marker='o', linestyle='-', color='#1F5591')
plt.title('Price Over Time')
plt.xlabel('Date')
plt.ylabel('Price')
plt.show()

#Analize the nature of the time series
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
# Plot ACF (Autocorrelation Function)
plt.figure(figsize=(12, 4))
plot_acf(data['Prices'], lags=30, title='Autocorrelation Function (ACF)')
plt.show()

#PACF
plt.figure(figsize=(12, 4))
plot_pacf(data['Prices'], lags=20, title='Partial Autocorrelation Function (PACF)')
plt.show()

#I'm going to forecast using a ARMA(2,0) model
model = ARIMA(data['Prices'], order=(2, 0, 0))
results = model.fit()
# Display model summary
print(results.summary())
# Plot diagnostics
results.plot_diagnostics()
plt.show()
#The error is white noise the Ljung-box coefficient confirms it, also the 2 lags are significant but the first lag it's
#almost 1, so I did a ADF test to prove the existence of unit root

#ADF to prove unit root
result = adfuller(data['Prices'], autolag='AIC')
test_statistic, p_value, _, _, _, _ = result
print(f'Test Statistic: {test_statistic}')
print(f'P-value: {p_value}')
# Interpret the results
if p_value <= 0.05:
    print("Reject the null hypothesis: The data is stationary.")
else:
    print("Fail to reject the null hypothesis: The data is non-stationary.")

#Running the model again with one differencing and seasonality
import statsmodels.api as sm

# Assuming 'data' is your DataFrame with a datetime index and 'Prices' column
order = (2, 1, 0)
seasonal_order = (2, 1, 0, 12)

# Fit SARIMA model
sarima_model = sm.tsa.SARIMAX(data['Prices'], order=order, seasonal_order=seasonal_order)
sarima_results = sarima_model.fit()

# View model summary
print(sarima_results.summary())

# Forecast for the next year using SARIMA(2,1,0,12) model
n_periods = 12
forecast = sarima_results.get_forecast(steps=n_periods)

# Plot the forecast
plt.figure(figsize=(10, 6))
plt.plot(data.index, data['Prices'], label='Observed')
plt.plot(forecast.predicted_mean.index, forecast.predicted_mean, color='#0000CD', label='Forecast')
plt.fill_between(forecast.predicted_mean.index,
                 forecast.conf_int()['lower Prices'],
                 forecast.conf_int()['upper Prices'], color='#1E90FF', alpha=0.3)
plt.legend()
plt.show()

#Monthly forecast
forecast_values = forecast.predicted_mean

for i, value in enumerate(forecast_values):
    print(f"Month {i+1}: {round(value,2)}")

"""## Task #1 - JPMC answer"""

#libraries
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from datetime import date, timedelta

date_time = ["10-2020", "11-2020", "12-2020"]
date_time = pd.to_datetime(date_time)
data = [1, 2, 3]

df = pd.read_csv('Nat_Gas.csv', parse_dates=['Dates']) #Makes "Dates" a datetime object instead a string or numeric value
prices = df['Prices'].values
dates = df['Dates'].values

# plot prices against dates
fig, ax = plt.subplots()
ax.plot_date(dates, prices, '-')
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.set_title('Natural Gas Prices')
ax.tick_params(axis='x', rotation=45)

plt.show()

# First we need the dates in terms of days from the start, to make it easier to interpolate later.
start_date = date(2020,10,31)
end_date = date(2024,9,30)
months = []
year = start_date.year
month = start_date.month + 1
while True:
    current = date(year, month, 1) + timedelta(days=-1)
    months.append(current)
    if current.month == end_date.month and current.year == end_date.year:
        break
    else:
        month = ((month + 1) % 12) or 12
        if month == 1:
            year += 1

days_from_start = [(day - start_date ).days for day in months]

# Simple regression for the trend will fit to a model y = Ax + B. The estimator for the slope is given by \hat{A} = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sum (x_i - \bar{x})^2},
# and that for the intercept by \hat{B} = \bar{y} - hat{A} * \xbar

def simple_regression(x, y):
    xbar = np.mean(x)
    ybar = np.mean(y)
    slope = np.sum((x - xbar) * (y - ybar))/ np.sum((x - xbar)**2)
    intercept = ybar - slope*xbar
    return slope, intercept

time = np.array(days_from_start)
slope, intercept = simple_regression(time, prices)

# Plot linear trend
plt.plot(time, prices)
plt.plot(time, time * slope + intercept)
plt.xlabel('Days from start date')
plt.ylabel('Price')
plt.title('Linear Trend of Monthly Input Prices')
plt.show()
print(slope, intercept)

# From this plot we see the linear trend has been captured. Now to fit the intra-year variation.
# Given that natural gas is used more in winter, and less in summer, we can guess the frequency of the price movements to be about a year, or 12 months.
# Therefore we have a model y = Asin( kt + z ) with a known frequency.Rewriting y = Acos(z)sin(kt) + Asin(z)cos(kt),
# we can use bilinear regression, with no intercept, to solve for u = Acos(z), w = Asin(z)

sin_prices = prices - (time * slope + intercept)
sin_time = np.sin(time * 2 * np.pi / (365))
cos_time = np.cos(time * 2 * np.pi / (365))

def bilinear_regression(y, x1, x2):
    # Bilinear regression without an intercept amounts to projection onto the x-vectors
    slope1 = np.sum(y * x1) / np.sum(x1 ** 2)
    slope2 = np.sum(y * x2) / np.sum(x2 ** 2)
    return(slope1, slope2)

slope1, slope2 = bilinear_regression(sin_prices, sin_time, cos_time)

# We now recover the original amplitude and phase shift as A = slope1 ** 2 + slope2 ** 2, z = tan^{-1}(slope2/slope1)
amplitude = np.sqrt(slope1 ** 2 + slope2 ** 2)
shift = np.arctan2(slope2, slope1)

# Plot smoothed estimate of full dataset
plt.plot(time, amplitude * np.sin(time * 2 * np.pi / 365 + shift))
plt.plot(time, sin_prices)
plt.title('Smoothed Estimate of Monthly Input Prices')

# Define the interpolation/extrapolation function
def interpolate(date):
    days = (date - pd.Timestamp(start_date)).days
    if days in days_from_start:
        # Exact match found in the data
        return prices[days_from_start.index(days)]
    else:
        # Interpolate/extrapolate using the sin/cos model
        return amplitude * np.sin(days * 2 * np.pi / 365 + shift) + days * slope + intercept

# Create a range of continuous dates from start date to end date
continuous_dates = pd.date_range(start=pd.Timestamp(start_date), end=pd.Timestamp(end_date), freq='D')

# Plot the smoothed estimate of the full dataset using interpolation
plt.plot(continuous_dates, [interpolate(date) for date in continuous_dates], label='Smoothed Estimate')

# Fit the monthly input prices to the sine curve
x = np.array(days_from_start)
y = np.array(prices)
fit_amplitude = np.sqrt(slope1 ** 2 + slope2 ** 2)
fit_shift = np.arctan2(slope2, slope1)
fit_slope, fit_intercept = simple_regression(x, y - fit_amplitude * np.sin(x * 2 * np.pi / 365 + fit_shift))
plt.plot(dates, y, 'o', label='Monthly Input Prices')
plt.plot(continuous_dates, fit_amplitude * np.sin((continuous_dates - pd.Timestamp(start_date)).days * 2 * np.pi / 365 + fit_shift) + (continuous_dates - pd.Timestamp(start_date)).days * fit_slope + fit_intercept, label='Fit to Sine Curve')

plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Natural Gas Prices')
plt.legend()
plt.show()

"""## Task #2"""

def PrincingModel (injt_date, whtwl_date, initial_price, final_price, max_volume, str_cost):
  #Initial trade agreement
  trade = (final_price - initial_price) * 1000000
  millions = abs(trade/1000000)
  ##Deductions and other costs
  #Injection/withdrawal dates
  inout_times = injt_date + whtwl_date
  trade = trade - (inout_times * 10000 * millions)
  #transport fees
  trade = trade - (inout_times * 50000)
  #storage
  storage_cost = max_volume * str_cost
  trade = trade - storage_cost
  trade_rtn = (trade/1000000) * 100
  trade_profit = f"The estimate contract value of the proposal trade is {trade} with a return of {trade_rtn}%"
  return trade_profit

PrincingModel(4,3,3,5,100000,3)