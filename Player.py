import pygame as pg
import Projectile
import Explosion_Generation
import Powerup
import Player_DB
import random, string
from time import gmtime, strftime


class Player:
    def __init__(self):
        self.img = pg.image.load("ship1.png").convert_alpha()
        self.transparent_img = self.img.copy()
        self.transparent_img.fill((255, 255, 255, 0), None, pg.BLEND_RGBA_MULT)
        self.current_img = self.img
        self.img_filename = "ship1.png"
        self.rect = self.img.get_rect()
        self.rect.x,self.rect.y = 100,250
        self.delay = 0
        self.bomb_delay = 50
        self.projectile_img = pg.image.load("projectile1.png")
        self.projectile_filename = "projectile1.png"
        self.restart()
        self.lives = 3
        self.flashing_tick = 0
        self.invunerable = False
        self.shoot_sound = pg.mixer.Sound("shoot.wav")
        self.hit_sound = pg.mixer.Sound("hit.wav")

        self.db = Player_DB.Database()
        self.make_guest_account()
        # self.UID = self.db.login("Matt", "Password", self.UID)[0]
        self.get_options()

    def restart(self):
        '''Default variables'''
        self.rect.x, self.rect.y = 100, 250
        self.dir = 1
        self.projectiles = []
        self.timeSinceLastShot = 0
        self.timeSinceLastBomb = 0
        self.explosions = []
        self.dead = False
        self.score = 0
        self.last_shown_score = 0
        self.enemies_killed = 0
        self.bullets_fired = 1
        self.bombs_fired = 0
        self.shields_destroyed = 0
        self.lives_added = 0
        self.powerup_tick = 900
        self.powerup = Powerup.Powerup()

    def move(self,key,movement_type):
        '''Returns if the user is using mouse mode as the function applies to keyboard movement
        Uses a dictionary to map keys with x and y movement values
        Maps the user onto the screen by checking screen bounds and only applying movement if the user is inside'''
        if movement_type == "mouse": return
        movement = {"w":(0,-15),"s":(0,15),"a":(-15,0),"d":(15,0)}
        if 0 <= self.rect.x + movement[key][0] <= 1000-self.rect.width:
            self.rect.x += movement[key][0]
        if 0 <= self.rect.y + movement[key][1] <= 500-self.rect.height:
            self.rect.y += movement[key][1]

    def shoot_bullet(self):
        '''Accesses Powerup class to generate the amount and y velocities of projectiles.
        Records the amounts of bullets fired and applies it to internal statistics'''
        projectiles = self.powerup.get_projectiles(self.timeSinceLastShot,self.rect.x,self.rect.y,self.rect.width,self.rect.height,self.dir,self.projectile_filename)
        if len(projectiles) > 0:
            self.bullets_fired += len(projectiles)
            self.shoot_sound.play()
            self.timeSinceLastShot = 0
            for i in projectiles: self.projectiles.append(i)

    def shoot_bomb(self):
        '''Creates Bomb projectile with different physics than a bullet. Upto 3 bombs can be stored at once
        Checks internal delays to see if a bomb should be fired'''
        if self.timeSinceLastBomb >= self.bomb_delay:
            self.bombs_fired += 1
            if self.dir: self.projectiles.append(Projectile.Bomb(self.rect.x+self.rect.width,self.rect.y+self.rect.height/2,self.dir))
            else: self.projectiles.append((Projectile.Bomb(self.rect.x, self.rect.y+self.rect.height/2,self.dir)))

            self.timeSinceLastBomb -= self.bomb_delay
            if self.timeSinceLastBomb > self.bomb_delay * 2: self.timeSinceLastBomb = self.bomb_delay * 2

    def change_dir(self,key):
        '''Flips the ship based on current direction and key press'''
        if key == "d" and not self.dir: self.dir = 1
        if (key == "a" and self.dir): self.dir = 0

    def bombs_available(self):
        '''Calculates the amount of bombs available, capping at 3'''
        if self.timeSinceLastBomb // self.bomb_delay >= 3: return 3
        elif self.timeSinceLastBomb // self.bomb_delay <=3: return self.timeSinceLastBomb // self.bomb_delay
        return None

    def update_objects(self):
        '''Removes dead marked projectiles, Removes Explosions at end of animation, Incriments Shot Timers
        Powerups should be generated every 900 ticks and last their internal value.
        Powerups with no time remaining default back to the normal shot'''
        self.projectiles = [i for i in self.projectiles if not i.dead]
        self.explosions = [i for i in self.explosions if i.frame < i.maxFrame]
        self.timeSinceLastBomb+=1
        self.timeSinceLastShot+=1
        self.score += 1
        if self.score//50000>self.lives_added:
            self.lives_added+=1
            self.lives+=1
        if self.invunerable:
            self.flashing_tick +=1
        if self.powerup.shots != 1:
            self.powerup.time_remaining -=1
            if self.powerup.time_remaining == 0: self.powerup = Powerup.Powerup()
        else:
            self.powerup_tick -= 1
            if self.powerup_tick == 0:
                self.powerup = random.choice([Powerup.ThreeShot(),Powerup.FiveShot(),Powerup.SevenShot()])
                self.powerup_tick = 900

    def collide_terrain(self,terrain_points):
        '''Checking if ship.rect collides with any point in the terrain
        Uses the point list for rect and point collisions,
        Removes a life from the user if they have more than one left
        Grants invunerability that makes them immune for a period of time'''
        for p in terrain_points:
            if self.rect.collidepoint(p[0],p[1]):
                if self.invunerable: return
                if self.lives >1:
                    self.lives-=1
                    self.invunerable = True
                else:
                    self.dead = True

    def check_enemy_killed(self,enemies):
        '''Checks if bullet rects collide with enemy rects
        Objects from the bomb class have destructive explosions that kill other enemies
        Score is based on the enemy internally storing score
        Records statistics foe the user
        Returns the enemies that were not killed'''
        for bullet in self.projectiles:
            for enemy in enemies:
                if bullet.check_collision(enemy):
                    if enemy.get_hit():
                        if isinstance(bullet,Projectile.Bullet):
                            self.explosions.append(Explosion_Generation.Explosion(bullet.rect.x,bullet.rect.y,30,False))
                        else:
                            self.explosions.append(Explosion_Generation.Explosion(bullet.rect.x,bullet.rect.y,30,True))
                            enemy.caused_explosion = True
                        self.score += enemy.score_yield
                        enemy.dead = True
                        self.enemies_killed += 1
                        enemies = [i for i in enemies if i != enemy]
                    else:
                        self.shields_destroyed += 1
                        if isinstance(bullet, Projectile.Bomb):
                            self.explosions.append(
                                Explosion_Generation.Explosion(bullet.rect.x, bullet.rect.y, 30, True))
        return enemies

    def hit_by_enemy(self,enemies):
        '''If the user is invunerable enemies will not hurt the player
        Gets concatinated list of enemies and enemy projectiles to test from
        Checks player.rect against theme other rects for collision'''
        if self.invunerable: return
        collisions = [i for i in enemies] + sum([i.projectiles for i in enemies],[])

        for obj in collisions:
            if self.rect.colliderect(obj.rect):
                if self.lives > 1:
                    self.lives -= 1
                    self.invunerable = True
                else:
                    self.dead = True

    def flashing_change(self):
        '''Users ship will flash from 0 alpha to 255 alpha using RGBA multiplication to make alpha 0
        Each flash will play a sound as a further indicator
        If the tick times out, invunerability stops'''
        if not self.invunerable: return

        if self.flashing_tick>=100:
            self.flashing_tick = 0
            self.invunerable = False
            self.current_img = self.img
        else:
            if self.flashing_tick%5==0:
                if self.flashing_tick%10==0: self.hit_sound.play()
                if self.current_img == self.img: self.current_img = self.transparent_img
                else: self.current_img = self.img

    def update_img(self):
        '''A new transparant image is loaded by copying the origional image
        RGBA is multiplied by 0 to make a transparent image of the same size
        Resets both current image transparent image'''
        self.img = pg.image.load(self.img_filename)
        self.transparent_img = self.img.copy()
        self.transparent_img.fill((255, 255, 255, 0), None, pg.BLEND_RGBA_MULT)
        self.current_img = self.img.copy()
        self.projectile_img = pg.image.load(self.projectile_filename)

    def upload_data(self,time):
        '''Generates a guest profile for the current session if the user is not logged in
        Add_User returns true if user exists so will loop until an unused name is found
        52 ^ 10 combinations (144,555,105,949,057,024)
        Accuracy is a rounded float of the proportion of enemies killed and bullets fired
        Stats are uploaded tied to the userID
        '''

        accuracy = round((self.enemies_killed / (self.bullets_fired+self.bombs_fired)),2)
        accuracy = min(1, accuracy) 

        self.db.add_stats(self.enemies_killed,
                          round(time,2),
                          self.shields_destroyed,
                          self.score,
                          self.bullets_fired,
                          self.bombs_fired,
                          accuracy,
                          strftime("%d/%m/%Y"),
                          self.UID)

    def make_guest_account(self):
        '''If there is no UID, a random guest name and password will be made.
        The user is automatically logged into this account.'''
        if not hasattr(self,"UID"):
            while True:
                guest_name = ''.join([random.choice(string.digits) for i in range(10)])
                if self.db.register("guest"+guest_name,guest_name): break
            sql = "SELECT UserID FROM Users WHERE Username = ?"
            self.UID = str(self.db.get_results(sql,("guest"+guest_name,),False))


    def upload_options(self,vol,terrain,movement):
        '''Options that already exist will be updated in the database
        If options do not exist options are added
        If options do exist options are updated'''
        if self.UID == None: return
        if len(self.db.get_results("SELECT * FROM Options WHERE UserId=?",(self.UID,))) > 0:
            self.db.update_options(self.img_filename,self.projectile_filename,vol,terrain,movement,self.UID)
        else:
            self.db.add_options(self.img_filename,self.projectile_filename,vol,terrain,movement,self.UID)

    def get_options(self):
        '''The database is accessed based on UID and the options are pulled and applied.'''
        if self.UID == None: return
        sql = "SELECT ShipName, ProjectileName FROM Options WHERE UserID=?"
        (shipname,projectilename) = self.db.get_results(sql,(self.UID,))[0]
        self.img_filename = shipname
        self.projectile_filename = projectilename
        self.update_img()