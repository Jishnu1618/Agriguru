import requests
import matplotlib.pyplot as plt
import io
import base64
from db.mongo import db
from datetime import datetime


API_KEY = "579b464db66ec23bdd000001fc9a038364fc46e756e42046b7710f83"
RESOURCE_ID = "35be999b-0208-4354-b557-f6ca9a5355de"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}?api-key={API_KEY}&format=json"

async def get_crop_trend_graph(district: str, crop: str):
    params = {
        "filters[district_name]": district,
        "filters[crop]": crop,
        "format": "json",
        "limit": 100
    }
    response = requests.get(BASE_URL, params=params)
    records = response.json().get("records", [])

    if not records:
        return None

    records = sorted(records, key=lambda x: (x["year"], x.get("season", "")))

    years = [r["year"] for r in records]
    production = [float(r["production"]) for r in records]

    plt.figure(figsize=(10, 4))
    plt.plot(years, production, marker='o')
    plt.title(f"Crop Trend for {crop} in {district}")
    plt.xlabel("Year")
    plt.ylabel("Production (tonnes)")
    plt.grid()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)

    img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
    plt.close()
    await db.crop_trends.insert_one({
    "district": district,
    "crop": crop,
    "years": years,
    "production": production,
    "image_base64": img_base64,
    "timestamp": datetime.utcnow()
})


    return img_base64

def get_unique_districts():
    response = requests.get(BASE_URL, params={"limit": 1000})
    records = response.json().get("records", [])

    districts = set()
    for r in records:
        if "district_name" in r:
            districts.add(r["district_name"].strip())

    return sorted(list(districts))

def get_unique_crops():
    response = requests.get(BASE_URL, params={"limit": 1000})
    records = response.json().get("records", [])

    crops = set()
    for r in records:
        if "crop" in r:
            crops.add(r["crop"].strip())

    return sorted(list(crops))
