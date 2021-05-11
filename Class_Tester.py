import pygame as pg
from pygame.locals import *
import random, math, time
import Terrain_Generation
import Explosion_Generation
import Projectile
import Background
import Player
import Enemy
import Swarm
import Achievement
from scipy.io.wavfile import read
import os, glob

class Tester:
    def __init__(self,sw,sh):
        self.current = 0
        '''Initialising Pygame'''
        self.screen = pg.display.set_mode((sw,sh))
        pg.font.init()
        pg.init()
        pg.mixer.pre_init()
        self.sw,self.sh = sw,sh
        self.clock = pg.time.Clock()
        self.player = Player.Player()
        self.projectile_img = pg.image.load("ship1.png")
        self.font = pg.font.SysFont("constantia",15)
        self.option_font = pg.font.SysFont("constantia",40)
        self.menu_font = pg.font.SysFont("constantia",80)
        self.start_time = time.time()
        self.restart()
        self.uploaded_data = True
        self.start = 0
        self.sstart = time.time()
        self.vals = []


        '''Menu Buttons'''
        self.start_button = Rect(100,200,800,80)
        self.personalise_button = Rect(100,300,800,80)
        self.options_button = Rect(100,400,375,80)
        self.quit_button = Rect(525,400,375,80)
        self.account_button = Rect(10,50,300,80)

        '''Options Buttons'''
        self.selected = None
        self.volume = "100"
        self.movement_type = "mouse"
        self.terrain_type = "music"
        self.load_options()

        '''Account Buttons'''
        self.username_rect = Rect(10,20,150,30)
        self.password_rect = Rect(10,70,150,30)
        self.login_button = Rect(10,120,75,30)
        self.register_button = Rect(85,120,75,30)
        self.scroller_rect = Rect(275,45,20,435)
        self.order_rect = Rect(275,20,40,25)
        self.back_button = Rect(10,185,150,30)
        self.search_type_rect = Rect(315,20,75,25)
        self.search_bar = Rect(390,20,500,25)
        self.account_buttons = [self.username_rect, self.password_rect, self.login_button,
                                self.register_button, self.order_rect, self.search_type_rect,
                                self.scroller_rect, self.search_bar, self.back_button]
        self.selected_form = None
        self.selected_catagory = "ID"
        self.account_text = ["ID","Enemy","Time","Shield","Score","Bullets","Bombs","Acc","Date","UID"]
        self.scroll_value = 0
        self.order = True
        self.search_type = True
        self.next_cap = False
        self.scrolling = False
        self.verification_text = ""

    def restart(self):
        '''Music Generation'''
        self.filename = self.get_random_song()
        if self.filename is None: self.filename = "background_music.wav"
        pg.mixer.music.load(self.filename)
        self.length = pg.mixer.Sound(self.filename).get_length() * 30
        self.input_data = read(self.filename)
        self.audio = self.input_data[1]
        '''Terrain / Background / Enemies / Swarm / Player Reset'''
        self.terrain = Terrain_Generation.Terrain(1000,500)
        self.terrain.prev_values = []
        self.current_background = 0
        self.background = Background.Background("background.jpg")
        self.enemies = []
        self.enemy_spawn_tick = 0
        self.player.dead = True
        self.player.lives = 3
        self.displayScore = self.player.score
        self.uploaded_data = False
        self.start_time = time.time()
        self.swarm = Swarm.Swarm()
        self.swarms = [Swarm.Swarm()]
        self.swarm_timing = 0
        self.average = [(i, 37) for i in range(0, 1000, 10)]
        self.options = False
        self.personalise = False
        self.account_menu = False
        pg.mouse.set_visible(True)
        self.scroll_tick = 0

    def update(self):
        '''Running each class methods and incrementing score.
        Updates score each 10 points
        Handles quitting with bost escape and manual window closure
        Runs Menus if not the main game'''
        event = pg.event.poll()
        keyinput = pg.key.get_pressed()
        if not self.player.dead:
            self.screen.fill((51, 25, 0))
            (x, y) = pg.mouse.get_pos()
            if self.movement_type == "mouse":
                self.player.rect.x, self.player.rect.y = x,y

            self.run_tests(keyinput,event)

            if self.player.score % 10 == 0: self.player.last_shown_score = self.player.score
            self.screen.blit(self.font.render("Score: %s"%(self.player.last_shown_score),True,(0,0,0)),(10,10))

            if keyinput[pg.K_ESCAPE]:
                self.player.db.clear_guests()
                raise SystemExit
            elif event.type == pg.QUIT:
                self.player.db.clear_guests()
                quit()
        elif self.options:
            self.options_menu(event,pg.mouse.get_pos())
        elif self.personalise:
            self.personalisation_menu(event,pg.mouse.get_pos())
        elif self.account_menu:
            self.user_menu(event,pg.mouse.get_pos())
        else:
            self.menu(event,pg.mouse.get_pos())

        #print(pg.time.get_ticks()-self.start)
        self.vals.append(pg.time.get_ticks() - self.start)
        if len(self.vals)>100: del self.vals[0]
        #print(1000//(sum(self.vals)/len(self.vals)))
        self.start = pg.time.get_ticks()
        #print(int(time.time()-self.sstart), len(self.vals))

        pg.display.flip()
        self.clock.tick(30)

    def get_random_song(self):
        '''Checks each file in playlist file filtering for the .wav extension and returns a random song
        If the folder is empty, a default song is loaded'''
        wavs = []
        path = "Playlist"
        files = os.listdir(path)
        for filename in glob.glob(os.path.join(path, '*.wav')):
            wavs.append(filename)
        if len(wavs) == 0: return "background_music.wav"
        return random.choice(wavs)

    def change_background(self):
        '''Changes the background and theme every 5000 score
        Uses a similar switch / case format using incimenting index %2 to get 0 or 1
        Applys the theme of the background to the game'''

        if self.player.score // 20000 <= self.current_background: return
        else: self.current_background = self.player.score // 20000
        choice = [("background.JPG", (102, 51, 0),(158, 76, 0)), ("background2.jpg", (30, 30, 30),(60,60,60))]
        choice = choice[self.current_background%2]
        self.background = Background.Background(choice[0])
        self.terrain.col1 = choice[1]
        self.terrain.col2 = choice[2]

    def run_tests(self,keypress,event):
        '''Runs each core modules functions separately'''
        self.change_background()
        self.background_tests()
        self.terrain_tests()
        self.player_tests(keypress,event)
        self.enemy_test()
        self.swarm_tests()

    def music_tests(self):
        '''Gets the current time in the song playig and allocates a proportion of samples per tick of animation
        Average is generated from the allocated samples (a slice of the sample array)
        Gets true average and halves, bounding excessive values to have maximum amounts
        The new average replaces the old and each y value moves down
        Music is reset upon the song ending'''
        current_time = pg.mixer.music.get_pos() // (1000 / 30)
        allocated = self.audio[int((len(self.audio) // self.length) * (current_time)): int(
            (len(self.audio) // self.length) * (int(current_time * (1000 / 30)) + 1) // (1000 / 30))]
        average = sum([sum(i)/2 for i in allocated]) / (len(self.audio)//self.length)
        average = sum([i[0] for i in allocated]) / (len(self.audio) // self.length)
        if current_time > len(self.average):
            while len(self.terrain.prev_values)<5: self.terrain.prev_values.append(average)
            del self.terrain.prev_values[0]
            average = sum([average]+self.terrain.prev_values)/6
            self.terrain.prev_values.append(average)
            del self.average[0]
            self.average.append((self.average[-1][0] + 10, 30+average))
            self.average = [(i[0] - 10, i[1]) for i in self.average]
        if self.length<=current_time:
            self.filename = self.get_random_song()
            pg.mixer.music.load(self.filename)
            self.length = pg.mixer.Sound(self.filename).get_length() * 30
            self.input_data = read(self.filename)
            self.audio = self.input_data[1]
            pg.mixer.music.play()


    def enemy_test(self):
        '''Generates different tiered enemies depending on user score
        Uses random choice for distribution probability (Binomial Distribution)
        Adds the enemy to the array and swarm
        Enemies apply velocity and shoot if possible
        Enemies with shields have a visual indicator depending on values'''
        spawn_tick = max(30, ((len(self.swarm.swarm)*20+1)-self.player.score//1000))
        if self.enemy_spawn_tick % spawn_tick == 0:
            self.enemy_spawn_tick = 0
            t0,t1,t2,t3 = Enemy.EnemyTier0(), Enemy.EnemyTier1(), Enemy.EnemyTier2(), Enemy.EnemyTier3()
            if 0<=self.player.score<=4999: tiers = [t0,t0,t0,t0,t0,t0,t1,t1]
            elif 5000<=self.player.score<=14999: tiers = [t0,t0,t0,t0,t1,t1,t1,t1]
            elif 15000<=self.player.score<=24999: tiers = [t0,t1,t1,t1,t2,t2,t2,t2]
            elif 25000<=self.player.score<=39999: tiers = [t2,t2,t2,t2,t3,t3,t3,t3]
            elif self.player.score>=40000: tiers = [t2,t3,t3,t3]

            self.enemies.append(random.choice(tiers))
            self.swarm.add_member(self.enemies[-1])
        self.enemy_spawn_tick += 1

        for i in self.enemies:
            i.move()
            i.shoot(self.player)
            self.screen.blit(i.img,i.rect)
            for j in range(i.shield):
                pg.draw.circle(self.screen,(0,0,255),(i.rect.x+12,i.rect.y+12),15+(j*5),3)
            for j in i.projectiles:
                self.screen.blit(j.img,j.rect)
                pg.draw.rect(self.screen,(0,255,0),j.rect,2)

        for i in self.enemies:
            if not i.check_bounds(): i.dead = True

    def terrain_tests(self):
        '''Music terrain is handled in the music_tests function
        Value generation offloaded into the terrain class for random
        Creates a polygon to draw based on the subset values generated and closure array points'''
        if self.terrain_type == "music":
            self.music_tests()
            self.terrain.values = self.average
        self.terrain.get_subset(self.terrain_type)
        if len(self.terrain.values) <= 1: return
        self.terrain.get_total()
        pg.draw.polygon(self.screen,self.terrain.col1,self.terrain.values+[(1000,0),(0,0)])
        pg.draw.polygon(self.screen, self.terrain.col1, self.terrain.b_values+[(1000,500),(0,500)])
        pg.draw.polygon(self.screen, self.terrain.col2, self.terrain.alt_values+[(1000,0),(0,0)])
        pg.draw.polygon(self.screen, self.terrain.col2, self.terrain.alt_b_values+[(1000,500),(0,500)])
        if self.terrain_type == "random":
            self.terrain.update_value()

    def background_tests(self):
        '''Backgrounds are displayed on the screen and scrolled'''
        for i in [self.background.x1,self.background.x2]: self.screen.blit(self.background.img,(i,0))
        self.background.scroll()

    def player_tests(self,keyinput,event):
        '''Displaying Player to the screen'''
        self.screen.blit(pg.transform.flip(self.player.current_img, not self.player.dir, 0), self.player.rect)
        '''Shows the amount of lives the player has on the screen dynamically depending on how many'''
        for i in range(self.player.lives):
            img = pg.transform.scale2x(pg.image.load("heart.png"))
            self.screen.blit(img,(130+i*30,5))

        self.player.flashing_change()

        '''Moving Player based on keypress or changing player direction they are facing'''
        for i in "wsad":
            if keyinput[ord(i)] == 1:
                if i == "a" or "d": self.player.change_dir(i)
                self.player.move(i,self.movement_type)

        '''Shooting bullet or bomb and adding to projectiles array'''
        if event.type == pg.MOUSEBUTTONUP:
            self.player.shoot_bullet()
            pg.event.clear()
        if keyinput[pg.K_SPACE]: self.player.shoot_bomb()

        '''Drawing and updating projectiles
        Bomb explosions can manually be triggered for terrain collision'''
        for i in self.player.projectiles:
            i.move()
            if isinstance(i,Projectile.Bomb):
                if i.explode():
                    self.player.explosions.append(Explosion_Generation.Explosion(i.x,i.y,30,True))
            self.screen.blit(i.img,(i.x,i.y))

        '''Drawing and cycling explosion animations
        Explosion dividers cut up a sprite sheet to get current image of the animation
        Explosions caused by bombs kill enemies that ollide with them between certain frames'''
        for i in reversed(self.player.explosions):
            total = 0
            i.move_frame()
            self.screen.blit(i.img, (i.x,i.y), i.divider)
            rect = Rect(i.x, i.y, 100, 100)
            if not i.isBomb or not 12<=i.frame<36: continue
            for j in self.enemies:
                if rect.colliderect(j.rect):
                    j.dead = True
                    if not j.caused_explosion:
                        self.player.explosions.append(Explosion_Generation.Explosion(j.rect.x,j.rect.y,30,True))
                        j.caused_explosion = True
                        j.hit_noise.play()
                    self.player.score += j.score_yield
                    total += 1

        '''Drawing bombs available indicators'''
        for i in range(self.player.bombs_available()):
            pg.draw.circle(self.screen, (0,0,0), (895 + 40 * (i - 1), 50), 18)
            pg.draw.circle(self.screen,(128,128,128),(895 + 40*(i-1),50),15)

        '''Checking collisions between projectiles and enemies
           Checking collisions between player and terrain'''
        self.enemies = self.player.check_enemy_killed(self.enemies)
        self.enemies = [i for i in self.enemies if not i.dead]
        self.player.hit_by_enemy(self.enemies)
        self.player.collide_terrain(self.terrain.get_total())
        if self.player.powerup.shots!=1:self.screen.blit(pg.image.load("x3.png"),(770,30))

        self.player.achievement.update_completed(self.player.score)
        for i in range(3):
            if self.player.achievement.completed[i]:
                filename = ["bronze.png","silver.png","gold.png"][i]
                self.screen.blit(pg.image.load(filename), (650 + (30*i),0))

        self.player.update_objects()

    def swarm_tests(self):
        '''Activates the main control system inside the swarm class
        Calculates time to generate new node values for enemies to orbit'''
        self.swarm.control(self.terrain,self.player)
        #pg.draw.circle(self.screen,(255,0,0),self.swarm.get_centre(),3)
        #pg.draw.line(self.screen,(255,0,0),(self.swarm.target_x,0),(self.swarm.target_x,500))
        for i in self.swarm.targets:
            pass
            #pg.draw.circle(self.screen, (0,0,255),(i.x,i.y),3)
        self.swarm.target_time +=1
        if self.swarm.target_time%max(10,30-(self.player.score//100))==0:
            self.swarm.generate_target()
            self.swarm_target_time = 0

    def menu(self,event,mousePos):
        '''Checks if the player data has been uploaded to a database and uploads'''
        if not self.uploaded_data:
            self.player.upload_data((time.time()-self.start_time))
            self.uploaded_data = True
            pg.mouse.set_visible(True)
            pg.event.clear()
        if self.player.UID == None: self.player.make_guest_account()
        '''Deaws the buttons and text in the menu'''
        self.screen.fill((0,0,0))
        pg.draw.rect(self.screen,(255,255,255),self.start_button,5)
        self.screen.blit(self.menu_font.render("Start Game",True,(255,255,255)), (self.start_button.x+200,self.start_button.y))

        pg.draw.rect(self.screen, (255, 255, 255), self.personalise_button,5)
        self.screen.blit(self.menu_font.render("Personalisation", True, (255, 255, 255)), (self.personalise_button.x + 150, self.personalise_button.y))

        pg.draw.rect(self.screen, (255, 255, 255), self.quit_button,5)
        self.screen.blit(self.menu_font.render("Quit", True, (255, 255, 255)), (self.quit_button.x + 100, self.quit_button.y ))

        pg.draw.rect(self.screen, (255, 255, 255), self.options_button,5)
        self.screen.blit(self.menu_font.render("Options", True, (255, 255, 255)), (self.options_button.x + 50, self.options_button.y))

        pg.draw.rect(self.screen, (255, 255, 255), self.account_button,5)
        self.screen.blit(self.menu_font.render("Account", True, (255,255,255)), (self.account_button.x, self.account_button.y))

        self.screen.blit(self.option_font.render(self.player.db.get_username(self.player.UID), True, (0,0,255)), (0,0))


        '''Shows the previous score for the last game'''
        self.displayScore = self.player.score
        if self.displayScore > 0: self.screen.blit(self.font.render("Previous Score: %s"%(self.displayScore),False,(255,255,255)),(750,10))
        '''Checks each rect to perform an action if clicked
        Options opens the options menu
        Personalise opens the personalisation menu
        Start button initialises the game and resets the player'''
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.quit_button.collidepoint(mousePos):
                self.player.db.clear_guests()
                raise SystemExit
            elif self.options_button.collidepoint(mousePos):
                self.options = True
                self.selected = None
            elif self.personalise_button.collidepoint(mousePos):
                self.personalise = True
            elif self.start_button.collidepoint(mousePos):
                self.restart()
                self.player.restart()
                self.player.dead = False
                pg.mouse.set_visible(False)
                pg.mixer.music.play(-1, 0)
                self.player.achievement = Achievement.Achievement(self.player.UID)
            elif self.account_button.collidepoint(mousePos):
                self.account_menu = True
                self.username_text = ""
                self.password_text = ""
                self.search_text = ""

    def options_menu(self,event,mousePos):
        '''Draws text for menu options and initialises button rects
        Sound rect is generated by the length of text
        Clicking on the sound rect highlights it for typing
        Assesses keyinputs to test if it is a number and allows typing and deleting
        Values are bounded to 0 or 100
        Sets the current volume to that number'''
        self.screen.fill((0,0,0))
        sound_rect = Rect(245,100,len(self.volume)*30,40)
        self.screen.blit(self.option_font.render("Music SFX: ", True, (255,255,255)), (10,100))
        self.screen.blit(self.option_font.render(self.volume, True, (255, 255, 255)), (250, 100))
        pg.draw.rect(self.screen, (255, 255, 255), sound_rect, 3)
        if sound_rect.collidepoint(mousePos) and event.type == MOUSEBUTTONDOWN:
            self.selected = "sound"
        elif event.type == MOUSEBUTTONDOWN:
            self.selected = None

        if self.selected == "sound":
            pg.draw.rect(self.screen,(0,0,255),sound_rect,3)
            if event.type == KEYDOWN:
                if pg.K_0 <= event.key <= pg.K_9:
                    if self.volume=="0": self.volume=""
                    self.volume+=chr(event.key)
                elif pg.K_BACKSPACE == event.key and len(self.volume) > 0: self.volume = self.volume[0:-1]
                if len(self.volume)>0:
                    if int(self.volume)>100: self.volume = "100"
                    pg.mixer.music.set_volume(int(self.volume)/100)
                else: self.volume = "0"

        '''Draws rects on screen. Drawn in blue if that option is currently selected.
        Switches choice depending on user clicking
        Applys settings to the current game upon generation
        Uploads / Updates player options depending on DB records existing'''
        k_movement_rect = Rect(345,200,180,40)
        m_movement_rect = Rect(595,200,130,40)
        if self.movement_type == "keyboard":
            pg.draw.rect(self.screen,(0,0,255),k_movement_rect,3)
            pg.draw.rect(self.screen, (255, 255, 255), m_movement_rect, 3)

        else:
            pg.draw.rect(self.screen,(255,255,255),k_movement_rect,3)
            pg.draw.rect(self.screen, (0,0, 255), m_movement_rect, 3)

        self.screen.blit(self.option_font.render("Movement Type: ",True,(255,255,255)),(10,200))
        self.screen.blit(self.option_font.render("Keyboard", True, (255, 255, 255)), (350, 200))
        self.screen.blit(self.option_font.render("Mouse", True, (255, 255, 255)), (600, 200))

        if k_movement_rect.collidepoint(mousePos) and event.type == MOUSEBUTTONDOWN: self.movement_type = "keyboard"
        elif m_movement_rect.collidepoint(mousePos) and event.type == MOUSEBUTTONDOWN: self.movement_type = "mouse"

        rand_terrain_rect = Rect(345,300,180,40)
        music_terrain_rect = Rect(595,300,130,40)
        quit_rect = Rect(350,400,100,50)
        if self.terrain_type == "random":
            pg.draw.rect(self.screen, (0,0,255),rand_terrain_rect,3)
            pg.draw.rect(self.screen, (255,255,255),music_terrain_rect,3)
        else:
            pg.draw.rect(self.screen, (0,0,255),music_terrain_rect,3)
            pg.draw.rect(self.screen, (255,255,255),rand_terrain_rect,3)

        pg.draw.rect(self.screen, (255,255,255),quit_rect,3)

        self.screen.blit(self.option_font.render("Terrain Type: ",True,(255,255,255)),(10,300))
        self.screen.blit(self.option_font.render("Random", True, (255, 255, 255)), (350, 300))
        self.screen.blit(self.option_font.render("Music", True, (255, 255, 255)), (600, 300))
        self.screen.blit(self.option_font.render("Back", True, (255,255,255)), (360, 410))

        if rand_terrain_rect.collidepoint(mousePos) and event.type == MOUSEBUTTONDOWN: self.terrain_type = "random"
        elif music_terrain_rect.collidepoint(mousePos) and event.type == MOUSEBUTTONDOWN: self.terrain_type = "music"


        self.current = (1 if self.current==0 else 0)

        if event.type == MOUSEBUTTONDOWN and quit_rect.collidepoint(mousePos):
            self.player.upload_options(self.volume,self.terrain_type,self.movement_type)
            self.options=False

    def personalisation_menu(self,event,mousePos):
        '''Uses a for loop to iter through possible filenames in common format (type+val.png)
        Scales images for larger display on screen, selected items are highlighted
        Updates the players ship and image in real time
        Uploads the options when changed to the player database upon exit'''
        self.screen.fill((0,0,0))

        back_rect = Rect(300,300,400,100)
        pg.draw.rect(self.screen,(255,255,255),back_rect,3)
        self.screen.blit(self.menu_font.render("Back",True,(255,255,255)),(425,318))

        for i in range(1,5):
            ship_filename = "ship"+str(i)+".png"
            ship_img = pg.image.load(ship_filename)
            scaled_ship_img = pg.transform.scale(ship_img, (100,100))
            if Rect((i*200)-50, 50,100,100).collidepoint(mousePos) and event.type == MOUSEBUTTONDOWN:
                self.player.ship = ship_img
                self.player.img_filename = ship_filename
                self.player.update_img()

            projectile_filename = "projectile"+str(i)+".png"
            projectile_img = pg.image.load(projectile_filename)
            scaled_projectile_img = pg.transform.scale(projectile_img, (100,50))
            if Rect((i*200)-50, 200,100,50).collidepoint(mousePos) and event.type == MOUSEBUTTONDOWN:
                self.player.projectile_img = projectile_img
                self.player.projectile_filename = projectile_filename

            self.screen.blit(scaled_ship_img, ((i*200)-50,50))
            self.screen.blit(scaled_projectile_img, ((i*200)-50,200))
            if ship_filename == self.player.img_filename: pg.draw.rect(self.screen, (0, 0, 255),Rect((i * 200) - 50, 50, 100, 100),3)
            if projectile_filename == self.player.projectile_filename: pg.draw.rect(self.screen, (0, 0, 255),Rect((i * 200) - 50, 200, 100, 50),3)

        if back_rect.collidepoint(mousePos) and event.type == MOUSEBUTTONDOWN:
            self.player.upload_options(self.volume, self.movement_type, self.terrain_type)
            self.personalise = False

    def load_options(self):
        '''Uses the player UID to access the database and load the users
        Specific saved options. This is then applied to the player.'''
        if self.player.UID == None: return
        sql = "SELECT Volume,Terrain_Type,Movement_Type FROM Options WHERE UserID=?"
        (vol, t_type, m_type) = self.player.db.get_results(sql,(self.player.UID,))[0]
        self.volume = str(vol)
        pg.mixer.music.set_volume(int(self.volume) / 100)
        self.terrain_type = t_type
        self.movement_type = m_type

    def user_menu(self, event, mousePos):
        '''This renders all rects needed for the menu and draws specific text on each rect to label them.'''
        self.screen.fill(0)
        self.screen.blit(self.font.render(self.player.db.get_username(self.player.UID),True,(255,255,255)),(800,0))
        for button in self.account_buttons:
            pg.draw.rect(self.screen, (255,255,255), button, 3)
        self.screen.blit(self.font.render("Username",True,(255,255,255)),(self.username_rect.x+160,self.username_rect.y))
        self.screen.blit(self.font.render("Password", True, (255, 255, 255)),(self.password_rect.x + 160, self.password_rect.y))
        self.screen.blit(self.font.render("Login",True,(255,255,255)),(self.login_button.x+10,self.login_button.y+5))
        self.screen.blit(self.font.render("Register", True, (255, 255, 255)), (self.register_button.x+2, self.register_button.y+5))
        self.screen.blit(self.font.render(("ASC" if not self.order else "DESC"), True, (255,255,255)),(self.order_rect.x,self.order_rect.y+5))
        self.screen.blit(self.font.render(("UID" if self.search_type else "Username"),True,(255,255,255)),(self.search_type_rect.x,self.search_type_rect.y+5))
        self.screen.blit(self.font.render(self.username_text,True,(255,255,255)),(self.username_rect.x,self.username_rect.y+5))
        self.screen.blit(self.font.render(self.password_text,True,(255,255,255)),(self.password_rect.x,self.password_rect.y+5))
        self.screen.blit(self.font.render(self.search_text,True,(255,255,255)),(self.search_bar.x,self.search_bar.y+5))
        self.screen.blit(self.font.render(self.verification_text,True,(0,0,255)), (self.login_button.x, self.login_button.y+40))
        self.screen.blit(self.font.render("Back",True,(255,255,255)),(self.back_button.x+50,self.back_button.y+5))

        '''The results from the search in the text box is loaded from the database class.
        Depending on the selected catagory of UID or Username, the display text changes
        as well as the search mode for htat catagory. The data is then sorted with an ascending or descending 
        flag within the DB class.'''

        data = (self.player.db.search_by_uid(self.search_text) if self.search_type else self.player.db.search_by_username(self.search_text))
        self.account_text[9] = ("UID" if self.search_type else "Username")
        if self.selected_catagory == 'Username' or self.selected_catagory == 'UID':
            self.selected_catagory = ('Username' if 'Username' in self.account_text else 'UID')
        data = self.player.db.sort_by(self.selected_catagory,data,self.order,self.search_type)

        '''Each menu text is loaded and drawn from a list and displayed on each box. Holding the 
        Mouse on the scroll bar will move the slider to the mouse and scroll based on the y until the 
        mouse is released. The y value is mapped between the minimum and maximum values.'''

        for i in range(0,10):
            self.screen.blit(self.font.render(self.account_text[i],True,(255,255,255)),(300+(i*70),50))
            pg.draw.rect(self.screen,(255,255,255),Rect(295+(i*70),45,70,35),3)

        pg.draw.rect(self.screen, (0,0,255),Rect(295+(self.account_text.index(self.selected_catagory)*70),45,70,35),3)
        pg.draw.rect(self.screen,(0,0,255),(275,45+self.scroll_value,20,20))

        if event.type == pg.MOUSEBUTTONDOWN and self.scroller_rect.collidepoint(mousePos):
            self.scrolling = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.scrolling = False
        if self.scrolling:
            self.scroll_value = min(435, max(0,mousePos[1]-45))

        '''Clicking on a catagory such as Score or Shields will sort by that catagory and be highlighted.
        Clicking Forms such as the login, register or search box will highlight and be ready to type in.
        Using login or register submits the forms. Going back ends the menu and returns.'''

        if event.type == pg.MOUSEBUTTONDOWN:
            if 45 <= mousePos[1] <= 80 and 295 <= mousePos[0] <= 995:
                self.selected_catagory = self.account_text[(mousePos[0]-295)//70]
            elif self.back_button.collidepoint(mousePos):
                self.account_menu = False
                self.verification_text = ""
            elif self.order_rect.collidepoint(mousePos):
                self.order = (True if not self.order else False)
            elif self.search_type_rect.collidepoint(mousePos):
                self.search_type = (True if not self.search_type else False)
            elif self.username_rect.collidepoint(mousePos):
                self.selected_form = self.username_rect
            elif self.password_rect.collidepoint(mousePos):
                self.selected_form = self.password_rect
            elif self.search_bar.collidepoint(mousePos):
                self.selected_form = self.search_bar
            elif self.login_button.collidepoint(mousePos):
                self.player.UID, self.verification_text = self.player.db.login(self.username_text,self.password_text,self.player.UID)

                self.username_text, self.password_text = "", ""
            elif self.register_button.collidepoint(mousePos):
                registered, self.verification_text = self.player.db.register(self.username_text,self.password_text)
                #self.player.UID = self.player.db.login(self.username_text,self.password_text,self.player.UID)
                #self.username_text,self.password_text = "",""

        '''If there is a selected form to type in, keys between a-Z will be accpted in all forms.
        Numbers are only accepted in database searches. Pressing shift means the next will be capital
        and backspace removes the last item.'''
        if self.selected_form != None:
            pg.draw.rect(self.screen,(0,0,255),self.selected_form,3)
            if event.type == KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    if self.selected_form == self.username_rect and len(self.username_text)>0:
                        self.username_text = self.username_text[:-1]
                    elif self.selected_form == self.password_rect and len(self.password_text)>0:
                        self.password_text = self.password_text[:-1]
                    elif self.selected_form == self.search_bar and len(self.search_text)>0:
                        self.search_text = self.search_text[:-1]
                elif event.key == pg.K_LSHIFT:
                    self.next_cap = True
                else:
                    if pg.K_a <= event.key <= pg.K_z:
                        key = (str(chr(event.key).upper()) if self.next_cap else chr(event.key))
                        self.next_cap = False
                        if self.selected_form == self.username_rect: self.username_text += key
                        elif self.selected_form == self.password_rect: self.password_text += key
                        elif self.selected_form == self.search_bar: self.search_text += key
                    elif pg.K_0<= event.key <= pg.K_9:
                        if self.selected_form == self.search_bar:
                            self.search_text += chr(event.key)

        '''Data is displayed on a table with 8 results per screen.
        Each segment will scroll one result past the previous meaning regardless of size,
        each result can be shown.'''

        segment = int(self.scroll_value // (435/(len(data)-8)))
        data = data[segment:9+segment]
        for i in range(0,len(data)):
            for j in range(0,len(data[i])):
                self.screen.blit(self.font.render(str(data[i][j]),True,(255,255,255)),(295+(j*70),45*(i+2)))



if __name__ == "__main__":
    t = Tester(1000, 500)
    while True: t.update()
