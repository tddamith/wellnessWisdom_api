# app/api/v1/trends.py
from fastapi import APIRouter, HTTPException
from pytrends.request import TrendReq
from pydantic import BaseModel
from typing import List

# Initialize the router
router = APIRouter()

# Initialize Pytrends
pytrends = TrendReq(hl='en-US', tz=360)

# Request model
class TrendsRequest(BaseModel):
    keywords: List[str]
    timeframe: str = "now 7-d"  # Default: Last 7 days
    region: str = "US"  # Default: United States

@router.post("/trends")
async def get_google_trends(request: TrendsRequest):
    """
    Fetch Google Trends data for specified keywords.
    """
    if len(request.keywords) > 5:
        raise HTTPException(status_code=400, detail="Maximum of 5 keywords allowed.")

    try:
        # Build payload
        pytrends.build_payload(kw_list=request.keywords, timeframe=request.timeframe, geo=request.region)

        # Fetch interest over time data
        data = pytrends.interest_over_time()

        if data.empty:
            raise HTTPException(status_code=404, detail="No data found for the given parameters.")

        # Convert to JSON-friendly format
        result = data.drop(columns=["isPartial"], errors="ignore").reset_index().to_dict(orient="records")
        return {"success": True, "data": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
