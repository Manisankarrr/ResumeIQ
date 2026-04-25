import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import time
import requests
from config import settings

def extract_skills(text: str) -> list[str]:
    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "Resume Screener"
    }
    
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {
                "role": "system", 
                "content": 'You are a technical skill extractor. Return ONLY a valid JSON array of strings. No explanation, no markdown, no backticks. Extract hard skills, tools, frameworks, certifications only. Max 30 items. Example: ["Python","Docker","AWS"]'
            },
            {"role": "user", "content": text}
        ],
        "temperature": 0.0
    }
    
    def _make_request():
        return requests.post(url, headers=headers, json=payload, timeout=30)
        
    try:
        response = _make_request()
        
        if response.status_code == 429:
            print("Rate limit hit - waiting 60s")
            time.sleep(60)
            response = _make_request()
            response.raise_for_status()
            
        elif response.status_code != 200:
            print(f"HTTP {response.status_code} Error: {response.text}")
            response.raise_for_status()
            
    except requests.exceptions.ConnectionError:
        print("Cannot reach OpenRouter - check internet")
        return []
    except requests.exceptions.Timeout:
        print("Request timed out")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected Error during API request: {str(e)}")
        return []

    try:
        data = response.json()
        content = data['choices'][0]['message']['content'].strip()
        
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
            
        if content.endswith("```"):
            content = content[:-3]
            
        content = content.strip()
        
        parsed = json.loads(content)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
        return []
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}\nContent was: {content}")
        return []
    except Exception as e:
        print(f"Unexpected formatting Error: {str(e)}")
        return []

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    test_response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": os.getenv("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
            "messages": [{"role": "user", "content": "say hello"}],
            "max_tokens": 10
        },
        timeout=30
    )
    print("Status:", test_response.status_code)
    print("Response:", test_response.text)

# Calls the OpenRouter LLM API to extract technical skills from text as a JSON array, with rate-limit retry and markdown stripping. Includes a standalone connectivity test when run directly.
