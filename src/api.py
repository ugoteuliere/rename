import sys
import json
import requests
import urllib.parse
from google import genai
from config import TMDB_API_KEY,GEMINI_API_KEY
from src.mail import send_email
from src.ui import print_log

def api_call(name, year, language, media_type):
    api_key = TMDB_API_KEY
    encoded_query = urllib.parse.quote(name)
    
    # build url
    url = f"https://api.themoviedb.org/3/search/{media_type}?query={encoded_query}&language={language}"
    if year:
        url += f"&year={year}"
        
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # call api
    try :
        response = requests.get(url, headers=headers)
    except Exception as e:
        print_log(f" ❌ API call failed \n\n # Error : {e} \n\n # Query : {name} {year}\n")
        sys.exit(1)
    
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        
        if results:
            best_match = results[0]
            if media_type == "movie" :
                tmdb_title = best_match.get('title', 'unknown')
            elif media_type == "tv" : 
                tmdb_title = best_match.get('name', 'unknown')
            release_date = best_match.get('release_date', 'unknown')
            tmdb_year = release_date[:4] if release_date else 'unknown'
            original_language = best_match.get('original_language', 'unknown')
            
            return [True, tmdb_title, tmdb_year, original_language]
        else:
            print_log(" ❌ API call failed : impossible to read the json data from TMBD API\n")
    else :
        print_log(f" ❌ API call failed \n\n # Code : {response.status_code} \n\n # Query : {name} {year}\n")
    
    return [False, None, None, None]

def gemini_api_call(media_info):
    prompt = f"""You are an expert media parsing assistant. Your task is to analyze the metadata of a media file where the standard regex cleaning function failed, and extract the correct Movie or TV Show information.

    Here is the file information:
    - File name: {media_info['File']}
    - Folder name: {media_info['Folder']}
    - Path of the file: {media_info['Path']}
    - Output of clean function: {media_info['Clean']}
    - Output of parsing function: {media_info['Parse']}
    - Media type: {media_info['Media']}

    Instructions:
    1. Identify the official name of the movie or TV show. CRITICAL: If the media is originally a French production (made in France/French language), you MUST provide its official French title. For all other productions, provide the standard international/English title.
    2. Identify the release year.
    3. Identify the original language of the production using standard 2-letter language codes (e.g., "fr" for French, "en" for English, "es" for Spanish).
    4. My cleaning function uses a list of common torrent tags (like 1080p, vo, vfi, bluray, x264, etc.). If the output of my cleaning function is cluttered with leftover tags that aren't part of the actual title, list this leftover tags (only the one in the cleaning function output) in the `missing_tags` array. 
    5. Set "success" to 1 if you confidently found the title, or 0 if you could not determine it.
    6. If you cannot determine the name, year, language, or missing tags, return `null` for those specific values.

    Respond STRICTLY with a valid JSON object matching the exact schema below. Do not include markdown formatting, code blocks, or any conversational text.

    {{
      "success": 1,
      "name": "string",
      "year": "string",
      "original_language": "string",
      "missing_tags": ["string", "string"]
    }}"""
    
    # call api
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_mime_type="application/json", 
            ),
        )
    except Exception as e:
        print_log(f" ❌ GEMINI API call failed \n\n # Error : {e} \n\n")
        raise e

    try:
        data = json.loads(response.text)
        
        if data.get("success") == 1:
            title = data.get('name')
            year = data.get('year')
            original_language = data.get('original_language', 'en')
            
            missing_tags = data.get('missing_tags') or []
            
            if missing_tags:
                #add_new_tags(missing_tags) # On appelle la nouvelle fonction
                message = f"Gemini API was called to rename the media file: {title}.\n    The following tag(s) was(were) added: {missing_tags}."
                send_email(message)
                print_log(f" ⚠️  Found new missing tags: {missing_tags}")

            print_log([title, year, original_language, missing_tags])
                
            return [True, title, year, original_language, missing_tags]
        else:
            print_log(" ❌ Gemini API call failed : impossible to read the json data from Gemini API\n")
            
    except json.JSONDecodeError:
        print_log(" ❌ Failed to parse Gemini response as JSON")
        
    return [False, None, None, None, None]