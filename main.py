from flask import Flask, g, render_template
import serial
import sqlite3
import ftplib
import schedule
import time
import logging

app = Flask(__name__)

# Serial communication parameters
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# Database parameters
DATABASE_PATH = 'sensor_data.db'

# FTP server credentials
FTP_HOST = 'ftp.yourserver.com'
FTP_USER = 'your_username'
FTP_PASS = 'your_password'
REMOTE_FILE_NAME = 'backup_sensor_data.db'

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_PATH)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize the serial object to None
ser = None

def setup_serial_connection():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        logging.info(f"Opened serial port {SERIAL_PORT} successfully.")
    except serial.SerialException as e:
        logging.error(f"Failed to open serial port {SERIAL_PORT}: {e}")

def read_serial_data():
    global ser
    if ser is None or not ser.is_open:
        setup_serial_connection()

    try:
        if ser is not None:
            data = ser.readline().decode('utf-8').strip()
            return data
    except serial.SerialException as e:
        logging.error(f"Error reading serial data: {e}")
    return None

def save_data_to_db(data):
    db = get_db()
    try:
        numeric_data = float(data)
        cursor = db.cursor()
        cursor.execute("INSERT INTO sensor_data (timestamp, value) VALUES (datetime('now'), ?)", (numeric_data,))
        db.commit()
        logging.info(f"Data saved to database: {data}")
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}")

# Other functions remain unchanged

@app.route('/')
def home():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10")
    sensor_data = cursor.fetchall()
    return render_template('index.html', sensor_data=sensor_data)

if __name__ == '__main__':
    try:
        app.run(debug=True)  # Enable debug mode
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Program stopped manually.")
    finally:
        if ser is not None and ser.is_open:
            ser.close()
