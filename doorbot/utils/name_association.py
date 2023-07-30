from fuzzywuzzy import fuzz, process
import json

def best_match(name, dictionary):
    """Find the best fuzzy match for name in the dictionary."""
    names = [value["name"] for value in dictionary.values()]
    best_match = process.extractOne(name, names)
    if best_match[1] >= 90:  # if similarity is above 70
        return best_match[0]
    else:
        return None

def is_substring(name1, name2):
    """Check if name1 is a substring of name2 or vice versa."""
    return name1.lower() in name2.lower() or name2.lower() in name1.lower()

def find_substring_match(name, dictionary):
    """Find a substring match for name in the dictionary."""
    for value in dictionary.values():
        if is_substring(name, value["name"]):
            return value["name"]
    return None

def name_associations(tidyhq, legacy, output_file):
    """Generate a JSON file with name associations between tidyhq and legacy."""
    # Load data from json files
    with open(tidyhq, 'r') as f:
        tidyhq_dict = json.load(f)
    with open(legacy, 'r') as f:
        legacy_dict = json.load(f)

    # Initialize dictionaries for matches and differences
    id_match = []
    id_different = []
    tidyhq_without_match = []
    legacy_without_match = []

    # For storing matched legacy names
    matched_legacy_names = []

    # Find best match for each name in tidyhq_dict from legacy_dict
    for tidyhq_id, tidyhq_value in tidyhq_dict.items():
        tidyhq_name = tidyhq_value["name"]
        tidyhq_door = tidyhq_value.get('door', None)
        legacy_name = best_match(tidyhq_name, legacy_dict) or find_substring_match(tidyhq_name, legacy_dict)
        if legacy_name:
            # Find the corresponding id in legacy_dict
            legacy_id = [id for id, value in legacy_dict.items() if value["name"] == legacy_name][0]
            legacy_door = legacy_dict[legacy_id].get('door', None)
        elif tidyhq_id in legacy_dict:
            legacy_id = tidyhq_id
            legacy_name = legacy_dict[legacy_id]["name"]
            legacy_door = legacy_dict[legacy_id].get('door', None)
        else:
            tidyhq_without_match.append({
                "tidyhq_id": tidyhq_id,
                "tidyhq_name": tidyhq_name,
                "tidyhq_door": tidyhq_door
            })
            continue

        matched_legacy_names.append(legacy_name)
        if tidyhq_id == legacy_id:
            id_match.append({
                "tidyhq_id": tidyhq_id, 
                "tidyhq_name": tidyhq_name, 
                "tidyhq_door": tidyhq_door,
                "legacy_id": legacy_id, 
                "legacy_name": legacy_name,
                "legacy_door": legacy_door
            })
        else:
            id_different.append({
                "tidyhq_id": tidyhq_id, 
                "tidyhq_name": tidyhq_name, 
                "tidyhq_door": tidyhq_door,
                "legacy_id": legacy_id, 
                "legacy_name": legacy_name,
                "legacy_door": legacy_door
            })

    # Find legacy names without a match in tidyhq
    for legacy_id, legacy_value in legacy_dict.items():
        if legacy_value.get('door', 1) != 0:  # Ignore if door equals 0
            legacy_name = legacy_value["name"]
            legacy_door = legacy_value.get('door', None)
            if legacy_name not in matched_legacy_names and not find_substring_match(legacy_name, tidyhq_dict):
                legacy_without_match.append({
                    "legacy_id": legacy_id,
                    "legacy_name": legacy_name,
                    "legacy_door": legacy_door
                })

    # Sort each category by name
    id_match = sorted(id_match, key=lambda x: x['tidyhq_name'])
    id_different = sorted(id_different, key=lambda x: x['tidyhq_name'])
    tidyhq_without_match = sorted(tidyhq_without_match, key=lambda x: x['tidyhq_name'])
    legacy_without_match = sorted(legacy_without_match, key=lambda x: x['legacy_name'])

    # Write associations to output file
    associations = {"id_match": id_match, "id_different": id_different, 
                    "tidyhq_without_match": tidyhq_without_match, "legacy_without_match": legacy_without_match}
    with open(output_file, 'w') as f:
        json.dump(associations, f, indent=4)

    print(f'Name associations saved to {output_file}.')

    # Print the number of items in each category
    print(f'Number of ID matches: {len(id_match)}')
    print(f'Number of ID differences: {len(id_different)}')
    print(f'Number of TidyHQ names without match: {len(tidyhq_without_match)}')
    print(f'Number of Legacy names without match: {len(legacy_without_match)}')

# usage
name_associations(
    '/mnt/usbdrive/doorbot-data/user_cache.json', 
    '/mnt/usbdrive/doorbot-data/keys_converted.json', 
    '/mnt/usbdrive/doorbot-data/associations.json')
