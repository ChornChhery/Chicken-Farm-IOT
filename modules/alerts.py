import requests
import os
from dotenv import load_dotenv
from utils.database import DatabaseConnection

load_dotenv()

class AlertSystem:
    def __init__(self):
        self.line_token = os.getenv('LINE_NOTIFY_TOKEN')
        self.threshold_alerts = {}
        self.db = DatabaseConnection()

    def send_line_notification(self, message):
        url = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': f'Bearer {self.line_token}'}
        data = {'message': message}
        response = requests.post(url, headers=headers, data=data)
        return response.status_code == 200

    def check_weight_threshold(self, device_id, weight, threshold):
        if weight > threshold:
            if device_id not in self.threshold_alerts:
                self.threshold_alerts[device_id] = True
                self.send_line_notification(
                    f"⚠️ Alert: Device {device_id} weight ({weight:.2f}kg) "
                    f"exceeded threshold ({threshold}kg)"
                )

    def check_weight_alerts(self, weight, standard_weight):
        alerts = []
        if weight < standard_weight * 0.9:
            alerts.append("Weight below normal range")
            self.send_line_notification(f"⚠️ Alert: Weight ({weight:.2f}kg) below normal range")
        elif weight > standard_weight * 1.1:
            alerts.append("Weight above normal range")
            self.send_line_notification(f"⚠️ Alert: Weight ({weight:.2f}kg) above normal range")
        return alerts

    def process_alerts(self, reading):
        alerts = []
        if reading['raw_weight'] < -10:
            alerts.append("Invalid low reading detected")
            self.send_line_notification("⚠️ Alert: Invalid low reading detected")
        elif reading['raw_weight'] > 5000:
            alerts.append("Invalid high reading detected")
            self.send_line_notification("⚠️ Alert: Invalid high reading detected")
        return alerts
