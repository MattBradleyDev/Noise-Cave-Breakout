import Projectile

class Powerup:
    def __init__(self):
        self.projectile_delay = 6
        self.time_remaining = 300
        self.shots = 1


    def get_projectiles(self,time,x,y,w,h,dir,img):
        '''Creates a new projectile object using the players data
        Returns an empty array if the delay is not fulfilled
        Else returns a projectile for each position it makes'''
        self.get_positions(h)
        if time<self.projectile_delay or self.positions == []: return []
        projectiles = []
        for yoff,yvel in self.positions:
            bullet = Projectile.Bullet(x+w, y+yoff, dir, img, yvel)
            projectiles.append(bullet)
        return projectiles

    def get_positions(self,height):
        '''Based on the number of shots, y velocity and y offsets will be applied
        Dynamically generates positions and velocity
        Returns into the get_projectiles function'''
        if self.shots == 1:
            self.positions = [(height/2,0)]
            return
        self.positions = []
        for i in range(0,self.shots):
            yoff = (i/(self.shots-1))*height
            yvel = i - self.shots//2
            self.positions.append((yoff,yvel))

'''Altering Delays and number of shots in ovveriding classes'''
class ThreeShot(Powerup):
    def __init__(self):
        super().__init__()
        self.shots = 3
        self.projectile_delay = 4

class FiveShot(Powerup):
    def __init__(self):
        super().__init__()
        self.shots = 5
        self.projectile_delay = 6

class SevenShot(Powerup):
    def __init__(self):
        super().__init__()
        self.shots = 7
        self.projectile_delay = 8