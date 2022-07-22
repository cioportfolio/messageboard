
import serial
import time
import math
import colorsys
import pygame
import sys
import argparse

pygame.init()

pScale = 50
pRad = int(pScale/2)
matrixWidth = 15
matrixHeight = 15
if sys.platform == 'win32':
    port = 'COM7'
    font = 'FreeSansBold.ttf'
else:
    port = '/dev/ttyACM0'
    font = '/project/FreeSansBold.ttf'
try:
    ser = serial.Serial(port, 115200, timeout=1)
    connected = True
    print("Connected to port ", port)
except:
    connected = False
    print("Could not connect to port ", port)
cycleTime = 23
myfont = pygame.font.Font(font, 13)
black = (0, 0, 0)
pygame.time.set_timer(pygame.USEREVENT, 20)
parser = argparse.ArgumentParser()
parser.add_argument('message', nargs='?',
                    help="Text to be sent", default="Hello World")
parser.add_argument("--hue", type=int,
                    help="Hue of the text colour", default=0)
parser.add_argument("-s", "--saturation", type=float,
                    help="Saturation of the text colour", default=0.0)
args = parser.parse_args()

def buildMessage(text, hue, sat):
    screen = pygame.display.set_mode(
        (matrixWidth * pScale, matrixHeight * pScale))
    col = (255, 0, 0)
    textsurface = myfont.render(text, True, col, (0, 0, 0)).convert_alpha()
    textWidth = textsurface.get_width()
    print(textWidth)
    leds = pygame.Surface((textWidth, matrixHeight),
                          pygame.SRCALPHA, screen)
    leds.blit(textsurface, (0, int((matrixHeight-textsurface.get_height())/2)))
    res = pygame.surfarray.pixels3d(leds)
    msg = bytes([textWidth & 0xFF, (textWidth >> 8) & 0xFF,
                 math.ceil(hue * 255/360), math.ceil(255*sat)])
    print(msg)
    for x in range(textWidth):
        acc = 0
        for y in range(matrixHeight):
            acc = acc | ((res[x, y, 0] >> 6) << ((y % 4)*2))
            if y % 4 == 3:
                msg += bytes([acc])
                acc = 0
        msg += bytes([acc])
    serMsg = serial.to_bytes(msg)
    return serMsg


message = args.message
hue = args.hue
sat = args.saturation

while connected:
        msg = buildMessage(message, hue, sat)
        msgsent = False
        msgack = False
        ticks = '.'
        print("message:", message, "hue:", hue, "saturation:", sat)
        i=0
        while connected and not msgack:
                # try:
                linein = ser.readline()
                if not linein:
                        print(ticks, sep="", end="\r")
                        ticks += '.'
                else:
                        ticks = '.'
                        print(linein)
                        if linein.endswith(b'OK\r\n'):
                                msgsent = False
                                print("Sending message")
                                print("Sent:", ser.write(msg[:32]), "bytes")
                                i=32
                        if linein.endswith(b'NEXT\r\n') and not msgsent:
                                print("Sent:", ser.write(msg[i:i+32]), "bytes")
                                i+=32
                        if i > len(msg):
                                msgsent = True
                                print("Sent message")
                        if linein.endswith(b'DONE\r\n') and msgsent:
                                print("Message acknowledged")
                                msgack = True
                        if linein.endswith(b'FAIL\r\n'):
                                print("Resending message")
                                msgsent=False         
                # except:
                #         connected = False
                #         print("Lost connection")
        if connected:
                message = input("Next message:")
                if len(message) == 0:
                        message = " "
                try:
                        hue = int(input("Hue[0]:"))
                        if hue < 0 or hue > 360:
                                hue = 0
                except ValueError:
                        hue = 0
                try:
                        sat = float(input("Saturation[0]:"))
                        if sat < 0 or sat > 1:
                                sat = 0
                except ValueError:
                        sat = 0        
        event = pygame.event.wait()
        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN):
                pygame.quit()
                sys.exit()
