import os
import json 
import urllib.request
import urllib.parse
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# Get API keys from environment variables
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
MBTA_API_KEY = os.getenv("MBTA_API_KEY")

# Useful base URLs (you need to add the appropriate parameters for each API request)
MAPBOX_BASE_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"
MBTA_BASE_URL = "https://api-v3.mbta.com/stops"


# A little bit of scaffolding if you want to use it
def get_json(url: str) -> dict:
    """
    Given a properly formatted URL for a JSON web API request, return a Python JSON object containing the response to that request.

    Both get_lat_lng() and get_nearest_station() might need to use this function.
    """
    try:
        with urllib.request.urlopen(url) as response:
            response_text = response.read().decode("utf-8")
            return json.loads(response_text)
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return {}


def get_lat_lng(place_name: str) -> tuple[str, str]:
    """
    Given a place name or address, return a (latitude, longitude) tuple with the coordinates of the given place.

    See https://docs.mapbox.com/api/search/geocoding/ for Mapbox Geocoding API URL formatting requirements.
    """
    if not MAPBOX_TOKEN:
        raise ValueError("MAPBOX_TOKEN not found. Please check your .env file.")
    
    # URL encode the place name
    encoded_place = urllib.parse.quote(place_name)
    
    # Build the URL
    url = f"{MAPBOX_BASE_URL}/{encoded_place}.json?access_token={MAPBOX_TOKEN}&limit=1"
    
    # Get the JSON response
    data = get_json(url)
    
    if not data or "features" not in data or len(data["features"]) == 0:
        raise ValueError(f"No location found for '{place_name}'")
    
    # Extract coordinates from the first result
    coordinates = data["features"][0]["geometry"]["coordinates"]
    longitude, latitude = coordinates  # Note: Mapbox returns [longitude, latitude]
    
    return str(latitude), str(longitude)

def get_nearest_station(latitude: str, longitude: str) -> tuple[str, bool]:
    """
    Given latitude and longitude strings, return a (station_name, wheelchair_accessible) tuple for the nearest MBTA station to the given coordinates.

    See https://api-v3.mbta.com/docs/swagger/index.html#/Stop/ApiWeb_StopController_index for URL formatting requirements for the 'GET /stops' API.
    """
    if not MBTA_API_KEY:
        raise ValueError("MBTA_API_KEY not found. Please check your .env file.")
    
    # Build the URL with query parameters
    params = {
        'api_key': MBTA_API_KEY,
        'sort': 'distance',
        'filter[latitude]': latitude,
        'filter[longitude]': longitude
    }
    
    query_string = urllib.parse.urlencode(params)
    url = f"{MBTA_BASE_URL}?{query_string}"
    
    # Get the JSON response
    data = get_json(url)
    
    if not data or "data" not in data or len(data["data"]) == 0:
        raise ValueError("No MBTA stations found near the specified location")
    
    # Get the nearest station (first in the sorted list)
    nearest_station = data["data"][0]
    station_name = nearest_station["attributes"]["name"]
    wheelchair_accessible = nearest_station["attributes"]["wheelchair_boarding"] == 1
    
    return station_name, wheelchair_accessible


def find_stop_near(place_name: str) -> tuple[str, bool]:
    """
    Given a place name or address, return the nearest MBTA stop and whether it is wheelchair accessible.

    This function might use all the functions above.
    """
    try:
        # Get coordinates for the place
        latitude, longitude = get_lat_lng(place_name)
        
        # Find the nearest MBTA station
        station_name, wheelchair_accessible = get_nearest_station(latitude, longitude)
        
        return station_name, wheelchair_accessible
        
    except Exception as e:
        raise ValueError(f"Error finding stop near '{place_name}': {e}")



def main():
    """
    You should test all the above functions here
    """
    try:
        # Test with a known location in Boston
        test_location = "Boston Common"
        print(f"Testing with location: {test_location}")
        
        # Test get_lat_lng
        lat, lng = get_lat_lng(test_location)
        print(f"Coordinates: {lat}, {lng}")
        
        # Test get_nearest_station
        station, accessible = get_nearest_station(lat, lng)
        print(f"Nearest station: {station}")
        print(f"Wheelchair accessible: {accessible}")
        
        # Test the combined function
        station, accessible = find_stop_near(test_location)
        print(f"Result from find_stop_near: {station}, Wheelchair accessible: {accessible}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        print("Make sure your API keys are set in the .env file!")


if __name__ == "__main__":
    main()
