from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import io
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

app = Flask(__name__, static_folder=".")
CORS(app)

# Load trained model once at startup
model = load_model("plant_disease_model_finetuned.h5")

class_names = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy",
    "Grape___Black_rot", "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
    "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]

sensor_state = {
    "soil_moisture": 42,
    "temperature": 29.0,
    "humidity": 61.0,
    "soil_status": "Moist",
    "climate_status": "Fair",
    "irrigation_level": "Monitor",
    "irrigation_advice": "Soil moisture is acceptable. Keep monitoring before the next watering cycle."
}


def parse_class_name(raw):
    parts = raw.split("___")
    plant = parts[0].replace("_", " ").replace("(", "").replace(")", "").strip()
    disease = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown"
    return plant, disease


def classify_soil_moisture(value):
    if value < 30:
        return "Dry"
    if value < 70:
        return "Moist"
    return "Wet"


def classify_climate(temperature, humidity):
    if temperature > 35 or humidity > 85:
        return "Stress risk"
    if temperature < 15 or humidity < 25:
        return "Low-growth"
    return "Fair"


def build_irrigation_advice(soil_moisture, temperature, humidity):
    if soil_moisture < 25:
        return (
            "Irrigate now",
            "Soil is very dry. Start irrigation now and recheck moisture after 10 to 15 minutes."
        )
    if soil_moisture < 40:
        if temperature >= 32 or humidity <= 35:
            return (
                "Irrigate soon",
                "Soil is getting dry and the air is harsh. Schedule irrigation soon to avoid plant stress."
            )
        return (
            "Monitor closely",
            "Soil is slightly dry. Plan a light watering cycle if moisture keeps falling."
        )
    if soil_moisture <= 70:
        return (
            "Hold irrigation",
            "Soil moisture is in a healthy range. No irrigation is needed right now."
        )
    return (
        "Stop irrigation",
        "Soil is already wet. Avoid watering until the moisture level drops."
    )


def build_sensor_payload():
    soil_moisture = int(sensor_state["soil_moisture"])
    temperature = round(float(sensor_state["temperature"]), 1)
    humidity = round(float(sensor_state["humidity"]), 1)
    soil_status = classify_soil_moisture(soil_moisture)
    climate_status = classify_climate(temperature, humidity)
    irrigation_level, irrigation_advice = build_irrigation_advice(
        soil_moisture,
        temperature,
        humidity
    )

    sensor_state.update({
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity,
        "soil_status": soil_status,
        "climate_status": climate_status,
        "irrigation_level": irrigation_level,
        "irrigation_advice": irrigation_advice
    })
    return sensor_state


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/sensor-data", methods=["GET"])
def get_sensor_data():
    return jsonify(build_sensor_payload())


@app.route("/sensor-data", methods=["POST"])
def update_sensor_data():
    data = request.get_json(silent=True) or {}

    missing_fields = [
        field for field in ("soil_moisture", "temperature", "humidity")
        if field not in data
    ]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        soil_moisture = int(float(data["soil_moisture"]))
        temperature = float(data["temperature"])
        humidity = float(data["humidity"])
    except (TypeError, ValueError):
        return jsonify({"error": "Sensor values must be numeric"}), 400

    if not 0 <= soil_moisture <= 100:
        return jsonify({"error": "soil_moisture must be between 0 and 100"}), 400
    if not -20 <= temperature <= 80:
        return jsonify({"error": "temperature looks out of range"}), 400
    if not 0 <= humidity <= 100:
        return jsonify({"error": "humidity must be between 0 and 100"}), 400

    sensor_state.update({
        "soil_moisture": soil_moisture,
        "temperature": temperature,
        "humidity": humidity
    })
    return jsonify(build_sensor_payload())


@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        img_bytes = file.read()
        img = image.load_img(io.BytesIO(img_bytes), target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        pred = model.predict(img_array)
        pred_index = int(np.argmax(pred))
        confidence = float(pred[0][pred_index] * 100)

        raw_name = class_names[pred_index]
        plant, disease = parse_class_name(raw_name)
        is_healthy = "healthy" in raw_name.lower()

        top3_indices = np.argsort(pred[0])[::-1][:3]
        top3 = []
        for i in top3_indices:
            top_plant, top_disease = parse_class_name(class_names[i])
            top3.append({
                "plant": top_plant,
                "disease": top_disease,
                "confidence": round(float(pred[0][i] * 100), 2),
                "healthy": "healthy" in class_names[i].lower()
            })

        return jsonify({
            "plant": plant,
            "disease": disease,
            "confidence": round(confidence, 2),
            "is_healthy": is_healthy,
            "raw": raw_name,
            "top3": top3
        })

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    print("Plant Disease Detector running at http://localhost:5000")
    app.run(debug=True, port=5000)
