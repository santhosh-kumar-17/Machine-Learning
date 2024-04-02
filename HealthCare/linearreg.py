# Importing necessary libraries
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Example data: house sizes and prices
house_sizes = np.array([750, 1000, 1200, 1500, 1800]).reshape(-1, 1)  # Independent variable (house sizes)
house_prices = np.array([300000, 400000, 450000, 550000, 6000000])  # Dependent variable (house prices)

# Creating and fitting the linear regression model
model = LinearRegression()
model.fit(house_sizes, house_prices)
jil=model.predict(house_sizes)
print(jil)

# Predicting prices for new house sizes
new_house_sizes = np.array([[900], [1100], [1300]])  # New house sizes for prediction
predicted_prices = model.predict(new_house_sizes)

# Plotting the data and the linear regression line
plt.scatter(house_sizes, house_prices, color='blue', label='Actual Prices')
plt.plot(house_sizes, model.predict(house_sizes), color='red', label='Predicted Prices')
plt.scatter(new_house_sizes, predicted_prices, color='green', label='Predicted for New Sizes')
plt.xlabel('House Size (sq ft)')
plt.ylabel('Price ($)')
plt.title('Linear Regression: House Prices Prediction')
plt.legend()
plt.show()
