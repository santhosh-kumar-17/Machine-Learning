import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt  # Importing matplotlib.pyplot module

# Load the data from the CSV file
data = pd.read_csv('bigtable_nifty.csv')

# Convert 'lasttradetime' to datetime
data['lasttradetime'] = pd.to_datetime(data['lasttradetime'])

# Filter data for the time range 9:15 to 15:15
data = data[(data['lasttradetime'].dt.time >= datetime.strptime('09:15', '%H:%M').time()) &
            (data['lasttradetime'].dt.time <= datetime.strptime('15:15', '%H:%M').time())]

# Group by 'lasttradetime' and calculate the mean of 'close' for each timestamp
data = data.groupby('lasttradetime')['close'].mean().reset_index()

# Set 'lasttradetime' as the index
data.set_index('lasttradetime', inplace=True)

# Split data into training and test sets
train_size = int(len(data) * 0.8)  # Use 80% of the data for training
train, test = data.iloc[:train_size], data.iloc[train_size:]

# Fit ARIMA model on the training set
model = ARIMA(train, order=(5, 1, 0))  # Adjust the order based on your data characteristics
fit_model = model.fit()

# Forecast future values for the test set
forecast_steps = len(test)  # Forecast for the same number of steps as the test set
forecast = fit_model.forecast(steps=forecast_steps)

# Calculate RMSE
rmse = np.sqrt(mean_squared_error(test['close'], forecast))
print(f"Root Mean Squared Error (RMSE): {rmse}")

# Plot the forecast
fig, ax = plt.subplots()
train.plot(ax=ax, figsize=(12, 6), label='Training Data')
test.plot(ax=ax, label='Test Data')
forecast.plot(ax=ax, label='Forecast', color='red', linestyle='--')
plt.title('Stock Price Forecast (9:15 to 15:15)')
plt.xlabel('Date')
plt.ylabel('Closing Price')
plt.legend()
plt.show()
