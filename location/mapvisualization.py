import folium
import pandas as pd
import numpy as np

# Sample data for Chennai locations
chennai_location_data = pd.DataFrame({
    "name": ["Chennai Location 1", "Chennai Location 2", "Chennai Location 3"],
    "latitude": [13.0827, 13.0674, 13.0624],  # Updated latitude coordinates for Chennai
    "longitude": [80.2707, 80.2556, 80.2204],  # Updated longitude coordinates for Chennai
    "data_value": [8.5, 6.2, 9.8]  # Example data values for visualization
})

# Create a base map centered at a specific location
m = folium.Map(location=[np.mean(chennai_location_data["latitude"]), np.mean(chennai_location_data["longitude"])], zoom_start=12)

# Add CircleMarker for each Chennai location with darkening based on data
for index, location in chennai_location_data.iterrows():
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
m.save('map_with_chennai_data_visualization.html')
