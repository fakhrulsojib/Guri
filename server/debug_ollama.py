import requests
import sys

try:
    print("Testing connection to http://ollama:11434/...")
    r = requests.get('http://ollama:11434/', timeout=5)
    print(f"Status Code: {r.status_code}")
    print("Response Headers:", r.headers)
    if r.status_code == 200:
        print("SUCCESS: Connection established.")
        sys.exit(0)
    else:
        print("FAILURE: Connection established but returned non-200.")
        sys.exit(1)
except Exception as e:
    print(f"EXCEPTION: {e}")
    sys.exit(1)
