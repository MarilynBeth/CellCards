from SPARQLWrapper import SPARQLWrapper, JSON


#TODO: For now, it only does it for ALL cells in a given ontology
def get_hgnc(connection, cursor):
    sparql = SPARQLWrapper("https://sparql.hegroup.org/sparql")
    sparql.setReturnFormat(JSON)
    query = """PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
SELECT ?cell_id (str(?gene_label) AS ?gene_label) ?hgnc_id

FROM <https://purl.org/ccf/ccf.owl>
WHERE
{
    ?cell a owl:Class .
    FILTER (STRSTARTS(str(?cell) , "http://purl.obolibrary.org/obo/CL_" ))
    ?cell rdfs:subClassOf ?restriction .
    ?restriction owl:onProperty <http://purl.obolibrary.org/obo/RO_0015004> .
    ?restriction owl:someValuesFrom ?class .
    ?class rdf:type owl:Class .
    ?class owl:intersectionOf ?intersection .
    ?intersection rdf:rest*/rdf:first ?restriction2 .
    ?restriction2 owl:onProperty <http://purl.org/ccf/has_marker_component> .
    ?restriction2 owl:someValuesFrom ?gene .
    ?gene rdfs:label ?gene_label
    BIND(REPLACE(STR(?cell), "http://purl.obolibrary.org/obo/",
"") AS ?cell_id)
    BIND(REPLACE(STR(?gene), "http://identifiers.org/hgnc/","") AS ?hgnc_id)

}
"""
    sparql.setQuery(query)
    try:
        results = sparql.query().convert()

        """connection.commit()
        cursor.close()
        connection.close()"""
        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


#TODO: string.replace takes O(n) time, should change it so it does it in O(1)
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
        query = query.replace("{cellID}", f"PREFIX cell: <http://purl.obolibrary.org/obo/{cell_id}>")
        if subclassBool:
            query = query.replace("{p}", """?cell_id rdfs:subClassOf* cell: .""")
        else:
            query = query.replace("{p}", """?cell_id rdf:type owl:Class .
            FILTER(?cell_id = cell:)
                    OPTIONAL { ?cell_id  rdfs:subClassOf ?p.
                    ?p rdfs:label ?label_p.}""")
    else:
        query = query.replace("{cellID}", "")
        query = query.replace("{p}", f"""?cell_id a owl:Class .
                   FILTER regex( ?cell_id, \"{ontology}_\")""")

    # print(query)
    sparql.setQuery(query)

    try:
        results = sparql.query().convert()

        #results["head"]["vars"].append("ontology")
        #y = {'type': 'literal', 'value': ontology}
        #for x in results["results"]["bindings"]:
        #   x["ontology"] = y

        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
