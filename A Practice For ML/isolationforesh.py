from sklearn.ensemble import IsolationForest
import numpy as np

# Example data
data = np.array([[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]])

# Create an isolation forest model
model = IsolationForest(contamination=0.1)  # Adjust contamination based on your dataset

# Fit the model
model.fit(data)

# Predict outliers
outliers = model.predict(data)

# Anomalies will have a prediction of -1
anomalies = data[np.where(outliers == -1)[0]]  # Corrected line
print("Anomalies:", anomalies)
