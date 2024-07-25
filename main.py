import pandas as pd
import argparse
import command_line
import create_tables
import connections
import sparql_queries
from load_biomarker import get_biomarkers

if __name__ == "__main__":
    # Change pw for password in database
    pw = ""
    # Change db for name of database
    db = ""

    connection = connections.create_database_connection("", "", pw, db)
    # The following commented code creates the ontology term,
    # ontology term relation and synonym table into the database, respectively

    connections.execute_query(connection, create_tables.createOntologyTerm)
    connections.execute_query(connection, create_tables.createTsynonymTable)
    connections.execute_query(connection, create_tables.createOntologyTermRelation)
    connections.execute_query(connection, create_tables.create_t_cells_table)
    connections.execute_query(connection, create_tables.create_t_gene_protein_table)

    cursor = connection.cursor(buffered=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", help="Writes the result of the SPARQL query in a csv file named OUTPUT",
                        type=str)
    parser.add_argument("-in", "--input",
                        help="Performs insertion on given IDs from INPUT csv file (either type the file address or "
                             "place the file in the same folder that the script is running in)",
                        type=str)
    args = parser.parse_args()
    outputFileName = args.output

    if args.input:
        try:
            file = pd.read_csv(args.input)
            result = (
                sparql_queries.perform_query(file.values[0][0], file.values[0][2], file.values[0][3].lower().strip() == 'y', False))
            for i in range(1, len(file)):
                cellID = file.values[i][0]
                ontology = file.values[i][2]
                subclassBool = file.values[i][3].lower().strip() == 'y'
                temp = sparql_queries.perform_query(cellID, ontology, subclassBool, False)
                for dicts in temp["results"]["bindings"]:
                    result["results"]["bindings"].append(dicts)

            command_line.output(outputFileName, result, cursor)
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"An error occurred: {e}")
            exit(1)
    else:
        #ontology = input("Enter ontology: ")
        #cellBool = input('All cells from ' + ontology + '? (y/n): ').lower().strip() == 'y'
        #if not cellBool:
            #cellID = input("Enter the cell ID: ")
            #subclassBool = input('All subclasses? (y/n): ').lower().strip() == 'y'
            #result = sparql_queries.perform_query(cellID, ontology, subclassBool, cellBool)
       # else:



        #TODO: reformat the logic behind this statement here
        result = sparql_queries.perform_query(None, 'CL', None, True)
        command_line.temp(result, cursor, connection, 'CL')
        get_biomarkers(cursor, connection)
        #command_line.output(outputFileName, result)


        cursor.close()
        connection.close()

