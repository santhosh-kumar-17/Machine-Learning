import numpy as np
import matplotlib.pyplot as plt
import sklearn
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Generate nonlinear data
np.random.seed(0)
X, y = make_regression(n_samples=100, n_features=1, noise=10, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

# Transform features to polynomial features to capture nonlinear relationships
poly = PolynomialFeatures(degree=2)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

# Fit a linear regression model on the transformed features
lin_reg = LinearRegression()
lin_reg.fit(X_train_poly, y_train)

# Predictions
y_pred_train = lin_reg.predict(X_train_poly)
y_pred_test = lin_reg.predict(X_test_poly)

# Calculate MSE
mse_train = mean_squared_error(y_train, y_pred_train)
mse_test = mean_squared_error(y_test, y_pred_test)

print(f"Train MSE: {mse_train}")
print(f"Test MSE: {mse_test}")

# Plot the results
plt.scatter(X, y, color='blue', label='Actual data')
plt.plot(X_train, y_pred_train, color='red', label='Predicted line')
plt.title('Nonlinear Regression Example')
plt.xlabel('X')
plt.ylabel('y')
plt.legend()
plt.show()

