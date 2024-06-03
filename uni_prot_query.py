import requests
import time


def get_ids_from_hgnc(hgnc_ids, ids, batch_size=500):
    url = "https://rest.genenames.org/fetch/hgnc_id/"
    headers = {
        'Accept': 'application/json'
    }


    # Process HGNC IDs in batches
    for i in range(0, len(hgnc_ids), batch_size):
        batch_ids = hgnc_ids[i:i + batch_size]
        print(f"Processing batch: {i // batch_size + 1}/{-(-len(hgnc_ids) // batch_size)}")

        for hgnc_id in batch_ids:
            response = requests.get(f"{url}{hgnc_id}", headers=headers)

            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                if docs:
                    uniprot_ids = docs[0].get("uniprot_ids", [])
                    entrez_id = docs[0].get("entrez_id", None)
                    uniprot_id = uniprot_ids[0] if uniprot_ids else None
                    ids[hgnc_id] = [uniprot_id, entrez_id]
            else:
                print(f"Failed to retrieve data for HGNC ID: {hgnc_id}")
            #print(f"Processed HGNC ID: {hgnc_id}")

        time.sleep(0.1)  # Sleep to respect API rate limits

    return ids

