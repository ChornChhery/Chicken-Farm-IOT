from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

def insert_test_data():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client.chicken_farm
    
    # Read the Excel file with your exact columns
    df = pd.read_excel('sensor_readings.xlsx')
    data_to_insert = []
    base_date = datetime(2025, 2, 8)
    
    # Process each day's 10 readings
    for day in range(57):  # Days 0 to 56
        day_data = df[df['Day'] == day]
        
        # Process each reading within the day
        for idx, row in day_data.iterrows():
            # Space readings every 2.4 hours (24 hours / 10 readings)
            hour_spacing = (idx % 10) * 2.4
            timestamp = base_date + timedelta(days=day, hours=hour_spacing)
            
            document = {
                'device_id': 'sensor_001',
                'timestamp': timestamp,
                'raw_weight': float(row['Sensor_Weight']),
                'batch_id': 'batch_2025_02',
                'day': day
            }
            data_to_insert.append(document)
    
    # Clear and insert new data
    db.sensor_readings.delete_many({})
    result = db.sensor_readings.insert_many(data_to_insert)
    print(f"Successfully inserted {len(result.inserted_ids)} sensor readings")

if __name__ == "__main__":
    insert_test_data()
