
import time
import math
import colorsys
import pygame
import sys
import argparse
import threading
import queue
import json
import os, fnmatch
from colour import Color 
import requests
import time
import numpy

pygame.init()

parser = argparse.ArgumentParser()
parser.add_argument('message', nargs='?',
                    help="Text to be sent", default="   Hello World   ")
parser.add_argument("-i", "--input", help="Message file", default="")
args = parser.parse_args()

connected = False
while not connected:
    try:
        s = requests.get('http://192.168.4.1/tetris?game=o')
        if s.status_code == 200:
            connected = True
            print("Connected to server ")
        else:
            connected = False
            print("Could not connect to server")
    except:
        connected = False
        print("Could not connect to port ")

matrixWidth = 15
matrixHeight = 15
font = 'FreeSansBold.ttf'
speed = 1/50

cycleTime = 23
#myfont = pygame.font.Font(font, 13)
myfont = pygame.font.SysFont("Ubuntu, Thin",13)
black = (0, 0, 0)
pygame.time.set_timer(pygame.USEREVENT, 20)
screen = pygame.display.set_mode((matrixWidth * 25, matrixHeight * 25))
def gameprint(text):
    screen.fill((0,0,0))
    textsurface = myfont.render(text, True, (255,255,255), (0,0,0))
    screen.blit(textsurface, (0,0))
    pygame.display.flip()

def buildMessage(fg,bg,text):
    textsurface = myfont.render(text, True, fg, bg).convert_alpha()
    textWidth = textsurface.get_width()
    print(textWidth, "x", textsurface.get_height())
    leds = pygame.Surface((textWidth, matrixHeight),
                          pygame.SRCALPHA, screen)
    leds.blit(textsurface, (0, int((matrixHeight-textsurface.get_height())/2)))
    res = pygame.surfarray.pixels3d(leds)

    return (bg, textWidth, res)

def res2hex(r, offset):
    bg, textWidth, res= r
    hexlist = ""
    for y in range(matrixHeight):
        for x in range(matrixWidth):
            if y % 2 == 1:
                ledx = x
            else:
                ledx = matrixWidth - 1 - x
            if ledx+offset >= textWidth or ledx+offset < 0:
                hexlist += c2hex(bg)
            else:
                hexlist += c2hex(res[ledx+offset, matrixHeight - 1 - y])
    return hexlist

def buildSprite(pixels):
    bytelist = []
    acc = 0
    y = 0
    for p in pixels:
        acc = acc | p << ((y % 4)*2)
        if y % 4 == 3:
            bytelist += [acc]
            acc = 0
        y += 1
        if y == matrixHeight:
            bytelist += [acc]
            acc=0
            y=0
    return serial.to_bytes(bytes(bytelist))

def n2hex(n):
    return '{:02X}'.format(int(n))

def c2hex(c):
    return n2hex(c[0]) + n2hex(c[1])+ n2hex(c[2])

message = args.message
whitehsv = [128,128,128]
blackhsv = [0,0,0]
q = queue.Queue()

def buff2hex(b):
    hexlist = ""
    for y in range(matrixHeight):
        for x in range(matrixWidth):
            if y % 2 == 1:
                ledx = x
            else:
                ledx = matrixWidth - 1 - x
            hexlist += c2hex(b[ledx, matrixHeight - 1 - y])
    return hexlist

def scroll(b):
    for x in range(matrixWidth-1):
        b[x] = b[x+1].copy()

def stream():
    global connected

    msglist = q.get()

    buffer = numpy.zeros((matrixWidth, matrixHeight, 3))

    while connected:
        for m in msglist:
            bg, textWidth, res = m
            for i in range(textWidth):
                scroll(buffer)
                buffer[matrixWidth-1] = res[i].copy()
                url = "http://192.168.4.1/screen?image=" + buff2hex(buffer)
                gameprint(url)
                s = requests.get(url)
                if s.status_code != 200:
                    print("Fail: "+s.text)
                    connected = False
                time.sleep(speed)
        for i in range(matrixWidth):
            scroll(buffer)
            for y in range(matrixHeight):
                buffer[matrixWidth-1,y] = bg
            url = "http://192.168.4.1/screen?image=" + buff2hex(buffer)
            s = requests.get(url)
            if s.status_code != 200:
                print("Fail: "+s.text)
                connected = False
            time.sleep(speed)
        if connected:
            try:
                msglist = q.get(timeout=2) 
            except queue.Empty:
                gameprint("Stream: Repeating last message")

def in2deg(input, default):
    try:
        output = int(input)
    except ValueError:
        return default
    if output < 0 or output > 360:
        return default
    return output

def in2one(input, default):
    try:
        output = float(input)
    except ValueError:
        try:
            output = int(input)
        except ValueError:
            return default
    if output < 0.0 or output > 1.0:
        return default
    return output

def in2col(input, default):
    if input == '':
        return default
    try:
        output = Color(input)
    except ValueError:
        return default
    return output.rgb

def mapchan(c):
    if c > 1.0:
        return c
    else:
        return c*255

def mapcol(col):
    return (mapchan(col[0]), mapchan(col[1]), mapchan(col[2]))

def loadList(filename):
    fp = open(filename, "r", encoding="utf-8")
    jsonlist = json.load(fp)
    retlist = []
    for item in jsonlist:
        if "msg" in item:
            msg = buildMessage(mapcol(item["fg"]),mapcol(item["bg"]),item["msg"])
            retlist += [msg]
    return retlist

threading.Thread(target=stream, daemon=True).start()
if args.input == "":
    msglist = [buildMessage(whitehsv, blackhsv, message)]
else:
    msglist = loadList(args.input)
while connected:
    q.put(msglist)
    msglist = []
    while msglist == []:
        msgfiles = [f for f in os.listdir('.') if fnmatch.fnmatch(f, "*.msg")]
        print("[0] Exit")
        print("[1] Manual message")
        for i,f in enumerate(msgfiles):
            print("[",i+2,"] ",f, sep='')
        optionList = input("Enter file number: ").split(',')
        for item in optionList:
            try:
                option = int(item)
            except ValueError:
                option = -1
            if option == -1:
                print(item,"is no a valid numbers")
                continue
            if option == 0:
                sys.exit()
            if option == 1:
                message = input('Next message: ')
                if len(message) == 0:
                    message = "..."
                fg = mapcol(in2col(input("Text colour: "), whitehsv))
                bg = mapcol(in2col(input("Background colour: "), blackhsv))
                msglist += [buildMessage(fg, bg, message)]
                continue
            if option < 2 or option > len(msgfiles)+1:
                print(item, " is not a valid option")
                continue
            filename = msgfiles[option - 2]
            msglist += loadList(filename)

