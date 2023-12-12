import mysql.connector

import pandas as pd

from SPARQLWrapper import SPARQLWrapper, JSON
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


createTable = """
create table meetingTable(
num int auto_increment primary key,
cell_id varchar(1000), 
label varchar(1000), 
definition varchar(1000), 
derivesFromSomePartOf varchar(1000), 
exactSynonyms varchar(1000), 
broadSynonyms varchar(1000),
databaseRef varchar(1000), 
partOf varchar(1000));
"""

sparql = SPARQLWrapper("https://sparql.hegroup.org/sparql")
sparql.setReturnFormat(JSON)

sparql.setQuery("""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX obo-term: <http://purl.obolibrary.org/obo/>
PREFIX obo-owl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX cell: <http://purl.obolibrary.org/obo/CL_0000066>

SELECT ?cell_id (str(?label) AS ?label) 
(str(?definition) AS ?definition) 
(str(?DerivesFromSomePartOf) AS ?DerivesFromSomePartOf) (str(?database) AS ?database) (GROUP_CONCAT(DISTINCT ?exactSynonym; SEPARATOR=", ") AS ?exactSynonyms)
    (GROUP_CONCAT(DISTINCT ?broadSynonym; SEPARATOR=", ") AS ?broadSynonyms) ?partOf



FROM <http://purl.obolibrary.org/obo/merged/CLO>

WHERE {

        ?cell_id rdfs:subClassOf* cell: .

        ?cell_id  rdfs:label ?label.

        # Retrieve the definition
        OPTIONAL { ?cell_id  obo-term:IAO_0000115 ?definition. }

         OPTIONAL { ?cell_id obo-owl:hasDbXref ?database.}

        OPTIONAL { ?cell_id  obo-owl:hasExactSynonym ?exactSynonym. }

        # Retrieve broad synonyms
        OPTIONAL { ?cell_id obo-owl:hasBroadSynonym ?broadSynonym. }


        # Retrieve "derives from" some "part of" some information
        OPTIONAL {
            ?cell_id   rdfs:subClassOf ?restriction.
            ?restriction rdf:type owl:Restriction.
            ?restriction owl:onProperty obo-term:RO_0001000.
            ?restriction owl:someValuesFrom ?part.
            ?part owl:onProperty obo-term:BFO_0000050.
            ?part owl:someValuesFrom ?a.
            ?a rdfs:label ?DerivesFromSomePartOf.
        }

    OPTIONAL {
            ?cell_id  rdfs:subClassOf ?restriction.
            ?restriction rdf:type owl:Restriction.
            ?restriction owl:onProperty obo-term:BFO_0000050.
            ?restriction owl:someValuesFrom ?part.
            ?part rdfs:label ?partOf.
        }

  }
    """
                )

ret = sparql.query().convert()

pw = ""
db = ""
connection = create_database_connection("", "", pw, db)

cursor = connection.cursor()


def get_value_from_result(key: str, obj: object) -> str:
    if key in obj:
        return result[key]["value"]
    return None


for result in ret["results"]["bindings"]:
    cell_id = result["cell_id"]["value"]
    label = result["label"]["value"]
    definition = get_value_from_result("definition", result)
    derivesFromSomePartOf = get_value_from_result("DerivesFromSomePartOf", result)
    exactSynonyms = get_value_from_result("exactSynonyms", result)
    broadSynonyms = get_value_from_result("broadSynonyms", result)
    databaseRef = get_value_from_result("database", result)
    partOf = get_value_from_result("partOf", result)

    insert_query = ("INSERT INTO meetingTable (cell_id, label,definition,derivesFromSomePartOf,"
                    "exactSynonyms,broadSynonyms,databaseRef,partOf) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    insert_values = (
    cell_id, label, definition, derivesFromSomePartOf, exactSynonyms, broadSynonyms, databaseRef, partOf)
    cursor.execute(insert_query, insert_values)

connection.commit()

