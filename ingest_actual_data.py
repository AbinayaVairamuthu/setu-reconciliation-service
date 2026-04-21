import json
import requests
import time

# The URL where your FastAPI is running
API_URL = "http://127.0.0.1:8000/events"

def upload_data():
    try:
        with open('sample_events.json', 'r') as f:
            events = json.load(f)
    except FileNotFoundError:
        print("Error: sample_events.json not found in this folder!")
        return

    print(f"🚀 Starting ingestion of {len(events)} events...")
    
    start_time = time.time()
    success_count = 0
    
    for i, event in enumerate(events):
        try:
            # Sending the data to your local API
            response = requests.post(API_URL, json=event)
            if response.status_code == 200:
                success_count += 1
            
            # Progress update every 1000 records
            if (i + 1) % 1000 == 0:
                print(f"✅ Processed {i + 1} events...")
        except Exception as e:
            print(f"❌ Error at event {i}: {e}")

    end_time = time.time()
    print(f"\n--- Ingestion Complete ---")
    print(f"Total time: {round(end_time - start_time, 2)} seconds")
    print(f"Successfully processed: {success_count} events")

if __name__ == "__main__":
    upload_data()