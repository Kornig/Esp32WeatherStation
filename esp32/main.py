
def wifi_connect(ssid, passwd, time_out = 10000):
    #uruchomienie interfejsu wifi w trybie statcji roboczej
    wifi = network.WLAN(network.STA_IF)
    #aktywacja interfejsu
    act = wifi.active(True)
    
    if DEBUG and act:
        print("\nWIFI ACTIVATED!")
    
    wifi.connect(ssid, passwd)
    
    #sprawdzanie czy uzyskano połączenie przez określony time_out
    start_time = time.ticks_ms()
    while not wifi.isconnected():
        #sprawdzam czy nie przekroczono time_out
        if (time.ticks_ms() - start_time) > time_out:
            wifi.disconnect()
            wifi.active(False)
            return None
            
        #odczekuje 200ms do ponownego sprawdzenia
        time.sleep(0.2)
    
    if DEBUG:
        print("SUCCESSFULLY CONNECTED TO: " + ssid)
    
    conf = wifi.ifconfig()
    
    if DEBUG:
        print("IP: " + conf[0])
        print("MASK: " + conf[1])
        print("=========================\n")

    return wifi



#podlaczenie do WIFI
wifi = wifi_connect(SSID, PASSWD)

#jesli sie nie udalo podlaczyc do wifi, odrazu przechodze w deep_sleep
if wifi == None:
    if DEBUG:
        print("\nFAILED TO CONNECT TO WIFI!")
        print("TRASITION INTO DEELSLEEP")
        print("=========================\n")
    deepsleep(DEEP_SLEEP_INTERVAL)
    
#synchronizacja czasu z internetem (czas UTC)
ntptime.settime()

#glowna czesc programu, nie kozysta z petli poniewaz wykorzystuje deepsleep
#while True:
#odczytanie danych z sensora
sensor = bme280.BME280(i2c=i2c)
temp = sensor.read_temperature() / 100 #dane w setnych czesciach celsjusza
hum = sensor.read_humidity() / 1024 #dane w wartosciahc 0-1024, konwersja na %
pres = sensor.read_pressure() / 25600 #kownwersja na hPa

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

#wyslanie danych do serwera REST
try:
    
    response = requests.post(SERV_URL, json=dataDict, headers=headers)

    if DEBUG:
        if response.status_code == 201:
            print("SENDING SUCCESSFUL!")
            print(response.json())
        else:
            print("SENDING UNSUCCESSFUL")
            print("STATUS CODE: " + response.status_code())
        print("=========================\n")

    response.close()
except:
    if DEBUG:
        print("EXCEPTION DURING REQUEST TO SERVER!")
        print("=========================\n")

#zamkniecie poloczenia wifi
wifi.disconnect()

#wylaczenie interfejsu
wifi.active(False)


if DEBUG:
    print("TRASITION INTO DEELSLEEP")
    print("=========================\n")

#przejscie w deep sleep mode na czas równy ustalonemu interwalowi
#z odjeciem bufora przeciwdzialajacemu zbyt szybkiemu zdesynchornizowaniu programu
deepsleep(DEEP_SLEEP_INTERVAL - 400)
    
    
