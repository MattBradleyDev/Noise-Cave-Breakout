import random


class Terrain:
    def __init__(self,sw,sh):
        self.width,self.height = sw,sh
        self.get_initial()
        self.col1 = (102, 51, 0)
        self.col2 = (158, 76, 0)

    def get_initial(self):
        '''Gets initial values for the terrain as a flat line as nothing has been generated'''
        self.values = [(0,0)]
        for i in range(0,self.width+10,10):
            self.get_value(i)
        self.values += [(1000,0),(0,0)]
        self.get_subset()

    def get_y(self,y):
        '''Generates a y value based on the previous y value with random offsets
        Offset is based on the previous y value meaning change will remain within a range
        Terrain can never be too large or too small'''
        offset = 0
        if y<30:
            offset = random.randint(10,20)
        elif y > 125:
            offset = random.randint(-20,-10)
        elif 80 < y < 120:
            offset = random.randint(-15,15)
        else: offset = random.choice([-20,20])
        return y + offset

    def get_value(self,x):
        '''Adds a value into the value list from the internal getting y function'''
        self.values.append( (x, self.get_y(self.values[-1][1] ) ) )

    def update_value(self):
        '''Cycles values down an index and adds a new generated value into the end
        Each x value remains the same but y values move down the array'''
        vals = self.values[1:-2]
        x_vals,y_vals = [i[0] for i in vals],[i[1] for i in vals]
        y_vals.append(self.get_y(y_vals[-1]))
        del y_vals[0]
        vals = [(x_vals[i],y_vals[i]) for i in range(0,len(x_vals))]
        self.values = [(0,0)] + vals + [(1000,0),(0,0)]
        self.get_subset()

    def get_subset(self,type="random"):
        '''Creates subset values based on the origional value list
        Bottom values are the reversal of top values which means discrepancy between
        both sets of values is minimised so the terrain will always be passable.
        Music values use a different offset for bottom values'''
        if type == "music":
            self.b_values = [(i[0],500-(50-i[1])) for i in self.values]
            self.alt_b_values = [(i[0],i[1]+12) for i in self.b_values]
            self.alt_values = [(i[0],i[1]-12) for i in self.values]
        else:
            self.b_values = [(i[0],500-i[1]) for i in self.values]
            self.alt_values = [(i[0],i[1]-50) for i in self.values]
            self.alt_b_values = [(i[0],550-i[1]) for i in self.values]

    def get_total(self):
        '''Returns a concatinated list of values to test collision for the player'''
        return self.values + self.b_values + self.alt_b_values + self.alt_values







