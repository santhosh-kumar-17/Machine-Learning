import pandas as pd
import statsmodels.api as sm
import plotly.graph_objects as go

# Load Time Series Data
file_path = "bigtable_nifty.csv"
data = pd.read_csv(file_path, parse_dates=['lasttradetime'], index_col='lasttradetime')

# Explore and Preprocess Data (Optional)
data = data.dropna()

# Fit ARIMA Model
p, d, q = 1, 1, 1  # Example values, adjust based on your data
arima_model = sm.tsa.ARIMA(data['close'], order=(p, d, q))
arima_result = arima_model.fit()

# Make Predictions
forecast_steps = 10  # Example number of forecast steps
forecast = arima_result.get_forecast(steps=forecast_steps)
forecast_index = pd.date_range(start=data.index[-1], periods=forecast_steps+1, freq='B')[1:]

# Create a Plotly Figure for Visualization
fig = go.Figure()

# Add Trace for Observed Data
fig.add_trace(go.Scatter(x=data.index, y=data['close'], mode='lines', name='Observed'))

# Add Trace for Forecasted Data
fig.add_trace(go.Scatter(x=forecast_index, y=forecast.predicted_mean, mode='lines', name='Forecast', line=dict(color='red')))

# Add Confidence Intervals
lower_bound = forecast.conf_int()['lower close']
upper_bound = forecast.conf_int()['upper close']
fig.add_trace(go.Scatter(x=forecast_index, y=lower_bound, fill=None, mode='lines', line=dict(color='red'), showlegend=False))
fig.add_trace(go.Scatter(x=forecast_index, y=upper_bound, fill='tonexty', mode='lines', line=dict(color='red'), name='Confidence Interval'))

# Update Layout
fig.update_layout(
    title='ARIMA Model Forecast',
    xaxis=dict(title='Time'),
    yaxis=dict(title='Closing Prices'),
    showlegend=True
)

# Show Plot
fig.show()
