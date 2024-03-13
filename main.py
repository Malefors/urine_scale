from flask import Flask, render_template
import sqlite3
import csv
import io
from datetime import datetime


app = Flask(__name__)

# Database parameters
DATABASE_PATH = 'sensor_data.db'

@app.route('/')
def show_data():
    # Connect to the SQLite database
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    
    # Query to select data from the table
    c.execute("SELECT timestamp, value FROM sensor_data ORDER BY timestamp DESC")
    data = c.fetchall()
    
    # Format the timestamp for each row to a more readable format
    formatted_data = [(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y %H:%M:%S'), row[1]) for row in data]
    
    # Close the database connection
    conn.close()
    
    # Use the template with CSS to display the data
    return render_template("index.html", data=formatted_data)

@app.route('/download/csv')
def download_csv():
    # Connect to the SQLite database
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()

    # Query to select data
    c.execute("SELECT timestamp, value FROM sensor_data ORDER BY timestamp DESC")
    data = c.fetchall()
    
    # Close the database connection
    conn.close()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

    # Write header
    writer.writerow(['Timestamp', 'Value'])

    # Write data
    for row in data:
        writer.writerow(row)

    # Seek to start
    output.seek(0)
    
    # Create a response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=sensor_data.csv"
    response.headers["Content-type"] = "text/csv"
    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)