from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import io
import base64
import os

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

def parse_class_name(raw):
    """Parse 'Plant___Disease' into readable plant + disease."""
    parts = raw.split("___")
    plant = parts[0].replace("_", " ").replace("(", "").replace(")", "").strip()
    disease = parts[1].replace("_", " ").strip() if len(parts) > 1 else "Unknown"
    return plant, disease

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

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

        # Top 3 predictions
        top3_indices = np.argsort(pred[0])[::-1][:3]
        top3 = []
        for i in top3_indices:
            p, d = parse_class_name(class_names[i])
            top3.append({
                "plant": p,
                "disease": d,
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

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🌿 Plant Disease Detector running at http://localhost:5000")
    app.run(debug=True, port=5000)
