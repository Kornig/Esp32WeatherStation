from machine import Pin
from machine import SoftI2C as I2C
from time import sleep
import bme280
import urequests as requests
import ntptime
from datetime import datetime
import network
import urequests

DEBUG = True


def wifi_connect(ssid, passwd):
    #uruchomienie interfejsu wifi w trybie statcji roboczej
    wifi = network.WLAN(network.STA_IF)
    #aktywacja interfejsu
    wifi.active(True)
    
    #podlaczenie sie do wifi
    wifi.connect(ssid,passwd)
    
    #active resting do momentu podlaczenia do sieci
    while !wifi.isconnected()
        pass
    
    print("Podlaczono do WIFI!")
    conf = wifi.ifconfig()
    print("IP: " + conf[0])
    print("MASK: " = conf[1])
    print("=========================\n")
    
    return wifi



#konfiguracja I2C
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)

#serwer do którego esp32 bedzie wysylac dane
WEB_URL = "http://192.168.3.141:5000/api/measurement"

#czas w sekundach od 1970-01-01 do 2000-01-01 (micropython zapisuje czas w sekundach od 2000-01-01)
#potrzebny do konwersji czasu odczytania danych
UNIX_TIME_OFFSET = 946684800

#podlaczenie do WIFI
wifi = wifi_connect("WIN10", "gulion1gulion2")
#synchronizacja czasu z internetem (czas UTC)
ntptime.settime()


#glowna petla
while True:
    #odczytanie danych z sensora
    sensor = bme280.BME280(i2c=i2c)
    temp = sensor.read_temperature() / 100
    hum = sensor.read_humidity() / 1024
    pres = sensor.read_pressure() / 256000

    if DEBUG:
        print('Temperature: ', temp)
        print('Humidity: ', hum)
        print('Pressure: ', pres)
    
    dataDict = {
        "UNIXtime": UNIX_TIME_OFFSET + time.time(),
        "Humidity": round(hum, 2),
        "Pressure": round(pres, 2),
        "Temperature": round(temp, 2)
    }

    headers = {
        "Content-type": "application/json"
    }

    response = requests.post(URL, json=dataDict, headers=headers)

    if DEBUG:
        if response.status_code == 201:
            print("SENDING SUCCRESSFUL!")
            print(response.json())
        else:
            print("SENDING UNSUCCRESSFUL")
            print("STATUS CODE: " + response.status_code())
        print("=========================\n")

    response.close()

    sleep(60)

    