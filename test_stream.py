import requests
import json

url = "http://localhost:8000/chat/stream"
payload = {
    "messages": [
        {"role": "user", "content": "what is sunlight?"}
    ]
}

print(f"Sending request to {url}...")

try:
    # Set stream=True to handle the StreamingResponse
    with requests.post(url, json=payload, stream=True) as response:
        response.raise_for_status()
        with open("result.txt", "w", encoding="utf-8") as f:
            f.write("Status: " + str(response.status_code) + "\n")
            f.write("--- Start of Stream ---\n")
            print("--- Start of Stream ---")
            for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                if chunk:
                    print(chunk, end='', flush=True)
                    f.write(chunk)
            print("\n--- End of Stream ---")
            f.write("\n--- End of Stream ---")

except Exception as e:
    with open("result.txt", "w") as f:
        f.write(f"Error: {e}")
    print(f"Error: {e}")
