# Flask Lighting

A web application using Flask to control lighting from a room using MQTT to a microcontroller.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
$ pip install -r requirements.txt
$ flask run
```

## Important Notes
This is just a sample project, to use it accordingly, you will need a MQTT broker and a microcontroller with Wi-Fi capabilities and support for the light controller used: the WS2812B. Micontrollers with support for MicroPython can be used, an example of this is the ESP8266. A Raspberry Pi can also be used as a controller.
