import logging
from configparser import ConfigParser

import numpy
import pyodbc
from flask import Flask
from sklearn.cluster import KMeans

app = Flask(__name__)

db_created = None
db_initialised = False


@app.route('/hello')
def hello():
    logging.error("Hello")
    logging.warning("Hello")
    logging.debug("Hello")
    logging.info("Hello")
    print("Hello")
    return "Hello world!"


@app.route('/check_sql')
def check_sql():
    print("Parsing config")
    parser = ConfigParser()
    parser.read('config.ini')

    server = parser.get('DATABASE', 'server')
    username = parser.get('DATABASE', 'username')
    password = parser.get('DATABASE', 'password')
    port = parser.get('DATABASE', 'port')

    print("Config parsed")

    cnxn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};PORT={port};DATABASE=master;'
        f'UID={username};PWD={password};TrustServerCertificate=Yes;')

    data = cnxn.getinfo(pyodbc.SQL_DBMS_VER)

    cnxn.close()

    return f"<b>Info: {data}</b>!"


@app.route('/create_sql_database')
def create_sql_database():
    print("Parsing config")
    parser = ConfigParser()
    parser.read('config.ini')

    server = parser.get('DATABASE', 'server')
    username = parser.get('DATABASE', 'username')
    password = parser.get('DATABASE', 'password')
    database = parser.get('DATABASE', 'database')
    port = parser.get('DATABASE', 'port')
    print("Config parsed")

    cnxn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};PORT={port};DATABASE=master;'
        f'UID={username};PWD={password};TrustServerCertificate=Yes;')

    sql = "SELECT name, database_id, create_date FROM sys.databases;"

    cursor = cnxn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()

    created = False

    for d in data:
        print(d)
        if d[0] == database:
            created = True
    cursor.close()
    response = ""
    if not created:
        sql = f'create database "{database}"'
        print("Making request to create db")
        cnxn.autocommit = True
        cnxn.execute(sql)
        print("Db created")
        response = "Db created"
    else:
        print("Db already exists")
        response = "Db already exists"

    cnxn.close()
    return f"<b>{response}</b>!"


@app.route('/load_data')
def load_data():
    print("Parsing config")
    parser = ConfigParser()
    parser.read('config.ini')

    server = parser.get('DATABASE', 'server')
    username = parser.get('DATABASE', 'username')
    password = parser.get('DATABASE', 'password')
    database = parser.get('DATABASE', 'database')
    port = parser.get('DATABASE', 'port')
    print("Config parsed")

    cnxn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};PORT={port};DATABASE=master;'
        f'UID={username};PWD={password};TrustServerCertificate=Yes;')

    sql = "SELECT name, database_id, create_date FROM sys.databases;"

    cursor = cnxn.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()

    created = False

    for d in data:
        print(d)
        if d[0] == database:
            created = True
    cursor.close()
    cnxn.close()
    print(f"Check completed: {created}")
    if not created:
        return "Database dn exists"

    cnxn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};PORT={port};DATABASE={database};'
        f'UID={username};PWD={password};TrustServerCertificate=Yes;')

    file_path = parser.get('DATASET', 'path')
    cnxn.autocommit = True
    cursor = cnxn.cursor()
    table_name = "kmeans_vectors_data"

    table_creation_sql = (f"CREATE TABLE {table_name} (vectorID int, vector_values text);")
    cursor.execute(table_creation_sql)

    with open(file_path, "r") as f:
        data = f.read().split("\n")
    counter = 0
    for index_, row in enumerate(data):
        vector_values = ";".join(row.split(","))
        sql = f"INSERT INTO {table_name} (vectorID, vector_values) VALUES ({index_}, '{vector_values}')"
        cursor.execute(sql)
        counter += 1
    print(f"Inserted: {counter}")

    check_sql_request = f"SELECT COUNT(*) FROM {table_name};"
    cursor.execute(check_sql_request)
    responce = ""
    result = cursor.fetchall()
    for r in result:
        print(f"Counted from table: {r[0]}")
        responce += str(r[0])

    cnxn.close()

    return f"Inserted: {counter} rows in table: {table_name} Selected: {responce[0]}"


@app.route('/processing')
def processing():
    print("Parsing config")
    parser = ConfigParser()
    parser.read('config.ini')

    server = parser.get('DATABASE', 'server')
    username = parser.get('DATABASE', 'username')
    password = parser.get('DATABASE', 'password')
    database = parser.get('DATABASE', 'database')
    port = parser.get('DATABASE', 'port')
    print("Config parsed")

    clusters_centers = numpy.load("model/kmeans.npy")
    model = KMeans(init=clusters_centers)

    cnxn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};PORT={port};DATABASE={database};'
        f'UID={username};PWD={password};TrustServerCertificate=Yes;')

    cnxn.autocommit = True
    cursor = cnxn.cursor()

    table_name_src = "kmeans_vectors_data"
    table_name_out = "kmeans_vectors_data"

    table_creation_sql = (f"CREATE TABLE {table_name_out} (vectorID int, result_cluster int);")
    cursor.execute(table_creation_sql)

    sql_getter = f"SELECT * FROM {table_name_src};"
    cursor.execute(sql_getter)
    counter = 0
    for index_elem, values in cursor.fetchall():
        vector_values = list(map(lambda x: float(x), values.split(";")))
        y = model.predict(vector_values)
        sql = f"INSERT INTO {table_name_out} (vectorID, result_cluster) VALUES ({index_elem}, '{y}')"
        cursor.execute(sql)
        counter += 1

    cursor.close()
    cnxn.close()

    return f"Processed: {counter}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8085)
