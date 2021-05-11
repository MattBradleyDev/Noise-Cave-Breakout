import pygame as pg
import Explosion_Generation


class Projectile:
    def __init__(self,x,y,dir,yvel=0):
        self.x = x
        self.y = y
        self.y_velocity = yvel
        self.dead = False
        if dir ==0: self.dir = -1
        else: self.dir = 1

    def move(self):
        '''Applies the velocity depending on direction of the shot
        Checks its own bounds to see if it is offscreen
        Changes its own velocity to apply acceleration'''
        self.x += self.x_velocity * self.dir
        self.y += self.y_velocity
        self.rect = pg.Rect(self.x,self.y,self.width,self.height)
        if not -50 <= self.x <= 1050 and -50 <= self.y <= 550: self.dead = True
        self.change_velocity()

    def check_collision(self,other):
        '''Checks if the projectile rect collides with another passed in rect'''
        if self.rect.colliderect(other):
            self.dead = True
            return True





class Bomb(Projectile):
    def __init__(self,x,y,dir):
        super().__init__(x,y,dir)
        self.x_velocity = 20
        self.total_velocity = self.x_velocity
        self.width = 13
        self.height = 13
        self.img = pg.image.load("bomb_projectile.png")
        self.type = 1
        self.rect = pg.Rect(x, y, self.width, self.height)

    def change_velocity(self):
        '''Changes the y velocity based on the reduced x velocity to apply gravity
        Bombs falling below a threshold will explode'''
        if self.x_velocity >= 0: self.x_velocity -= 1
        self.y_velocity = self.total_velocity - self.x_velocity

        if self.y >= 480: self.explode()

    def explode(self):
        '''Checks y pos to see if the bomb can explode without colliding with an enemy'''
        if self.y <480: return False
        self.dead = True
        return True


class Bullet(Projectile):
    def __init__(self,x,y,dir,img,yvel=0):
        super().__init__(x,y-4,dir,yvel)
        self.x_velocity = 5
        self.width = 15
        self.height = 8
        self.img = pg.image.load(img)
        self.rect = pg.Rect(x, y, self.width, self.height)
        self.type = 0

    def change_velocity(self):
        '''Has x velocity acceleration applied'''
        self.x_velocity += 1

