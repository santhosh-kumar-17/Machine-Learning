import numpy as np

def calculate_zscore(data):
    mean = np.mean(data)
    std_dev = np.std(data)
    z_scores = (data - mean) / std_dev
    return z_scores

# Example data
data = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

z_scores = calculate_zscore(data)
print("Z-scores:", z_scores)
