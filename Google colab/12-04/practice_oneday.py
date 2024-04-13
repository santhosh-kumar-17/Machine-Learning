import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import logging
import time

start_time =time.time()
# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname="mydb",
    user="test",
    password="test123",
    host="192.168.1.141",
    port="5432"
)

# Create a cursor object using the cursor() method
cursor = conn.cursor()



instrument_query=f"select distinct instrumentidentifier from whole_indices_futures where instrumentidentifier like '%NIFTY18APR242%' limit 1"
cursor.execute(instrument_query)
instrument_identifiers = [row[0] for row in cursor.fetchall()]
print("instrument_identifiers",instrument_identifiers)
print("Number of instrument identifiers:", len(instrument_identifiers))

cursor.close()

success =True
failed_identifiers =[]
for instrument_identifier in instrument_identifiers:
    try:
        cursor =conn.cursor()

        # Calculate tomorrow's date and time
        tomorrow = datetime.now()
        insert_time = tomorrow.strftime('%Y-%m-%d 09:15:00+00')
        insert_time_dt = datetime.strptime(insert_time, '%Y-%m-%d %H:%M:%S+00')
        num_minutes = 365  # For example, 5 minutes of data
        timestamps = [insert_time_dt + timedelta(minutes=i) for i in range(num_minutes)]

        sql_query = f"SELECT TO_TIMESTAMP(lasttradetime) AT TIME ZONE 'Asia/Kolkata' AS time, open, high, low, close FROM whole_indices_futures WHERE instrumentidentifier = '{instrument_identifier}' and TO_TIMESTAMP(lasttradetime) AT TIME ZONE 'Asia/Kolkata' <= '2024-04-09 15:30:00' ORDER BY time;" 
        cursor.execute(sql_query)
        rows=cursor.fetchall()
    #========================================================================
        df=pd.DataFrame(rows,columns=[desc[0] for desc in cursor.description])
        df.set_index('time', inplace=True)
        df.fillna(method="ffill", inplace=True)	
        scaler = MinMaxScaler(feature_range=(0, 1))
        df_scaled = scaler.fit_transform(df)
        lookback_window = 3
        features = 4

        def create_sequences(data, lookback_window):
            X, y = [], []
            for i in range(len(data) - lookback_window - 1): 
                X.append(data[i:(i + lookback_window), :])
                y.append(data[i + lookback_window, 0:4]) 
            return np.array(X), np.array(y)

        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=(lookback_window, features)))
        model.add(LSTM(units=50))
        model.add(Dense(units=4)) 
        model.compile(loss='mean_squared_error', optimizer='adam')

        X, y = create_sequences(df_scaled, lookback_window)
        train_size = int(len(X) * 0.8)
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]
        model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_test, y_test))
        y_pred = model.predict(X_test)
        y_pred_original = scaler.inverse_transform(y_pred)
        data = pd.DataFrame(y_pred_original, columns=['open', 'high', 'low' ,'close'])

        def generate_predictions(model, last_sequence, num_predictions):
            predictions = []
            current_sequence = last_sequence.reshape(1, lookback_window, features)  # Reshape to match model input shape
            for _ in range(num_predictions):
                next_prediction = model.predict(current_sequence)  
                predictions.append(next_prediction[0]) 
                current_sequence = np.append(current_sequence[:, 1:, :], next_prediction.reshape(1, 1, features), axis=1)  # Update the current sequence
            return predictions

        last_sequence = X_test[-1]  # Using the last sequence from the test data
        num_predictions = 365
        predicted_data = generate_predictions(model, last_sequence, num_predictions)
        predicted_data_original = scaler.inverse_transform(predicted_data)
        predicted_df = pd.DataFrame(predicted_data_original, columns=['open', 'high', 'low', 'close'])
        print(predicted_df)
        df=predicted_df

    #========================================================
        # Insert data into the table
        for timestamp, row in zip(timestamps, predicted_df.itertuples(index=False)):
            insert_query =f"INSERT INTO onetwothree (lasttradetime,open, high, low, close,instrumentidentifier) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(insert_query, (timestamp,row.open, row.high, row.low, row.close , instrument_identifier))
        print("inserted successfully")

        conn.commit()
        cursor.close()

    except Exception as e:
        success = False
        failed_identifiers.append(instrument_identifier)
        print(f"Error occurred for instrument identifier: {instrument_identifier}, Error: {str(e)}")
        continue

conn.close()

if success:
    print("All instrument identifiers processed successfully.")
else:
    print("Some instrument identifiers failed to process.")
    print("Failed instrument identifiers:", failed_identifiers)
    # Log failed instrument identifiers to a file
    log_error_instrument = datetime.now().strftime("%Y-%m-%d") + "_failed_instrument_identifiers.log"
    logging.basicConfig(filename=log_error_instrument, level=logging.INFO)
    logging.info("Failed instrument identifiers: " + str(failed_identifiers))

end_time = time.time()
execution_time =start_time -end_time
print("execution_time",execution_time)
