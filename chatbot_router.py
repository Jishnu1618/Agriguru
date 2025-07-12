# chatbot/chatbot_router.py
from fastapi import APIRouter, Query
from chatbot.chatbot_engine import get_top_answers

router = APIRouter()

@router.get("/chatbot", tags=["Chatbot"])
def chatbot(query: str = Query(..., description="Ask your farming question")):
    """
    Fetches top relevant answers based on user query using semantic search.
    """
    try:
        results = get_top_answers(query)
        return {
            "query": query,
            "answers": results
        }
    except Exception as e:
        return {"error": str(e)}
from chatbot.mandi_prices import fetch_mandi_prices
from chatbot.crop_trends import get_crop_trend_graph
from fastapi.responses import JSONResponse

@router.get("/mandi-prices", tags=["Market"])
def get_mandi_prices(commodity: str, state: str = "", district: str = "", limit: int = 10):
    try:
        data = fetch_mandi_prices(commodity, state, district, limit)
        return {"commodity": commodity, "results": data}
    except Exception as e:
        return {"error": str(e)}


from chatbot.crop_trends import get_unique_districts, get_unique_crops

@router.get("/crop-trends/districts", tags=["Crop Trends"])
def list_districts():
    return {"districts": get_unique_districts()}

@router.get("/crop-trends/crops", tags=["Crop Trends"])
def list_crops():
    return {"crops": get_unique_crops()}
