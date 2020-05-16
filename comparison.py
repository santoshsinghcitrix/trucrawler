import hashlib
import json


def comapare_data(current_pagesource_data):
    hashed_current_pagesource_data = []
    diff = []
    for pagesource in current_pagesource_data:
        result = hashlib.sha256(pagesource.encode())
        hashed_current_pagesource_data.append(result)

    f = open('previous_pagesources.json', "r")
    previous_hashed_data = json.loads(f.read())
    f.close()
    for item in hashed_current_pagesource_data:
        if item not in previous_hashed_data:
            diff.append(item)

    all_data = previous_hashed_data + diff
    with open("previous_pagesources.json", "w") as jsonFile:
        json.dump(all_data, jsonFile)