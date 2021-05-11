def music_tests(self):
    # For INIT
    from scipy.io.wavfile import read
    pg.init()
    pg.mixer.pre_init()
    pg.mixer.music.load("Pouya.wav")
    pg.mixer.music.play()
    self.average = [(0, 250)]
    ####################################
    tick_rate = 30
    current_time = pg.mixer.music.get_pos() // (1000 / tick_rate)
    length = pg.mixer.Sound("Pouya.wav").get_length() * tick_rate
    input_data = read("Pouya.wav")
    audio = input_data[1]

    allocated = audio[int((len(audio) // length) * (current_time)): int(
        (len(audio) // length) * (int(current_time * (1000 / tick_rate)) + 1) // (1000 / tick_rate))]
    average = sum([i[1] for i in allocated]) / (len(audio) // length)
    if current_time > len(self.average):
        average *= 0.5
        if len(self.average) == 1000 / 5:
            del self.average[0]
            self.average.append((self.average[-1][0] + 5, 250 + average))
            self.average = [(i[0] - 5, i[1]) for i in self.average]

        else:
            self.average.append((self.average[-1][0] + 5, 250 + average))

    if len(self.average) > 1:
        pg.draw.lines(self.screen, (0, 0, 255), 0, self.average, 3)