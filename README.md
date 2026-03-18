🌿 Plant Disease Identifier
A deep learning web app that detects plant diseases from leaf images. Upload a photo of a leaf and the model will identify the disease along with a confidence score.

⚠️ Disclaimer: This is a learning project built to practice deep learning and web development. The model is not 100% accurate and should not be used for professional agricultural decisions.


📸 Demo
Upload a leaf image → Get instant disease diagnosis + top 3 predictions with confidence scores.

🧠 Model

Architecture: Fine-tuned CNN (Transfer Learning)
Input Size: 224 × 224 px
Classes: 38 disease categories across 14 plant species
Final Training Accuracy: ~94.8%
Final Validation Accuracy: ~96.4%

Training Graphs
Model AccuracyModel LossShow ImageShow Image
The model was trained for 5 epochs. Validation accuracy stayed consistently high (~96%) while training accuracy steadily improved, indicating good generalization with minimal overfitting.

🌱 Datasets Used
Trained on two Kaggle datasets:

PlantVillage by Mohit Singh — 857 MB
New Plant Diseases Dataset by Samir Bhattarai — 3 GB


🌾 Supported Plants & Diseases
PlantConditionsAppleApple Scab, Black Rot, Cedar Apple Rust, HealthyBlueberryHealthyCherryPowdery Mildew, HealthyCorn (Maize)Cercospora Leaf Spot, Common Rust, Northern Leaf Blight, HealthyGrapeBlack Rot, Esca (Black Measles), Leaf Blight, HealthyOrangeHaunglongbing (Citrus Greening)PeachBacterial Spot, HealthyBell PepperBacterial Spot, HealthyPotatoEarly Blight, Late Blight, HealthyRaspberryHealthySoybeanHealthySquashPowdery MildewStrawberryLeaf Scorch, HealthyTomatoBacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy

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

Add the model file
Download or copy your plant_disease_model_finetuned.h5 file into the project root folder (same level as app.py). The model file is not included in the repo due to GitHub's file size limits.
Run the app

bash   python app.py

Open in browser

   http://localhost:5000

🗂️ Project Structure
Plant-disease-identifier/
├── app.py                            # Flask backend API
├── index.html                        # Frontend web UI
├── requirements.txt                  # Python dependencies
├── plant_disease_model_finetuned.h5  # Trained model (not in repo)
├── acc_impv.png                      # Accuracy training graph
└── losss_impv.png                    # Loss training graph

🛠️ Tech Stack

Model: TensorFlow / Keras
Backend: Flask + Flask-CORS
Frontend: HTML, CSS, JavaScript (vanilla)
Image Processing: Pillow, NumPy


📚 What I Learned

Transfer learning and fine-tuning pre-trained CNN models
Building a REST API with Flask to serve ML models
Connecting a web frontend to a Python backend
Image preprocessing pipelines for deep learning


📄 License
This project is open source and available under the MIT License.