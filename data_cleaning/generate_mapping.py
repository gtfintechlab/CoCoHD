import json

def generate_mapping(input_json):
    with open(input_json, 'r') as json_file:
        data = json.load(json_file)

    new_data = {}
    for key, values in data.items():
        for value in values:
            new_data[value] = key

    return new_data

def write(output_json):
    house_json = '../data/mappings/house_committee_names.json'
    senate_json = '../data/mappings/senate_committee_names.json'
    joint_json = '../data/mappings/joint_committee_names.json'

    house_data = generate_mapping(house_json)
    senate_data = generate_mapping(senate_json)
    joint_data = generate_mapping(joint_json)

    output_data = {'House of Representatives': house_data, 'Senate': senate_data, 'Joint': joint_data}

    with open(output_json, 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

if __name__ == "__main__":
    write('../data/mappings/committee_name_mapping.json')
