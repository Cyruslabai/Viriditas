import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import tkinter as tk
from tkinter import filedialog

# Load trained model
model = load_model("plant_disease_model_finetuned.h5")

# Class names
class_names = [
"Apple___Apple_scab","Apple___Black_rot","Apple___Cedar_apple_rust","Apple___healthy",
"Blueberry___healthy",
"Cherry_(including_sour)___Powdery_mildew","Cherry_(including_sour)___healthy",
"Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot","Corn_(maize)___Common_rust",
"Corn_(maize)___Northern_Leaf_Blight","Corn_(maize)___healthy",
"Grape___Black_rot","Grape___Esca_(Black_Measles)","Grape___Leaf_blight_(Isariopsis_Leaf_Spot)","Grape___healthy",
"Orange___Haunglongbing_(Citrus_greening)",
"Peach___Bacterial_spot","Peach___healthy",
"Pepper,_bell___Bacterial_spot","Pepper,_bell___healthy",
"Potato___Early_blight","Potato___Late_blight","Potato___healthy",
"Raspberry___healthy",
"Soybean___healthy",
"Squash___Powdery_mildew",
"Strawberry___Leaf_scorch","Strawberry___healthy",
"Tomato___Bacterial_spot","Tomato___Early_blight","Tomato___Late_blight",
"Tomato___Leaf_Mold","Tomato___Septoria_leaf_spot",
"Tomato___Spider_mites Two-spotted_spider_mite","Tomato___Target_Spot",
"Tomato___Tomato_Yellow_Leaf_Curl_Virus","Tomato___Tomato_mosaic_virus",
"Tomato___healthy"
]

# Open file picker
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(title="Select Leaf Image")

# Load image
img = image.load_img(file_path, target_size=(224,224))
img_array = image.img_to_array(img)
img_array = np.expand_dims(img_array, axis=0) / 255.0

# Predict
pred = model.predict(img_array)
pred_index = np.argmax(pred)
confidence = pred[0][pred_index] * 100

# Show result
plt.imshow(img)
plt.axis("off")
plt.title(class_names[pred_index])
plt.show()

print("Predicted Disease:", class_names[pred_index])
print("Confidence:", round(confidence,2), "%")