import random
import math
import scipy

class Swarm:
    def __init__(self):
        self.moving_back = False
        self.swarm = []
        self.minimum_distance = 30
        self.target_x = 0
        self.generate_target()
        self.target_time = 0
        self.target_rate = 30

    def get_centre(self,member=None,members=[]):
        '''Returns the average location of the swarm
        If there is no member argument passed then the whole avergae is calclater
        Else the average is without itself'''
        if len(self.swarm) == 0: return (0,0)
        members = [i for i in members if i != member]
        if len(members) == 0: members = self.swarm

        if member is not None:
            cx = (sum(i.rect.x for i in members) - member.rect.x * len(members)) / len(members)
            cy = (sum(i.rect.y for i in members) - member.rect.y * len(members)) / len(members)
            return (cx,cy)
        return (sum(i.rect.x for i in members)//len(members),sum(i.rect.y for i in members)//len(members))

    def get_centre_node(self,member):
        '''Assignes the centre to be the difference between a members target position and a members x position
        Finds a new target each time'''
        member.assign_target(self.targets)
        cx = member.target.x - member.rect.x
        cy = member.target.y - member.rect.y

        return (cx,cy)

    def dump_members(self,cx,cy):
        '''Removes all members too far away from the centre of the swarm'''
        outOfBounds = [i for i in self.swarm if i.get_difference(cx,cy)[0] > 300 and i.get_difference(cx,cy)[1] > 200]
        self.swarm = [i for i in self.swarm if i not in outOfBounds]

    def move_central(self,members,member):
        '''Far away members are moved closer to the centre by applying a proportion of distance
        Increaces velocity based on distance'''
        member.x_velocity -= self.get_centre_node(member)[0] / 100
        member.y_velocity -= self.get_centre_node(member)[1] / 100

    def move_away(self,members,member):
        '''Distance is calculated using the formula SQRT( (x1 - x2) ^2  +  (y1 - y2) ^2 )
        Calculates the internal distance between members
        Averages the distance between close members and moves away from them'''
        totalX,totalY = 0,0
        for i in members:
            otherMemberDistX,otherMemberDistY = member.rect.x - i.rect.x, member.rect.y - i.rect.y
            otherMemberDistX = ((1 if otherMemberDistX>=0 else -1) * math.sqrt(self.minimum_distance))- otherMemberDistX
            otherMemberDistY = ((1 if otherMemberDistY >= 0 else -1) * math.sqrt(self.minimum_distance)) - otherMemberDistY
            totalX += otherMemberDistX
            totalY += otherMemberDistY
        member.x_velocity -= totalX/(len(members) if len(members)>0 else 1)
        member.y_velocity -= totalY/(len(members) if len(members)>0 else 1)

    def move_with(self,members,member):
        '''Moves with other members instead of circling the centre points with positive velocity change'''
        cx, cy = self.get_centre_node(member)
        member.x_velocity += cx / 20
        member.y_velocity += cy / 20

    def control(self,terrain,player):
        if len(self.swarm) == 0: return
        '''Distance is calculated using the formula SQRT( (x1 - x2) ^2  +  (y1 - y2) ^2 )
        Checks the distance against minimum distance to generate close members list
        Movement for each member, i, is based on what other members are close for directional movement
        Members move away from the top and bottom of the terrain to stay on screen
        Members seeking the player have separate movement
        Reloads the swarm array to flush dead members'''
        for i in self.swarm:
            close = [m for m in [j for j in self.swarm if not j.seeking]
                     if not i==m and math.sqrt((i.rect.x - m.rect.x)**2 + (i.rect.y - m.rect.y)**2) < self.minimum_distance]
            for j in [self.move_central, self.move_away, self.move_with]: j(close,i)


        self.steer_from_terrain()
        self.seek_player(player)
        self.swarm = [i for i in self.swarm if not i.dead]
        self.target_rate = len(self.swarm)

    def steer_from_terrain(self):
        '''Adds proportional velocity depending on distance from terrain
        Larger velocities based on distance from the terrain
        Centre movement is deactivated when below a threshhold for normal movement'''
        for member in self.swarm:
            if member.dodgingTerrain:
                member.y_velocity -= (member.rect.y - 250)/50
            if 30 <= member.rect.y <= 470: member.dodgingTerrain = False
            else: member.dodgingTerrain = True

    def generate_target(self,):
        '''Generates a temporary target class to store the x and y of a target object
        A target_x line moves back and forth actoss the screen
        Three target values are generated around the target x, One opposite to it.
        Each target becomes a artificial centre of the swarm'''
        class Target:
            def __init__(self,x,y):
                self.x,self.y = x,y
        self.targets = [Target(self.target_x + random.randint(-100,100),random.randint(100,400)) for i in range(3)]
        for i in self.swarm:
            i.target = random.choice(self.targets)
        if not self.moving_back: self.target_x += 50
        else: self.target_x -= 50
        if self.target_x > 900: self.moving_back = True
        elif self.target_x < 100: self.moving_back = False

    def add_member(self,enemy):
        '''Applys the identifier to enemies added into the swarm'''
        enemy.inSwarm = True
        self.swarm.append(enemy)

    def seek_player(self,player):
        '''Generates seeking enemies for every 3 members alive
        When a member dies, another seeking target takes its place
        Proportionally moves toward the player based on distance
        At different distances speed is increaced due to working with proportions
        If the player has been hit and is invunderable, seeking members instead flee from the player
        Fleeing enemies remain targeting the player afterwards'''
        if len(self.swarm) < 3: return
        while len([i for i in self.swarm if i.seeking]) < len(self.swarm)//3:
            i = random.choice([i for i in self.swarm if not i.seeking])
            i.seeking = True
        for i in [i for i in self.swarm if i.seeking]:
            i.x_velocity, i.y_velocity = (player.rect.x - i.rect.x) / 20, (player.rect.y - i.rect.y) / 20
            distance = abs(math.sqrt( (player.rect.x - i.rect.x) ** 2 + (player.rect.y - i.rect.y) ** 2 ))


            if distance < 100:
                i.x_velocity, i.y_velocity = (player.rect.x - i.rect.x) / 10, (player.rect.y - i.rect.y) / 10
            i.x_velocity = ((i.rect.x - player.rect.x)/50 if player.invunerable else i.x_velocity)
            i.y_velocity = ((i.rect.y - player.rect.y)/50 if player.invunerable else i.y_velocity)









