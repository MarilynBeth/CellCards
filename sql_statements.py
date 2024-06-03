insertSYN = """
    INSERT INTO t_synonym(c_synonym_label, c_ontology_term_id, 
    c_synonym_annotation_property_label, c_synonym_annotation_property_iri,c_synonym_type)
    VALUES (%s, %s, %s, %s, %s)"""

insertOntolTermRelation = """
INSERT INTO t_ontology_term_relation(c_subject_term_label, c_subject_term_id, 
c_predicate_term_label, c_predicate_term_id,c_object_term_label, c_object_term_id)
VALUES (%s, %s, %s, %s, %s, %s)"""

insertOntologyTermQuery = """
INSERT INTO t_ontology_term(c_ontology_term_id,c_name, c_definition, c_source, c_database_reference)
VALUES (%s, %s, %s, %s, %s)"""

insert_in_t_gene_protein = """INSERT INTO t_gene_protein(c_entrez_gene_id, c_cell_id, c_HGNC_id, c_gene_label, c_OGG_id, c_PR_id, c_description) 
VALUES (%s, %s, %s, %s, %s, %s, %s)"""

insert_1000_in_t_gene_protein = """INSERT INTO t_gene_protein(c_entrez_gene_id, c_cell_id, c_HGNC_id, c_gene_label, c_OGG_id, c_PR_id, c_description) 
VALUES """

insert_in_t_cells = """INSERT INTO  t_cells(c_cell_ontology_term_id,c_cell_name,c_related_ontology_id,c_related_ontology_label) 
VALUES (%s, %s, %s, %s)"""


def insertOntologyTerm(cursor, cellId, cellLabel, cellDefinition, ontology, databaseRef):
    database_list = databaseRef.replace(',', ';')
    cursor.execute(insertOntologyTermQuery, (cellId, cellLabel, cellDefinition, ontology, database_list))


def insertSyn(cursor, synLabel, cell_id, annotation_label, annotation_property_iri, synonym_type):
    synLabelList = synLabel.split(',')
    for syn in synLabelList:
        syn = syn.strip()
        cursor.execute(insertSYN, (syn, cell_id,
                                   annotation_label,
                                   annotation_property_iri, synonym_type))


def insertOntologyTermRelation(cursor, subject_term_label,
                               subject_term_id, predicate_term_label, predicate_term_id,
                               object_term_label, object_term_id):
    cursor.execute(insertOntolTermRelation,
                   (subject_term_label, subject_term_id, predicate_term_label, predicate_term_id,
                    object_term_label, object_term_id))


def insertInGeneTable(cursor,entrez_id, cell_id,HGNC_id, gene_label,OGG_id, PR_id, description):
    cursor.execute(insert_in_t_gene_protein, (entrez_id, cell_id, HGNC_id, gene_label, OGG_id, PR_id, description))


def insertInTCells(cursor,cellID,  cell_label, related_id, related_label):
    cursor.execute(insert_in_t_cells, (cellID, cell_label, related_id, related_label))



#TODO: gets ALL cell_ids from t_cells
def get_cell_id(cursor):
    query = f"""SELECT c_cell_ontology_term_id, c_cell_id FROM t_cells"""
    cursor.execute(query)
    if cursor is not None:
        return list(cursor.fetchall())
