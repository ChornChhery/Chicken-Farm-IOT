import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_line_notify():
    token = os.getenv('LINE_NOTIFY_TOKEN')
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {token}'}
    data = {'message': '🐔 Test notification from Chicken Farm Monitor\nSystem is running successfully!'}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print("Line Notify Test: Success!")
            print("Check your Line app for the test message")
        else:
            print(f"Line Notify Test: Failed (Status Code: {response.status_code})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_line_notify()
