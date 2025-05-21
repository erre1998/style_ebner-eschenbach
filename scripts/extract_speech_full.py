import os
import re
import xml.etree.ElementTree as ET


def convert_ordinal(ordinal_str):
    """
    Converts a German ordinal term (from the head, e.g., "Erster", "Zweiter") 
    to a number string.
    """
    mapping = {
        "Erster": "1", "Zweiter": "2", "Dritter": "3", "Vierter": "4",
        "Fünfter": "5", "Sechster": "6", "Siebter": "7", "Achter": "8",
        "Neunter": "9", "Zehnter": "10", "Elfter": "11", "Zwölfter": "12"
    }
    token = ordinal_str.split()[0].strip() if ordinal_str else ''
    return mapping.get(token, token)


def extract_text_without_stage(elem):
    """
    Recursively extracts the text of an element, ignoring content from <stage> and <speaker> elements.
    """
    text = elem.text or ""
    for child in elem:
        if not (child.tag.endswith('stage') or child.tag.endswith('speaker')):
            text += extract_text_without_stage(child)
        if child.tail:
            text += child.tail
    return text


def build_person_mappings(root, NS):
    """
    Creates mappings from character IDs to full names and to gender labels.
    """
    name_map = {}
    sex_map = {}
    for person in root.findall('.//tei:person', NS):
        pid = person.get('{http://www.w3.org/XML/1998/namespace}id')
        sex_attr = person.get('sex', 'UNKNOWN')
        sex_label = sex_attr.title()
        persName_el = person.find('tei:persName', NS)
        if pid and persName_el is not None:
            full_name = ' '.join(persName_el.itertext()).strip()
            name_map[pid] = full_name
            sex_map[pid] = sex_label
    for grp in root.findall('.//tei:personGrp', NS):
        gid = grp.get('{http://www.w3.org/XML/1998/namespace}id')
        sex_attr = grp.get('sex', 'UNKNOWN')
        sex_map[gid] = sex_attr.title()
        name_el = grp.find('tei:name', NS)
        if gid and name_el is not None:
            name_map[gid] = ' '.join(name_el.itertext()).strip()
    return name_map, sex_map


def sanitize_filename(name):
    """
    Remove or replace characters that are invalid in filenames.
    """
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def process_sp(sp, speaker_map, speeches, NS):
    """
    Extracts the speech text from a <sp> block and accumulates it per speaker ID.
    """
    who_attr = sp.get('who', '')
    speaker_ids = [i.strip().lstrip('#') for i in who_attr.split() if i.strip()]
    if not speaker_ids:
        return

    elems = sp.findall('.//tei:p', NS) or sp.findall('.//tei:l', NS)
    for elem in elems:
        txt = extract_text_without_stage(elem).strip()
        if txt:
            for sid in speaker_ids:
                speeches.setdefault(sid, []).append(txt)


def extract_title(root, NS):
    """
    Extracts the title of the play from the TEI header.
    """
    title_el = root.find('.//tei:titleStmt/tei:title', NS)
    if title_el is not None and title_el.text:
        return title_el.text.strip()
    # fallback: file-based title if needed
    return 'UnknownTitle'


def process_file(file_path, output_folder):
    """
    Processes a TEI XML file and writes each character's full speech to separate TXT files.
    File naming: GenderAbbr_Title_SpeakerName.txt
    """
    NS = {'tei': 'http://www.tei-c.org/ns/1.0'}
    tree = ET.parse(file_path)
    root = tree.getroot()

    name_map, sex_map = build_person_mappings(root, NS)
    # Map gender to abbreviation
    abbr_map = {'Male': 'M', 'Female': 'F'}

    # Extract title of the piece
    title = sanitize_filename(extract_title(root, NS))

    speeches = {}

    # Collect all speeches
    for sp in root.findall('.//tei:sp', NS):
        process_sp(sp, name_map, speeches, NS)

    os.makedirs(output_folder, exist_ok=True)
    for sid, texts in speeches.items():
        speaker_name = sanitize_filename(name_map.get(sid, sid))
        gender_full = sex_map.get(sid, 'Unknown')
        gender_abbr = abbr_map.get(gender_full, 'U')
        file_name = f"{gender_abbr}_{title}_{speaker_name}.txt"
        output_path = os.path.join(output_folder, file_name)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(texts))
    print(f"Processed: {file_path}\nResults saved in: {output_folder}")


def main():
    # Configuration: Paths for input and output files
    input_folder = r"E:\python\input"
    output_folder = r"E:\python\output"

    for fname in os.listdir(input_folder):
        if fname.lower().endswith('.xml'):
            process_file(os.path.join(input_folder, fname), output_folder)


if __name__ == '__main__':
    main()
