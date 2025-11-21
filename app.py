# ==========================
# app.py  (Updated version)
# ==========================
from flask import Flask, render_template, request, jsonify
import numpy as np
import base64
import io
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

app = Flask(__name__)

# ---- CONFIG ----
MODEL_PATH = r"C:\Users\Nagaraj\OneDrive\Desktop\skin_disease_app\skin_disease_model.h5"   # ✅ updated
IMAGE_SIZE = (64, 64)   # ✅ match training size
# Load model
model = load_model(MODEL_PATH)

# Automatically get labels from your HAM10000 training
# You can also manually list them if you know them (e.g., ['akiec','bcc','bkl','df','mel','nv','vasc'])
LABELS = ['akiec','bcc','bkl','df','mel','nv','vasc']   # replace with your dataset's class names

# ==========================
# Helper function
# ==========================
def preprocess_image_pil(img_pil):
    img = img_pil.convert('RGB')
    img = img.resize(IMAGE_SIZE)
    arr = image.img_to_array(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    return arr

# ==========================
# Routes
# ==========================
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # case 1: JSON base64 (from camera)
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            if 'image' not in data:
                return jsonify({'error': 'No image key in JSON'}), 400
            img_b64 = data['image'].split(",")[1] if "," in data['image'] else data['image']
            img_bytes = base64.b64decode(img_b64)
            img = Image.open(io.BytesIO(img_bytes))

        # case 2: file upload form
        elif 'image' in request.files:
            file = request.files['image']
            img = Image.open(file.stream)
        else:
            return jsonify({'error': 'No image provided'}), 400

        # preprocess and predict
        x = preprocess_image_pil(img)
        preds = model.predict(x)
        idx = int(np.argmax(preds, axis=1)[0])
        label = LABELS[idx]
        confidence = float(np.max(preds))

        return jsonify({'prediction': label, 'confidence': round(confidence, 4)})

    except Exception as e:
        print("Error in /predict:", e)
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
