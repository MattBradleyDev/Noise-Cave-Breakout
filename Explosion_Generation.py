import pygame as pg

class Explosion:
    def __init__(self,x,y,framerate,isBomb):
        self.x = x-50
        self.y = y-50
        self.framerate = framerate
        self.isBomb = isBomb
        self.img = pg.image.load("bomb.png")
        self.frame = 0
        self.maxFrame = 80
        self.divider = (0,0,100,100)

    def move_frame(self):
        '''Normalises Speed Based on Game Framerate, Uses divider to move portion of sprite sheet'''
        self.frame+=int(self.maxFrame/self.framerate)
        if self.frame>self.maxFrame: return False
        self.divider = ((self.frame%9)*100,(self.frame//9)*100,100,100)
        self.x -= 10
        return True
