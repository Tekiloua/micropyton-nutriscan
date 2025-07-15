from machine import Pin
from hx711 import HX711
import _thread
import urequests as requests
import time
import ujson
import network

#Configuration des broches
dout_pin = 22  # GPIO 4
sck_pin = 23   # GPIO 5

hx = HX711(dout_pin, sck_pin)
print("Activation du balance en cours...")
hx.tare()  # Mise à zéro (sans poids)
hx.set_scale(120.0)  # À ajuster selon l'étalonnage
print("Balance activé")


sta_if = network.WLAN(network.STA_IF)
led = Pin(2, Pin.OUT)
led_poids = Pin(21, Pin.OUT)
led_aliment = Pin(19, Pin.OUT)

led_poids.value(0)
led_aliment.value(1)

button1 = Pin(15, Pin.IN, Pin.PULL_UP)
button2 = Pin(4, Pin.IN, Pin.PULL_UP)
button3 = Pin(5, Pin.IN, Pin.PULL_UP)
button4 = Pin(18, Pin.IN, Pin.PULL_UP)

WIFI_NAME = "nutriscan"
WIFI_PASSWORD = "********"

def connexion() :
    sta_if.active(True)
    time.sleep(0.2)
    while not sta_if.isconnected() :
        try:
            sta_if.connect(WIFI_NAME, WIFI_PASSWORD)
        except:
            print("Erreur de connexion !")
            led.value(1)
            time.sleep(0.3)
            led.value(0)
            time.sleep(0.3)

post_dataSalade = ujson.dumps({ "nom": "Salade","categorie":"Legume","fraicheur":90 ,"glucide":5 ,"protide":7, "eau":2, "vitamine_A":4, "vitamine_B":3, "vitamine_C":1})
post_dataCarotte = ujson.dumps({ "nom": "Carotte","categorie":"Legume","fraicheur":78 ,"glucide":20 ,"protide":31, "eau":15, "vitamine_A":32, "vitamine_B":6, "vitamine_C":42})
post_dataBanane = ujson.dumps({ "nom": "Banane","categorie":"Fruit","fraicheur":40 ,"glucide":12 ,"protide":16, "eau":6, "vitamine_A":3, "vitamine_B":13, "vitamine_C":19})
post_dataPomme = ujson.dumps({ "nom": "Pomme","categorie":"Fruit","fraicheur":51 ,"glucide":8 ,"protide":11, "eau":3, "vitamine_A":5, "vitamine_B":13, "vitamine_C":19})

request_url_insert_poids = "http://10.42.0.1:3001/poids"
request_url_insert_aliment = "http://10.42.0.1:3001/aliment"
request_url_insert_canweigh = "http://10.42.0.1:3001/can-weigh" # also url for GET request

connexion()
isPressedCount1 = False
isPressedCount2 = False
isPressedCount3 = False
isPressedCount4 = False
canWeigh = False
poids = hx.get_weight(3)

def fetch_canweigh():
    global canWeigh, poids
    while True:
        try:
            res = requests.get(url=request_url_insert_canweigh)
            time.sleep(2.5)
            print(res.text)
            if res.json()["data"]["valeur"]==1:
                canWeigh = True
            else :
                canWeigh = False
        except:
            print("canweigh non recupérer ",canWeigh)
        if canWeigh :
            # Envoi du poids vers la bdd
            try:
                res = requests.post(request_url_insert_poids, headers = {'content-type': 'application/json'}, data = ujson.dumps({"valeur":poids}))
                print(res.text)
                time.sleep(1)
                res = requests.post(request_url_insert_canweigh, headers = {'content-type': 'application/json'}, data = ujson.dumps({"valeur":0}))
                print(res.text)
                led_poids.value(0)
            except :
                print("Erreur d'envoie poids ! , ",poids)
                canWeigh = False
                led_poids.value(0)

def afficher_poids():
    global poids
    while True:
        poids = hx.get_weight(5)  # Lire le poids moyen sur 5 mesures
        print("Poids: {:.2f} g".format(poids))
        time.sleep(1)

_thread.start_new_thread(fetch_canweigh, ())
#_thread.start_new_thread(afficher_poids, ())

while True :
    poids = hx.get_weight(3)  # Lire le poids moyen sur 5 mesures
    print("Poids: {:.2f} g".format(poids))
    #time.sleep(0.2)
    
    '''try:
        res = requests.get(url=request_url_insert_canweigh)
        time.sleep(0.5)
        print(res.text)
        if res.json()["data"]["valeur"]==1:
            canWeigh = True
        else :
            canWeigh = False
    except:
        print("canweigh non recupérer ",canWeigh)
        time.sleep(0.2)
    if canWeigh :
        led_poids.value(1)
        time.sleep(0.2)
        # Envoi du poids vers la bdd
        try:
            res = requests.post(request_url_insert_poids, headers = {'content-type': 'application/json'}, data = ujson.dumps({"valeur":poids}))
            print(res.text)
            time.sleep(0.8)
            res = requests.post(request_url_insert_canweigh, headers = {'content-type': 'application/json'}, data = ujson.dumps({"valeur":0}))
            print(res.text)
            led_poids.value(0)
        except :
            print("Erreur d'envoie poids ! , ",poids)
            canWeigh = False
            led_poids.value(0)
        time.sleep(0.5)

    '''
    if not button1.value():
        isPressedCount1 = True # si on clique le boutton (0 si on clique)
    if not button2.value():
        isPressedCount2 = True # si on clique le boutton (0 si on clique)
    if not button3.value():
        isPressedCount3 = True # si on clique le boutton (0 si on clique)
    if not button4.value():
        isPressedCount4 = True # si on clique le boutton (0 si on clique)
    
    if isPressedCount1 :    
        try:
            print("salade")
            res = requests.post(request_url_insert_aliment, headers = {'content-type': 'application/json'}, data = post_dataSalade)
            print(res.text)
            led_poids.value(1)
            time.sleep(1)
            res = requests.post(request_url_insert_canweigh, headers = {'content-type': 'application/json'}, data = ujson.dumps({"valeur":1}))
            print(res.text)
            isPressedCount1 = False
            led_poids.value(0)
        except :
            print("Erreur d'envoie Salade ! , ",isPressedCount1)
            isPressedCount1 = False
            #connexion()
        time.sleep(0.3)
        
    if isPressedCount2 :    
        try:
            res = requests.post(request_url_insert_aliment, headers = {'content-type': 'application/json'}, data = post_dataCarotte)
            print(res.text)
            led_poids.value(1)
            time.sleep(1)
            res = requests.post(request_url_insert_canweigh, headers = {'content-type': 'application/json'}, data = ujson.dumps({"valeur":1}))
            print(res.text)
            isPressedCount2 = False
            led_poids.value(0)
        except :
            print("Erreur d'envoie Carotte ! , ",isPressedCount2)
            isPressedCount2 = False
            #connexion()
        time.sleep(0.5)
        
    if isPressedCount3 :    
        try:
            res = requests.post(request_url_insert_aliment, headers = {'content-type': 'application/json'}, data = post_dataBanane)
            print(res.text)
            led_poids.value(1)
            time.sleep(1)
            res = requests.post(request_url_insert_canweigh, headers = {'content-type': 'application/json'}, data = ujson.dumps({"valeur":1}))
            print(res.text)
            isPressedCount3 = False
            led_poids.value(0)
        except :
            print("Erreur d'envoie banane ! , ",isPressedCount3)
            isPressedCount3 = False
            #connexion()
        time.sleep(0.5)
        
    if isPressedCount4 :    
        try:
            res = requests.post(request_url_insert_aliment, headers = {'content-type': 'application/json'}, data = post_dataPomme)
            print(res.text)
            led_poids.value(1)
            time.sleep(1)
            res = requests.post(request_url_insert_canweigh, headers = {'content-type': 'application/json'}, data = ujson.dumps({"valeur":1}))
            print(res.text)
            isPressedCount4 = False
            led_poids.value(0)
        except :
            print("Erreur d'envoie banane ! , ",isPressedCount3)
            isPressedCount4 = False
            #connexion()
        time.sleep(0.5)
        
