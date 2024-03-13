import serial
import sqlite3
import logging
import ftplib
from datetime import datetime

# Serial communication parameters
SERIAL_PORT = '/dev/cu.usbserial-10'
BAUD_RATE = 9600

# FTP server credentials
FTP_HOST = 'ftp.matsvinn.se'
FTP_USER = 'urine@matsvinn.se'
FTP_PASS = 'fiskarnaihavet'
REMOTE_FILE_NAME = 'backup_sensor_data.db'

# Database parameters
DATABASE_PATH = 'sensor_data.db'

# Setup logging
logging.basicConfig(filename='serial_reader.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                      (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, value REAL)''')
    conn.commit()
    conn.close()

# Function to save data to the database
def save_data_to_db(data):
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sensor_data (value) VALUES (?)", (data,))
    conn.commit()
    conn.close()

# Function to read data from the serial port
def read_serial_data():
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
        ser.flushInput()
        data = ser.read_until(b'\r').decode('utf-8').strip()
        if 'S' in data:
            # Find the start of the numeric value
            start_index = data.find('W') + 1
            # Find the end of the numeric value (just before 'kg')
            end_index = data.find('kg')
            
            # Extract the value
            value = data[start_index:end_index].strip()
            return value

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

# Main function to run the scheduled task
def run():
    try:
        data = read_serial_data()
        if data:
            save_data_to_db(data)
            sync_database_over_ftp()
            logging.info(f"Data saved to database: {data}")
        else:
            logging.warning("No data received from serial port.")
    except Exception as e:
        logging.error(f"Error in run: {e}")

if __name__ == '__main__':
    init_db()
    run()