🌿 Plant Disease Identifier
A deep learning web app that identifies plant diseases from leaf images. Upload a photo of a leaf and the model instantly diagnoses the disease with a confidence score and top 3 predictions.

⚠️ Disclaimer: This is a personal learning project built to practice deep learning and web development. The model is not 100% accurate and should not be used for professional or agricultural decisions.


🧠 Model Performance

Architecture: Fine-tuned CNN (Transfer Learning)
Input Size: 224 × 224 px
Classes: 38 disease categories across 14 plant species
Final Training Accuracy: ~94.8%
Final Validation Accuracy: ~96.4%
Epochs: 5

📊 Training Graphs
## 📊 Training Graphs

<p align="center">
  <img src="images/acc_impv.png" width="45%" alt="Model Accuracy"/>
  <img src="images/losss_impv.png" width="45%" alt="Model Loss"/>
</p>
Validation accuracy stayed consistently high (~96%) throughout training while training accuracy steadily caught up — showing good generalization with minimal overfitting.

🌱 Datasets Used
Trained on two Kaggle datasets:

PlantVillage by Mohit Singh · 857 MB
New Plant Diseases Dataset by Samir Bhattarai · 3 GB


🌾 Supported Plants & Diseases
PlantConditions Detected🍎 AppleApple Scab, Black Rot, Cedar Apple Rust, Healthy🫐 BlueberryHealthy🍒 CherryPowdery Mildew, Healthy🌽 Corn (Maize)Cercospora Leaf Spot, Common Rust, Northern Leaf Blight, Healthy🍇 GrapeBlack Rot, Esca (Black Measles), Leaf Blight, Healthy🍊 OrangeHaunglongbing (Citrus Greening)🍑 PeachBacterial Spot, Healthy🫑 Bell PepperBacterial Spot, Healthy🥔 PotatoEarly Blight, Late Blight, Healthy🫐 RaspberryHealthy🌱 SoybeanHealthy🎃 SquashPowdery Mildew🍓 StrawberryLeaf Scorch, Healthy🍅 TomatoBacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy

🚀 Getting Started
Prerequisites

Python 3.8+
PyCharm (recommended) or any Python IDE

Installation

Clone the repo

bash   git clone https://github.com/Pushpak-Cyrus/Plant-disease-identifier.git
   cd Plant-disease-identifier

Install dependencies

bash   pip install -r requirements.txt

Run the app

bash   python app.py

Open in browser

   http://localhost:5000

🗂️ Project Structure
Plant-disease-identifier/
├── app.py              # Flask backend API
├── index.html          # Frontend web UI
├── requirements.txt    # Python dependencies
├── acc_impv.png        # Accuracy training graph
└── losss_impv.png      # Loss training graph

🛠️ Tech Stack
LayerTechnologyModelTensorFlow / KerasBackendFlask + Flask-CORSFrontendHTML, CSS, JavaScriptImage ProcessingPillow, NumPy

📚 What I Learned

Transfer learning and fine-tuning pre-trained CNN models
Building a REST API with Flask to serve ML models
Connecting a web frontend to a Python backend
Image preprocessing pipelines for deep learning


📄 License
© 2025 Pushpak-Cyrus. All Rights Reserved.
This project is for viewing purposes only. Copying, distributing, or reusing any part of this code is strictly prohibited. See LICENSE for details.
