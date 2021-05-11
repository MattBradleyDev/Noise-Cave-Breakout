import pygame as pg

class Background:
    def __init__(self,filename):
        self.img = pg.image.load(filename)
        self.switching = False
        self.width = self.img.get_rect().width
        self.x1 = 0
        self.x2 = self.width

    def scroll(self):
        '''Moves the background image across the screen and resets when a full cycle is complete
        Continuous textures means images always scroll
        Works dynamically for any width image'''
        self.x1,self.x2 = self.x1-5,self.x2-5
        if self.x1<= -self.width: self.x1,self.x2 = 0,self.width
