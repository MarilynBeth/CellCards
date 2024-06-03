import load_non_biomarker
import csv

def temp(ret,cursor, connection, ontology):
    load_non_biomarker.catch_results(ret, cursor, connection, ontology)
def output(fileName, ret, cursor):
    if fileName is not None:
        writeFile(fileName, ret)
        print('File created successfully\n')
    else:
        printResults(ret)
    if input('Proceed with insertion? (y/n): ').lower().strip() == 'y':
        load_non_biomarker.catch_results(ret, cursor)


def printResults(ret):
    headers = []
    for x in ret["head"]["vars"]:
        headers.append(x)
    print(headers)
    for result in ret["results"]["bindings"]:
        cell_id = result["clId"]["value"]
        label = result["label"]["value"]
        ontology = result["ontology"]["value"]
        definition = load_non_biomarker.get_value_from_result("definition", result)
        derivesFromSomePartOf = load_non_biomarker.get_value_from_result("DerivesFromSomePartOf", result)
        exactSynonyms = load_non_biomarker.get_value_from_result("exactSynonyms", result)
        broadSynonyms = load_non_biomarker.get_value_from_result("broadSynonyms", result)
        narrowSynonyms = load_non_biomarker.get_value_from_result("narrowSyn", result)
        databaseRef = load_non_biomarker.get_value_from_result("database", result)
        partOf = load_non_biomarker.get_value_from_result("partOf", result)
        partOfId = load_non_biomarker.get_value_from_result("partID", result)

        parent = load_non_biomarker.get_value_from_result("parent", result)
        label_p = load_non_biomarker.get_value_from_result("label_p", result)
        print(
            [cell_id, label, partOfId, definition, derivesFromSomePartOf, databaseRef, exactSynonyms, broadSynonyms,
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
            definition = load_non_biomarker.get_value_from_result("definition", result)
            derivesFromSomePartOf = load_non_biomarker.get_value_from_result("DerivesFromSomePartOf", result)
            exactSynonyms = load_non_biomarker.get_value_from_result("exactSynonyms", result)
            broadSynonyms = load.get_value_from_result("broadSynonyms", result)
            narrowSynonyms = load_non_biomarker.get_value_from_result("narrowSyn", result)
            databaseRef = load_non_biomarker.get_value_from_result("database", result)
            partOf = load.get_value_from_result("partOf", result)
            partOfId = load_non_biomarker.get_value_from_result("partID", result)

            parent = load_non_biomarker.get_value_from_result("parent", result)
            label_p = load.get_value_from_result("label_p", result)
            writer.writerow(
                [cell_id, label, partOfId, partOf, definition, derivesFromSomePartOf, databaseRef, exactSynonyms,
                 broadSynonyms, narrowSynonyms, parent, label_p,
                 ontology])