import mysql.connector
import pandas as pd
import csv
import argparse
from SPARQLWrapper import SPARQLWrapper, JSON
from mysql.connector import Error


insertSYN = """
    INSERT INTO t_synonym(c_synonym_label, c_ontology_term_id, 
    c_synonym_annotation_property_label, c_synonym_annotation_property_iri,c_synonym_type)
    VALUES (%s, %s, %s, %s, %s)"""

insertOntolTermRelt = """
INSERT INTO t_ontology_term_relation(c_subject_term_label, c_subject_term_id, 
c_predicate_term_label, c_predicate_term_id,c_object_term_label, c_object_term_id)
VALUES (%s, %s, %s, %s, %s, %s)"""

insertOntologyTermQuery = """
INSERT INTO t_ontology_term(c_ontology_term_id,c_name, c_definition, c_source, c_database_reference)
VALUES (%s, %s, %s, %s, %s)"""

createOntologyTerm = """
CREATE TABLE `t_ontology_term` (
  `c_ontology_term_id` varchar(25) NOT NULL,
  `c_name` varchar(255) DEFAULT NULL,
  `c_definition` varchar(2000) DEFAULT NULL,
  `c_source` varchar(200) DEFAULT NULL,
  `c_category` varchar(200) DEFAULT NULL,
  `c_is_user_defined` varchar(100) DEFAULT NULL,
  `c_uri` varchar(500) DEFAULT NULL,
  `c_notes` varchar(4000) DEFAULT NULL,
  `c_minimum_level` int DEFAULT NULL,
  `c_maximum_level` int DEFAULT NULL,
  `c_number_of_levels` int DEFAULT NULL,
  `c_database_reference` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`c_ontology_term_id`)
);
"""

createTsynonymTable = """CREATE TABLE `t_synonym` (
  `c_synonym_id` int NOT NULL AUTO_INCREMENT,
  `c_synonym_label` varchar(2000) NOT NULL,
  `c_ontology_term_id` varchar(25) NOT NULL,
  `c_synonym_annotation_property_label` varchar(100) DEFAULT NULL,
  `c_synonym_annotation_property_iri` varchar(25) DEFAULT NULL,
  `c_synonym_type` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`c_synonym_id`),
  KEY `synonym_onto_term_id` (`c_ontology_term_id`),
  CONSTRAINT `synonym_onto_term_id` FOREIGN KEY (`c_ontology_term_id`) REFERENCES `t_ontology_term` (`c_ontology_term_id`)
)"""

createOntologyTermRelation = """
CREATE TABLE `t_ontology_term_relation` (
  `c_relationship_id` int NOT NULL AUTO_INCREMENT,
  `c_subject_term_label` varchar(2000) DEFAULT NULL,
  `c_subject_term_id` varchar(100) DEFAULT NULL,
  `c_predicate_term_label` varchar(100) DEFAULT NULL,
  `c_predicate_term_id` varchar(100) DEFAULT NULL,
  `c_object_term_label` varchar(1000) DEFAULT NULL,
  `c_object_term_id` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`c_relationship_id`)
)"""

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

# Simple function to execute SQL commands
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query success")
    except Error as err:
        print(f"Error: '{err}'")


# Unused function that returns all cell ids from a given ontology
def select_multiple(ontology):
    sparql = SPARQLWrapper("https://sparql.hegroup.org/sparql")
    sparql.setReturnFormat(JSON)
    query = """SELECT ?clId ?label
FROM <http://purl.obolibrary.org/obo/merged/{o}>
WHERE
{
?s a owl:Class .
?s rdfs:label ?label .

FILTER regex( ?s, "{o}_" )
BIND(REPLACE(STR(?s), "http://purl.obolibrary.org/obo/", "") AS ?clId)
}
"""
    query = query.replace("{o}", ontology)
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()
        for ret in results["results"]["bindings"]:
            cell_id = ret["clId"]["value"]
            queryResult = perform_query(cell_id, ontology, False)
            catch_results(queryResult)
        connection.commit()
        cursor.close()
        connection.close()


    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Performs the main query where all the data comes from
def perform_query(cell_id, ontology, subclassBool, cellBool):
    sparql = SPARQLWrapper("https://sparql.hegroup.org/sparql")
    sparql.setReturnFormat(JSON)

    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX obo-term: <http://purl.obolibrary.org/obo/>
    PREFIX obo-owl: <http://www.geneontology.org/formats/oboInOwl#>
    
    {cellID}
    
    SELECT DISTINCT ?clId (str(?label) AS ?label) ?partID (GROUP_CONCAT(DISTINCT ?partOf; SEPARATOR=", ") AS ?partOf)
        (str(?definition) AS ?definition) 
    (str(?DerivesFromSomePartOf) AS ?DerivesFromSomePartOf) (GROUP_CONCAT(DISTINCT ?database; SEPARATOR=", ") AS ?database) (GROUP_CONCAT(DISTINCT ?exactSynonym; SEPARATOR=", ") AS ?exactSynonyms) (GROUP_CONCAT(DISTINCT ?broadSynonym; SEPARATOR=", ") AS ?broadSynonyms) (str(?narrowSyn) AS ?narrowSyn)
    (str(?parent) AS ?parent) (str(?label_p) AS ?label_p) 

    FROM <http://purl.obolibrary.org/obo/merged/{onto}>

    WHERE {
            
        {p}

        ?cell_id  rdfs:label ?label.
        
        OPTIONAL { ?cell_id  rdfs:subClassOf ?p.
                    ?p rdfs:label ?label_p.}
        
        # Retrieve the definition
        OPTIONAL { ?cell_id  obo-term:IAO_0000115 ?definition. }

        OPTIONAL { ?cell_id obo-owl:hasDbXref ?database.}

        OPTIONAL { ?cell_id  obo-owl:hasExactSynonym ?exactSynonym. }

        # Retrieve broad synonyms
        OPTIONAL { ?cell_id obo-owl:hasBroadSynonym ?broadSynonym. }
         
        OPTIONAL { ?cell_id obo-owl:hasNarrowSynonym ?narrowSyn }

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
        BIND(REPLACE(STR(?cell_id), "http://purl.obolibrary.org/obo/", "") AS ?clId)
        BIND(REPLACE(STR(?part), "http://purl.obolibrary.org/obo/", "") AS ?partID)
        BIND(REPLACE(STR(?p), "http://purl.obolibrary.org/obo/", "") AS ?parent)

  }
    """

    query = query.replace("{onto}", ontology)

    if not cellBool:
        query = query.replace("{cellID}", "PREFIX cell: <http://purl.obolibrary.org/obo/" + cell_id + ">")
        if subclassBool:
            query = query.replace("{p}", """?cell_id rdfs:subClassOf* cell: .""")
        else:
            query = query.replace("{p}", """?cell_id rdf:type owl:Class .
            FILTER(?cell_id = cell:)
                    OPTIONAL { ?cell_id  rdfs:subClassOf ?p.
                    ?p rdfs:label ?label_p.}""")
    else:
        query = query.replace("{cellID}", "")
        query = query.replace("{p}", """?cell_id a owl:Class .
                   FILTER regex( ?cell_id, \"""" + ontology + """_\")""")

    #print(query)
    sparql.setQuery(query)

    try:
        results = sparql.query().convert()

        results["head"]["vars"].append("ontology")
        y = {'type':'literal', 'value': ontology}
        for x in results["results"]["bindings"]:
            x["ontology"] = y

        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Prevents error by not trying to access a Null value that might be returned from the SPARQL query
def get_value_from_result(key: str, obj: object) -> str:
    if key in obj:
        return obj[key]["value"]
    return ''


def insertOntologyTerm(cellId, cellLabel, cellDefinition, ontology, databaseRef):
    database_list = databaseRef.replace(',', ';')
    cursor.execute(insertOntologyTermQuery, (cellId, cellLabel, cellDefinition, ontology, database_list))

# Checks for duplicates in the db
def duplicate (tableName, id, cursor) -> bool:
    query = ("SELECT * FROM " + tableName +" WHERE c_ontology_term_id = '" + id + "'")
    cursor.execute(query)
    d = False
    if cursor.rowcount == 1:
        d = True
    return d

def insertSyn(synLabel, cell_id, annotation_label,annotation_property_iri, synonym_type):
    synLabelList = synLabel.split(',')
    for syn in synLabelList:
        syn = syn.strip()
        cursor.execute(insertSYN,(syn, cell_id,
                                  annotation_label,
                                  annotation_property_iri, synonym_type))



def insertOntologyTermRelation( subject_term_label,
                               subject_term_id, predicate_term_label, predicate_term_id,
                               object_term_label, object_term_id):
    cursor.execute(insertOntolTermRelt, (subject_term_label,subject_term_id,predicate_term_label,predicate_term_id,
                            object_term_label, object_term_id))


# Parses JSON into insert statement (no input file)
def catch_results(ret):
    if ret["results"]["bindings"] is None:
        print("No results.")
    else:
        for result in ret["results"]["bindings"]:
            cell_id = result["clId"]["value"]

            if duplicate("t_ontology_term", cell_id, cursor):
                continue

            label = result["label"]["value"]
            ontology = result["ontology"]["value"]

            definition = get_value_from_result("definition", result)
            parent = get_value_from_result("parent", result)
            label_p = get_value_from_result("label_p", result)
            #TODO: get id from this if not null
            derivesFromSomePartOf = get_value_from_result("DerivesFromSomePartOf", result)

            exactSynonyms = get_value_from_result("exactSynonyms", result)
            broadSynonyms = get_value_from_result("broadSynonyms", result)
            narrowSynonyms = get_value_from_result("narrowSyn", result)
            databaseRef = get_value_from_result("database", result)
            partOf = get_value_from_result("partOf", result)
            partOfId = get_value_from_result("partID", result)

            insert_terms(exactSynonyms, broadSynonyms, narrowSynonyms,databaseRef,partOf,partOfId,
                         cell_id, label, definition, ontology, parent, label_p)




def insert_terms(exactSynonyms, broadSynonyms, narrowSynonyms,databaseRef,partOf,partOfId, cell_id, label, definition, ontology, parent, label_p):
    insertOntologyTerm(cell_id, label, definition, ontology, databaseRef)
    if broadSynonyms:
        insertSyn(broadSynonyms, cell_id, "has_broad_synonym", "hasBroadSynonym", "broad synonym")
    if exactSynonyms:
        insertSyn(exactSynonyms, cell_id, "has_exact_synonym", "hasExactSynonym", "exact synonym")
    if narrowSynonyms:
        insertSyn(narrowSynonyms, cell_id, "has_narrow_synonym", "hasNarrowSynonym", "narrow synonym")
    if partOf:
        insertOntologyTermRelation(label, cell_id,
                                   "part of", "BFO_0000050",
                                   partOf, partOfId)
        #TODO:
    if parent:
        insertOntologyTermRelation(label, cell_id,
                                   "subClassOf", "rdfs:subClassOf",
                                   label_p, parent)

    connection.commit()


def output(fileName, ret):
    if fileName is not None:
        writeFile(fileName, ret)
        print('File created successfully\n')
    else:
        printResults(ret)
    if input('Proceed with insertion? (y/n): ').lower().strip() == 'y':
        catch_results(ret)


def printResults(ret):
    headers = []
    for x in ret["head"]["vars"]:
        headers.append(x)
    print(headers)
    for result in ret["results"]["bindings"]:
        cell_id = result["clId"]["value"]
        label = result["label"]["value"]
        ontology = result["ontology"]["value"]
        definition = get_value_from_result("definition", result)
        derivesFromSomePartOf = get_value_from_result("DerivesFromSomePartOf", result)
        exactSynonyms = get_value_from_result("exactSynonyms", result)
        broadSynonyms = get_value_from_result("broadSynonyms", result)
        narrowSynonyms = get_value_from_result("narrowSyn", result)
        databaseRef = get_value_from_result("database", result)
        partOf = get_value_from_result("partOf", result)
        partOfId = get_value_from_result("partID", result)

        parent = get_value_from_result("parent", result)
        label_p = get_value_from_result("label_p", result)
        print(
            [cell_id, label, partOfId,definition, derivesFromSomePartOf, databaseRef, exactSynonyms, broadSynonyms,
             partOf, narrowSynonyms, parent, label_p,
             ontology])


def writeFile(fileName, ret):
    headers = []
    for x in ret["head"]["vars"]:
        headers.append(x)
    with open(fileName, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        for result in ret["results"]["bindings"]:
            cell_id = result["clId"]["value"]
            label = result["label"]["value"]
            ontology = result["ontology"]["value"]
            definition = get_value_from_result("definition", result)
            derivesFromSomePartOf = get_value_from_result("DerivesFromSomePartOf", result)
            exactSynonyms = get_value_from_result("exactSynonyms", result)
            broadSynonyms = get_value_from_result("broadSynonyms", result)
            narrowSynonyms = get_value_from_result("narrowSyn", result)
            databaseRef = get_value_from_result("database", result)
            partOf = get_value_from_result("partOf", result)
            partOfId = get_value_from_result("partID", result)

            parent = get_value_from_result("parent", result)
            label_p = get_value_from_result("label_p", result)
            writer.writerow([cell_id,label,partOfId,partOf,definition,derivesFromSomePartOf,databaseRef,exactSynonyms,broadSynonyms,narrowSynonyms, parent, label_p,
                             ontology])


if __name__ == "__main__":
    # Change pw for password in database
    pw = "maryczelus009"
    # Change db for name of database
    db = "testing"

    connection = create_database_connection("localhost", "root", pw, db)
    # The following commented code creates the ontology term,
    # ontology term relation and synonym table into the database, respectively
    execute_query(connection, createOntologyTerm)
    execute_query(connection, createOntologyTermRelation)
    execute_query(connection, createTsynonymTable)
    cursor = connection.cursor(buffered=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output" ,help="Writes the result of the SPARQL query in a csv file named OUTPUT",
                        type=str)
    parser.add_argument("-in", "--input", help="Performs insertion on given IDs from INPUT csv file (either type the file address or place the file in the same folder that the script is running in)",
                        type=str)
    args = parser.parse_args()
    outputFileName = args.output

    if args.input:
        try:
            file = pd.read_csv(args.input)
            result = (perform_query(file.values[0][0], file.values[0][2], file.values[0][3].lower().strip() == 'y', False))
            for i in range(1,len(file)):
                cellID = file.values[i][0]
                ontology = file.values[i][2]
                subclassBool = file.values[i][3].lower().strip() == 'y'
                temp = perform_query(cellID, ontology, subclassBool, False)
                for dicts in temp["results"]["bindings"]:
                    result["results"]["bindings"].append(dicts)

            output(outputFileName, result)
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"An error occurred: {e}")
            exit(1)
    else:
        ontology = input("Enter ontology: ")
        cellBool = input('All cells from ' + ontology + '? (y/n): ').lower().strip() == 'y'
        if not cellBool:
            cellID = input("Enter the cell ID: ")
            subclassBool = input('All subclasses? (y/n): ').lower().strip() == 'y'
            result = perform_query(cellID, ontology, subclassBool, cellBool)
        else:
            result = perform_query(None, ontology, None, cellBool)
        output(outputFileName, result)
        cursor.close()
        connection.close()


