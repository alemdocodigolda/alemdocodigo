import requests
import json
import time

def test_api():
    url = "http://localhost:8081/api/analyze"
    payload = {"url": "https://www.creditoaqui.pt"}
    headers = {"Content-Type": "application/json"}

    print("Sending request to API...")
    start = time.time()
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Time taken: {time.time() - start:.2f}s")
        
        if response.status_code == 200:
            data = response.json()
            print("Success!")
            print(f"Score: {data['score']}")
            print(f"Status: {data['status']}")
            print(f"Issues: {len(data['issues'])}")
        else:
            print("Failed!")
            print(response.text)
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_api()
