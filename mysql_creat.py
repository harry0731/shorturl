import mysql.connector
import configparser
import argparse

config = configparser.ConfigParser()
config.read("config.ini")

def make_sql_cursor(config):
    """
    Make MySQL cursor at sql level.
    """
    mydb = mysql.connector.connect(
        host=config["mysql"]["host"],
        user=config["mysql"]["user"],
        passwd=config["mysql"]["passwd"],
        auth_plugin='mysql_native_password')
    return mydb

def make_db_cursor(config):
    """
    Make MySQL cursor at database level.
    """
    mydb = mysql.connector.connect(
        host=config["mysql"]["host"],
        user=config["mysql"]["user"],
        passwd=config["mysql"]["passwd"],
        auth_plugin='mysql_native_password',
        database="shorturl")
    return mydb

def creat_db(config):
    """
    Creat database.
    """
    mydb = make_sql_cursor(config)
    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE shorturl")

def check_db(config):
    """
    Check if databese exist.
    """
    mydb = make_sql_cursor(config)
    mycursor = mydb.cursor()
    mycursor.execute("SHOW DATABASES")
    flag = False
    for x in mycursor:
        if x[0] == "shorturl":
            flag = True
    if flag:
        print("Database exist!")
    else:
        print("Database not found!")
    

def creat_table(config):
    """
    Creat table.
    """
    mydb = make_db_cursor(config)
    mycursor = mydb.cursor()
    mycursor.execute(f"""CREATE TABLE IF NOT EXISTS shorturl (
        `url_hash_id` INT(11) UNSIGNED PRIMARY KEY AUTO_INCREMENT,
        `hash` VARCHAR(100),
        `url` VARCHAR({config["DEFAULT"]["MAX_URL_LEN"]}),
        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(`hash`),
        UNIQUE(`url`)
        );""")

def check_table(config):
    """
    Check if table exist.
    """
    mydb = make_db_cursor(config)
    mycursor = mydb.cursor()
    mycursor.execute("SHOW TABLES")
    flag = False
    for x in mycursor:
        if x[0] == "shorturl":
            flag = True
    if flag:
        print("Table exist!")
    else:
        print("Table not found!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--creatdb", help="creat database", action="store_true")
    parser.add_argument("--checkdb", help="check database", action="store_true")
    parser.add_argument("--creattable", help="creat table", action="store_true")
    parser.add_argument("--checktable", help="check table", action="store_true")
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read("config.ini") 

    if args.creatdb:
        creat_db(config)
    if args.checkdb:
        check_db(config)
    if args.creattable:
        creat_table(config)
    if args.checktable:
        check_table(config)