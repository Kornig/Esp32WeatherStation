from machine import Pin
from time import sleep
from machine import Pin, SoftI2C as I2C, deepsleep, reset_cause, DEEPSLEEP_RESET
import esp32
import time
import bme280
import urequests as requests
import ntptime
import network


DEBUG = True
SSID = ""
PASSWD = ""

#serwer do którego esp32 bedzie wysylac dane
SERV_URL = "http://192.168.3.141:5000/api/measurement"

#czas w sekundach od 1970-01-01 do 2000-01-01 (micropython zapisuje czas w sekundach od 2000-01-01)
#potrzebny do konwersji czasu odczytania danych
UNIX_TIME_OFFSET = 946684800

#czas przez ktory urzadzenie ma spac (byc w DEEP SLEEP, radykalnie obniza zuzycie energii)
#3min
DEEP_SLEEP_INTERVAL = (3 * 60 * 1000)

#konfiguracja I2C
i2c = I2C(scl=Pin(22), sda=Pin(21), freq=10000)

#pin do wybudzenia z deepsleep i zatrzymaania programu
guard_pin = Pin(4, Pin.IN, Pin.PULL_UP)

if guard_pin.value() == 1:
    if DEBUG:
        print("\nLEAVING")
    raise KeyboardInterrupt
    
#gdy guard_pin zmieni sie w stan wysoki (odlaczenie go od masy, rezystor pull-up)
#to wykonaj funkcje leaver (jesli nastapi to podczas deepsleep, to mikrokontroler
#zostanie wybudzony)
esp32.wake_on_ext0(pin=guard_pin, level=esp32.WAKEUP_ANY_HIGH)

