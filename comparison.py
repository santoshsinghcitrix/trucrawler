import hashlib
import json
import glob
import os
import constants


def comapare_data():
    hashed_current_pagesource_data = []
    diff = []
    files_list = glob.glob(os.path.join(constants.ROOT_DIR, "images", '') + "*")
    for file_name in files_list :
        hashed_current_pagesource_data.append(file_name.split("__")[1].split(".png")[0])

    f = open('previous_pagesources.json', "r")
    previous_hashed_data = json.loads(f.read())
    f.close()
    for item in hashed_current_pagesource_data:
        if item not in previous_hashed_data:
            diff.append(item)

    all_data = previous_hashed_data + diff
    with open("previous_pagesources.json", "w") as jsonFile:
        json.dump(all_data, jsonFile)
    with open("diff.json", "w") as jsonFile:
        json.dump(diff, jsonFile)
    print("Diff::")
    print(diff)