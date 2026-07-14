import io
import numpy as np
import tensorflow as tf
from PIL import Image, UnidentifiedImageError
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# --- Leaf Validation Thresholds ---
CONFIDENCE_THRESHOLD = 95.0   # percent — genuine leaves typically score 98%+
ENTROPY_THRESHOLD = 1.5       # nats — low = confident, high = uncertain (max ~2.7 for 15 classes)
MARGIN_THRESHOLD = 30.0       # percent — difference between top-1 and top-2

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
    "Pepper: Bacterial Spot": {
        "prevention": "Ensure proper spacing between plants, avoid overhead irrigation, use disease-free seeds, and maintain good field sanitation.",
        "remedy": "Remove infected leaves immediately and apply copper-based bactericides or organic fungicides during early morning hours."
    },

    "Pepper: Healthy": {
        "prevention": "Continue regular monitoring, maintain balanced fertilization, ensure adequate airflow, and follow proper watering schedules.",
        "remedy": "No treatment required. Continue current cultivation practices to maintain plant health."
    },

    "Potato: Early Blight": {
        "prevention": "Practice crop rotation, avoid excessive leaf moisture, use certified disease-free seed potatoes, and maintain proper plant spacing.",
        "remedy": "Remove affected foliage and apply copper-based fungicides or Bacillus subtilis treatments to limit disease spread."
    },

    "Potato: Late Blight": {
        "prevention": "Avoid overhead watering, ensure proper drainage, improve air circulation, and inspect crops regularly during humid weather.",
        "remedy": "Immediately remove severely infected plants and apply preventive copper-based fungicides to protect remaining crops."
    },

    "Potato: Healthy": {
        "prevention": "Maintain proper irrigation, monitor for pests and diseases regularly, and continue balanced nutrient management.",
        "remedy": "No treatment necessary. Continue existing crop management practices."
    },

    "Tomato: Bacterial Spot": {
        "prevention": "Avoid overhead watering, use disease-free seeds, rotate crops regularly, and sanitize pruning equipment after each use.",
        "remedy": "Apply copper fungicide treatments and remove infected leaves to reduce bacterial spread."
    },

    "Tomato: Early Blight": {
        "prevention": "Mulch the soil, avoid wetting foliage, maintain proper spacing, and prune lower leaves to reduce fungal infection risks.",
        "remedy": "Remove infected foliage and apply organic bio-fungicides or copper-based fungicides."
    },

    "Tomato: Late Blight": {
        "prevention": "Maintain greenhouse humidity below 80%, improve ventilation, avoid prolonged leaf wetness, and inspect plants frequently.",
        "remedy": "Quarantine infected plants immediately and apply approved copper fungicides or bio-pesticides."
    },

    "Tomato: Leaf Mold": {
        "prevention": "Reduce humidity levels, improve greenhouse ventilation, avoid overcrowding, and water plants early in the day.",
        "remedy": "Apply sulfur-based sprays or bio-fungicides and remove heavily infected foliage."
    },

    "Tomato: Septoria Leaf Spot": {
        "prevention": "Use mulch to prevent soil splash, avoid overhead irrigation, and ensure adequate spacing between plants.",
        "remedy": "Prune affected leaves and apply fungicides containing copper or chlorothalonil."
    },

    "Tomato: Spider Mites": {
        "prevention": "Maintain adequate humidity, regularly inspect leaf undersides, and encourage beneficial insects in the garden.",
        "remedy": "Apply neem oil or insecticidal soap and introduce predatory mites to control infestations naturally."
    },

    "Tomato: Target Spot": {
        "prevention": "Promote airflow through pruning, avoid excess moisture, practice crop rotation, and remove crop debris after harvest.",
        "remedy": "Treat plants with copper fungicides or bio-fungicides and remove infected plant material."
    },

    "Tomato: Yellow Leaf Curl Virus": {
        "prevention": "Control whitefly populations using insect netting, sticky traps, and regular monitoring of crops.",
        "remedy": "Remove infected plants immediately and manage whitefly vectors to prevent further transmission."
    },

    "Tomato: Mosaic Virus": {
        "prevention": "Use certified disease-free seeds, control weeds, avoid tobacco contamination, and disinfect tools regularly.",
        "remedy": "There is no cure. Remove and destroy infected plants immediately to prevent spread."
    },

    "Tomato: Healthy": {
        "prevention": "Maintain balanced fertilization, monitor crops regularly, provide adequate sunlight, and follow proper irrigation practices.",
        "remedy": "No treatment required. Continue routine care and disease monitoring."
    }
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
    # 1. MIME type validation
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image spec.")

    # 2. Read and decode the image
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except (UnidentifiedImageError, Exception):
        raise HTTPException(
            status_code=422,
            detail="The uploaded file could not be read as a valid image. Please upload a clear photo of a leaf."
        )

    try:
        # 3. Pre-process matching exact training configurations
        # PIL Bilinear resize to 160x160
        processed_img = image.resize((160, 160))
        img_array = np.array(processed_img)
        img_array = np.expand_dims(img_array, axis=0)

        # Normalize between [-1.0, 1.0] using MobileNetV2 preprocessing
        img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

        # 4. Neural inference
        prediction = model.predict(img_array)
        probs = prediction[0]
        idx = np.argmax(probs)
        predicted_class = CLASS_NAMES[idx]
        confidence_pct = float(probs[idx]) * 100

        # Compute validation signals
        sorted_probs = np.sort(probs)[::-1]
        top1 = float(sorted_probs[0]) * 100
        top2 = float(sorted_probs[1]) * 100
        margin = top1 - top2

        # Shannon entropy: -sum(p * log(p)), measures prediction spread
        # Low entropy = concentrated/confident, High = spread out/uncertain
        clipped = np.clip(probs, 1e-10, 1.0)
        entropy = -np.sum(clipped * np.log(clipped))

        # Debug logging — visible in server terminal
        print(f"[VALIDATION] Class: {predicted_class}")
        print(f"[VALIDATION] Confidence: {confidence_pct:.2f}% | Entropy: {entropy:.3f} | Margin: {margin:.2f}%")
        print(f"[VALIDATION] Thresholds — Conf>{CONFIDENCE_THRESHOLD}% | Entropy<{ENTROPY_THRESHOLD} | Margin>{MARGIN_THRESHOLD}%")

        # 5. Leaf validation gate — reject non-leaf images
        # Image must pass ALL three checks to be accepted
        is_low_confidence = confidence_pct < CONFIDENCE_THRESHOLD
        is_high_entropy = entropy > ENTROPY_THRESHOLD
        is_low_margin = margin < MARGIN_THRESHOLD

        if is_low_confidence or is_high_entropy or is_low_margin:
            failed_checks = []
            if is_low_confidence:
                failed_checks.append(f"confidence {confidence_pct:.1f}% < {CONFIDENCE_THRESHOLD}%")
            if is_high_entropy:
                failed_checks.append(f"entropy {entropy:.2f} > {ENTROPY_THRESHOLD}")
            if is_low_margin:
                failed_checks.append(f"margin {margin:.1f}% < {MARGIN_THRESHOLD}%")
            print(f"[REJECTED] Failed checks: {', '.join(failed_checks)}")
            raise HTTPException(
                status_code=422,
                detail=(
                    "The uploaded image does not appear to be a valid leaf specimen. "
                    "Our AI could not confidently identify any known plant disease pattern. "
                    "Please upload a clear, close-up photo of a Pepper, Potato, or Tomato leaf."
                )
            )

        print(f"[ACCEPTED] {predicted_class} at {confidence_pct:.1f}%")

        # 6. Extract species and disease status
        species = predicted_class.split(":")[0].strip()
        status = "healthy" if "Healthy" in predicted_class else "pathogenic"
        advice_data = BOTANICAL_ADVICE.get(
            predicted_class,
            {
                "prevention": "No prevention advice available.",
                "remedy": "No remedy available."
            }
        )

        # Get top-3 categories for advanced visual progress bars
        top_indices = np.argsort(probs)[::-1][:3]
        top_predictions = [
            {
                "class": CLASS_NAMES[i],
                "confidence": float(probs[i]) * 100
            }
            for i in top_indices
        ]

        return {
            "class": predicted_class,
            "confidence": confidence_pct,
            "species": species,
            "status": status,
            "prevention": advice_data["prevention"],
            "remedy": advice_data["remedy"],
            "top_predictions": top_predictions
        }

    except HTTPException:
        raise  # Re-raise leaf validation HTTPException as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference pipeline execution failure: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    reload = os.getenv("RELOAD", "false").lower() == "true"
    uvicorn.run("server:app", host=host, port=port, reload=reload)