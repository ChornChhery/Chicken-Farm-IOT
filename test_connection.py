from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

def test_mongodb_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client.chicken_farm
    
    try:
        client.admin.command('ping')
        print("MongoDB Connection: Success!")
        
        test_data = {
            "device_id": "test_device_001",
            "weight": 2.5,
            "timestamp": datetime.now(),
            "temperature": 25.0,
            "humidity": 65.0,
            "batch_id": "batch_001"
        }
        
        result = db.weights.insert_one(test_data)
        print(f"Test data inserted with ID: {result.inserted_id}")
        
        retrieved_data = db.weights.find_one({"device_id": "test_device_001"})
        print(f"Retrieved test data: {retrieved_data}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_mongodb_connection()
