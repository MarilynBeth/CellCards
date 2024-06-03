import mysql.connector
from mysql.connector import Error

# Connections
def create_server_connection(hostName, userName, userPassword):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=hostName,
            user=userName,
            password=userPassword
        )
        print("MySQL DB connection success")
    except Error as err:
        print(f"Error: '{err}'")
    return connection


def create_database(connection, query):
    # connection cursor executes SQL statements with python
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")


# Connecting to the database just created
def create_database_connection(hostName, userName, userPassword, databaseName):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=hostName,
            user=userName,
            password=userPassword,
            database=databaseName
        )
        print("MySQL db connection success")
    except Error as err:
        print(f"Error: '{err}'")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query success")
    except Error as err:
        print(f"Error: '{err}'")