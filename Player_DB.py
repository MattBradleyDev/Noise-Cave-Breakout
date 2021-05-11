import sqlite3
from passlib.apps import custom_app_context as user_password_hash
import string
import scipy.stats,math
import numpy as np
from statistics import mean,stdev
class Database:
    def __init__(self):
        self.database = "user_data.db"
        self.tables = {
            "Users":"""create table Users
        (UserID integer,
        Username text,
        PasswordSalt text,
        Exp integer,
        Level integer,
        primary key (UserID))""",

        "Stats":"""create table Stats
        (StatsID integer,
        Enemies_Killed integer,
        Time_Alive real,
        Shields_Destroyed integer,
        Score integer,
        Bullets_Fired integer,
        Bombs_Fired integer,
        Accuracy real,
        Date_Made text,
        UserID integer,
        foreign key (UserID) REFERENCES Users,
        primary key (StatsID))""",

        "Options":"""create table Options 
        (OptionsID integer,
        ShipName text,
        ProjectileName text,
        Volume integer,
        Terrain_Type text,
        Movement_Type text,
        UserID integer,
        foreign key (UserID) REFERENCES Users,
        primary key (OptionsID))"""
        }

    def create_tables(self):
        '''Creates a table if it does not exist. Will not remake a table'''
        with sqlite3.connect(self.database) as db:
            cursor = db.cursor()
            for table_name in self.tables:
                cursor.execute("SELECT name FROM sqlite_master WHERE name=?", (table_name,))
                sql = self.tables[table_name]
                if len(cursor.fetchall())!=1:
                    cursor.execute(sql)
                    db.commit()

    def run_sql_query(self,sql,data):
        '''Runs query but does not return any results'''
        with sqlite3.connect(self.database) as db:
            cursor = db.cursor()
            cursor.execute(sql, data)
            db.commit()

    def add_user(self,username,password_salt):
        '''Hashes a user psssword to store in the database
        Returns true if the user already exists in the database
        Else inserts a new player and returns false'''
        hashed_password = password_salt
        hashed_password = user_password_hash.hash(password_salt)
        if len(self.get_results("SELECT * from Users WHERE Username=?",(username,)))>0: return True
        sql = "insert into Users (Username,PasswordSalt, Exp, Level) values(?,?,?,?)"
        data = (username, hashed_password,0,1)
        self.run_sql_query(sql,data)
        return False

    def add_stats(self,EnemiesKilled, TimeAlive, ShieldsKilled, Score, BulletsFired, BombsFired, Accuracy, Time, UID):
        '''Stat tracking for each user calculates each statistic
        Inserts it into a new table for statistics linked to the player with UserID'''
        sql = "insert into Stats (Enemies_Killed, Time_Alive, Shields_Destroyed, Score, Bullets_Fired, Bombs_Fired, Accuracy, Date_Made, UserID) values(?,?,?,?,?,?,?,?,?)"
        data = (EnemiesKilled, TimeAlive, ShieldsKilled, Score, BulletsFired, BombsFired, Accuracy, Time, UID)
        self.run_sql_query(sql,data)

    def add_options(self,Ship, Projectile, Vol, Terrain, Movement, UID):
        '''Inserts a new option record into options table for the user with a UID'''
        sql = "insert into Options (ShipName, ProjectileName, Volume, Terrain_Type, Movement_Type, UserID) values(?,?,?,?,?,?)"
        data = (Ship, Projectile, Vol, Terrain, Movement, UID)
        self.run_sql_query(sql, data)

    def update_options(self,Ship, Projectile, Vol,Terrain, Movement, UID):
        '''Updates the current of options for the player so that there is no repeated values or data redundancy'''
        sql = "UPDATE Options SET ShipName=?, ProjectileName=?, Volume=?, Terrain_Type=?, Movement_Type=? WHERE UserID=?"
        data = (Ship,Projectile,Vol,Terrain,Movement,UID)
        self.run_sql_query(sql,data)

    def check_options_exist(self,UID):
        '''Checks if the UID is present in the users table
        Determines the action taken by returning true or false'''
        sql = "SELECT * FROM Options WHERE UserID=?"
        if len(self.get_results(sql,(UID,))) > 0: return True
        return False

    def get_results(self,sql,data=None,all=True):
        '''Runs a SQL query with all results returned back to the user'''
        with sqlite3.connect(self.database) as db:
            cursor = db.cursor()
            cursor.execute(sql) if data is None else cursor.execute(sql, data)
            return (cursor.fetchall() if all else cursor.fetchone()[0])

    def search_by_uid(self,uid):
        '''If there is no ID, the stats for all users are returned
        Else any ID including the given ID will be Searched.'''
        if uid == "":
            sql = "SELECT * FROM Stats"
            res = self.get_results(sql)
        else:
            sql = "SELECT * FROM Stats WHERE UserID GLOB ? ORDER BY UserID ASC, Score ASC"
            data = '*'+uid+'*'
            res = self.get_results(sql,(data,))
        return res

    def search_by_username(self,username):
        '''The username includes all string that contain that username.
        If there is no username all stats are returned, else only those including that name.'''
        if len(username) == 0:
            statSql = "SELECT * FROM Stats"
            res = [list(i) for i in self.get_results(statSql)]
        else:
            statSql = "SELECT * FROM Stats WHERE UserID = ? ORDER BY UserID ASC, Score ASC"
            idSql = "SELECT UserID FROM Users WHERE Username LIKE ?"
            data = '%' + username + '%'
            res = []
            for i in self.get_results(idSql,(data,)):
                for j in self.get_results(statSql, (i[0],)):
                    res.append(list(j))
        nameSql = "SELECT Username FROM Users WHERE UserID=?"
        names = list([self.get_results(nameSql, (str(i[9]),))[0][0] for i in res])
        for i in range(0,len(res)):
            res[i][9] = names[i]
        return res

    def sort_by(self,sort_key,data,desc,search_type):
        '''Using a dict, the catagory is an index to the statistics for each character.
        The data is sorted using an anonymous function to use the index to sort.
        The order is based on desc flag passed in.'''
        key_lookup = {"ID":0,"Enemy":1,"Time":2,"Shield":3,"Score":4,"Bullets":5,"Bombs":6,"Acc":7,"Date":8,("UID" if search_type else "Username"):9}
        data = sorted(data,reverse=desc,key=lambda x:x[key_lookup[sort_key]])
        return data

    def login(self,username,password,guest_id):
        '''Checks hashed passwords against password pulled from DB.
        Returns validation text of success or failure.'''
        sql = "SELECT PasswordSalt FROM Users WHERE Username=?"
        pass_hash = self.get_results(sql,(username,))
        if len(pass_hash)==0: return guest_id, "User Does Not Exist"
        if user_password_hash.verify(password,pass_hash[0][0]):
            user_id = self.get_results("SELECT UserID FROM Users WHERE Username=?",(username,))[0][0]
            if len(self.get_results("SELECT * FROM Options WHERE UserID=?",(user_id,))) == 0:
                self.add_options("ship1.png", "projectile1.png", 100, "music", "mouse", user_id)
            return str(user_id), "Successfully Logged In"

        else: return guest_id, "Password Incorrect"

    def register(self,username,password):
        '''Checks the availability of credentials to existing.
        Sets default settings per user and logs in.'''
        sql = "SELECT Username FROM Users WHERE Username=?"
        username_exists = len(self.get_results(sql,(username,)))>0
        if len(username)==0 or len(password)==0: return False, "Must Be At Least 1 Char"
        if not username_exists:
            self.add_user(username,password)
            uid = self.get_results("SELECT UserID FROM Users WHERE Username=?",(username,),False)
            self.add_options("ship1.png","projectile1.png",100,"music","mouse",uid)
            return True, "Successfully Registered"
        else: return False, "User Already Exists"

    def get_username(self,id):
        '''Gets a username based on user ID'''
        if id==None: return ""
        return self.get_results("SELECT Username FROM Users WHERE UserID=?",(id,),False)

    def delete_user(self,id):
        '''Deletes a user from the DB based on ID'''
        if len(self.get_results("SELECT * FROM Stats WHERE UserID=?",(id,)))==0:
            self.run_sql_query("DELETE FROM Users WHERE UserID=?",(id,))
            self.run_sql_query("DELETE FROM Options WHERE UserID=?",(id,))

    def clear_guests(self):
        '''Removes all guests from the DB which do not have any scores.
        This avoids guests made before being logged in, filling the DB.'''
        sql = "SELECT UserID FROM Users WHERE Username LIKE 'guest%'"
        guests = self.get_results(sql)
        for i in guests:
            if len(self.get_results("SELECT * FROM Stats WHERE UserID=?",(i[0],))) == 0:
                self.delete_user(i[0])

    def get_confidence_interval(self,id):
        '''Uses a sample t-distribution to create a confidence interval based
        on the maximum of 10 or 1/3 top scores at a 90% confidence. Bronze, silver
        and gold are based on the sample mean one confidence width
        below and one confidence width above.'''
        res = self.search_by_uid(id)
        if len(res)<10: return 10000,30000,50000
        sorted_res = self.sort_by("Score",res,True,True)
        sorted_scores = [i[4] for i in sorted_res]
        sorted_scores = sorted_scores[0:max(10,len(sorted_scores)//3)]
        s_mean, standard_error = mean(sorted_scores), scipy.stats.sem(sorted_scores)
        confidence_width = standard_error * scipy.stats.t.ppf(0.90, len(sorted_scores)-1)
        bronze, silver, gold = int(s_mean-confidence_width), int(s_mean), int(s_mean+confidence_width)
        return bronze,silver,gold

