import serial
SERIAL_PORT = "COM10"  # Change this to your actual COM port
BAUD_RATE = 115200


# def send_to_serial(ser, data):
#     print('in serial')
#     ser.write(data.encode())
ser=None
while True:
    message=int(input('enter message '))
    # send_to_serial(ser, message)
    if message==1:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        ser = None 
        print('1')
    else:
        print('0')
