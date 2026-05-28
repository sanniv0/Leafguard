import io
import numpy as np
import tensorflow as tf
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# --- Class Names Matrix ---
CLASS_NAMES = [
    'Pepper: Bacterial Spot', 'Pepper: Healthy',
    'Potato: Early Blight', 'Potato: Late Blight', 'Potato: Healthy',
    'Tomato: Bacterial Spot', 'Tomato: Early Blight', 'Tomato: Late Blight',
    'Tomato: Leaf Mold', 'Tomato: Septoria Leaf Spot',
    'Tomato: Spider Mites', 'Tomato: Target Spot',
    'Tomato: Yellow Leaf Curl Virus', 'Tomato: Mosaic Virus', 'Tomato: Healthy'
]

# --- Botanical Advice Library ---
BOTANICAL_ADVICE = {
    "Pepper: Bacterial Spot": "Apply organic copper-based fungicides early in the morning. Remove and destroy infected leaves. Ensure adequate spacing between pepper plants to maximize airflow and reduce moisture retention.",
    "Pepper: Healthy": "Specimen shows robust vascular structure and healthy chlorophyll levels. Maintain current watering and organic compost schedules.",
    "Potato: Early Blight": "Remove affected lower foliage to prevent spores from splashing onto healthy leaves. Apply organic copper sprays or Bacillus subtilis. Implement a crop rotation schedule next season.",
    "Potato: Late Blight": "WARNING: Highly contagious pathogen. Immediately destroy heavily infected plants. Apply preventive copper-based fungicides. Keep foliage dry by watering at the base.",
    "Potato: Healthy": "Vigorous foliage detected. Excellent tuber development potential. Continue companion planting with marigolds to deter pests.",
    "Tomato: Bacterial Spot": "Avoid overhead watering to prevent bacterial spread. Apply copper fungicide treatments. Keep pruning tools sanitized using alcohol or bleach solutions between cuts.",
    "Tomato: Early Blight": "Prune lower leaves up to 12 inches from the soil to prevent soil-borne spores from splashing onto foliage. Mulch the soil bed and apply organic bio-fungicides.",
    "Tomato: Late Blight": "High epidemic threat. Immediately quarantine the crop. Apply organic copper fungicides or bio-pesticides. Keep greenhouse humidity below 80% if growing indoors.",
    "Tomato: Leaf Mold": "Increase greenhouse ventilation and space plants to lower humidity. Avoid watering late in the evening. Treat with sulfur-based sprays or bio-fungicides.",
    "Tomato: Septoria Leaf Spot": "Prune affected leaves immediately. Apply organic fungicides containing copper or chlorothalonil. Apply organic mulch under plants to create a barrier against soil spores.",
    "Tomato: Spider Mites": "Increase local humidity by misting plants. Spray foliage with organic insecticidal soap or neem oil solutions. Introduce natural predators like predatory mites.",
    "Tomato: Target Spot": "Improve air circulation through regular pruning. Apply copper fungicides or organic bio-fungicides. Ensure proper crop rotation and remove crop residues after harvest.",
    "Tomato: Yellow Leaf Curl Virus": "Viral pathogen spread by whiteflies. Shield plants using insect mesh nets. Remove infected specimens immediately. Use yellow sticky traps to capture whitefly vectors.",
    "Tomato: Mosaic Virus": "Viral infection with no chemical cure. Immediately isolate and destroy infected specimens. Keep weed populations down and thoroughly sanitize all hands, gloves, and garden tools.",
    "Tomato: Healthy": "Specimen is highly vigorous and disease-free. Maintain balanced nitrogen-potassium levels and monitor for minor pests regularly."
}

# --- FastAPI Initialization ---
app = FastAPI(
    title="LeafGuard AI Inference Engine",
    description="Decoupled high-performance backend serving MobileNetV2 botanical leaf disease classifications.",
    version="1.0.0"
)

# --- CORS Configurations ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows local React Vite server (typically localhost:5173)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Model Variables ---
MODEL_PATH = "best_model.keras"
model = None

@app.on_event("startup")
def load_model():
    global model
    print(f"[INFO] Caching deep learning model from '{MODEL_PATH}' in-memory...")
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        print("[INFO] Model loaded successfully.")
    except Exception as e:
        print(f"[FATAL] Failed to load model: {str(e)}")
        raise e

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "engine": "FastAPI",
        "model": "MobileNetV2 (Custom Head)",
        "classes_supported": len(CLASS_NAMES),
        "tensorflow_version": tf.__version__
    }

@app.post("/predict")
async def predict_specimen(file: UploadFile = File(...)):
    # 1. Validation check
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image spec.")
        
    try:
        # 2. Read bytes and load image using PIL
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        
        # 3. Pre-process matching exact training configurations
        # PIL Bilinear resize to 160x160
        processed_img = image.resize((160, 160))
        img_array = np.array(processed_img)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Normalize between [-1.0, 1.0] using MobileNetV2 preprocessing
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)
        
        # 4. Neural inference
        prediction = model.predict(img_array)
        idx = np.argmax(prediction)
        predicted_class = CLASS_NAMES[idx]
        confidence = float(np.max(prediction))
        
        # 5. Extract species and disease status
        species = predicted_class.split(":")[0].strip()
        status = "healthy" if "Healthy" in predicted_class else "pathogenic"
        advice = BOTANICAL_ADVICE.get(predicted_class, "No advice available for this category.")
        
        # Get top-3 categories for advanced visual progress bars
        top_indices = np.argsort(prediction[0])[::-1][:3]
        top_predictions = [
            {
                "class": CLASS_NAMES[i],
                "confidence": float(prediction[0][i]) * 100
            }
            for i in top_indices
        ]
        
        return {
            "class": predicted_class,
            "confidence": confidence * 100,
            "species": species,
            "status": status,
            "advice": advice,
            "top_predictions": top_predictions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference pipeline execution failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
