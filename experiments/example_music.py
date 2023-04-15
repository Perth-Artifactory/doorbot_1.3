# https://raspberrypi.stackexchange.com/questions/7088/playing-audio-files-with-python
# 
# To get around 
# NotImplementedError: mixer module not available (ImportError: libSDL2_mixer-2.0.so.0: cannot open shared object file: No such file or directory)
# > sudo apt-get install python3-sdl2

import pygame
pygame.mixer.init()
# pygame.mixer.music.load("sounds/granted.mp3")
pygame.mixer.music.load("sounds/custom/1952718_cd3d9dd904aca51abc55dbe7b7cc7b28.mp3")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy() == True:
    continue

import time
# time.sleep(0.5)

# import os
# os.system ("mpg123 -q {} &".format("sounds/granted.mp3"))
