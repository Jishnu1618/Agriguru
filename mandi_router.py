from fastapi import APIRouter, Query
import requests

router = APIRouter()

API_KEY = "579b464db66ec23bdd000001fc9a038445364fc46e756e42046b7710f83"
RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0078970"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}?api-key={API_KEY}&format=json&limit=1000"

def fetch_all_data():
    response = requests.get(BASE_URL)
    return response.json().get("records", [])

@router.get("/mandi/states", tags=["Mandi Prices"])
def get_states():
    data = fetch_all_data()
    states = sorted(list(set(item["state"] for item in data)))
    return {"states": states}

@router.get("/mandi/districts", tags=["Mandi Prices"])
def get_districts(state: str = Query(...)):
    data = fetch_all_data()
    districts = sorted(list(set(item["district"] for item in data if item["state"] == state)))
    return {"districts": districts}

@router.get("/mandi/commodities", tags=["Mandi Prices"])
def get_commodities():
    data = fetch_all_data()
    commodities = sorted(list(set(item["commodity"] for item in data)))
    return {"commodities": commodities}

@router.get("/mandi/prices", tags=["Mandi Prices"])
def get_prices(
    state: str = Query(...),
    district: str = Query(...),
    commodity: str = Query(...)
):
    data = fetch_all_data()
    filtered = [
        {
            "state": item["state"],
            "district": item["district"],
            "market": item["market"],
            "commodity": item["commodity"],
            "variety": item["variety"],
            "arrival_date": item["arrival_date"],
            "min_price": item["min_price"],
            "max_price": item["max_price"],
            "modal_price": item["modal_price"]
        }
        for item in data
        if item["state"].lower() == state.lower() and
   item["district"].lower() == district.lower() and
   item["commodity"].lower() == commodity.lower()

    ]
    return {"results": filtered}

