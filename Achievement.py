import Player_DB

class Achievement:
    def __init__(self,id):
        self.id = id
        self.db = Player_DB.Database()
        self.get_values()

    def get_values(self):
        b, s, g = self.db.get_confidence_interval(self.id)
        self.scores = [b,s,g]
        self.completed = [False,False,False]

    def update_completed(self,score):
        for i in range(3):
            if self.scores[i] <= score: self.completed[i] = True



