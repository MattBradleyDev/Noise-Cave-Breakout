#creating a new table in an existing database

import sqlite3

def create_table(db_name,table_name,sql):
    with sqlite3.connect(db_name) as db:
        print(table_name)
        cursor = db.cursor()
        cursor.execute("select name from sqlite_master where name=?",(table_name,))
        result = cursor.fetchall()
        keep_table = True
        if len(result) == 1:
            response = input("The table {0} already exists, do you wish to recreate it? (y/n): ".format(table_name))
            if response == "y":
                keep_table = False
                print("The {0} table will be recreated - all existing data will be lost".format(table_name))
                cursor.execute("drop table if exists {0}".format(table_name))
                db.commit()
            else:
                print("The existing animal table was kept")
        else:
            keep_table = False
        if not keep_table:
            cursor.execute(sql)
            db.commit()

if __name__ == "__main__":
    db_name = "drivingschool.db"
    '''
    sql = """create table Product
            (ProductID integer,
            Name text,
            Price real,
            primary key(ProductID))"""
    '''
    sql = """create table Student
            (StudentID integer,
            Title text,
            Firstname text,
            Lastname text,
            Address text,
            Postcode text,
            TelNo text,
            MobileNo text,
            DateOfBith date,
            TheoryTestDate date,
            PassedTheoryTest bool,
            PracticalTestDate date,
            PassedPracticalTest bool,
            primary key(StudentID))"""

    sql = """create table Instructor
            (InstructorID integer,
            Title text,
            Surname text,
            Forename text,
            Address text,
            Postcode text,
            HomeTelNo text,
            MobileNo text,
            primary key(InstructorID))"""
    sql = """create table Lesson
            (LessonNo integer,
            StudentID integer,
            InstructorID integer,
            DateOfLesson text,
            StartTime text,
            LengthOfLesson text,
            CollectionPoint text,
            DropoffPoint text,
            LessonType text,
            primary key(LessonNo))"""
    sql = """create table Lesson_Type
            (LessonType text,
            Cost float,
            primary key(LessonType))"""
    
    create_table(db_name, "Lesson_Type", sql)
    
