from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# ------------------------------------------------------------
# Fichiers du modèle et du scaler
#
# Structure attendue :
# backend/
# ├── main.py
# └── models/
#     ├── modele_chiffres.pkl
#     └── scaler.pkl
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "modele_chiffres.pkl"
SCALER_PATH = BASE_DIR / "models" / "scaler.pkl"


# ------------------------------------------------------------
# Charger le modèle et le scaler au démarrage
# ------------------------------------------------------------
if not MODEL_PATH.exists():
    raise RuntimeError(
        f"Modèle introuvable : {MODEL_PATH}\n"
        "Placez modele_chiffres.pkl dans le dossier models."
    )

if not SCALER_PATH.exists():
    raise RuntimeError(
        f"Scaler introuvable : {SCALER_PATH}\n"
        "Placez scaler.pkl dans le dossier models."
    )

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)


# ------------------------------------------------------------
# Créer l’application FastAPI
# ------------------------------------------------------------
app = FastAPI(
    title="Devine le chiffre",
    description="API de reconnaissance de chiffres manuscrits avec MNIST.",
    version="1.0.0",
)

# Configuration pratique pour le développement local.
# En production, remplacez "*" par l'adresse exacte de votre frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------
# Format de la requête reçue depuis le frontend
# ------------------------------------------------------------
class PredictionRequest(BaseModel):
    pixels: list[list[float]]


# ------------------------------------------------------------
# Vérifier que le backend fonctionne
# ------------------------------------------------------------
@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Le backend fonctionne. Envoyez une requête POST à /predict."
    }


# ------------------------------------------------------------
# Prédire le chiffre
# ------------------------------------------------------------
@app.post("/predict")
def predict(request: PredictionRequest):
    # Convertir les pixels en tableau numérique.
    try:
        pixels = np.asarray(request.pixels, dtype=np.float32)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Les pixels doivent être des nombres."
        )

    # Vérifier les dimensions.
    if pixels.shape != (28, 28):
        raise HTTPException(
            status_code=400,
            detail=(
                "L'image doit mesurer exactement 28 x 28 pixels. "
                f"Dimensions reçues : {pixels.shape}"
            )
        )

    # Refuser NaN et les valeurs infinies.
    if not np.isfinite(pixels).all():
        raise HTTPException(
            status_code=400,
            detail="Les valeurs des pixels doivent être des nombres finis."
        )

    # Le frontend envoie des valeurs comprises entre 0 et 255.
    if np.any(pixels < 0) or np.any(pixels > 255):
        raise HTTPException(
            status_code=400,
            detail="Chaque pixel doit avoir une valeur comprise entre 0 et 255."
        )

    # Le frontend dessine en blanc sur fond noir.
    # Refuser une image vide ou presque vide.
    nombre_pixels_clairs = int(np.count_nonzero(pixels > 20))

    if nombre_pixels_clairs < 8:
        return {
            "digit": None,
            "confidence": 0.0,
            "message": "Aucun chiffre détecté. Dessinez un chiffre avant de prédire."
        }

    # Préparer les données :
    # 28 x 28 -> 1 x 784.
    # Ne pas diviser par 255 : le scaler sauvegardé s'en charge.
    flat_pixels = pixels.reshape(1, 784)
    prepared_pixels = scaler.transform(flat_pixels)

    # Obtenir les probabilités pour les classes 0 à 9.
    if not hasattr(model, "predict_proba"):
        raise HTTPException(
            status_code=500,
            detail="Le modèle chargé ne permet pas de calculer les probabilités."
        )

    probabilities = model.predict_proba(prepared_pixels)[0]
    best_index = int(np.argmax(probabilities))
    confidence = float(probabilities[best_index])

    # Les classes du modèle peuvent être des chaînes, par exemple "7".
    try:
        digit = int(model.classes_[best_index])
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=500,
            detail="Impossible de convertir la classe prédite en chiffre."
        )

    # Rejeter les prédictions peu sûres.
    # Ce seuil est à ajuster avec des exemples réels.
    MIN_CONFIDENCE = 0.70

    if confidence < MIN_CONFIDENCE:
        return {
            "digit": None,
            "confidence": round(confidence, 4),
            "message": "Le chiffre est incertain. Essayez de le dessiner plus clairement."
        }

    return {
        "digit": digit,
        "confidence": round(confidence, 4)
    }