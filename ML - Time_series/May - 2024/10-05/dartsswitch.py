import psycopg2
import pandas as pd
import numpy as np
import logging
import time
import os
import yaml
import random
from datetime import datetime, timedelta
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from concurrent.futures import ThreadPoolExecutor

# Load YAML configuration
with open("prediction_input.yaml", 'r') as f:
    input_data = yaml.load(f, Loader=yaml.SafeLoader)

# Define default_time as a constant
DEFAULT_TIME = "09:15"

def create_sequences(data, lookback_window):
    X, y = [], []
    for i in range(len(data) - lookback_window - 1):
        X.append(data[i:(i + lookback_window), :])
        y.append(data[i + lookback_window, :])
    return np.array(X), np.array(y)


# Create log folder if it doesn't exist
current_directory = os.getcwd()
logs_folder = "prediction_log_folder"
log_folder_path = os.path.join(current_directory, logs_folder)
if not os.path.exists(log_folder_path):
    os.makedirs(log_folder_path)

# Define the log file name
prediction_log = "prediction_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
log_file_path = os.path.join(current_directory, logs_folder, prediction_log)
logging.basicConfig(filename=log_file_path, level=logging.INFO)

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    dbname="pindb",
    user="tradingview",
    password="tradingview123",
    host="192.168.1.142",
    port="5432" 
)

# Create a cursor object
cursor = conn.cursor()

# Modify the instrument_identifiers list to include only the desired instrument identifier
instrument_identifiers = ['NIFTY09MAY2422800CE']

# Create table if it doesn't exist
try:
    cursor.execute(f"select exists(select * from {input_data['input_data']['put_table_data']} AS table_existence);")
    raise Exception(f"Table already exists: {input_data['input_data']['put_table_data']}")
except Exception:
    conn.commit()
    column_names = [f"{key} {values}" for key, values in input_data['input_data']['column_name'].items()]
    create_table_query = f"CREATE TABLE {input_data['input_data']['put_table_data']} ({','.join(column_names)});"
    cursor.execute(create_table_query)
    conn.commit()

# Define a function to process a group of instrument identifiers
def process_instrument_group(instrument_identifiers):
    try:
        for instrument_identifier in instrument_identifiers:
            # Calculate tomorrow's date and time
            tomorrow = datetime.now() + timedelta(days=input_data['input_data']['interval'])
            insert_time = tomorrow.strftime(f'%Y-%m-%d {DEFAULT_TIME}:00+00')
            insert_time_dt = datetime.strptime(insert_time, '%Y-%m-%d %H:%M:%S+00')
            number_of_predictions = input_data['input_data']["number_of_predictions"]
            timestamps = [insert_time_dt + timedelta(minutes=i) for i in range(number_of_predictions)]

            # Fetch data from the database
            sql_query = f"SELECT TO_TIMESTAMP(lasttradetime) AT TIME ZONE 'Asia/Kolkata' AS time, open, high, low, close, tradedqty FROM {input_data['input_data']['get_table_data']} WHERE instrumentidentifier = '{instrument_identifier}' and TO_TIMESTAMP(lasttradetime) AT TIME ZONE 'Asia/Kolkata' BETWEEN TIMESTAMP WITH TIME ZONE '{input_data['input_data']['from_date']} {input_data['input_data']['from_time']}:00+00' AND TIMESTAMP WITH TIME ZONE '{input_data['input_data']['to_date']} {input_data['input_data']['to_time']}:00+00'"
            cursor.execute(sql_query)
            rows = cursor.fetchall()

            # Convert data to DataFrame
            df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
            df.set_index(input_data['input_data']["put_set_index"], inplace=True)
            scaler = MinMaxScaler(feature_range=(0, input_data['input_data']["scalar_range"]))
            df_scaled = scaler.fit_transform(df)
            lookback_window = input_data['input_data']["lookback_window"]
            features = df.shape[1]

            # Create sequences
            X, y = create_sequences(df_scaled, lookback_window)
            X_train, y_train = X, y

            # Train the model
            model = Sequential()
            model.add(LSTM(units=input_data['input_data']["units"], return_sequences=True, input_shape=(lookback_window, features)))
            model.add(LSTM(units=input_data['input_data']["units"]))
            model.add(Dense(units=features))
            model.compile(loss=input_data['input_data']["model_compile_loss"], optimizer=input_data['input_data']["model_compile_optimizer"])
            model.fit(X_train, y_train, epochs=input_data['input_data']["epochs"], batch_size=input_data['input_data']["batch_size"])

            # Forecast values
            forecasted_values = []
            last_sequence = X_train[-1]
            for _ in range(number_of_predictions):
                next_data_point = model.predict(np.expand_dims(last_sequence, axis=0))
                next_data_point_original = scaler.inverse_transform(next_data_point)
                forecasted_values.append(next_data_point_original.flatten())
                last_sequence = np.append(last_sequence[1:], next_data_point, axis=0)
                

            forecast_df = pd.DataFrame(forecasted_values, columns=df.columns)

            # Insert forecasted data into the table
            for timestamp, row in zip(timestamps, forecast_df.itertuples(index=False)):
                insert_query = f"INSERT INTO {input_data['input_data']['put_table_data']} (lasttradetime, open, high, low, close, instrumentidentifier, tradedqty) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (timestamp, row.open, row.high, row.low, row.close, instrument_identifier, row.tradedqty))
                conn.commit()

            print("Inserted successfully for instrument identifier:", instrument_identifier)

    except Exception as e:
        print("Error occurred:", str(e))

# Split instrument identifiers into groups for parallel processing
num_threads = input_data['input_data']["thread_count"]
instrument_groups = [instrument_identifiers[i::num_threads] for i in range(num_threads)]

# Create a thread pool with the desired number of threads
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    # Submit processing tasks for each instrument group
    futures = [executor.submit(process_instrument_group, group) for group in instrument_groups]

    # Wait for all tasks to complete
    for future in futures:
        future.result()

# Close cursor and connection
cursor.close()
conn.close()
