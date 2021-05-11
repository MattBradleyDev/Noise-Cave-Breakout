import random
import pygame as pg
import math
import Projectile

class Enemy:
    def __init__(self,sw=1000,sh=500):
        '''Initialising default setting for each enemy'''
        self.rect = pg.Rect(1000,random.randint(100,400),24,24)

        self.img = pg.image.load("enemy1.png")
        self.x_velocity = -3
        self.y_velocity = 0
        self.dead = False
        self.inSwarm = None
        self.max_velocity = 15
        self.target = None
        self.dodgingTerrain = False
        self.seeking = False
        self.projectiles = []
        self.shot_timer = 0
        self.caused_explosion = False
        pg.init()
        pg.mixer.pre_init(44100, 16, 2, 4096)
        self.hit_noise = pg.mixer.Sound(file="sound.wav")


    def move(self):
        '''Proportianally scales x and y velocity based on the maximum velocity applied
        Speed is divided by the amount of shields the enemy has. When an enemy loses
        Shield its velocity increaces.'''
        self.x_velocity *= 1/((self.shield+1)/2)
        self.y_velocity *= 1/((self.shield+1)/2)
        if abs(self.x_velocity) > self.max_velocity or abs(self.y_velocity) > self.max_velocity:
            sf = self.max_velocity / max(abs(self.x_velocity),abs(self.y_velocity))
            self.x_velocity, self.y_velocity = self.x_velocity*sf, self.y_velocity*sf

        self.rect.x += self.x_velocity
        self.rect.y += self.y_velocity
        self.shot_timer+=1
        for i in self.projectiles: i.move()

    def check_bounds(self):
        '''Checks whether the enemy is within vertical bounds'''
        return 0 <= self.rect.y <= 500

    def get_difference(self,cx,cy):
        '''Gets the difference in position from an x,y coordinate'''
        return (abs(self.rect.x-cy),abs(self.rect.y-cy))

    def assign_target(self,targets):
        '''Finds the distances of each target and assigns the smallest distance'''
        getDiff = lambda i:math.sqrt((self.rect.x - i.x) ** 2 + (self.rect.y - i.y) ** 2)
        self.target = min(targets,key=getDiff)

    def get_hit(self):
        '''Reduces shield if available, else returns True'''
        self.hit_noise.play()
        if self.shield == 0: return True
        self.shield -= 1

    def shoot(self,player):
        '''Shoots in the direction of the player based on its own position.
        Each time it shoots, each projectile is also checked to see if it is on screen
        Off screen projectiles are removed.'''
        if self.shot_timer > 100:
            dir = 1 if player.rect.x > self.rect.x else 0
            self.projectiles.append(Projectile.Bullet(self.rect.x,self.rect.y+12,dir,"projectile1.png"))
            self.shot_timer = 0
        self.projectiles = [i for i in self.projectiles if 0 < i.rect.x < 1000]


class EnemyTier0(Enemy):
    '''Each tier alters the image, max velocity, shield and score.
    Tier 0 and 1 cannot shoot.'''
    def __init__(self):
        super().__init__()
        self.shield = 0
        self.max_velocity = 8
        self.score_yield = 200
        self.img = pg.image.load("enemy1.png")

    def shoot(self,player):
        return

class EnemyTier1(Enemy):
    def __init__(self):
        super().__init__()
        self.shield = random.choice([0,0,0,1,1])
        self.max_velocity = 10
        self.score_yield = 400 + (50*self.shield)
        self.img = pg.image.load("enemy2.png")

    def shoot(self,player):
        return

class EnemyTier2(Enemy):
    '''Tier 2 and 3 can shoot'''
    def __init__(self):
        super().__init__()
        self.shield = random.choice([1,1,1,1,2])
        self.max_velocity = 12
        self.score_yield = 750 + (100*self.shield)
        self.img = pg.image.load("enemy3.png")

class EnemyTier3(Enemy):
    def __init__(self):
        super().__init__()
        self.shield = random.choice([2,2,2,2,3])
        self.max_velocity = 14
        self.score_yield = 1000 + (150*self.shield)
        self.img = pg.image.load("enemy4.png")






