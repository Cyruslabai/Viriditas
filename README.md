# Plant Disease Identifier with Sensor-Based Irrigation Monitoring

This project is a smart agriculture web application that combines plant disease detection with real-time environmental monitoring. It allows a user to upload a leaf image for disease prediction while also receiving live soil moisture, temperature, and humidity readings from connected sensors. Based on the sensor values, the system generates simple irrigation recommendations to support better plant care.

## Overview

The application has two core parts:

1. A deep learning image classification pipeline that predicts plant disease from a leaf image.
2. An IoT monitoring workflow that receives sensor readings from an ESP32-CAM with a soil moisture sensor and a DHT11 sensor.

The web interface brings both parts together in a single dashboard so the user can:

- upload a leaf image
- view disease prediction results and confidence
- monitor soil moisture, temperature, and humidity
- receive automatic irrigation advice

## Key Features

- Leaf image-based plant disease detection
- Top prediction with confidence score and top 3 probable classes
- Soil moisture monitoring
- Temperature and humidity monitoring using DHT11
- Automatic irrigation recommendation based on sensor values
- Web dashboard with automatic sensor data refresh
- Sensor integration over Wi-Fi using ESP32-CAM

## Tech Stack

### Backend

- Python
- Flask
- Flask-CORS
- TensorFlow / Keras
- NumPy
- Pillow

### Frontend

- HTML
- CSS
- JavaScript

### Hardware

- ESP32-CAM
- Soil moisture sensor
- DHT11 temperature and humidity sensor

## How the System Works

### Disease Detection Flow

1. The user uploads a leaf image through the web interface.
2. The Flask backend preprocesses the image to `224 x 224`.
3. The trained TensorFlow model predicts the disease class.
4. The application returns the plant name, predicted disease, confidence score, and top 3 predictions.

### Sensor Monitoring Flow

1. The soil moisture sensor and DHT11 are connected to the ESP32-CAM.
2. The ESP32-CAM reads soil moisture, temperature, and humidity values.
3. The board sends the readings to the Flask backend using a `POST /sensor-data` request over Wi-Fi.
4. The web application fetches the latest sensor data automatically and updates the dashboard.
5. The backend evaluates the readings and returns irrigation advice such as:
   - `Irrigate now`
   - `Irrigate soon`
   - `Hold irrigation`
   - `Stop irrigation`

## Model Information

- Model type: CNN-based plant disease classifier
- Input size: `224 x 224`
- Total classes: `38`
- Plants covered: `14`

The disease classes currently configured in the application include crops such as apple, blueberry, cherry, corn, grape, orange, peach, bell pepper, potato, raspberry, soybean, squash, strawberry, and tomato.

## Project Structure

```text
Plant-disease-identifier/
|-- app.py                        Flask backend and prediction API
|-- index.html                    Frontend dashboard
|-- arduino_sensor_sender.ino     ESP32-CAM sensor sender sketch
|-- test.py                       Local image testing script
|-- requirements.txt              Python dependencies
|-- images/                       Training graph images
|-- README.md                     Project documentation
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Pushpak-Cyrus/Plant-disease-identifier.git
cd Plant-disease-identifier
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the trained model file

Place the trained model file below in the project root:

```text
plant_disease_model_finetuned.h5
```

The application will not start correctly unless this file is present.

### 4. Run the Flask application

```bash
python app.py
```

The app runs on port `5000` and is configured to listen on the local network so that the ESP32-CAM can send sensor readings to it.

### 5. Open the web app

Open the following address in your browser:

```text
http://localhost:5000
```

## Sensor Setup

### ESP32-CAM sketch

The project includes the file:

```text
arduino_sensor_sender.ino
```

Before uploading it to the board, update:

- `YOUR_WIFI_NAME`
- `YOUR_WIFI_PASSWORD`
- `YOUR_COMPUTER_IP`

Example:

```cpp
const char* serverUrl = "http://192.168.1.5:5000/sensor-data";
```

### Sensor pins used in the sketch

- `DHTPIN = 13`
- `SOIL_PIN = 33`

### Sensor update behavior

- The ESP32-CAM sends readings every 10 seconds.
- The web dashboard refreshes sensor data automatically every 5 seconds.

## API Endpoints

### `POST /predict`

Accepts a leaf image file and returns:

- plant name
- disease name
- confidence score
- healthy/diseased status
- top 3 predictions

### `GET /sensor-data`

Returns the current sensor state, including:

- soil moisture
- temperature
- humidity
- soil status
- climate status
- irrigation level
- irrigation advice

### `POST /sensor-data`

Accepts JSON sensor readings in the format:

```json
{
  "soil_moisture": 55,
  "temperature": 28.4,
  "humidity": 62.1
}
```

## Training Graphs

Training graphs used in the project are stored in the `images/` folder.

<p align="center">
  <img src="images/acc_impv.png" width="45%" alt="Model accuracy graph" />
  <img src="images/losss_impv.png" width="45%" alt="Model loss graph" />
</p>

## Educational Value

This project demonstrates how artificial intelligence and IoT can work together in agriculture. It covers:

- image preprocessing for deep learning
- model inference with TensorFlow
- Flask API development
- frontend and backend integration
- sensor-based data collection
- simple rule-based irrigation support

## Disclaimer

This project was built for learning and demonstration purposes. The predictions and irrigation advice should not be treated as a replacement for professional agricultural guidance.

## License

Copyright (c) 2025 Pushpak-Cyrus.
All rights reserved.
