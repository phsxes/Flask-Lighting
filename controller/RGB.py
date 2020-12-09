
import time
import board
import neopixel
from datetime import datetime
import paho.mqtt.client as mqtt
import threading


# Initial variables
ORDER = neopixel.GRB
num_pixels = 15
pixels = neopixel.NeoPixel(board.D18, num_pixels)
type = "static"
current_static = (255,255,255)


# Thread running the visual effects continously while the other code executes
def effects():
    global type
    global current_static
    t = threading.currentThread()
    while getattr(t, "do_run", True):
        if type == "static":
            pass
        elif type == "rainbow":
            rainbow_cycle(0.001)
        elif type == "pulse":
            colorWipe(current_static)
        elif type == "cylon":
            theaterChase(current_static)

t = threading.Thread(target=effects, args=())
t.start()


####### THEATER CHASE ########

def theaterChase(color, wait_ms=150, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, num_pixels, 3):
                if type != "cylon":
                    return
                pixels[i+q] = color
            pixels.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, num_pixels, 3):
                if type != "cylon":
                    return
                pixels[i+q] = (0,0,0)

##############################


######## COLOR WIPE  #########

def colorWipe(color, wait_ms=75):
    "Wipe color across display a pixel at a time."
    for i in range(num_pixels):
        if type != "pulse":
            return
        pixels[i] = color
        time.sleep(wait_ms/1000.0)
    for i in range(num_pixels):
        if type != "pulse":
            return
        pixels[i] = (0,0,0)
        time.sleep(wait_ms/1000.0)

##############################


######  RAINBOW EFFECTS ######


def wheel(pos):
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def rainbow_cycle(wait):
    global type
    for j in range(255):
        for i in range(num_pixels):
            if type != "rainbow":
                return
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)

##############################


def on_connect(client, userdata, flags, rc):
    print("Connected with code: " + str(rc))
    client.subscribe("light/color")
    client.subscribe("light/effects")


def on_message(client, userdata, msg):

    if msg.topic == "light/color":
        global type
        global current_static
        type = "static"
        color = msg.payload.decode("utf-8")
        print(color)
        print("trying to decode color..")
        try:
            c = color.split(',')
            RGB = list(map(int, c[:-1]))
            current_static = tuple(RGB)
            br = float(c[-1])
            pixels.fill((RGB[0],RGB[1],RGB[2]))
            pixels.brightness = br
            print("brightness set to: " + str(br))
            pixels.show()
            print("Color changed: " + str(c))
        except Exception as e:
            print("Couldn't change color, bad format: " + str(e))
    else:
        global type
        type = msg.payload.decode("utf-8")
        pass


# Main configuration
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("", 1883, 60)
client.username_pw_set("", "")
pixels.fill((0,0,0))
pixels.show()
client.loop_start()

# Infinite loop (reporting state and publishing to topic)
while True:
    report = datetime.now()
    dt_string = report.strftime("%d/%m/%Y %H:%M:%S")
    client.publish("light/status", dt_string)
    print("sent status: " + dt_string)
    time.sleep(60)
