import threading
import sparql_queries
import sql_statements
import uni_prot_query


def parse_biomarkers(cursor, connection, hgnc_ids):
    terms_to_insert = dict()
    someList = dict(sql_statements.get_cell_id(cursor))
    set_of_all_hgnc = []
    for id in hgnc_ids["results"]["bindings"]:
        hgnc_id = id["hgnc_id"]["value"]
        if hgnc_id not in set_of_all_hgnc:
            set_of_all_hgnc.append(hgnc_id)
        cell_id = id["cell_id"]["value"]
        table_id = someList[cell_id]
        if hgnc_id not in terms_to_insert:
            terms_to_insert[hgnc_id] = [id["gene_label"]["value"], table_id]
        else:
            terms_to_insert[hgnc_id].append(table_id)
        # dict has key hgnc and list in order = gene_label, cell_id, cell_id......
        # Note that cell_id refers to id from table t_cells

        #print(id["cell_id"]["value"])

    print("done")
    return terms_to_insert, set_of_all_hgnc


def add_entrez_and_pr(terms, hgnc_entrez_uniprot, cursor, connection):
    for key in terms:
        gene_label = terms[key][0]
        uniprot_id = hgnc_entrez_uniprot[key][0]
        entrez_id = hgnc_entrez_uniprot[key][1]
        for i in range(1, len(terms[key])):
            sql_statements.insertInGeneTable(cursor, entrez_id, terms[key][i], key, gene_label, None, uniprot_id, None)
        connection.commit()

    # hgnc_entrez_uniprot[key] = [uniprot_id, entrez_id]
    # terms[key] = [label, cell_id, cell_id,......]


def get_biomarkers(cursor, connection):
    hgnc_ids = sparql_queries.get_hgnc(connection, cursor)
    terms, hgnc_set = parse_biomarkers(cursor, connection, hgnc_ids)
    #hgnc_entrez_uniprot = uni_prot_query.get_ids_from_hgnc(hgnc_set)
    add_entrez_and_pr(terms, thread_maker(hgnc_set), cursor, connection)
    print("done")


def thread_maker(list_of_hgnc_ids):
    # Function to handle thread creation and joining
    def create_and_start_threads(segments, results):
        threads = []
        for i, segment in enumerate(segments):
            thread = threading.Thread(target=uni_prot_query.get_ids_from_hgnc, args=(segment, results[i]))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()

    # Split the list into halves and then into quarters
    mid_index = len(list_of_hgnc_ids) // 2
    first_half = list_of_hgnc_ids[:mid_index]
    second_half = list_of_hgnc_ids[mid_index:]

    first_quarter = first_half[:len(first_half) // 2]
    second_quarter = first_half[len(first_half) // 2:]
    third_quarter = second_half[:len(second_half) // 2]
    fourth_quarter = second_half[len(second_half) // 2:]

    segments = [first_quarter, second_quarter, third_quarter, fourth_quarter]
    results = [{} for _ in range(4)]

    create_and_start_threads(segments, results)

    # Combine results
    combined_results = {}
    for result in results:
        combined_results.update(result)

    return combined_results
