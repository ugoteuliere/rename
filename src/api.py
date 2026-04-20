import sys
import json
import requests
import urllib.parse
from google import genai
from src.mail import send_email
from src.ui import print_log, print_error
from data.data import TAGS

import config
TMDB_API_KEY = getattr(config, 'TMDB_API_KEY', None)
GEMINI_API_KEY = getattr(config, 'GEMINI_API_KEY', None)

def api_call(name, year, language, media_type):
    api_key = TMDB_API_KEY
    if api_key == None:
        print_log("❌ Missing configuration: \nThe global variable TMDB_API_KEY needs to be configured in a config.py file at the root of the script. Please refer to the following documentation: https://github.com/ugoteuliere/rename\n\n Stopping program.")
        sys.exit(1)
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
        raise RuntimeError(print_error(f" ❌ Error: TMDB API call failed \n Query : {name} {year}",e))
    
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
            print_log(f" ❌ API call failed : impossible to read the JSON data from TMDB API\n\n # Query : {name} {year}\n")
    else :
        print_log(f" ❌ API call failed \n\n # Code : {response.status_code} \n\n # Query : {name} {year}\n")
    
    return [False, None, None, None]

def gemini_api_call(media_info):
    prompt = f"""You are an elite Media Metadata Extraction API. Your task is to act as a fallback parser to analyze highly obfuscated media filenames when standard regex cleaning algorithms fail.

    CONTEXT:
    - Original File Name: "{media_info['File']}"
    - Folder Name: "{media_info['Folder']}"
    - Absolute Path: "{media_info['Path']}"
    - Clean Function Output (Failed): "{media_info['Clean']}"
    - Parse Function Output (Failed): "{media_info['Parse']}"
    - Media Type: "{media_info['Media']}"

    KNOWN TAGS DICTIONARY (Already handled by the algorithm):
    {TAGS}

    EXTRACTION RULES:
    1. Title Identification: Extract the exact, official name of the movie or TV show.
    - CRITICAL: If the media is originally a French production (made in France / French language), you MUST output its official French title. 
    - For all other productions, output the standard English/International title.
    2. Release Year: Extract the release year (4 digits).
    3. Original Language: Identify the original production language using standard ISO 639-1 2-letter codes (e.g., "fr" for French, "en" for English, "es" for Spanish).
    4. Tag Analysis (Missing Tags): Standard release tags include resolutions (1080p), codecs (x264, HEVC), languages (MULTI, VFF), and release groups (YTS, RARGB). Analyze the "Clean Function Output" for any residual tags that the algorithm failed to remove. 
    5. Tag Comparison: Compare any residual tags you found against the KNOWN TAGS DICTIONARY. If you identify valid torrent/release tags that caused the clean function to fail because they are missing from the known list, add them to the "missing_tags" array.

    OUTPUT FORMAT:
    Respond STRICTLY with a valid JSON object matching the exact schema below. Do not wrap the JSON in markdown blocks (e.g., ```json), do not include code blocks, and do not add any conversational text.

    {{
    "success": 1,
    "name": "string",
    "year": "string",
    "original_language": "string",
    "missing_tags": ["tag1", "tag2"]
    }}

    Note: 
    - Set "success" to 1 if you confidently found the title, otherwise set it to 0.
    - If you cannot determine the year, language, or missing_tags, use `null` for those fields.
    """
    
    if GEMINI_API_KEY == None:
        print_log("❌ Missing configuration: \nThe global variable GEMINI_API_KEY needs to be configured in a config.py file at the root of the script. Please refer to the following documentation: https://github.com/ugoteuliere/rename\n\n Stopping program.")
        sys.exit(1)
    
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
        raise RuntimeError(print_error(" ❌ Error: GEMINI API call failed",e))
    

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
            print_log(" ❌ Error: Impossible to read the json data from Gemini API \n")
            
    except json.JSONDecodeError as e:
        raise RuntimeError(print_error(" ❌ Error: Failed to parse Gemini response as JSON",e))
        
    return [False, None, None, None, None]