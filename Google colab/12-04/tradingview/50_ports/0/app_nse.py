from flask import Flask, render_template, jsonify, request,g
import pandas as pd
import psycopg2
import re

app = Flask(__name__)

# Replace these parameters with your PostgreSQL database credentials
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'mydb'
DB_USER = 'test'
DB_PASSWORD = 'test123'

def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Exception as e:
        print(f"Error: Unable to connect to the database. {e}")
        return None
    
def get_connection():
    if 'db_connection' not in g:
        g.db_connection = connect_to_db()
    return g.db_connection

@app.route('/')
def index():
    # Connect to the database
    connection = get_connection()

    if connection:
        try:
            # Query instrument identifiers from the database
            query = "SELECT DISTINCT instrumentidentifier FROM options union SELECT DISTINCT instrumentidentifier FROM futures order by instrumentidentifier ASC "
            with connection, connection.cursor() as cursor:
                cursor.execute(query)
                instrument_identifiers = [row[0] for row in cursor.fetchall()]

            # Render the template with instrument identifiers
            return render_template('index.html', instrument_identifiers=instrument_identifiers)
        except Exception as e:
            print(f"Error: Unable to execute the query. {e}")
            return jsonify({"error": f"Unable to execute the query. {e}"})
        finally:
            # Connection is closed automatically due to the use of the 'with' statement
            pass
    else:
        return jsonify({"error": "Unable to connect to the database."})

@app.route('/get_data')
def get_data():
    # Connect to the database
    connection = connect_to_db()

    if connection:
        try:
            # Get the selected symbol from the request parameters
            selected_symbol = request.args.get('symbol')

            # Extract the common prefix (e.g., "NIFTY")
            common_prefix = re.split(r'\d+', selected_symbol)[0]
            # print(common_prefix)

            if 'CE' in selected_symbol:
                querype = f"select lasttradetime as date, high, low , open, close from options where instrumentidentifier LIKE '{common_prefix}%PE'"
            else:
                querype = f"select lasttradetime as date, high, low, open, close from options where instrumentidentifier LIKE '{common_prefix}%CE'"

            query = f"select lasttradetime as date, open, high, low, close, tradedqty from options where instrumentidentifier='{selected_symbol}' union select lasttradetime as date, open, high, low, close, tradedqty from futures where instrumentidentifier='{selected_symbol}'"
           # querype = f"select distinct lasttradetime as date,instrumentidentifier, high, low from options where instrumentidentifier LIKE '{common_prefix}%PE' order by lasttradetime asc"
            #redline_query = f" select lasttradetime as date,level1,level2,level3,level4,level5,level6,level7,level8,level9,level10,null as level11,null as level12,null as level13,null as level14,null as level15,null as level16,null as level17,null as level18,null as level19,null as level20,null as level21,null as level22  from options_i1 where instrumentidentifier='{selected_symbol}'  union select lasttradetime as date,level1,level2,level3,level4,level5,level6,level7,level8,level9,level10,level11,level12,level13,level14,level15,level16,level17,level18,level19,level20,level21,level22 from futures_i1 where instrumentidentifier='{selected_symbol}'"
            redline_query = f"SELECT lasttradetime AS date, level1, level2, level3, level4, level5, level6, level7, level8, level9, level10, NULL AS level11, NULL AS level12, NULL AS level13, NULL AS level14, NULL AS level15, NULL AS level16, NULL AS level17, NULL AS level18, NULL AS level19, NULL AS level20, NULL AS level21, NULL AS level22, NULL AS level23, NULL AS level24, NULL AS level25, NULL AS level26, NULL AS level27, NULL AS level28, NULL AS level29, NULL AS level30, NULL AS level31, NULL AS level32, NULL AS level33, NULL AS level34, NULL AS level35, NULL AS level36, NULL AS level37, NULL AS level38, NULL AS level39, NULL AS level40, NULL AS level41, NULL AS level42, NULL AS level43, NULL AS level44, NULL AS level45, NULL AS level46, NULL AS level47, NULL AS level48, NULL AS level49, NULL AS level50, NULL AS level51, NULL AS level52, NULL AS level53, NULL AS level54, NULL AS level55, NULL AS level56, NULL AS level57, NULL AS level58, NULL AS level59, NULL AS level60 FROM options_i1 WHERE instrumentidentifier = '{selected_symbol}' UNION SELECT lasttradetime AS date, level1, level2, level3, level4, level5, level6, level7, level8, level9, level10, level11, level12, level13, level14, level15, level16, level17, level18, level19, level20, level21, level22, level23, level24, level25, level26, level27, level28, level29, level30, level31, level32, level33, level34, level35, level36, level37, level38, level39, level40, level41, level42, level43, level44, level45, level46, level47, level48, level49, level50, level51, level52, level53, level54, level55, level56, level57, level58, level59, level60 FROM futures_i1 WHERE instrumentidentifier = '{selected_symbol}'"

            with connection, connection.cursor() as cursor:
                cursor.execute(query)
                data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

                cursor.execute(redline_query)
                redline_data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

                cursor.execute(querype)
                querype_data = pd.DataFrame(cursor.fetchall(), columns=[desc[0] for desc in cursor.description])

            # Merge dataframes based on the 'date' column
            data = pd.merge(data, redline_data, on='date', how='left')

            # Merge querype_data based on the 'date' column
            data = pd.merge(data, querype_data, on='date', how='left')

            # Replace NaN values with None in the DataFrame
            data = data.where(pd.notna(data), None)
            # print(data)

            # Convert the combined DataFrame to JSON
            data_json = data.to_dict(orient='records')

            # Return the combined data as JSON
            return jsonify(data_json)

        except Exception as e:
            print(f"Error: Unable to execute the query. {e}")
        finally:
            # Connection is closed automatically due to the use of the 'with' statement
            pass
    else:
        return jsonify({"error": "Unable to connect to the database."})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9000)
