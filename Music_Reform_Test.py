import pygame as pg
from pygame.locals import *
from scipy.io.wavfile import read


class Music:
    def __init__(self):
        pg.mixer.pre_init()
        pg.init()
        self.screen = pg.display.set_mode((1000,700))
        self.clock = pg.time.Clock()
        self.values = []
        self.skip_tick = 0
        self.filename = "Playlist\\music.wav"
        self.filename = "background_music.wav"
        pg.mixer.music.load(self.filename)

        self.length = pg.mixer.Sound(self.filename).get_length() * 30
        self.input_data = read(self.filename)
        self.audio = self.input_data[1]
        pg.mixer.music.play()



        self.view_tick = 100
        self.prev_values = []
        self.increacing = True
        self.colour = [20,20,20]
        self.values2 = []
        self.prev_values2 = []
        self.values3 = []
        self.prev_values3 = []

    def load(self):
        print(len(self.audio))
        print(self.length)
        print(len(self.audio)//self.length)
        vals = []
        prev = []
        step = int(len(self.audio)//self.length)
        for i in range(0,len(self.audio)-step,step):
            values = self.audio[i:i+step]
            val = sum([sum(i)/2 for i in values])/len(values)
            while len(prev)<5: prev.append(val)
            del prev[0]
            prev.append(val)
            val = sum([val]+prev)/6
            vals.append(val/10)
            print(i,len(self.audio))
        for i in vals: print(i)
        self.values = vals
        self.ind = 0
        self.disp = []
        pg.mixer.music.play()

    def update(self):
        event = pg.event.poll()
        keyinput = pg.key.get_pressed()
        self.screen.fill(0)
        self.music_test()
        #self.test()
        self.display()
        pg.display.flip()
        self.clock.tick(30)

    def test(self):
        if self.ind == len(self.values): raise SystemExit
        while len(self.disp)<101:
            self.disp.append([(10*len(self.disp)),350+self.values[self.ind]])
            self.ind+=1
        self.disp.append([(10 * len(self.disp)), 350 + self.values[self.ind]])
        self.ind+=1
        del self.disp[0]
        self.disp = [ [i[0]-10, i[1] ] for i in self.disp]
        pg.draw.lines(self.screen,(255,255,255),0,self.disp,2)



    def music_test(self):
        self.skip_tick = (0 if self.skip_tick == 1 else 1)
        if self.skip_tick == 1: return
        current_time = pg.mixer.music.get_pos() // (1000 / 30)
        allocated = self.audio[int((len(self.audio) // self.length) * (current_time)): int(
            (len(self.audio) // self.length) * (int(current_time * (1000 / 30)) + 30) // (1000 / 30))]
        split = len(allocated)//100
        allocated1 = [i[0] for i in allocated]
        allocated2 = [i[1] for i in allocated]
        allocated3 = [sum(i)/len(i) for i in allocated]
        '''Values 1 = i[0]'''
        new_vals = [allocated1[i*split:(i+1)*split] for i in range(100)]
        new_vals = [(sum(i)/(len(i) if len(i)>1 else 1))/100 for i in new_vals]
        self.values = new_vals

        if len(self.prev_values)<5: self.prev_values.append(new_vals)
        else:
            del self.prev_values[0]
            self.prev_values.append(new_vals)
        '''Values 2 = i[1]'''
        new_vals = [allocated2[i*split:(i+1)*split] for i in range(100)]
        new_vals = [(sum(i)/(len(i) if len(i)>1 else 1))/100 for i in new_vals]
        self.values2 = new_vals

        if len(self.prev_values2)<5: self.prev_values2.append(new_vals)
        else:
            del self.prev_values2[0]
            self.prev_values2.append(new_vals)
        '''Values 3 = Avg i[0]+i[1]'''
        new_vals = [allocated3[i*split:(i+1)*split] for i in range(100)]
        new_vals = [(sum(i)/(len(i) if len(i)>1 else 1))/100 for i in new_vals]
        self.values3 = new_vals

        if len(self.prev_values3)<5: self.prev_values3.append(new_vals)
        else:
            del self.prev_values3[0]
            self.prev_values2.append(new_vals)


        if self.length<=current_time:
            try:
                pg.mixer.music.set_pos(0)
            except:
                pg.mixer.music.load(self.filename)
                self.length = pg.mixer.Sound(self.filename).get_length() * 30
                self.input_data = read(self.filename)
                self.audio = self.input_data[1]
                pg.mixer.music.play()



    def display(self):
        self.screen.fill(0)
        self.colour = (0,0,255)
        self.colour2 = (255,0,0)
        self.colour3 = (0,255,0)
        self.colour4 = (255,255,255)
        self.values = [sum(i)/len(i) for i in zip(*self.prev_values)]
        self.values = [sum(i) / len(i) for i in zip(*self.prev_values2)]
        display_values1 = [(i*10,self.values[i]+150) for i in range(0,len(self.values))]
        if len(display_values1)<2: return
        display_values2 = [(i*10,self.values2[i]+300) for i in range(0,len(self.values2))]
        display_values3 = [(i*10,self.values3[i]+450) for i in range(0,len(self.values3))]
        left_channel = []
        for i in range(0,len(self.values3)):
            left_channel.append(self.values3[i]-self.values2[i])
        '''Values 4 = Diff Values3 Values2'''
        display_values4 = [(i*10,left_channel[i]+600) for i in range(0,len(left_channel))]


        pg.draw.lines(self.screen, self.colour, False, display_values1, 2)
        pg.draw.lines(self.screen, self.colour2, False, display_values2, 2)
        pg.draw.lines(self.screen, self.colour3, False, display_values3, 2)
        pg.draw.lines(self.screen, self.colour4, False, display_values4, 2)

        pg.draw.line(self.screen, self.colour, (0, 150), (1000, 150), 2)
        pg.draw.line(self.screen, self.colour2, (0, 300), (1000, 300), 2)
        pg.draw.line(self.screen, self.colour3, (0, 450), (1000, 450), 2)
        pg.draw.line(self.screen, self.colour4, (0, 600), (1000, 600), 2)





m = Music()
while True: m.update()
