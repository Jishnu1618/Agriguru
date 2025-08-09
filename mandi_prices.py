import requests

API_KEY = "579b464db66ec23bdd0000158901fc9a038364fc46e756e42046b7710f83"
RESOURCE_ID = "cef25fe2-9231-4128-8aec-2c948152fedd43f"
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}?api-key={API_KEY}&format=json"

def fetch_mandi_prices(commodity: str, state: str = "", district: str = "", max_records: int = 10):
    params = {
        "filters[commodity]": commodity,
        "filters[state]": state,
        "filters[district]": district,
        "limit": max_records,
        "format": "json"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    # Customize output if needed
    return data.get("records", [])

