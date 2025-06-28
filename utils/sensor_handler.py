import time
from datetime import datetime
from utils.database import DatabaseConnection
from modules.alerts import AlertSystem

class SensorHandler:
    def __init__(self, db: DatabaseConnection, alert_system: AlertSystem):
        self.db = db
        self.alert_system = alert_system
        self.running = False

    def start_monitoring(self):
        self.running = True
        while self.running:
            self.process_sensor_data()
            time.sleep(5)  # 5-second interval

    def process_sensor_data(self):
        try:
            # Simulate sensor reading for now
            # Replace with actual sensor reading code
            reading = self.read_sensor()
            if reading:
                self.db.process_sensor_reading(
                    raw_weight=reading['raw_weight'],
                    average_weight=reading['average_weight'],
                    timestamp=datetime.now()
                )
                self.alert_system.check_weight_alerts(reading['average_weight'])
        except Exception as e:
            print(f"Error processing sensor data: {e}")

    def read_sensor(self):
        # Placeholder for actual sensor reading code
        # Replace with your sensor implementation
        return {
            'raw_weight': 0.0,
            'average_weight': 0.0,
            'timestamp': datetime.now()
        }

    def stop_monitoring(self):
        self.running = False
