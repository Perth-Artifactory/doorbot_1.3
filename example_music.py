# https://raspberrypi.stackexchange.com/questions/7088/playing-audio-files-with-python

import pygame
pygame.mixer.init()
pygame.mixer.music.load("sounds/denied.mp3")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue
