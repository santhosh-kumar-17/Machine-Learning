import folium
import pandas as pd
import numpy as np

# Sample data - Replace this with your actual data
np.random.seed(42)
location_data = pd.DataFrame({
    "name": [f"Location {i}" for i in range(1, 6)],
    "latitude": np.random.uniform(34, 35, 5),
    "longitude": np.random.uniform(-119, -118, 5),
    "data_value": np.random.rand(5) * 10  # Sample data values
})

# Create a base map centered at a specific location
m = folium.Map(location=[np.mean(location_data["latitude"]), np.mean(location_data["longitude"])], zoom_start=12)

# Add CircleMarker for each location with darkening based on data
for index, location in location_data.iterrows():
    folium.CircleMarker(
        location=[location["latitude"], location["longitude"]],
        radius=10,
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=location["data_value"] / 10,  # Adjust opacity based on data
        popup=f"{location['name']} - Data Value: {location['data_value']:.2f}"
    ).add_to(m)

# Save the map as an HTML file
m.save('map_with_data_visualization.html')
