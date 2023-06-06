import json
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def best_match(name, dict_names, score_cutoff=80):
    """Return the best match to the name from dict_names.
    Only return matches with a score above score_cutoff."""
    names_list = [v["name"] for v in dict_names.values()]
    best_match = process.extractOne(name, names_list, scorer=fuzz.token_sort_ratio)
    if best_match and best_match[1] > score_cutoff:
        return best_match[0]
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
        legacy_name = best_match(tidyhq_name, legacy_dict)
        if legacy_name:
            # Find the corresponding id in legacy_dict
            legacy_id = [id for id, value in legacy_dict.items() if value["name"] == legacy_name][0]
            legacy_door = legacy_dict[legacy_id].get('door', None)
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
        else:
            tidyhq_without_match.append({
                "tidyhq_id": tidyhq_id,
                "tidyhq_name": tidyhq_name,
                "tidyhq_door": tidyhq_door
            })

    # Find legacy names without a match in tidyhq
    for legacy_id, legacy_value in legacy_dict.items():
        if legacy_value.get('door', 1) != 0:  # Ignore if door equals 0
            legacy_name = legacy_value["name"]
            legacy_door = legacy_value.get('door', None)
            if legacy_name not in matched_legacy_names:
                legacy_without_match.append({
                    "legacy_id": legacy_id,
                    "legacy_name": legacy_name,
                    "legacy_door": legacy_door
                })

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
name_associations('user_cache.json', 'legacy-converted.json', 'associations.json')
