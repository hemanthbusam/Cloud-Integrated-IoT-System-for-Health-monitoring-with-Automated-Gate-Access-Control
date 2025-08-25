#include <ESP8266WiFi.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <WiFiClient.h>

// Replace with your network credentials
const char* ssid = "Datapro - Digital"; //"E";// 
const char* password = "Datapro@123$"; // "1234567890";//
const char* ipadr="192.168.2.89";

// DHT Sensor setup
#define DHTPIN D4      // Pin connected to DHT sensor
#define DHTTYPE DHT11  // or DHT22

DHT dht(DHTPIN, DHTTYPE);

// Flask API endpoint
const char* server = "192.168.2.89"; //:5000/upload_data";  // Flask server IP

WiFiClient client;

void setup() {
  Serial.begin(115200);
  dht.begin();

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println("IP address: " + WiFi.localIP().toString());
}

void loop() {
  // Read temperature and humidity
  float temperature = 98; //dht.readTemperature();  // in Celsius
  float alcohol = 0; //readAlcoholSensor();        // Assume this is a custom function for your alcohol sensor
  Serial.println(dht.readTemperature());
  // Check if readings are valid
  // if (isnan(temperature) || isnan(alcohol)) {
  //   Serial.println("Failed to read from DHT sensor!");
  //   delay(5000);
  //   return;
  // }

  // Prepare JSON data
  String empid = "E123";  // Example employee ID, can be dynamic
  String jsonData = createJson(empid, temperature, alcohol);
  
  // Send data to Flask API
  sendDataToServer(jsonData);
  
  // Wait 5 seconds before sending next data
  delay(5000);
}

// Function to create JSON payload
String createJson(String empid, float temperature, float alcohol) {
  StaticJsonDocument<200> doc;
  doc["employee_id"] = empid;
  doc["temperature"] = temperature;
  doc["alcohol_detected"] = alcohol;
  doc["mask_detected"] = 0;

  String output;
  serializeJson(doc, output);
  //Serial.println(output);
  return output;
}

// Function to send data to Flask API
void sendDataToServer(String jsonData) {
  // if (client.connect(server, 5000)) {
  //   client.println("POST /upload_data HTTP/1.1");
  //   client.println("Host: 192.168.2.89");
  //   client.println("Content-Type: application/json");
  //   client.print("Content-Length: ");
  //   client.println(jsonData.length());
  //   client.println();
  //   client.println(jsonData);  // Send JSON payload
  //   Serial.println(jsonData);
  // } else {
  //   Serial.println("Connection failed!");
  // }

  if (client.connect("192.168.2.89", 5000)) {
    Serial.println("Connected to server!");
    client.println("GET /upload_data HTTP/1.1");
    client.println("Host: 192.168.2.89");
    client.println("Content-Type: application/json");
    client.print("Content-Length: ");
    client.println(jsonData.length());
    client.println();
    client.println(jsonData);  // Send JSON payload
    Serial.println(jsonData);
    while (client.available()) {
      String line = client.readStringUntil('\n');
      Serial.println(line);
    }
    client.println("Connection: close");
    client.println();
    // Read the response from the server
  } else {
    Serial.println("Connection failed!");
  }

}
