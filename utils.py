import json


def save_to_json(data, filename):
    """Save data to a JSON file."""
    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=4)


def load_json(name):
    # Open and load the JSON file into a Python dictionary
    with open(name, "r") as json_file:
        roster = json.load(json_file)

    return roster
