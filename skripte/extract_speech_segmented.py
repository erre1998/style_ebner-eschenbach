import os
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
    token = ordinal_str.split()[0].strip()
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
    Creates mappings from character IDs to full names and to abbreviated gender labels (M, F, U).
    """
    name_map = {}
    sex_map = {}
    abbreviation = {'male': 'M', 'female': 'F'}

    for person in root.findall('.//tei:person', NS):
        pid = person.get('{http://www.w3.org/XML/1998/namespace}id')
        sex_attr = person.get('sex', 'unknown').lower()
        sex_abbr = abbreviation.get(sex_attr, 'U')
        persName_el = person.find('tei:persName', NS)
        if pid and persName_el is not None:
            full_name = ' '.join(persName_el.itertext()).strip()
            name_map[pid] = full_name
            sex_map[pid] = sex_abbr

    for grp in root.findall('.//tei:personGrp', NS):
        gid = grp.get('{http://www.w3.org/XML/1998/namespace}id')
        sex_attr = grp.get('sex', 'unknown').lower()
        sex_abbr = abbreviation.get(sex_attr, 'U')
        name_el = grp.find('tei:name', NS)
        if gid and name_el is not None:
            name_map[gid] = ' '.join(name_el.itertext()).strip()
            sex_map[gid] = sex_abbr

    return name_map, sex_map


def process_sp(sp, grouping_key, speeches, NS):
    """
    Extracts the speech text from a <sp> block and adds it to all corresponding speaker entries.
    grouping_key is the act or scene number used in naming the file.
    """
    who_attr = sp.get('who', '')
    speaker_ids = [i.strip().lstrip('#') for i in who_attr.split() if i.strip()]
    if not speaker_ids:
        return

    texts = []
    elems = sp.findall('.//tei:p', NS) or sp.findall('.//tei:l', NS)
    for elem in elems:
        txt = extract_text_without_stage(elem).strip()
        if txt:
            texts.append(txt)
    if not texts:
        return
    full_text = '\n'.join(texts)

    for sid in speaker_ids:
        key = (sid, grouping_key)
        speeches.setdefault(key, []).append(full_text)


def process_file(file_path, output_folder):
    """
    Processes a TEI XML file and writes each character's speech to separate TXT files.
    File naming: {GenderAbbr}_{Name}_{ActOrScene}.txt
    """
    NS = {'tei': 'http://www.tei-c.org/ns/1.0'}
    tree = ET.parse(file_path)
    root = tree.getroot()

    name_map, sex_map = build_person_mappings(root, NS)
    speeches = {}

    acts = root.findall('.//tei:div[@type="act"]', NS)
    if len(acts) == 1:
        for scene in acts[0].findall('.//tei:div[@type="scene"]', NS):
            head = scene.find('tei:head', NS)
            key = convert_ordinal(head.text) if head is not None and head.text else 'Unknown'
            for sp in scene.findall('.//tei:sp', NS):
                process_sp(sp, key, speeches, NS)
    else:
        for act in acts:
            head = act.find('tei:head', NS)
            key = convert_ordinal(head.text) if head is not None and head.text else 'Unknown'
            for sp in act.findall('.//tei:sp', NS):
                process_sp(sp, key, speeches, NS)

    os.makedirs(output_folder, exist_ok=True)
    for (sid, group_key), texts in speeches.items():
        speaker_name = name_map.get(sid, sid)
        gender_abbr = sex_map.get(sid, 'U')
        file_name = f"{gender_abbr}_{speaker_name}_{group_key}.txt"
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
