import serial
import sqlite3
import ftplib
import schedule
import time
import logging

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

# Setup database connection
conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# Create the sensor data table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS sensor_data
             (timestamp TEXT, value REAL)''')
conn.commit()

def read_serial_data():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            data = ser.readline().decode('utf-8').strip()
            return data
    except serial.SerialException as e:
        logging.error(f"Error reading serial data: {e}")
        return None

def save_data_to_db(data):
    try:
        numeric_data = float(data)
        c.execute("INSERT INTO sensor_data (timestamp, value) VALUES (datetime('now'), ?)", (numeric_data,))
        conn.commit()
        logging.info(f"Data saved to database: {data}")
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}")

def upload_file(ftp, filepath, remote_filename):
    """Uploads a file to an FTP server."""
    with open(filepath, 'rb') as file:
        ftp.storbinary(f'STOR {remote_filename}', file)

def sync_database_over_ftp():
    try:
        ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
        ftp.set_pasv(True)
        upload_file(ftp, DATABASE_PATH, REMOTE_FILE_NAME)
        ftp.quit()
        logging.info("Database successfully uploaded to FTP server.")
    except ftplib.all_errors as e:
        logging.error(f"FTP error: {e}")

def scheduled_task():
    data = read_serial_data()
    if data:
        save_data_to_db(data)
    else:
        logging.warning("No data received from serial port.")
    sync_database_over_ftp()

schedule.every(5).minutes.do(scheduled_task)

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    logging.info("Program stopped manually.")
finally:
    conn.close()
