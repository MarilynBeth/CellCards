import sql_statements
def catch_results(ret, cursor, connection, ontology):
    cellList = []
    if ret["results"]["bindings"] is None:
        print("No results.")
    else:
        for result in ret["results"]["bindings"]:
            cell_id = result["clId"]["value"]
            cellList.append(cell_id)

            if duplicate("t_ontology_term", cell_id, cursor):
                continue

            label = result["label"]["value"]
            #ontology = result["ontology"]["value"]

            definition = get_value_from_result("definition", result)
            parent = get_value_from_result("parent", result)
            label_p = get_value_from_result("label_p", result)
            # TODO: get id from this if not null
            derivesFromSomePartOf = get_value_from_result("DerivesFromSomePartOf", result)

            exactSynonyms = get_value_from_result("exactSynonyms", result)
            broadSynonyms = get_value_from_result("broadSynonyms", result)
            narrowSynonyms = get_value_from_result("narrowSyn", result)
            databaseRef = get_value_from_result("database", result)
            partOf = get_value_from_result("partOf", result)
            partOfId = get_value_from_result("partID", result)

            insert_terms(connection, cursor, exactSynonyms, broadSynonyms, narrowSynonyms, databaseRef, partOf,
                         partOfId,
                         cell_id, label, definition, ontology, parent, label_p)


def insert_terms(connection, cursor, exactSynonyms, broadSynonyms, narrowSynonyms, databaseRef, partOf, partOfId,
                 cell_id,
                 label,
                 definition, ontology, parent, label_p):
    sql_statements.insertOntologyTerm(cursor, cell_id, label, definition, ontology, databaseRef)
    sql_statements.insertInTCells(cursor, cell_id, label, None, None)
    if broadSynonyms:
        sql_statements.insertSyn(cursor, broadSynonyms, cell_id, "has_broad_synonym", "hasBroadSynonym",
                                    "broad synonym")
    if exactSynonyms:
        sql_statements.insertSyn(cursor, exactSynonyms, cell_id, "has_exact_synonym", "hasExactSynonym",
                                    "exact synonym")
    if narrowSynonyms:
        sql_statements.insertSyn(cursor, narrowSynonyms, cell_id, "has_narrow_synonym", "hasNarrowSynonym",
                                    "narrow synonym")
    if partOf:
        sql_statements.insertOntologyTermRelation(cursor, label, cell_id,
                                                     "part of", "BFO_0000050",
                                                     partOf, partOfId)
        # TODO:
    if parent:
        sql_statements.insertOntologyTermRelation(cursor, label, cell_id,
                                                     "subClassOf", "rdfs:subClassOf",
                                                     label_p, parent)

    connection.commit()




# Prevents error by not trying to access a Null value that might be returned from the SPARQL query
def get_value_from_result(key: str, obj: object) -> str:
    if key in obj:
        return obj[key]["value"]
    return ''


# Checks for duplicates in the db
#TODO: c_ontology_term_id might not work for the other tables as a means to check for duplicate CELLS (not biomarkers)
def duplicate(tableName, arg_id, cursor) -> bool:
    query = ("SELECT * FROM " + tableName + " WHERE c_ontology_term_id = '" + arg_id + "'")
    cursor.execute(query)
    d = False
    if cursor.rowcount == 1:
        d = True
    return d
