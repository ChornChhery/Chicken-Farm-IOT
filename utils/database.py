from pymongo import MongoClient, ASCENDING, DESCENDING
import os
from dotenv import load_dotenv
from datetime import datetime
from modules.data_generator import get_standard_weight

load_dotenv()

class DatabaseConnection:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.client = MongoClient(os.getenv('MONGODB_URI'))
            cls._instance.db = cls._instance.client.chicken_farm
            cls._instance.collection = cls._instance.db.sensor_readings
            
            # Create indexes for better performance
            cls._instance.collection.create_index([('timestamp', DESCENDING)])
            cls._instance.collection.create_index([('device_id', ASCENDING)])
            cls._instance.collection.create_index([('batch_id', ASCENDING)])
        
        return cls._instance

    def get_valid_readings(self):
        """Get only valid chicken weight readings"""
        all_readings = list(self.collection.find().sort('timestamp', -1))
        valid_readings = []
        
        birth_date = datetime(2025, 2, 8)  # Day 0 - chicken birth date
        
        for reading in all_readings:
            current_day = (reading['timestamp'] - birth_date).days
            std_weight = get_standard_weight(current_day)
            raw_weight = reading['raw_weight']
            
            # Skip invalid readings
            if any([
                raw_weight < 0,  # Negative values
                raw_weight < 5,  # Too small values
                raw_weight > (std_weight * 1.5),  # Too large values
                current_day == 0 and not (35 <= raw_weight <= 45)  # Day 0 weight range
            ]):
                continue
                
            valid_readings.append(reading)
        
        return valid_readings

    def get_all_readings(self):
        """Get all readings from database (including raw data)"""
        return list(self.collection.find().sort('timestamp', -1))

    def get_daily_stats(self, date):
        """Get daily statistics for valid readings"""
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        valid_readings = self.get_valid_readings()
        day_readings = [r for r in valid_readings 
                       if start_of_day <= r['timestamp'] <= end_of_day]
        
        if day_readings:
            weights = [r['raw_weight'] for r in day_readings]
            return {
                'date': date,
                'average_weight': sum(weights) / len(weights),
                'min_weight': min(weights),
                'max_weight': max(weights),
                'reading_count': len(weights)
            }
        return None

    def process_sensor_reading(self, raw_weight, timestamp):
        """Store new sensor reading in database"""
        birth_date = datetime(2025, 2, 8)
        current_day = (timestamp - birth_date).days
        std_weight = get_standard_weight(current_day)
        
        data = {
            'timestamp': timestamp,
            'raw_weight': raw_weight,
            'device_id': 'sensor_001',
            'batch_id': 'batch_2025_02',
            'day': current_day
        }
        
        self.collection.insert_one(data)

    def get_readings_by_timerange(self, start_date, end_date):
        """Get valid readings within a time range"""
        valid_readings = self.get_valid_readings()
        return [r for r in valid_readings 
                if start_date <= r['timestamp'] <= end_date]

    def get_latest_valid_reading(self):
        """Get the most recent valid reading"""
        valid_readings = self.get_valid_readings()
        return valid_readings[0] if valid_readings else None
