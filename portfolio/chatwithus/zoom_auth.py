import os        
import time    
import requests  
from requests.auth import HTTPBasicAuth 


ACC_ID = os.getenv("ZOOM_ACCOUNT_ID")      
CLI_ID = os.getenv("ZOOM_CLIENT_ID")       
CLI_SECRET = os.getenv("ZOOM_CLIENT_SECRET") 

_TOKEN = {"value": None, "exp": 0}

def get_zoom_token() -> str:
    """
    Fetch and return a valid Zoom access token.
    If the old one is still valid, reuse it.
    """
   
    if _TOKEN["value"] and _TOKEN["exp"] > time.time() + 30:
        print("Reusing existing Zoom token")
        return _TOKEN["value"]

    
    if not (ACC_ID and CLI_ID and CLI_SECRET):
        raise RuntimeError("Missing Zoom credentials! Please set them in Railway environment.")

 
    url = "https://zoom.us/oauth/token"
    params = {
        "grant_type": "account_credentials",
        "account_id": ACC_ID
    }

 
    print("Fetching new Zoom token...")
    resp = requests.post(url, params=params, auth=HTTPBasicAuth(CLI_ID, CLI_SECRET), timeout=20)

   
    if resp.status_code != 200:
        raise RuntimeError(f"Zoom token request failed: {resp.status_code} - {resp.text}")

 
    data = resp.json()
    access_token = data.get("access_token")
    expires_in = data.get("expires_in", 3600)


    _TOKEN["value"] = access_token
    _TOKEN["exp"] = time.time() + expires_in - 10  # refresh 10 sec early

    print("Zoom token fetched successfully!")
    return access_token


