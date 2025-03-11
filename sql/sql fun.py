# Copyright © PG Online 2023
# All rights reserved


import sqlite3
import os
import time

currentSelectedDB = "earthquakes.db"
connection = sqlite3.connect(currentSelectedDB)
cursor = connection.cursor()


def showDBInfo(db):
    if db == "countries.db":
        return """This database has one table
Real data is used in this database from 2023.

countries
---------
id (primary key)
name (name of country)
population
area (land area in km2)
life_expect (life expectancy in years)
health_spend (health spend as a percentage of GDP)
unemploy (unemployment as a percentage)
gdp (Gross Domestic Product in billions of dollars)
eu (1 means a member of the EU, 0 means not a member)
g7 (1 means a member of the G7, 0 means not a member)

"""
    elif db == "earthquakes.db":
        return """This database has one table.
Real data is used in this database.

earthquakes
-----------
id (primary key)
location
country
magnitude
year
"""

    elif db == "tunnels.db":
        return """This database has one table.
Real data is used in this database.

tunnels
-------
id (primary key)
name
country
length
year
type
"""

    elif db == "carreg.db":
        return """This database has one table.
This database uses fictitious data.

carreg
------
first_name
last_name
car_reg
car_colour
car_make
"""

    elif db == "films.db":
        return """This database has two tables
Real data is used in this database.

films
-----
id (primary key)
title
year
duration
certificate
director
rating

directors
---------
id (primary key)
first_name
last_name
birth_year
"""
    else:
        return "Database information not found"


def pause(t):
    time.sleep(t)


def clearScreen(t):
    time.sleep(t)
    os.system('cls' if os.name == 'nt' else 'clear')
    print("------ Currently selected database:", currentSelectedDB, "-------")


def printTable(table):
    # procedure to print the results of a query as a table
    widths = []
    columns = []
    bar = '|'
    separator = '+'

    if len(table) == 0:
        print("0 rows returned")
    else:

        # go through all records to find the largest field length for each field
        # save these in widths list
        firstRow = True
        for row in table:
            for i in range(len(row)):
                if firstRow:
                    widths.append(len(str(row[i])))
                elif len(str(row[i])) > widths[i]:
                    widths[i] = len(str(row[i]))
            firstRow = False

        # save the field names in columns list
        for i in range(len(cursor.description)):
            nextRow = cursor.description[i]
            columns.append(nextRow[0])
            if len(columns[i]) > widths[i]:
                widths[i] = len(columns[i])

        for w in widths:
            bar += " %-" + "%ss |" % (w,)
            separator += '-' * w + '--+'

        print(separator)
        print(bar % tuple(columns))
        print(separator)
        for row in table:
            print(bar % row)
        print(separator)

        print("Number of records:", len(table))


def runSQL(name, sql):
    try:
        global connection
        global cursor
        connection.close()
        connection = sqlite3.connect(name)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
    except sqlite3.Error as e:
        print("SQL error: %s" % (" ".join(e.args)))


def dropAll():
    pause(0.2)
    sql = """DROP TABLE IF EXISTS "earthquakes";"""
    runSQL("earthquakes.db", sql)
    print("Removed data from earthquakes")
    pause(0.2)
    sql = """DROP TABLE IF EXISTS "countries";"""
    runSQL("countries.db", sql)
    print("Removed data from countries")
    pause(0.2)
    sql = """DROP TABLE IF EXISTS "carreg";"""
    runSQL("carreg.db", sql)
    print("Removed data from carreg")
    pause(0.2)
    sql = """DROP TABLE IF EXISTS "films";"""
    runSQL("films.db", sql)
    print("Removed data from films")
    pause(0.2)
    sql = """DROP TABLE IF EXISTS "directors";"""
    runSQL("films.db", sql)
    print("Removed data from directors")
    pause(0.2)
    sql = """DROP TABLE IF EXISTS "tunnels";"""
    runSQL("tunnels.db", sql)
    print("Removed data from tunnels")


def makeDatabases():
    print("Creating databases")
    print("Building earthquakes database")
    pause(0.2)
    makeEarthquakes()
    print("Building tunnels database")
    pause(0.2)
    makeTunnels()
    print("Building countries database")
    pause(0.2)
    makeCountries()
    print("Building carreg database")
    pause(0.2)
    makeCarReg()
    print("Building films database")
    pause(0.2)
    makeFilms()

    global currentSelectedDB
    currentSelectedDB = "earthquakes.db"
    connectToDB()

    input("\nPress enter to continue")


def restoreDatabases():
    clearScreen(0)
    dropAll()
    print("----------")
    makeDatabases()


def connectToDB():
    global connection
    connection.close()
    connection = sqlite3.connect(currentSelectedDB)
    global cursor
    cursor = connection.cursor()


def selectDatabase():
    dbName = ""
    clearScreen(0)
    print("Select Database")
    print()
    print("1. Earthquakes database")
    print("2. Tunnels database")
    print("3. Countries database")
    print("4. Car registration database")
    print("5. Films database")
    print("6. Return to menu")
    print()
    choice = input("Enter your choice: ")
    global currentSelectedDB
    if choice == "1":
        currentSelectedDB = "earthquakes.db"
    elif choice == "2":
        currentSelectedDB = "tunnels.db"
    elif choice == "3":
        currentSelectedDB = "countries.db"
    elif choice == "4":
        currentSelectedDB = "carreg.db"
    elif choice == "5":
        currentSelectedDB = "films.db"
    elif choice.lower() == "m" or choice == "6":
        print("Returning to menu")
    else:
        print("Menu choice not available")
        selectDatabase()
    if choice != "6" and choice.lower() != "m":
        connectToDB()
        enterSQL()


def enterSQL():
    endCommands = False
    clearScreen(0)
    print(showDBInfo(currentSelectedDB))
    while not endCommands:
        print("Enter SQL statements (enter 'm' for main menu or 'i' for database information)")
        sql = input("Enter your SQL statement:\n")
        if sql.lower() == "m":
            endCommands = True
        elif sql.lower() == "i":
            print("\n" * 5, "---------------------------", currentSelectedDB, "-------------------------------", "\n")
            print(showDBInfo(currentSelectedDB))
        else:
            try:
                cursor.execute(sql)
                connection.commit()
                results = cursor.fetchall()
                print()
                printTable(results)
            except sqlite3.Error as e:
                print("SQL error: %s" % (" ".join(e.args)))

            print("SQL statement entered:", sql)
            print("-" * 70)
            print()


def enterInjection():
    global currentSelectedDB
    currentSelectedDB = "carreg.db"
    connectToDB()

    endCommands = False
    clearScreen(0)
    print("Welcome to the car registration database")
    print("Just enter the number plate to find the owner details.")
    print("Enter 'm' to return to the main menu.")

    while not endCommands:
        numberPlate = input("Enter number plate: ")
        if numberPlate.lower() == "m":
            endCommands = True
        else:
            sqlCommands = numberPlate.split(";")
            firstCommand = True
            for sql in sqlCommands:
                if firstCommand:
                    sql = "SELECT * FROM carreg WHERE car_reg=\"" + sql + "\""
                    firstCommand = False
                try:
                    print("Processing behind the scenes:", sql)
                    cursor.execute(sql)
                    connection.commit()
                    results = cursor.fetchall()
                    print()
                    printTable(results)
                except sqlite3.Error as e:
                    print("SQL error: %s" % (" ".join(e.args)))


def endProgram():
    print("Thank you for using SQL statement")


def showMenu():
    clearScreen(1)
    print("SQL database menu")
    print("1. Restore the databases")
    print("2. Select database")
    print("3. Enter SQL statements")
    print("4. SQL injection")
    print("5. Quit program")
    print()
    choice = input("Enter your choice: ")

    if choice == "1":
        restoreDatabases()
        showMenu()
    elif choice == "2":
        selectDatabase()
        showMenu()
    elif choice == "3":
        enterSQL()
        showMenu()
    elif choice == "4":
        enterInjection()
        showMenu()
    elif choice == "5":
        endProgram()
    else:
        print("Menu choice not available")
        showMenu()


def main():
    print("Do you want to (re)build the databases? (y/n)\n")
    print("(Re)building the databases will remove any previous data you")
    print("have saved to them.\n")
    print("If this is your first time using the program, enter 'y'\n")

    buildDatabases = input("Rebuild databases (y/n): ")
    if buildDatabases.lower() == 'y' or buildDatabases.lower() == 'yes':
        restoreDatabases()

    showMenu()

    input("Press enter to quit")


def makeEarthquakes():
    sql = """CREATE TABLE IF NOT EXISTS "earthquakes" (
	"id"	INTEGER,
	"location"	TEXT,
	"country"	TEXT,
	"magnitude"	REAL,
	"year"	INTEGER,
	PRIMARY KEY("id")
);"""
    runSQL("earthquakes.db", sql)

    sql = """INSERT INTO "earthquakes" ("id","location","country","magnitude","year") VALUES (1,'Manchester','UK',4.3,2002),
 (2,'Bio-Bio','Chile',9.5,1960),
 (3,'West coast','Northern Sumatra',8.2,2012),
 (4,'Coast of Chiapas','Mexico',8.2,2017),
 (5,'Illapel','Chile',8.3,2015),
 (6,'Iquique','Chile',8.2,2014),
 (7,'Wombourn','UK',4.8,2002),
 (8,'West coast','Northern Sumatra',8.6,2012),
 (9,'Warwick','UK',4.0,2000),
 (10,'Winchester','UK',2.9,2015),
 (11,'Quirihue','Chile',8.8,2010),
 (12,'Matavai','Samoa',8.1,2009),
 (13,'Market Rasen','UK',4.8,2008),
 (14,'Southern Alaska','USA',9.2,1964),
 (15,'West coast','Northern Sumatra',9.1,2004),
 (16,'Lympne','UK',4.6,2007),
 (17,'East Honshu Coast','Japan',9.1,2011),
 (18,'East Kamchatka Coast','Russia',9.0,1952),
 (19,'Souuthern Peru Coast','Peru',8.4,2001),
 (20,'Clydach','UK',4.3,2018),
 (21,'East Honshu Coast','Japan',8.4,1933),
 (22,'Kermadec Islands','New Zealand',8.1,2021),
 (23,'Cheadle','UK',2.7,2023),
 (24,'Navarro','Peru',8.0,2019);
"""
    runSQL("earthquakes.db", sql)


def makeTunnels():
    sql = """CREATE TABLE IF NOT EXISTS "tunnels" (
	"id"	INTEGER,
	"name"	TEXT,
	"country"	TEXT,
	"length"	REAL,
	"year"	INTEGER,
	"type"	TEXT,
	PRIMARY KEY("id")
);"""
    runSQL("tunnels.db", sql)

    sql = """INSERT INTO "tunnels" ("id","name","country","length","year","type") VALUES (1,'Harecastle Tunnel, Staffordshire','UK',1.7,1827,'Canal'),
 (2,'Line 18, Guangzhou Metro','China',36.2,2021,'UG'),
 (3,'Yamate Tunnel','Japan',11.3,2015,'Road'),
 (4,'Zhongnanshan Tunnel','China',11.2,2007,'Road'),
 (5,'Line 3, Guangzhou Metro','China',36.0,2018,'UG'),
 (6,'Line 6, Chengdu Metro','China',42.4,2020,'UG'),
 (7,'Bolshaya K. line, Moscow Metro','Moscow',38.0,2023,'UG'),
 (8,'Severn Tunnel','UK',4.4,1886,'Rail'),
 (9,'Higham and Strood Tunnel','UK',2.2,1824,'Rail'),
 (10,'Mt. Blanc','France',7.2,1965,'Road'),
 (11,'Balcombe tunnel, West Sussex','UK',0.6,1841,'Rail'),
 (12,'Northern Line, London Tube','UK',17.2,1940,'UG'),
 (13,'Gotthard Base Tunnel','Switzerland',35.5,2016,'Rail'),
 (14,'Victoria line, London Tube','UK',13.05,1971,'UG'),
 (15,'Yulhyeon Tunnel','South Korea',31.3,2016,'Rail'),
 (16,'Songshan Lake Tunnel','China',22.0,2016,'Rail'),
 (17,'Preston Brook Tunnel, Cheshire','UK',0.7,1775,'Canal'),
 (18,'Line 10, Beijing Subway','China',35.5,2012,'UG'),
 (19,'Line 5, Seoul Subway','South Korea',29.6,1996,'UG'),
 (20,'Seikan Tunnel','Japan',33.5,1988,'Rail'),
 (21,'Channel Tunnel','UK',31.4,1994,'Rail'),
 (22,'St. Gotthard','Switzerland',10.5,1980,'Road'),
 (23,'Dudley Tunnel, West Midlands','UK',1.8,1792,'Canal'),
 (24,'Laerdal','Norway',15.2,2000,'Road');
"""
    runSQL("tunnels.db", sql)


def makeCountries():
    sql = """CREATE TABLE IF NOT EXISTS "countries" (
	"id"	INTEGER,
	"name"	TEXT,
	"population"	INTEGER,
	"area"	INTEGER,
	"life_expect"	REAL,
	"health_spend"	REAL,
	"unemploy"	REAL,
	"gdp"	INTEGER,
	"eu"	INTEGER,
	"g7"	INTEGER,
	PRIMARY KEY("id")
);"""
    runSQL("countries.db", sql)

    sql = """INSERT INTO "countries" ("id","name","population","area","life_expect","health_spend","unemploy","gdp","eu","g7") VALUES (1,'China',1367485388,9596960,75.41,5.4,4.1,17630,NULL,NULL),
 (2,'India',1251695584,3287263,68.13,4.0,8.6,7277,NULL,NULL),
 (3,'United States',321368864,9826675,79.68,17.9,6.2,17460,NULL,1),
 (4,'Indonesia',255993674,1904569,72.45,3.0,5.7,2554,NULL,NULL),
 (5,'Brazil',204259812,8514877,73.53,9.3,5.5,3073,NULL,NULL),
 (6,'Pakistan',199085847,796095,67.39,2.7,6.8,884.2,NULL,NULL),
 (7,'Nigeria',181562056,923768,53.02,6.1,23.9,1058,NULL,NULL),
 (8,'Bangladesh',168957745,143998,70.94,3.6,5.0,535.6,NULL,NULL),
 (9,'Russia',142423773,17098242,70.47,6.3,4.9,3568,NULL,NULL),
 (10,'Japan',126919659,377915,84.74,10.1,3.6,4807,NULL,1),
 (11,'Mexico',121736809,1964375,75.65,6.1,4.7,2143,NULL,NULL),
 (12,'Philippines',100998376,300000,68.96,4.6,7.2,694.6,NULL,NULL),
 (13,'Ethiopia',99465819,1104300,61.48,3.8,17.5,139.4,NULL,NULL),
 (14,'Vietnam',94348835,331210,73.16,6.6,3.1,509.5,NULL,NULL),
 (15,'Egypt',88487396,1001450,73.7,5.0,13.4,945.4,NULL,NULL),
 (16,'Iran',81824270,1648195,71.15,6.7,10.3,1284,NULL,NULL),
 (17,'Germany',80854408,357022,80.57,11.3,5.0,3621,1,1),
 (18,'Turkey',79414269,783562,74.57,6.3,9.4,1512,NULL,NULL),
 (19,'Congo, Dem Rep',79375136,2344858,56.93,5.6,NULL,55.73,NULL,NULL),
 (20,'Thailand',67976405,513120,74.43,3.9,1.0,990.1,NULL,NULL),
 (21,'France',66553766,643801,81.75,11.7,9.7,2587,1,1),
 (22,'United Kingdom',64088222,243610,80.54,9.4,5.7,2435,NULL,1),
 (23,'Italy',61855120,301340,82.12,9.2,12.5,2066,1,1),
 (24,'Burma',56320206,676578,66.29,1.8,5.1,244.3,NULL,NULL),
 (25,'South Africa',53675563,1219090,62.34,8.8,25.0,683.1,NULL,NULL),
 (26,'Tanzania',51045882,947300,61.71,7.0,NULL,92.53,NULL,NULL),
 (27,'Korea, South',49115196,99720,80.04,7.5,3.3,1786,NULL,NULL),
 (28,'Spain',48146134,505370,81.57,9.6,24.3,1534,1,NULL),
 (29,'Colombia',46736728,1138910,75.48,6.8,9.2,642.7,NULL,NULL),
 (30,'Kenya',45925301,580367,63.77,4.7,40.0,134.7,NULL,NULL),
 (31,'Ukraine',44429471,603550,71.57,7.6,8.8,373.1,NULL,NULL),
 (32,'Argentina',43431886,2780400,77.69,8.5,7.7,927.4,NULL,NULL),
 (33,'Algeria',39542166,2381741,76.59,5.2,9.7,552.6,NULL,NULL),
 (34,'Poland',38562189,312685,77.4,6.7,12.7,941.4,1,NULL),
 (35,'Uganda',37101745,241038,54.93,8.0,NULL,66.65,NULL,NULL),
 (36,'Iraq',37056169,438317,74.85,3.6,16.0,505.4,NULL,NULL),
 (37,'Sudan',36108853,1861484,63.68,7.2,20.0,159.5,NULL,NULL),
 (38,'Canada',35099836,9984670,81.76,10.9,6.9,1579,NULL,1),
 (39,'Morocco',33322699,446550,76.71,6.4,9.6,254.4,NULL,NULL),
 (40,'Afghanistan',32564342,652230,50.87,8.6,35.0,61.69,NULL,NULL),
 (41,'Nepal',31551305,147181,67.52,5.5,46.0,66.92,NULL,NULL),
 (42,'Malaysia',30513848,329847,74.75,4.0,2.9,746.8,NULL,NULL),
 (43,'Peru',30444999,1285216,73.48,5.1,7.6,376.7,NULL,NULL),
 (44,'Venezuela',29275460,912050,74.54,4.6,7.8,545.7,NULL,NULL),
 (45,'Uzbekistan',29199942,447400,73.55,5.9,4.9,170.3,NULL,NULL),
 (46,'Saudi Arabia',27752316,2149690,75.05,3.2,11.2,1616,NULL,NULL),
 (47,'Yemen',26737317,527968,65.18,5.5,27.0,106,NULL,NULL),
 (48,'Ghana',26327649,238533,66.18,5.2,11.0,109.4,NULL,NULL),
 (49,'Mozambique',25303113,799380,52.94,6.4,17.0,29.76,NULL,NULL),
 (50,'Korea, North',24983205,120538,70.11,NULL,NULL,40,NULL,NULL),
 (51,'Madagascar',23812681,587041,65.55,4.1,NULL,33.64,NULL,NULL),
 (52,'Cameroon',23739218,475440,57.93,5.1,30.0,67.23,NULL,NULL),
 (53,'Taiwan',23415126,35980,79.98,NULL,3.8,1022,NULL,NULL),
 (54,'Cote d''Ivoire',23295302,322463,58.34,7.1,NULL,71.95,NULL,NULL),
 (55,'Australia',22751014,7741220,82.15,9.1,6.0,1100,NULL,NULL),
 (56,'Sri Lanka',22053488,65610,76.56,3.3,4.2,217.1,NULL,NULL),
 (57,'Romania',21666350,238391,74.92,5.1,7.0,386.5,1,NULL),
 (58,'Angola',19625353,1246700,55.63,3.5,NULL,175.5,NULL,NULL),
 (59,'Burkina Faso',18931686,274200,55.12,6.2,77.0,30.08,NULL,NULL),
 (60,'Kazakhstan',18157122,2724900,70.55,4.2,5.1,420.6,NULL,NULL),
 (61,'Niger',18045729,1267000,55.13,7.2,NULL,17.67,NULL,NULL),
 (62,'Malawi',17964697,118484,60.66,9.2,NULL,13.76,NULL,NULL),
 (63,'Chile',17508260,756102,78.61,7.2,6.5,410.3,NULL,NULL),
 (64,'Syria',17064854,185180,74.69,3.4,33.0,107.6,NULL,NULL),
 (65,'Mali',16955536,1240192,55.34,5.8,30.0,27.1,NULL,NULL),
 (66,'Netherlands',16947904,41543,81.23,12.4,7.2,798.1,1,NULL),
 (67,'Ecuador',15868396,283561,76.56,6.4,5.0,182,NULL,NULL),
 (68,'Cambodia',15708756,181035,64.14,5.4,0.0,50.25,NULL,NULL),
 (69,'Zambia',15066266,752618,52.15,6.5,15.0,61.79,NULL,NULL),
 (70,'Guatemala',14918999,108889,72.02,6.7,4.1,118.7,NULL,NULL),
 (71,'Zimbabwe',14229541,390757,57.05,NULL,95.0,26.88,NULL,NULL),
 (72,'Senegal',13975834,196722,61.32,5.0,48.0,33.68,NULL,NULL),
 (73,'Rwanda',12661733,26338,59.67,10.7,NULL,18.7,NULL,NULL),
 (74,'South Sudan',12042910,644329,NULL,2.6,NULL,23.31,NULL,NULL),
 (75,'Guinea',11780162,245857,60.08,6.3,NULL,15.31,NULL,NULL),
 (76,'Chad',11631456,1284000,49.81,3.5,NULL,29.85,NULL,NULL),
 (77,'Belgium',11323973,30528,80.88,10.8,8.5,467.1,1,NULL),
 (78,'Tunisia',11037225,163610,75.89,7.0,15.2,125.1,NULL,NULL),
 (79,'Cuba',11031433,110860,78.39,8.6,3.6,128.5,NULL,NULL),
 (80,'Portugal',10825309,92090,79.16,9.4,14.2,276,1,NULL),
 (81,'Bolivia',10800882,1098581,68.86,5.8,7.3,70.38,NULL,NULL),
 (82,'Greece',10775643,131957,80.43,9.3,26.8,284.3,1,NULL),
 (83,'Burundi',10742276,27830,60.09,8.1,NULL,8.396,NULL,NULL),
 (84,'Czech Republic',10644842,78867,78.48,7.7,7.9,299.7,1,NULL),
 (85,'Somalia',10616380,637657,51.96,NULL,NULL,5.896,NULL,NULL),
 (86,'Dominican Republic',10478756,48670,77.97,5.4,14.6,135.7,NULL,NULL),
 (87,'Benin',10448647,112622,61.47,4.5,NULL,19.85,NULL,NULL),
 (88,'Haiti',10110019,27750,63.51,6.4,40.6,18.54,NULL,NULL),
 (89,'Hungary',9897541,93028,75.69,7.8,7.1,239.9,1,NULL),
 (90,'Sweden',9801616,450295,81.98,9.6,7.9,434.2,1,NULL),
 (91,'Azerbaijan',9780780,86600,72.2,5.4,5.4,168.4,NULL,NULL),
 (92,'Belarus',9589689,207600,72.48,5.0,1.0,171.2,NULL,NULL),
 (93,'Honduras',8746673,112090,71.0,8.6,4.3,38.95,NULL,NULL),
 (94,'Austria',8665550,83871,81.39,11.5,4.5,386.9,1,NULL),
 (95,'Tajikistan',8191958,143100,67.39,5.8,2.5,22.22,NULL,NULL),
 (96,'Switzerland',8121830,41277,82.5,11.3,3.2,444.7,NULL,NULL),
 (97,'Jordan',8117564,89342,74.35,9.8,12.3,79.77,NULL,NULL),
 (98,'Israel',8049314,20770,82.27,7.5,6.6,268.3,NULL,NULL),
 (99,'Togo',7552318,56785,64.51,8.6,NULL,10.18,NULL,NULL),
 (100,'Bulgaria',7186893,110879,74.39,7.4,11.0,123.3,1,NULL),
 (101,'Serbia',7176794,77474,75.26,10.5,26.1,90.32,NULL,NULL),
 (102,'Hong Kong',7141106,1108,82.86,NULL,3.1,400.6,NULL,NULL),
 (103,'Laos',6911544,236800,63.88,2.9,1.3,34.48,NULL,NULL),
 (104,'Paraguay',6783272,406752,76.99,10.3,7.3,57.87,NULL,NULL),
 (105,'Papua New Guinea',6672429,462840,67.03,5.2,1.9,18.11,NULL,NULL),
 (106,'Eritrea',6527689,117600,63.81,2.6,8.6,7.855,NULL,NULL),
 (107,'Libya',6411776,1759540,76.26,3.9,30.0,103.3,NULL,NULL),
 (108,'Lebanon',6184701,10400,77.4,7.3,NULL,80.51,NULL,NULL),
 (109,'El Salvador',6141350,21041,74.42,6.7,6.2,50.9,NULL,NULL),
 (110,'Nicaragua',5907881,130370,72.98,8.2,7.4,29.85,NULL,NULL),
 (111,'Sierra Leone',5879098,71740,57.79,15.1,NULL,12.89,NULL,NULL),
 (112,'UAE',5779760,83600,77.29,2.8,2.4,605,NULL,NULL),
 (113,'Singapore',5674472,697,84.68,4.7,1.9,445.2,NULL,NULL),
 (114,'Kyrgyzstan',5664939,199951,70.36,7.1,8.6,19.29,NULL,NULL),
 (115,'Denmark',5581503,43094,79.25,11.2,5.2,248.7,1,NULL),
 (116,'Finland',5476922,338145,80.77,9.1,8.6,221.5,1,NULL),
 (117,'Slovakia',5445027,49035,76.88,7.8,12.7,149.9,1,NULL),
 (118,'Central African Rep',5391539,622984,51.81,3.8,8.0,2.861,NULL,NULL),
 (119,'Turkmenistan',5231422,488100,69.78,2.0,60.0,82.15,NULL,NULL),
 (120,'Norway',5207689,323802,81.7,9.0,3.4,339.5,NULL,NULL),
 (121,'Georgia',4931226,69700,75.95,9.2,14.9,34.27,NULL,NULL),
 (122,'Ireland',4892305,70273,80.68,8.1,11.3,224.7,1,NULL),
 (123,'Costa Rica',4814144,51100,78.4,10.1,8.5,71.21,NULL,NULL),
 (124,'Congo, Rep',4755097,342000,58.79,3.2,53.0,28.09,NULL,NULL),
 (125,'Croatia',4464844,56594,76.61,6.8,21.0,87.3,1,NULL),
 (126,'New Zealand',4438393,267710,81.05,10.3,5.9,158.7,NULL,NULL),
 (127,'Liberia',4195666,111369,58.6,15.5,85.0,3.771,NULL,NULL),
 (128,'Bosnia and Herz.',3867055,51197,76.55,9.9,44.3,38.08,NULL,NULL),
 (129,'Panama',3657024,75420,78.47,7.6,4.5,76.95,NULL,NULL),
 (130,'Puerto Rico',3598357,13790,79.25,NULL,16.0,64.84,NULL,NULL),
 (131,'Mauritania',3596702,1030700,62.65,6.4,31.0,12.86,NULL,NULL),
 (132,'Moldova',3546847,33851,70.42,11.7,6.2,17.19,NULL,NULL),
 (133,'Uruguay',3341893,176215,77.0,8.9,6.7,69.78,NULL,NULL),
 (134,'Oman',3286936,309500,75.21,2.6,15.0,163.6,NULL,NULL),
 (135,'Armenia',3056382,29743,74.37,4.5,15.9,24.26,NULL,NULL),
 (136,'Albania',3029278,28748,78.13,6.0,13.3,30.66,NULL,NULL),
 (137,'Mongolia',2992908,1564116,69.29,6.3,8.8,29.71,NULL,NULL),
 (138,'Jamaica',2950210,10991,73.55,5.9,13.6,24.28,NULL,NULL),
 (139,'Lithuania',2884433,65300,74.69,6.7,11.1,78.95,1,NULL),
 (140,'Kuwait',2788534,17818,77.82,2.5,3.0,283.9,NULL,NULL),
 (141,'West Bank',2785366,5860,75.91,NULL,16.0,20.12,NULL,NULL),
 (142,'Namibia',2212307,824292,51.62,8.3,27.4,23.59,NULL,NULL),
 (143,'Qatar',2194817,11586,78.59,2.2,0.4,323.2,NULL,NULL),
 (144,'Botswana',2182719,581730,54.18,5.3,17.8,33.62,NULL,NULL),
 (145,'Macedonia',2096015,25713,76.02,7.1,28.0,27.41,NULL,NULL),
 (146,'Latvia',1986705,64589,74.23,6.0,9.5,48.59,1,NULL),
 (147,'Slovenia',1983412,20273,78.01,8.8,13.6,60.54,NULL,NULL),
 (148,'Gambia, The',1967709,11295,64.6,5.0,NULL,3.362,NULL,NULL),
 (149,'Lesotho',1947701,30355,52.86,11.6,28.1,5.589,NULL,NULL),
 (150,'Kosovo',1870981,10887,NULL,NULL,30.9,16.89,NULL,NULL),
 (151,'Gaza Strip',1869055,360,74.87,NULL,45.1,NULL,NULL,NULL),
 (152,'Guinea-Bissau',1726170,36125,50.23,5.9,NULL,2.502,NULL,NULL),
 (153,'Gabon',1705336,267667,52.04,3.5,21.0,34.28,NULL,NULL),
 (154,'Swaziland',1435613,17364,51.05,8.5,40.0,8.672,NULL,NULL),
 (155,'Bahrain',1346613,760,78.73,3.9,3.8,61.56,NULL,NULL),
 (156,'Mauritius',1339827,2040,75.4,4.8,8.0,23.42,NULL,NULL),
 (157,'Estonia',1265420,45228,76.47,5.9,8.6,35.4,1,NULL),
 (158,'Timor-Leste',1231116,14874,67.72,4.3,18.4,8.364,NULL,NULL),
 (159,'Trinidad and Tobago',1222363,5128,72.59,5.4,5.3,42.23,NULL,NULL),
 (160,'Cyprus',1189197,9251,78.51,7.3,15.9,24.94,1,NULL),
 (161,'Fiji',909389,18274,72.43,4.0,7.6,7.292,NULL,NULL),
 (162,'Djibouti',828324,23200,62.79,8.8,60.0,2.858,NULL,NULL),
 (163,'Comoros',780971,2235,63.85,4.5,20.0,1.211,NULL,NULL),
 (164,'Bhutan',741919,38394,69.51,3.8,2.9,5.867,NULL,NULL),
 (165,'Equatorial Guinea',740743,28051,63.85,4.7,22.3,25.33,NULL,NULL),
 (166,'Guyana',735222,214969,68.09,6.6,11.0,5.498,NULL,NULL),
 (167,'Montenegro',647073,13812,NULL,7.6,19.1,9.499,NULL,NULL),
 (168,'Solomon Islands',622469,28896,75.12,8.0,NULL,1.046,NULL,NULL),
 (169,'Macau',592731,28,84.51,NULL,1.9,51.68,NULL,NULL),
 (170,'Suriname',579633,163820,71.97,5.9,9.0,9.24,NULL,NULL),
 (171,'Western Sahara',570866,266000,62.64,NULL,NULL,0.9065,NULL,NULL),
 (172,'Luxembourg',570252,2586,82.17,6.9,7.1,50.65,1,NULL),
 (173,'Cabo Verde',545993,4033,71.85,3.9,21.0,3.286,NULL,NULL),
 (174,'Brunei',429646,5765,76.97,2.3,2.6,32.11,NULL,NULL),
 (175,'Malta',413965,316,80.25,9.1,5.9,13.38,1,NULL),
 (176,'Maldives',393253,298,75.37,8.5,11.0,4.254,NULL,NULL),
 (177,'Belize',347369,22966,68.59,5.8,15.5,2.907,NULL,NULL),
 (178,'Iceland',331918,103000,82.97,9.1,4.5,13.81,NULL,NULL),
 (179,'Bahamas, The',324597,13880,72.2,7.5,16.2,9.034,NULL,NULL),
 (180,'Barbados',290604,430,75.18,6.3,11.5,4.513,NULL,NULL),
 (181,'French Polynesia',282703,4167,76.98,NULL,21.8,7.15,NULL,NULL),
 (182,'Vanuatu',272264,12189,73.06,3.6,1.7,0.687,NULL,NULL),
 (183,'New Caledonia',271615,18575,77.5,NULL,17.1,11.1,NULL,NULL),
 (184,'Samoa',197773,2831,73.46,6.8,NULL,0.995,NULL,NULL),
 (185,'Sao Tome',194006,964,64.58,7.9,NULL,0.612,NULL,NULL),
 (186,'Saint Lucia',163922,616,77.6,8.5,20.0,1.893,NULL,NULL),
 (187,'Guam',161785,544,78.98,NULL,8.2,4.6,NULL,NULL),
 (188,'Curacao',146836,444,77.98,NULL,13.0,3.128,NULL,NULL),
 (189,'Aruba',112162,180,76.56,NULL,6.9,2.516,NULL,NULL),
 (190,'Grenada',110694,344,74.05,6.4,33.5,1.248,NULL,NULL),
 (191,'Tonga',106501,747,76.04,5.4,13.0,0.523,NULL,NULL),
 (192,'Kiribati',105711,811,65.81,10.7,2.0,0.18,NULL,NULL),
 (193,'Micronesia',105216,702,72.62,12.8,22.0,0.331,NULL,NULL),
 (194,'Virgin Islands',103574,1910,79.89,NULL,6.2,1.577,NULL,NULL),
 (195,'Saint Vincent',102627,389,75.09,5.2,18.8,1.198,NULL,NULL),
 (196,'Jersey',97294,116,81.76,NULL,1.7,5.771,NULL,NULL),
 (197,'Antigua and Barbuda',92436,443,76.33,5.2,11.0,1.989,NULL,NULL),
 (198,'Seychelles',92430,455,74.49,4.7,2.0,2.304,NULL,NULL),
 (199,'Isle of Man',87545,572,81.09,NULL,2.0,6.298,NULL,NULL),
 (200,'Andorra',85580,468,82.72,8.3,4.0,3.163,NULL,NULL),
 (201,'Dominica',73607,751,76.79,5.9,23.0,0.757,NULL,NULL),
 (202,'Marshall Islands',72191,181,72.84,15.6,36.0,0.178,NULL,NULL),
 (203,'Bermuda',70196,54,81.15,NULL,8.0,5.6,NULL,NULL),
 (204,'Guernsey',66080,78,82.47,NULL,0.9,3.42,NULL,NULL),
 (205,'Greenland',57733,2166086,72.1,NULL,9.4,2.133,NULL,NULL),
 (206,'Cayman Islands',56092,264,81.13,NULL,4.0,2.507,NULL,NULL),
 (207,'American Samoa',54343,199,75.14,NULL,29.8,0.5753,NULL,NULL),
 (208,'N. Mariana Islands',52344,464,77.82,NULL,11.2,0.733,NULL,NULL),
 (209,'Saint Kitts and Nevis',51936,261,75.52,5.9,4.5,1.22,NULL,NULL),
 (210,'Turks, Caicos Islands',50280,948,79.69,NULL,10.0,0.632,NULL,NULL),
 (211,'Faroe Islands',50196,1393,80.24,NULL,5.5,1.471,NULL,NULL),
 (212,'Sint Maarten',39689,34,77.61,NULL,12.0,0.3658,NULL,NULL),
 (213,'Liechtenstein',37624,160,81.77,NULL,2.3,3.2,NULL,NULL),
 (214,'British Virgin Islands',33454,151,78.46,NULL,8.7,0.5,NULL,NULL),
 (215,'San Marino',33020,61,83.24,6.5,7.0,2.007,NULL,NULL),
 (216,'Saint Martin',31754,54,NULL,NULL,NULL,0.5615,NULL,NULL),
 (217,'Monaco',30535,2,89.52,4.4,2.0,6.79,NULL,NULL),
 (218,'Gibraltar',29258,7,79.28,NULL,3.0,1.85,NULL,NULL),
 (219,'Palau',21265,459,72.87,9.5,4.2,0.272,NULL,NULL),
 (220,'Anguilla',16418,91,81.31,NULL,8.0,0.1754,NULL,NULL),
 (221,'Wallis and Futuna',15613,142,79.57,NULL,12.2,0.06,NULL,NULL),
 (222,'Tuvalu',10869,26,66.16,15.4,NULL,0.035,NULL,NULL),
 (223,'Cook Islands',9838,236,75.6,3.4,13.1,0.1832,NULL,NULL),
 (224,'Nauru',9540,21,66.75,7.5,90.0,0.06,NULL,NULL),
 (225,'Saint Helena',7795,308,79.36,NULL,14.0,0.0311,NULL,NULL),
 (226,'Saint Pierre',5657,242,80.39,NULL,9.9,0.2153,NULL,NULL),
 (227,'Montserrat',5241,102,74.14,NULL,6.0,0.04378,NULL,NULL),
 (228,'Falkland Islands',3361,12173,NULL,NULL,4.1,0.1645,NULL,NULL),
 (229,'Norfolk Island',2210,36,NULL,NULL,NULL,NULL,NULL,NULL),
 (230,'Svalbard',1872,62045,NULL,NULL,NULL,NULL,NULL,NULL),
 (231,'Christmas Island',1530,135,NULL,NULL,NULL,NULL,NULL,NULL),
 (232,'Tokelau',1337,12,NULL,NULL,NULL,0.0015,NULL,NULL),
 (233,'Niue',1190,260,NULL,6.7,12.0,0.01001,NULL,NULL),
 (234,'Vatican City',842,0,NULL,NULL,NULL,NULL,NULL,NULL),
 (235,'Cocos Islands',596,14,NULL,NULL,60.0,NULL,NULL,NULL),
 (236,'Pitcairn Islands',48,47,NULL,NULL,NULL,NULL,NULL,NULL);
"""
    runSQL("countries.db", sql)


def makeCarReg():
    sql = """CREATE TABLE IF NOT EXISTS "carreg" (
	"id"	INTEGER,
	"first_name"	TEXT,
	"last_name"	TEXT,
	"car_reg"	TEXT,
	"car_colour"	TEXT,
	"car_make"	TEXT,
	PRIMARY KEY("id")
);"""
    runSQL("carreg.db", sql)

    sql = """INSERT INTO "carreg" ("id","first_name","last_name","car_reg","car_colour","car_make") VALUES (1,'Lucy','Hughes','DR11 AEW','Black','Rover'),
 (2,'Katie','Wright','AH52 DWD','Grey','Jaguar'),
 (3,'Joseph','Baker','MY13 CPJ','Black','Bentley'),
 (4,'Lily','Taylor','MS54 PBH','Blue','Mini'),
 (5,'Grace','Wilson','BY15 DKB','Grey','Alfa Romeo'),
 (6,'Amelia','Edwards','VD56 MKJ','Red','Skoda'),
 (7,'Oliver','Jackson','WC17 GHP','Black','Dacia'),
 (8,'George','Clarke','XK58 KGD','Blue','Subaru'),
 (9,'Sophie','Lewis','VW19 SSS','Yellow','Tesla'),
 (10,'Charlotte','Wright','XG50 YCY','Grey','Saab'),
 (11,'Lucy','Brown','MR11 SRU','Black','Daewoo'),
 (12,'Lily','Williams','WC52 XAK','Black','Ford'),
 (13,'William','Walker','MR13 XHX','Red','Audi'),
 (14,'Amelia','Jones','MY51 JUE','Red','Rolls-Royce'),
 (15,'Lewis','White','BY12 VRJ','Blue','Hyundai'),
 (16,'Lewis','Harrison','AL53 YAD','Blue','Bentley'),
 (17,'Callum','Thomas','ED14 BXU','Black','McLaren'),
 (18,'Charlie','Evans','AH55 YLT','Black','Toyota'),
 (19,'Jessica','Turner','RU16 SVF','Yellow','Vauxhall'),
 (20,'James','Evans','AH57 MXM','Grey','Mini'),
 (21,'Amy','Wood','MR18 ATU','Grey','BMW'),
 (22,'Luke','Thomas','EH59 KDR','Black','Subaru'),
 (23,'Joseph','Moore','MY10 MMK','Green','Volvo'),
 (24,'Amelia','King','XH51 TUE','Black','McLaren'),
 (25,'Lewis','White','XG12 NTP','Yellow','Ford'),
 (26,'Samuel','Jones','VD53 WWN','White','Mercedes-Benz'),
 (27,'Matthew','Lewis','ED11 GDR','Black','Rolls-Royce'),
 (28,'Samuel','Wood','AL52 EHA','Black','Mercedes-Benz'),
 (29,'Harry','Morris','SU13 UDL','Red','Audi'),
 (30,'Charlotte','Wilson','XG54 BAS','White','Daewoo'),
 (31,'Callum','Morris','VW15 RGG','Blue','Subaru'),
 (32,'Lucy','Davies','XK56 YEX','White','Jaguar'),
 (33,'Amy','Thomas','ED17 NSX','Black','Dacia'),
 (34,'Abigail','Evans','AH58 DBN','Red','Audi'),
 (35,'Jessica','Thomas','ED19 SVC','Black','BMW'),
 (36,'Daniel','Taylor','AL50 BWK','Grey','Fiat'),
 (37,'Olivia','Robinson','VD11 BPN','White','Lexus'),
 (38,'Katie','Baker','EH52 AHE','Silver','Daewoo'),
 (39,'Ethan','Wilson','AL13 FPU','Black','Volkswagen'),
 (40,'Ruby','Hall','AH51 XHB','Green','Hyundai'),
 (41,'Mohammed','Malik','DR12 CUY','Black','Alfa Romeo'),
 (42,'Callum','King','ED53 GPP','Green','Peugeot'),
 (43,'Joseph','Robinson','MR14 KVX','White','Nissan'),
 (44,'Lucy','Harris','XH55 RXS','Orange','Vauxhall'),
 (45,'Jake','Martin','RU16 TUG','Orange','Mercedes-Benz'),
 (46,'Samuel','Lewis','AL57 REP','Black','Rolls-Royce'),
 (47,'Oliver','Robinson','ED18 BDS','Red','Subaru'),
 (48,'Hannah','Evans','VD59 EXV','Grey','Isuzu'),
 (49,'Amelia','Davies','WC10 WAE','Yellow','Hyundai'),
 (50,'Samuel','Thompson','MR51 KPJ','Green','Toyota'),
 (51,'Callum','Evans','NF12 SUL','Red','Lexus'),
 (52,'Sophie','Lewis','NF53 DSV','Silver','Land Rover'),
 (53,'Jake','Williams','DR11 YDM','Grey','Fiat'),
 (54,'Lewis','Harrison','EH52 MSD','White','Lamborghini'),
 (55,'William','Jones','DR13 AFJ','Blue','Toyota'),
 (56,'Oliver','White','EH54 RET','Grey','Rolls-Royce'),
 (57,'Amelia','Williams','XG15 XGM','Silver','Peugeot'),
 (58,'Benjamin','Thomas','XH56 NBF','Black','Mercedes-Benz'),
 (59,'Ruby','Roberts','WC17 WWD','White','Rolls-Royce'),
 (60,'Abigail','Davies','XH58 FNP','Green','Daewoo'),
 (61,'Samuel','Ward','XH19 PMK','Grey','Lamborghini'),
 (62,'Grace','Lee','BY50 MVE','Red','Lexus'),
 (63,'Hannah','Davies','RU11 AKX','Black','Land Rova'),
 (64,'Daniel','Jones','DR52 YLJ','Silver','Isuzu'),
 (65,'James','Johnson','RU13 VPL','Silver','Hyundai'),
 (66,'Megan','Hall','XG51 NGS','White','Ford'),
 (67,'Jack','Turner','SU12 CBU','Green','Volkswagen'),
 (68,'Joseph','Davies','ED53 YYH','Black','Vauxhall'),
 (69,'Ellie','Jackson','NF14 TFL','Blue','Land Rover'),
 (70,'James','Smith','XG55 TUF','Red','Lexus'),
 (71,'Charlie','Taylor','NF16 LAL','White','McLaren'),
 (72,'Hannah','Davies','NF57 TMD','Black','Ferrari'),
 (73,'Harry','Taylor','RU18 BAF','Silver','McLaren'),
 (74,'Hannah','Hall','EH59 DVN','Blue','Lamborghini'),
 (75,'Jake','Harris','AH10 HUJ','Grey','McLaren'),
 (76,'Benjamin','Clarke','XH51 BNB','Black','BMW'),
 (77,'Harry','Moore','DR12 SUD','Blue','Land Rover'),
 (78,'Charlotte','Thomas','XG53 LFG','Red','Honda'),
 (79,'Jack','Harris','VD11 TSK','Silver','Rolls-Royce'),
 (80,'Grace','Robinson','VW52 CYX','Black','Land Rover'),
 (81,'Hannah','King','MS13 EUY','Silver','Dacia'),
 (82,'Callum','Smith','NF54 TTG','Black','Isuzu'),
 (83,'Lily','Clarke','NF15 UJD','Black','Rolls-Royce'),
 (84,'Ella','Walker','AL56 ANN','Black','Subaru'),
 (85,'James','Davies','NF17 BXP','Silver','Toyota'),
 (86,'Ruby','Roberts','ED58 AYA','Orange','Lexus'),
 (87,'Mohammed','Rahim','VW19 VPL','Grey','Audi'),
 (88,'Charlie','Lewis','VW50 PYP','Red','Land Rover'),
 (89,'Charlie','Wilson','RU11 MLL','Silver','Land Rover'),
 (90,'James','White','AH52 AWU','Green','Isuzu'),
 (91,'Luke','White','AL13 AKD','Blue','Peugeot'),
 (92,'Ellie','Wilson','VD51 FKT','Silver','Lexus'),
 (93,'Amelia','Jackson','NF12 FCC','Blue','Subaru'),
 (94,'Ethan','Baker','VW53 YTF','Grey','Vauxhall'),
 (95,'Narayan','Patel','MY14 TKB','Silver','Land Rova'),
 (96,'Charlotte','Clarke','ED55 UNP','Blue','Honda'),
 (97,'Ethan','Thompson','AL16 YPN','Grey','Nissan'),
 (98,'Daniel','Jones','WC57 BKK','Black','Lamborghini'),
 (99,'George','Hall','ED18 BDC','Black','Bentley'),
 (100,'Matthew','Roberts','XG59 XLA','Silver','Mazda'),
 (101,'Lucy','Martin','XK10 UFH','Grey','Fiat'),
 (102,'Anushka','Patel','VD51 HTE','Orange','Ford'),
 (103,'Harry','Baker','NF12 FHN','Blue','Land Rova'),
 (104,'Harry','Morgan','ED53 EPB','Grey','Mini'),
 (105,'Amelia','Turner','AH11 KMH','Red','Volkswagen'),
 (106,'Callum','Jackson','AL52 RFT','White','Lamborghini'),
 (107,'Samuel','Green','XH13 AMY','Grey','Lexus'),
 (108,'Hannah','Johnson','MS54 FAB','White','Kia'),
 (109,'Sophie','Wright','DR15 MYF','Grey','Nissan'),
 (110,'Arjuna','Patel','WC56 VCM','Yellow','Fiat'),
 (111,'Ethan','Green','AH17 PGK','Grey','Bentley'),
 (112,'James','Morgan','AH58 UHA','Grey','Porsche'),
 (113,'George','Turner','MY19 SJU','Yellow','Dacia'),
 (114,'Ethan','Lewis','MY50 VWH','White','Audi'),
 (115,'Jack','Moore','XK11 VNC','Red','Subaru'),
 (116,'Lewis','Clarke','DR52 GAX','Green','Alfa Romeo'),
 (117,'Lewis','Edwards','XK13 KUW','Grey','Fiat'),
 (118,'Joshua','Lewis','DR51 REK','Orange','Nissan'),
 (119,'Amelia','Wilson','AH12 PBG','Silver','Toyota'),
 (120,'Luke','Edwards','NF53 DGP','Grey','Tesla'),
 (121,'Thomas','King','XH14 NGJ','White','Lamborghini'),
 (122,'Callum','Taylor','BY55 NVA','Black','Land Rova'),
 (123,'Amelia','Walker','XH16 CAF','Red','Porsche'),
 (124,'Mohammed','Ahmad','NF57 SPK','White','Lexus'),
 (125,'Matthew','Baker','VW18 PRY','Silver','Daewoo'),
 (126,'Benjamin','Lewis','EH59 RAA','Grey','Alfa Romeo'),
 (127,'Sophie','Cooper','NF10 CVA','Silver','Hyundai'),
 (128,'Lily','Hughes','MY51 HXV','Black','McLaren'),
 (129,'Emily','Thompson','MS12 APW','Silver','Alfa Romeo'),
 (130,'William','Roberts','ED53 BWA','White','Fiat'),
 (131,'George','White','EH11 GYH','Blue','Lexus'),
 (132,'Lewis','Martin','MY52 LPX','White','McLaren'),
 (133,'Megan','Thomas','VW13 GGA','Black','Volvo'),
 (134,'Jake','Clarke','WC54 DLN','White','Hyundai'),
 (135,'Benjamin','Thomas','ED15 FEM','Grey','Tesla'),
 (136,'Lewis','Lewis','MR56 EYX','White','Mini'),
 (137,'Amy','Robinson','VW17 UPK','Black','Peugeot'),
 (138,'Lucy','Davies','EH58 UDE','White','Toyota'),
 (139,'Ella','Smith','RU19 WRT','Black','Honda'),
 (140,'Samuel','Green','WC50 HXU','Silver','Saab'),
 (141,'Lily','Cooper','XH11 UEW','Red','Saab'),
 (142,'Emily','Harrison','RU52 TTB','Blue','Honda'),
 (143,'Megan','Cooper','MY13 LXV','Grey','Hyundai'),
 (144,'Olivia','Jackson','MY51 MVU','Black','Bentley'),
 (145,'William','Brown','VW12 GSX','Yellow','Subaru'),
 (146,'James','Morris','XH53 PET','Red','Rolls-Royce'),
 (147,'Benjamin','Hughes','RU14 DVE','Black','Mini'),
 (148,'James','Hall','XH55 XGL','Green','Tesla'),
 (149,'James','Hughes','XG16 SJD','White','Subaru'),
 (150,'Harry','King','EH57 NSP','Green','BMW'),
 (151,'Harry','Baker','MS18 CPL','Black','Jaguar'),
 (152,'Grace','Hall','SU59 PKS','Black','Lexus'),
 (153,'Amelia','Jackson','AL10 URD','Blue','Land Rova'),
 (154,'Daniel','Clarke','BY51 XNV','Black','Isuzu'),
 (155,'Grace','White','XH12 GNW','Red','Rover'),
 (156,'Samuel','Green','MY53 SBX','Red','Jaguar'),
 (157,'Benjamin','Clarke','XG11 VBG','Red','Rolls-Royce'),
 (158,'Matthew','Thompson','XG52 KYR','White','Ford'),
 (159,'Ruby','Thomas','XK13 WKM','Blue','Lotus'),
 (160,'Callum','Johnson','XH54 CWF','Black','Kia'),
 (161,'Benjamin','Taylor','AH15 XUP','Green','Lexus'),
 (162,'Ella','White','DR56 GDW','Blue','Mini'),
 (163,'James','Walker','AH17 STF','Black','Bentley'),
 (164,'Charlotte','Lee','EH58 YWE','Yellow','Kia'),
 (165,'Mohammed','Baraka','RU19 RWX','Silver','Lotus'),
 (166,'Megan','Ward','NF50 NCK','Red','Lexus'),
 (167,'Oliver','Wood','XK11 URK','Grey','Ford'),
 (168,'Abigail','White','XK52 WBL','Black','Audi'),
 (169,'Lily','Smith','XG13 YJW','Blue','Lexus'),
 (170,'Callum','Wood','VW51 NNT','Grey','Skoda'),
 (171,'Jack','Baker','XH12 NXC','Black','Ferrari'),
 (172,'Jake','Davies','AL53 HEC','White','Mercedes-Benz'),
 (173,'Joshua','Lewis','BY14 EME','Grey','Bentley'),
 (174,'Ellie','Ward','NF55 BKF','Black','Volvo'),
 (175,'Katie','Thomas','RU16 EUG','White','McLaren'),
 (176,'Harry','Martin','WC57 YFJ','Red','Vauxhall'),
 (177,'Ellie','Edwards','VW18 FKF','Green','Volkswagen'),
 (178,'Charlie','Hughes','VD59 BVG','Red','Saab'),
 (179,'Ella','Walker','MS10 DPA','Black','Peugeot'),
 (180,'Joseph','Jones','XG51 BXJ','Red','Hyundai'),
 (181,'Amelia','Williams','XK12 PKJ','Orange','Mazda'),
 (182,'Amy','Wood','XH53 KYD','Silver','Mini'),
 (183,'Chloe','White','SU11 GHY','Blue','Peugeot'),
 (184,'Daniel','Turner','MR52 DYK','Grey','Rover'),
 (185,'Hannah','Harris','XH13 TRJ','Silver','Volvo'),
 (186,'George','Brown','XG54 SNY','White','Subaru'),
 (187,'Lucy','Martin','BY15 JWU','Grey','Saab'),
 (188,'Megan','Wood','WC56 PWF','White','Porsche'),
 (189,'Abigail','Martin','NF17 PVB','Black','Lexus'),
 (190,'Samuel','Evans','MR58 GCS','Yellow','Daewoo'),
 (191,'Amelia','Johnson','ED19 VKP','Grey','Volvo'),
 (192,'Joshua','Harris','XG50 UUR','Black','Bentley'),
 (193,'Samuel','Walker','DR11 LWX','Black','Skoda'),
 (194,'Bhavani','Patel','ED52 DGG','White','Alfa Romeo'),
 (195,'Thomas','Lee','EH13 VFK','Grey','Volvo'),
 (196,'Charlie','Davies','MY51 LRV','White','Land Rova'),
 (197,'Samuel','Roberts','AL12 JVS','Grey','Mazda'),
 (198,'Sai','Patel','XH53 WFR','Silver','Audi'),
 (199,'Shilpa','Patel','XH14 WWC','Blue','Rolls-Royce'),
 (200,'Megan','Hill','VD55 FWL','Black','Honda'),
 (201,'Harry','Wright','MS16 GBH','Yellow','Saab'),
 (202,'Hannah','Martin','DR57 GYM','Blue','Lotus'),
 (203,'Mohammed','Zar','SU18 HCK','White','Mini'),
 (204,'Jake','Clarke','ED59 KLK','Red','Fiat'),
 (205,'Matthew','Smith','RU10 YRY','Black','Lamborghini'),
 (206,'Hannah','King','XG51 PDT','Red','Rolls-Royce'),
 (207,'Amy','Morgan','MR12 XWL','Black','Rolls-Royce'),
 (208,'Amelia','Lee','VW53 DDY','White','Saab'),
 (209,'Mia','Turner','MY14 FTP','Black','Toyota'),
 (210,'Olivia','Robinson','VD55 KJN','Red','Volvo'),
 (211,'Samuel','Evans','MR16 KCW','White','Volvo'),
 (212,'Amelia','Lee','BY57 EXA','Grey','Kia'),
 (213,'William','Johnson','MR18 DCG','Black','Tesla'),
 (214,'Hannah','Davies','WC59 TRD','Black','Lexus'),
 (215,'Lily','Thomas','DR10 ENH','Grey','Land Rova'),
 (216,'Matthew','Thomas','AL51 SMX','Blue','Mercedes-Benz'),
 (217,'Charlotte','Lee','NF12 HRR','Black','Rover'),
 (218,'Hariom','Patel','MY53 MHT','Grey','Isuzu'),
 (219,'Joshua','Turner','VD11 VEH','Yellow','Skoda'),
 (220,'Ruby','Hughes','ED52 SHX','Blue','Peugeot'),
 (221,'Joseph','Cooper','DR13 REK','Black','Hyundai'),
 (222,'Sophie','Taylor','MY54 MMR','Orange','Bentley'),
 (223,'Amy','Hall','VD15 TPL','White','Hyundai'),
 (224,'Mohammed','Abdullah','XG56 TPE','Yellow','Lotus'),
 (225,'Ellie','Harrison','NF17 PHH','Red','Lexus'),
 (226,'Thomas','Evans','NF58 GTX','Grey','McLaren'),
 (227,'James','Harrison','MR19 CPA','Silver','Peugeot'),
 (228,'George','Hughes','XK50 MFF','White','Subaru'),
 (229,'Amelia','Ward','DR11 WDU','Blue','Mercedes-Benz'),
 (230,'Mia','Evans','ED52 MAA','Silver','Daewoo'),
 (231,'Charlotte','Thompson','XG13 PJR','Silver','Lamborghini'),
 (232,'Charlotte','Hall','BY51 SEV','Black','Subaru'),
 (233,'Harry','Lewis','MS12 GWH','Black','Rover'),
 (234,'Luke','Wilson','XH53 TDP','Green','Nissan'),
 (235,'Charlotte','Smith','XG14 SRW','Blue','Tesla'),
 (236,'Ethan','King','EH55 GPC','Grey','Lexus'),
 (237,'Katie','Jackson','RU16 VBX','Blue','Isuzu'),
 (238,'Grace','Jackson','DR57 SUV','Orange','Mazda'),
 (239,'Chloe','Clarke','BY18 WBM','Blue','BMW'),
 (240,'Ethan','Morris','ED59 YPD','Red','Nissan');
"""
    runSQL("carreg.db", sql)


def makeFilms():
    sql = """CREATE TABLE IF NOT EXISTS "directors" (
	"id"	INTEGER,
	"first_name"	TEXT,
	"last_name"	TEXT,
	"birth_year"	INTEGER,
	PRIMARY KEY("id")
);"""
    runSQL("films.db", sql)

    sql = """CREATE TABLE IF NOT EXISTS "films" (
	"id"	INTEGER,
	"title"	TEXT,
	"year"	INTEGER,
	"duration"	INTEGER,
	"certificate"	TEXT,
	"director"	INTEGER,
	"rating"	INTEGER,
	PRIMARY KEY("id")
);"""
    runSQL("films.db", sql)

    sql = """INSERT INTO "directors" ("id","first_name","last_name","birth_year") VALUES (1,'Steven','Spielberg',1946),
 (2,'Kenneth','Branagh',1960),
 (3,'Frank','Darabont',1959),
 (4,'Christopher','Nolan',1970),
 (5,'Fernando','Meirelles',1955),
 (6,'Daniel','Kwan',1988),
 (7,'Irvin','Kershner',1923),
 (8,'Edward','Berger',1970),
 (9,'Ryusuke','Hamaguchi',1978),
 (10,'Peter','Jackson',1961),
 (11,'Jason','Friedberg',1970),
 (12,'Jonathan','Demme',1944),
 (13,'Charles','Chaplin',1889),
 (14,'Paul Thomas','Anderson',1970),
 (15,'Hayao','Miyazaki',1941),
 (16,'Sergio','Leone',1929),
 (17,'Bob','Persichetti',1973),
 (18,'Sarah','Polley',1979),
 (19,'Luc','Besson',1959),
 (20,'Reinaldo Marcus','Green',1981),
 (21,'Michael','Rianda',1984),
 (22,'Jane','Campion',1954),
 (23,'Roberto','Benigni',1952),
 (24,'Lana','Wachowski',1965),
 (25,'Don','Hall',1969),
 (26,'Alfred','Hitchcock',1899),
 (27,'David','Fincher',1962),
 (28,'Todd','Field',1964),
 (29,'Francis Ford','Coppola',1939),
 (30,'Akira','Kurosawa',1910),
 (31,'Sergio','Leone',1929),
 (32,'Ruben','Ostlund',1974),
 (33,'Jared','Bush',1974),
 (34,'Bryan','Singer',1965),
 (35,'Frank','Capra',1897),
 (36,'James','Cameron',1954),
 (37,'Robert','Zemeckis',1952),
 (38,'Bob','Clark',1939),
 (39,'Martin','Scorsese',1942),
 (40,'Baz','Luhrmann',1962),
 (41,'Guillermo del','Toro',1964),
 (42,'Sian','Heder',1977),
 (43,'Martin','McDonagh',1970),
 (44,'Milos','Forman',1932),
 (45,'Tony','Kaye',1952),
 (46,'Joseph','Kosinski',1974),
 (47,'Quentin','Tarantino',1963),
 (48,'Denis','Villeneuve',1967),
 (49,'Adam','McKay',1968),
 (50,'Sidney','Lumet',1924),
 (51,'George','Lucas',1944);
"""
    runSQL("films.db", sql)

    sql = """INSERT INTO "films" ("id","title","year","duration","certificate","director","rating") VALUES (1,'Saving Private Ryan',1998,169,'15',1,5),
 (2,'Belfast',2021,98,'12A',2,3),
 (3,'The Shawshank Redemption',1994,142,'15',3,5),
 (4,'Inception',2010,148,'12A',4,5),
 (5,'City of God',2002,130,'18',5,5),
 (6,'Everything Everywhere all at Once',2022,139,'15',6,4),
 (7,'Jurassic Park',1993,127,'PG',1,4),
 (8,'Star Wars: Episode V - The Empire Strikes Back',1980,124,'U',7,5),
 (9,'All Quiet on the Western Front',2022,148,'15',8,4),
 (10,'Drive My Car',2021,179,'15',9,4),
 (11,'The Lord of the Rings: The Two Towers',2002,179,'12A',10,5),
 (12,'Epic Movie',2007,86,'12A',11,1),
 (13,'Indiana Jones and the Kingdom of the Crystal Skull',2008,122,'12A',1,2),
 (14,'Tenet',2020,150,'12A',4,3),
 (15,'The Silence of the Lambs',1991,118,'18',12,5),
 (16,'Bridge of Spies',2015,142,'12A',1,4),
 (17,'City Lights',1931,87,'U',13,5),
 (18,'Schindler''s List',1993,195,'15',1,5),
 (19,'Licorice Pizza',2021,133,'15',14,3),
 (20,'Amistad',1997,155,'15',1,3),
 (21,'War of the Worlds',2005,116,'12A',1,3),
 (22,'Spirited Away',2001,125,'PG',15,5),
 (23,'The Lord of the Rings: The Return of the King',2003,201,'12A',10,5),
 (24,'Jaws',1975,124,'12',1,4),
 (25,'The Prestige',2006,130,'12A',4,5),
 (26,'The Dark Knight Rises',2012,164,'12A',4,4),
 (27,'The Dark Knight',2008,152,'12A',4,5),
 (28,'Insomnia',2002,118,'15',4,3),
 (29,'Lincoln',2012,150,'12A',1,3),
 (30,'Once Upon a Time in the West',1968,165,'15',16,5),
 (31,'The Dark Knight',2008,152,'12A',4,5),
 (32,'Spider-Man: Into the Spider-Verse',2018,117,'PG',17,5),
 (33,'Women Talking',2022,104,'15',18,3),
 (34,'Léon',1994,110,'18',19,5),
 (35,'King Richard',2021,144,'12A',20,4),
 (36,'Saving Private Ryan',1998,169,'15',1,5),
 (37,'Munich',2005,164,'15',1,4),
 (38,'The Mitchells vs The Machines',2021,114,'U',21,4),
 (39,'The Power of the Dog',2021,126,'12A',22,3),
 (40,'Interstellar',2014,169,'12A',4,5),
 (41,'Catch Me If You Can',2002,141,'12A',1,4),
 (42,'The Lost World: Jurassic Park',1997,129,'PG',1,3),
 (43,'Raiders of the Lost Ark',1981,115,'PG',1,4),
 (44,'Life is Beautiful',1997,116,'PG',23,5),
 (45,'Interstellar',2014,169,'12A',4,5),
 (46,'The Matrix',1999,136,'15',24,5),
 (47,'Raya and the Last Dragon',2021,107,'PG',25,3),
 (48,'Psycho',1960,109,'15',26,5),
 (49,'Se7en',1995,127,'18',27,5),
 (50,'Tar',2022,158,'15',28,4),
 (51,'The Godfather',1972,175,'18',29,5),
 (52,'Dunkirk',2017,106,'12A',4,4),
 (53,'Seven Samurai',1954,207,'PG',30,5),
 (54,'The Good, the Bad and the Ugly',1966,161,'18',16,5),
 (55,'The Adventures of Tintin: The Secret of the Unicorn',2011,107,'PG',1,3),
 (56,'Hook',1991,142,'U',1,3),
 (57,'Minority Report',2002,145,'12',1,4),
 (58,'West Side Story',2021,156,'12A',1,3),
 (59,'Close Encounters of the Third Kind',1977,138,'PG',1,4),
 (60,'Triangle of Sadness',2022,147,'15',32,3),
 (61,'Batman Begins',2005,140,'12A',4,4),
 (62,'The Terminal',2004,128,'12A',1,3),
 (63,'The Fabelmans',2022,151,'12A',1,4),
 (64,'Encanto',2021,102,'PG',33,3),
 (65,'E.T. the Extra-Terrestrial',1982,115,'U',1,4),
 (66,'The Usual Suspects',1995,106,'18',34,5),
 (67,'It''s a Wonderful Life',1946,130,'U',35,5),
 (68,'Avatar: The Way of Water',2022,192,'12A',36,4),
 (69,'Forrest Gump',1994,142,'12',37,5),
 (70,'Superbabies: Baby Geniuses 2',2004,88,'U',38,1),
 (71,'Inception',2010,148,'12A',4,5),
 (72,'Goodfellas',1990,146,'18',39,5),
 (73,'The Sugarland Express',1974,110,'PG',1,3),
 (74,'Elvis',2022,159,'12A',40,3),
 (75,'The Shape of Water',2017,123,'15',41,3),
 (76,'The Godfather: Part II',1974,202,'18',29,5),
 (77,'Coda',2021,111,'12A',42,4),
 (78,'The Banshees of Inisherin',2022,114,'15',43,4),
 (79,'Schindler''s List',1993,195,'15',1,5),
 (80,'Nightmare Alley',2021,150,'15',41,3),
 (81,'One Flew Over the Cuckoo''s Nest',1975,133,'15',44,5),
 (82,'Firelight',1964,140,NULL,1,2),
 (83,'Top Gun: Maverick',2022,130,'12A',46,4),
 (84,'Memento',2000,113,'15',4,4),
 (85,'The BFG',2016,87,'PG',1,2),
 (86,'Pulp Fiction',1994,154,'18',47,5),
 (87,'The Lord of the Rings: The Fellowship of the Ring',2001,178,'PG',10,5),
 (88,'Disaster Movie',2008,87,'12A',11,1),
 (89,'Dune',2021,155,'12A',48,4),
 (90,'Don''t Look Up',2021,138,'15',49,3),
 (91,'Oppenheimer',2023,180,'15',4,5),
 (92,'The Post',2017,116,'12A',1,3),
 (93,'12 Angry Men',1957,96,'U',50,5),
 (94,'Star Wars',1977,121,'U',51,5),
 (95,'Fight Club',1999,139,'18',27,5),
 (96,'The Green Mile',1999,189,'18',3,5),
 (97,'Following',1998,69,'15',4,4),
 (98,'Empire of the Sun',1987,153,'PG',1,4),
 (99,'War Horse',2011,146,'12A',1,3),
 (100,'A.I. Artificial Intelligence',2001,146,'12',1,3),
 (101,'American History X',1998,119,'18',45,5),
 (102,'Indiana Jones and the Temple of Doom',1989,118,'12A',1,4),
 (103,'Ready Player One',2018,140,'12A',1,3);
"""
    runSQL("films.db", sql)


if __name__ == '__main__':
    main()





