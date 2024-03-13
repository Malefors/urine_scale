import serial,time, re
if __name__ == '__main__':
    
    print('Running. Press CTRL-C to exit.')
    with serial.Serial("/dev/cu.usbserial-10", 9600, timeout=1) as ser:
        time.sleep(0.1) #wait for serial to open
        if ser.isOpen():
            print("{} connected!".format(ser.port))
            try:
                while True:
                    #print("running?")
                    ser.flushInput()

                    data = ser.read_until(b'\r').decode('utf-8').strip()
                    print(data)
                    
                    #lines = data.split(b'\r')  # Split using the expected terminator
                    #for line in lines:
                    #    print(line.decode('utf-8'))
                    #data = device.read(10)  # Attempt to read 10 bytes
                    #print(data)
                    #data = ser.readlines().decode()
                    #print(data)
                    #line = device.readline()
                    #print(line)
            except KeyboardInterrupt:
                print("KeyboardInterrupt has been caught.")