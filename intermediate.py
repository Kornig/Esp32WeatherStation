import requests
import time

while True:
    response = requests.get("https://esp32weatherstation.onrender.com", timeout=(30, 120))
    print(response.text)
    time.sleep(3560)
