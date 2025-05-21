import requests
import pandas as pd
import time
import os

# Configuration: Paths for input and output files
input_file = r"E:\python\input"
output_file = r"E:\python\output"

def fetch_wikidata_entity(entity_id):
    """
    Fetches JSON data for an entity from Wikidata.
    :param entity_id: The Wikidata ID of the work (e.g., Q12345)
    :return: A dictionary with JSON data or None if an error occurs.
    """
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Checks for HTTP errors.
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {entity_id}: {e}")
        return None

def extract_person_ids(claims, property_key):
    """
    Extracts person IDs for a given property from claims.
    :param claims: The 'claims' dictionary from Wikidata data.
    :param property_key: The property key (e.g., 'P50' for author).
    :return: A list of found person IDs.
    """
    person_ids = []
    if property_key in claims:
        for claim in claims[property_key]:
            mainsnak = claim.get('mainsnak', {})
            datavalue = mainsnak.get('datavalue')
            if datavalue:
                value = datavalue.get('value')
                if isinstance(value, dict) and 'id' in value:
                    person_ids.append(value['id'])
    return person_ids

def main():
    # Check if the input file exists
    if not os.path.exists(input_file):
        print(f"File {input_file} not found.")
        return

    # Load the Excel file
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return

    # Ensure the column 'wikidataId' exists
    if 'wikidataId' not in df.columns:
        print("Column 'wikidataId' not found in the Excel file.")
        return

    # Add new columns for output
    df['Author_P50'] = None
    df['Composer_P86'] = None
    df['Librettist_P87'] = None

    # Process each row (each work)
    for idx, row in df.iterrows():
        entity_id = row['wikidataId']
        print(f"Processing work ID: {entity_id}")

        # Fetch Wikidata data
        data = fetch_wikidata_entity(entity_id)
        if data is None:
            print(f"  No data received for {entity_id}.")
            continue

        # Access entity data and claims
        entity_data = data.get('entities', {}).get(entity_id, {})
        claims = entity_data.get('claims', {})

        # Extract author (P50)
        author_ids = extract_person_ids(claims, 'P50')
        if author_ids:
            df.at[idx, 'Author_P50'] = ', '.join(author_ids)
            print(f"  Author(s): {author_ids}")
        else:
            print("  No authors found.")

        # Extract composer (P86)
        composer_ids = extract_person_ids(claims, 'P86')
        if composer_ids:
            df.at[idx, 'Composer_P86'] = ', '.join(composer_ids)
            print(f"  Composer(s): {composer_ids}")
        else:
            print("  No composers found.")

        # Extract librettist (P87)
        librettist_ids = extract_person_ids(claims, 'P87')
        if librettist_ids:
            df.at[idx, 'Librettist_P87'] = ', '.join(librettist_ids)
            print(f"  Librettist(s): {librettist_ids}")
        else:
            print("  No librettists found.")

        # Short pause to avoid overloading the API
        time.sleep(0.1)

    # Save processed data to a new Excel file
    try:
        df.to_excel(output_file, index=False)
        print(f"\nResults successfully saved to '{output_file}'.")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    main()
