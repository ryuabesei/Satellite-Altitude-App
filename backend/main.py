"""
FastAPI backend for satellite altitude tracking.
Fetches TLE data from CelesTrak and calculates altitude using SGP4 propagation.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from skyfield.api import EarthSatellite, load, wgs84
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Satellite Altitude Tracker API",
    description="Calculate and retrieve satellite altitude variations using TLE data",
    version="1.0.0"
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Skyfield time scale
ts = load.timescale()

# Constants
EARTH_RADIUS_KM = 6371.0
MAX_DATA_POINTS = 20000
CELESTRAK_TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE"


async def fetch_tle_from_celestrak(norad_id: int) -> tuple[str, str]:
    """
    Fetch TLE data from CelesTrak for a given NORAD catalog number.
    
    Args:
        norad_id: NORAD catalog number
        
    Returns:
        Tuple of (line1, line2) TLE strings
        
    Raises:
        HTTPException: If TLE cannot be fetched
    """
    url = CELESTRAK_TLE_URL.format(norad_id=norad_id)
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"NORAD ID {norad_id} not found in CelesTrak database"
                )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"CelesTrak returned status {response.status_code}"
                )
            
            # Parse TLE (3 lines: name, line1, line2)
            lines = response.text.strip().split('\n')
            if len(lines) < 3:
                raise HTTPException(
                    status_code=502,
                    detail="Invalid TLE format received from CelesTrak"
                )
            
            return lines[1], lines[2]
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=502,
            detail="CelesTrak request timed out"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to connect to CelesTrak: {str(e)}"
        )


def calculate_altitude_series(
    tle_line1: str,
    tle_line2: str,
    start_time: datetime,
    end_time: datetime,
    step_seconds: int
) -> List[Dict[str, Any]]:
    """
    Calculate altitude time series using SGP4 propagation.
    
    Args:
        tle_line1: First line of TLE
        tle_line2: Second line of TLE
        start_time: Start time (UTC)
        end_time: End time (UTC)
        step_seconds: Time step in seconds
        
    Returns:
        List of data points with time and altitude
    """
    # Create satellite object
    satellite = EarthSatellite(tle_line1, tle_line2, "Satellite", ts)
    
    # Generate time array
    total_seconds = (end_time - start_time).total_seconds()
    num_points = int(total_seconds / step_seconds) + 1
    
    points = []
    current_time = start_time
    
    for i in range(num_points):
        # Convert to Skyfield time
        t = ts.utc(
            current_time.year,
            current_time.month,
            current_time.day,
            current_time.hour,
            current_time.minute,
            current_time.second
        )
        
        # Get geocentric position
        geocentric = satellite.at(t)
        
        # Calculate distance from Earth center
        position = geocentric.position.km
        geocentric_distance = (position[0]**2 + position[1]**2 + position[2]**2) ** 0.5
        
        # Calculate altitude above Earth surface
        altitude_km = geocentric_distance - EARTH_RADIUS_KM
        
        # Add data point
        points.append({
            "t": current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alt_km": round(altitude_km, 2)
        })
        
        # Increment time
        current_time = start_time + (i + 1) * __import__('datetime').timedelta(seconds=step_seconds)
        
        if current_time > end_time:
            break
    
    return points


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/altitude")
async def get_altitude(
    n: int = Query(..., description="NORAD catalog number", ge=1),
    start: str = Query(..., description="Start time in ISO8601 format (UTC)", regex=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"),
    end: str = Query(..., description="End time in ISO8601 format (UTC)", regex=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"),
    step: int = Query(60, description="Time step in seconds", ge=1, le=3600, alias="step_seconds")
):
    """
    Calculate satellite altitude over a time range.
    
    Returns altitude data points calculated using SGP4 propagation from TLE data.
    """
    try:
        # Parse timestamps
        start_time = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end.replace('Z', '+00:00'))
        
        # Validate time range
        if start_time >= end_time:
            raise HTTPException(
                status_code=400,
                detail="Start time must be before end time"
            )
        
        # Calculate number of points
        total_seconds = (end_time - start_time).total_seconds()
        num_points = int(total_seconds / step) + 1
        
        if num_points > MAX_DATA_POINTS:
            raise HTTPException(
                status_code=400,
                detail=f"Too many data points ({num_points}). Maximum allowed is {MAX_DATA_POINTS}. "
                       f"Please increase step_seconds or reduce time range."
            )
        
        # Fetch TLE from CelesTrak
        tle_line1, tle_line2 = await fetch_tle_from_celestrak(n)
        
        # Extract TLE epoch for metadata
        # TLE epoch is in line 1, columns 19-32
        tle_epoch_str = tle_line1[18:32].strip()
        
        # Calculate altitude series
        points = calculate_altitude_series(
            tle_line1,
            tle_line2,
            start_time,
            end_time,
            step
        )
        
        # Build response
        return {
            "norad_id": n,
            "start": start,
            "end": end,
            "step_seconds": step,
            "points": points,
            "meta": {
                "tle_source": "celestrak",
                "tle_epoch": tle_epoch_str,
                "earth_radius_km": EARTH_RADIUS_KM
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid timestamp format: {str(e)}"
        )
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error calculating altitude: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
