
import requests
import cv2
import numpy as np
# import serial
import time
import json

ESP32_CAM_URL = "http://192.168.137.32//capture"
INFERENCE_API_URL = "https://detect.roboflow.com"
API_KEY = "Jtwl6gEJyH1vr1Qom11a"
MODEL_ID = "mask-detection-qwd3s/2"

# Configure the serial connection
SERIAL_PORT = "COM7"  # Change this to your actual COM port
BAUD_RATE = 115200

def get_image_from_esp32():
    response = requests.get(ESP32_CAM_URL, stream=True)
    if response.status_code == 200:
        image_data = np.frombuffer(response.content, np.uint8)
        img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
        return img, response.content
    else:
        print("Failed to fetch image from ESP32-CAM")
        return None, None
message="0"
def send_to_inference_api(image_bytes):
    files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
    response = requests.post(
        f"{INFERENCE_API_URL}/{MODEL_ID}",
        params={"api_key": API_KEY},
        files=files
    )
    return response.json()

def send_to_serial(ser, data):
    global message 
    # Convert the data to a simple format for serial communication
    if 'predictions' in data and data['predictions']:
        prediction = data['predictions'][0]
        mask_detected = prediction['confidence'] > 0.4
        message = "1\n"
    else:
        message = "0\n"
    
    print(f"Sending to serial: {message}")
    ser.write(message.encode())
import serial 
if __name__== "__main__":
    try:
        # Initialize serial connection
        # ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        # print(f"Serial connection established on {SERIAL_PORT}")
        time.sleep(10)  # Allow time for serial connection to initialize
        
        img, img_bytes = get_image_from_esp32()
        if img is not None:
            cv2.imwrite("mask.jpg", img)
            cv2.imshow("ESP32-CAM Image", img)
            cv2.waitKey(5000)  # Show image for 2 seconds
            cv2.destroyAllWindows()

            from inference_sdk import InferenceHTTPClient

            CLIENT = InferenceHTTPClient(
                api_url="https://detect.roboflow.com",
                api_key="Jtwl6gEJyH1vr1Qom11a"
            )

            result = CLIENT.infer('mask.jpg', model_id="mask-detection-qwd3s/2")
            print("Inference Result:", result)
            if len(result['predictions'])>0:
                message=1
                ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
                ser = None 
                print(1)
            else:
                message=0
                print(0)
            # Send result to serial monitor
            #send_to_serial(ser, message)
            
        else:
            pass 
            # print("No image received")
            # Send no detection message to serial
            # ser.write("0\n".encode())
            
    except Exception as e:
        print(f"Serial error: {e}")
    finally:
        # Close serial connection if it exists and is open
        # if 'ser' in locals() and ser.is_open:
            # ser.close()
            # print("Serial connection closed")
        pass 
import flask 
app=flask.Flask(__name__)
@app.route('/')
def index():
    global message 
    return message
app.run(host='0.0.0.0')
