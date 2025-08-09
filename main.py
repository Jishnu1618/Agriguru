from fastapi import FastAPI, UploadFile, File, Query
import tensorflow as tf
import numpy as np
from PIL import Image
import joblib
import json
import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace * with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("models/disease_cures.json", "r") as f:
    disease_cure_mapping = json.load(f)




# ------------------ Utility Functions ------------------

def is_dangerous(condition: str, temp: float, rainfall: float, wind_kph: float) -> bool:
    condition = condition.lower()
    return (
        "storm" in condition
        or "thunder" in condition
        or "hail" in condition
        or rainfall > 50
        or temp > 40
        or temp < 5
        or wind_kph > 60
    )

# ------------------ Load Models ------------------

crop_model = joblib.load("models/crop_prediction_model")
label_encoder = joblib.load("models/label_encoder")

disease_model = tf.keras.models.load_model("models/plant_disease_model")
with open("models/class_indices.json", "r") as f:
    class_indices = json.load(f)
disease_labels = list(class_indices.keys())
# Load disease cures from JSON
with open("models/disease_cures.json", "r") as f:
    disease_cure_mapping = json.load(f)


# ------------------ Weather API Setup ------------------

API_KEY = "73692c9477c84540b245583346251107"
BASE_URL = "http://api.weatherapi.com/v1/current.json"

def fetch_weather(city):
    params = {"key": API_KEY, "q": city}
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    temp = data["current"]["temp_c"]
    humidity = data["current"]["humidity"]
    rainfall = data["current"].get("precip_mm", 0.0)
    return temp, humidity, rainfall

# ------------------ Routes ------------------

@app.get("/")
def read_root():
    return {"message": "AgriGuru backend is running!"}

@app.post("/predict_disease")
def predict_disease(file: UploadFile = File(...)):
    try:
        image = Image.open(file.file).convert("RGB").resize((224, 224))
        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=0)

        predictions = disease_model.predict(image)[0]
        predicted_index = np.argmax(predictions)
        predicted_label = disease_labels[predicted_index]
        confidence = round(float(predictions[predicted_index]) * 100, 2)
        cure = disease_cure_mapping.get(predicted_label, "No cure information available.")

        return {
            "predicted_disease": predicted_label,
            "confidence": f"{confidence}%",
            "suggested_cure": cure
        }

    except Exception as e:
        return {"error": str(e)}
    
@app.get("/predict-crop")
def predict_crop(n: float, p: float, k: float, ph: float, city: str):
    try:
        temp, humidity, rainfall = fetch_weather(city)
        features = np.array([[n, p, k, temp, humidity, ph, rainfall]])
        probabilities = crop_model.predict_proba(features)[0]
        top_indices = np.argsort(probabilities)[-3:][::-1]
        top_crops = label_encoder.inverse_transform(top_indices)

        return {
            "city": city,
            "input": {
                "N": n, "P": p, "K": k, "pH": ph,
                "temperature": temp, "humidity": humidity, "rainfall": rainfall
            },
            "top_3_crops": [
                {"crop": top_crops[0], "confidence": round(probabilities[top_indices[0]] * 100, 2)},
                {"crop": top_crops[1], "confidence": round(probabilities[top_indices[1]] * 100, 2)},
                {"crop": top_crops[2], "confidence": round(probabilities[top_indices[2]] * 100, 2)}
            ]
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/weather-info")
def get_weather_info(city: str = "Burdwan", days: int = 3):
    try:
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {"key": API_KEY, "q": city, "days": days, "aqi": "no", "alerts": "no"}
        response = requests.get(url, params=params)
        data = response.json()

        current = data["current"]
        forecast_data = data["forecast"]["forecastday"]

        result = {
            "location": data["location"]["name"],
            "current": {
                "temp_c": current["temp_c"],
                "humidity": current["humidity"],
                "condition": current["condition"]["text"],
                "rain_mm": current.get("precip_mm", 0.0)
            },
            "forecast": [
                {
                    "date": day["date"],
                    "max_temp_c": day["day"]["maxtemp_c"],
                    "min_temp_c": day["day"]["mintemp_c"],
                    "avg_humidity": day["day"]["avghumidity"],
                    "precip_mm": day["day"]["totalprecip_mm"],
                    "condition": day["day"]["condition"]["text"]
                }
                for day in forecast_data
            ]
        }

        return result

    except Exception as e:
        return {"error": str(e)}

@app.get("/weather-alerts")
def weather_alerts(city: str = "Burdwan"):
    try:
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {"key": API_KEY, "q": city, "days": 1, "alerts": "no"}
        response = requests.get(url, params=params)
        data = response.json()

        forecast = data["forecast"]["forecastday"][0]["day"]
        condition = forecast["condition"]["text"]
        temp = forecast["maxtemp_c"]
        rainfall = forecast["totalprecip_mm"]
        wind = forecast["maxwind_kph"]

        alert = is_dangerous(condition, temp, rainfall, wind)

        result = {
            "city": city,
            "condition": condition,
            "max_temperature_c": temp,
            "total_rainfall_mm": rainfall,
            "max_wind_kph": wind,
            "alert": alert,
            "message": "⚠️ Weather Alert: Please take precautions!" if alert else "✅ Weather is safe for now."
        }
        return result

    except Exception as e:
        return {"error": str(e)}
    
from chatbot.chatbot_router import router as chatbot_router
app.include_router(chatbot_router)
from mandi import mandi_router
app.include_router(mandi_router.router)
from chatbot.chatbot_router import router as chatbot_router
app.include_router(chatbot_router)



