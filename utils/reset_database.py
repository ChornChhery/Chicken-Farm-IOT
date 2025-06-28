from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

def reset_database():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client.chicken_farm
    
    db.weights.delete_many({})
    
    daily_weights = {
        1: 0.040, 2: 0.055, 3: 0.070, 4: 0.085, 5: 0.100,
        6: 0.125, 7: 0.150, 8: 0.180, 9: 0.210, 10: 0.240,
        11: 0.270, 12: 0.310, 13: 0.350, 14: 0.400, 15: 0.450,
        16: 0.500, 17: 0.550, 18: 0.610, 19: 0.670, 20: 0.730,
        21: 0.800, 22: 0.870, 23: 0.940, 24: 1.010, 25: 1.080,
        26: 1.160, 27: 1.230, 28: 1.300, 29: 1.380, 30: 1.460,
        31: 1.540, 32: 1.620, 33: 1.680, 34: 1.740, 35: 1.800,
        36: 1.880, 37: 1.960, 38: 2.040, 39: 2.120, 40: 2.180,
        41: 2.240, 42: 2.300, 43: 2.350, 44: 2.400, 45: 2.450,
        46: 2.500, 47: 2.530, 48: 2.560, 49: 2.600, 50: 2.640,
        51: 2.680, 52: 2.720, 53: 2.740, 54: 2.760, 55: 2.780,
        56: 2.800, 57: 2.820
    }
    
    start_date = datetime.now() - timedelta(days=56)
    
    for day in range(1, 58):
        data = {
            'day': day,
            'weight': daily_weights[day],
            'timestamp': start_date + timedelta(days=day-1)
        }
        db.weights.insert_one(data)
    
    print("Database populated with weight tracking data!")
    print("\nKey growth milestones (kg):")
    for day in [1, 7, 14, 21, 28, 35, 42, 49, 56]:
        print(f"Day {day}: {daily_weights[day]:.3f}")

if __name__ == "__main__":
    reset_database()
