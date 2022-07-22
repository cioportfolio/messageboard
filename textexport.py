
import time
import math
import colorsys
import pygame
import sys

gamma8 = [
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
    1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
    2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
    5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
   10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
   17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
   25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
   37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
   51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
   69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
   90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
  115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
  144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
  177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
  215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255
]

pygame.init()

pScale = 50
pRad = int(pScale/2)
matrixWidth = 15
matrixHeight = 15
if sys.platform == 'win32':
        port = 'COM5'
        font = 'FreeSansBold.ttf'
else:
        port = '/dev/ttyACM0'
        font = '/project/FreeSansBold.ttf'
cycleTime = 23
myfont = pygame.font.Font(font, 13)
black = (0,0,0)
pygame.time.set_timer ( pygame.USEREVENT , 20 )

def buildMessage(text, name):
        screen = pygame.display.set_mode((matrixWidth * pScale, matrixHeight * pScale))
        col = (255, 0, 0)
        textsurface = myfont.render(text, True, col, (0,0,0)).convert_alpha()
        textWidth = textsurface.get_width()
        print(textWidth)
        screen = pygame.display.set_mode((textWidth * pScale, matrixHeight * pScale))
        leds = pygame.Surface((textWidth, matrixHeight),pygame.SRCALPHA, screen)
        leds.blit(textsurface, (0,int((matrixHeight-textsurface.get_height())/2)))
        res = pygame.surfarray.pixels3d(leds)
        screen.fill(black)
        defFile  = open(name+".h", "w")
        defFile.write("const uint16_t k"+name+"Width = " + repr(textWidth) + ";\n")
        defFile.write("const PROGMEM uint8_t "+name+"[" + repr(textWidth) + "][" + repr(math.ceil(matrixHeight/4.0)) + "] = {")
        for x in range(textWidth):
                if x>0:
                        defFile.write(",")
                defFile.write("\n{\n")
                acc = 0
                for y in range(matrixHeight):
                        pygame.draw.circle(screen, ((res[x,y,0] >> 6) << 6,res[x,y,1],res[x,y,2]),[int(x * pScale + pRad), int(y * pScale + pRad)], pRad)
                        acc = acc | ((res[x,y,0] >> 6) << ((y % 4)*2))
                        if y % 4 == 3:
                                if y > 4:
                                        defFile.write(", ")
                                defFile.write(hex(acc))
                                acc=0
                defFile.write(", "+hex(acc)+"\n}")
        defFile.write("\n};")
        defFile.close()
        pygame.display.flip()
        
buildMessage("Stay at home ", "stay")
buildMessage("Save lives ", "save")
buildMessage("Protect the NHS ", "nhs")
while 1:
        event = pygame.event.wait()
        if (event.type == pygame.QUIT) or (event.type == pygame.KEYDOWN):
                pygame.quit()
                sys.exit()
